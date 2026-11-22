"""Authentication, roles and per-user data scope.

Sessions are signed JWTs in an HttpOnly cookie. OIDC/Authentik can replace the
local password flow without changing any of the data-scoping code below.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from backend import config
from backend.models.access import Household, HouseholdMember
from backend.models.user import User
from backend.services.db_services import get_db


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_session_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user.user_id),
        "name": user.name,
        "role": user.role,
        "provider": user.auth_provider,
        "iat": now,
        "exp": now + timedelta(hours=config.SESSION_TTL_HOURS),
        "typ": "session",
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def decode_session_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
        if payload.get("typ") != "session":
            return None
        return payload
    except jwt.PyJWTError:
        return None


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    token = request.cookies.get(config.SESSION_COOKIE)
    payload = decode_session_token(token) if token else None
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid session")
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Account is not active")
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_admin_for_writes(
    request: Request, user: User = Depends(get_current_user)
) -> User:
    """Readers may list reference data; only admins may change it."""
    if request.method in ("POST", "PUT", "PATCH", "DELETE") and user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_view_mode(request: Request) -> str:
    """The user's chosen view for this login, from the persistent view cookie."""
    return (
        "household"
        if request.cookies.get(config.VIEW_COOKIE) == "household"
        else "personal"
    )


def household_for_user(db: Session, user_id: int) -> Household | None:
    return (
        db.query(Household)
        .join(HouseholdMember, HouseholdMember.household_id == Household.household_id)
        .filter(
            HouseholdMember.user_id == user_id,
            HouseholdMember.scope_mode == "household",
            Household.is_active.is_(True),
        )
        .first()
    )


def can_view_household(db: Session, user_id: int) -> bool:
    return household_for_user(db, user_id) is not None


def get_data_scope(
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[int]:
    """Owner ids visible for the current request.

    Admin accounts intentionally have an empty scope: they manage users and
    configuration but never see anyone's personal financial data. A regular
    user sees their own id, plus every household member's id only when they
    are permitted to use the combined view and have switched to it.
    """
    if user.role == "admin":
        return []
    scope = [user.user_id]
    if get_view_mode(request) == "household":
        household = household_for_user(db, user.user_id)
        if household:
            member_ids = [
                row[0]
                for row in db.query(HouseholdMember.user_id)
                .filter(HouseholdMember.household_id == household.household_id)
                .all()
            ]
            # Keep the authenticated user first: writes are always attributed
            # to them, even when reading a combined household view.
            scope = [user.user_id] + sorted(set(member_ids) - {user.user_id})
    return scope


def user_payload(
    user: User, db: Session, view: str = "personal"
) -> dict:
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "must_change_password": bool(user.must_change_password),
        "view": view,
        "can_household_view": can_view_household(db, user.user_id),
    }
