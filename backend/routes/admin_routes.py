"""Admin-only user and household management."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models.access import Household, HouseholdMember
from backend.models.user import User
from backend.services.auth import hash_password, require_admin
from backend.services.db_services import get_db

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


class AdminUserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"


class AdminUserUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    role: str | None = None
    is_active: bool | None = None


class PasswordReset(BaseModel):
    new_password: str


class HouseholdCreate(BaseModel):
    name: str
    members: list[dict]  # {"user_id": int, "scope_mode": "self"|"household"}


class HouseholdUpdate(BaseModel):
    name: str | None = None
    is_active: bool | None = None
    shared_domains: list[str] | None = None


class MemberUpdate(BaseModel):
    scope_mode: str


def _validate_role(role: str) -> str:
    if role not in ("user", "admin"):
        raise HTTPException(status_code=400, detail="Role must be user or admin")
    return role


def _validate_scope_mode(mode: str) -> str:
    if mode not in ("self", "household"):
        raise HTTPException(status_code=400, detail="scope_mode must be self or household")
    return mode


def _user_row(user: User) -> dict:
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": bool(user.is_active),
        "auth_provider": user.auth_provider,
        "must_change_password": bool(user.must_change_password),
    }


@router.get("/users")
def admin_list_users(db: Session = Depends(get_db)):
    rows = db.query(User).order_by(User.user_id).all()
    return [_user_row(row) for row in rows]


@router.post("/users", status_code=201)
def admin_create_user(payload: AdminUserCreate, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    if len(payload.password) < 10:
        raise HTTPException(status_code=400, detail="Use at least 10 characters")
    user = User(
        name=payload.name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role=_validate_role(payload.role),
        is_active=True,
        auth_provider="local",
        must_change_password=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_row(user)


@router.put("/users/{user_id}")
def admin_update_user(
    user_id: int, payload: AdminUserUpdate, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "role":
            value = _validate_role(value)
        if field == "email":
            value = value.strip().lower()
            clash = (
                db.query(User)
                .filter(User.email == value, User.user_id != user_id)
                .first()
            )
            if clash:
                raise HTTPException(status_code=409, detail="Email already in use")
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return _user_row(user)


@router.post("/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: int, payload: PasswordReset, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if len(payload.new_password) < 10:
        raise HTTPException(status_code=400, detail="Use at least 10 characters")
    if user.auth_provider != "local":
        raise HTTPException(status_code=400, detail="Password is managed by the SSO provider")
    user.password_hash = hash_password(payload.new_password)
    user.must_change_password = True
    db.commit()
    return {"status": "ok"}


@router.get("/households")
def admin_list_households(db: Session = Depends(get_db)):
    households = db.query(Household).order_by(Household.household_id).all()
    result = []
    for household in households:
        members = (
            db.query(HouseholdMember)
            .filter(HouseholdMember.household_id == household.household_id)
            .all()
        )
        result.append(
            {
                "household_id": household.household_id,
                "name": household.name,
                "is_active": bool(household.is_active),
                "shared_domains": household.shared_domains,
                "members": [
                    {
                        "user_id": m.user_id,
                        "name": (
                            db.query(User.name)
                            .filter(User.user_id == m.user_id)
                            .scalar()
                        ),
                        "scope_mode": m.scope_mode,
                    }
                    for m in members
                ],
            }
        )
    return result


@router.post("/households", status_code=201)
def admin_create_household(payload: HouseholdCreate, db: Session = Depends(get_db)):
    if len(payload.members) < 2:
        raise HTTPException(status_code=400, detail="A household needs two members")
    household = Household(
        name=payload.name.strip(),
        shared_domains="all",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db.add(household)
    db.flush()
    seen = set()
    for member in payload.members:
        user_id = int(member["user_id"])
        if user_id in seen:
            raise HTTPException(status_code=400, detail="Duplicate member")
        seen.add(user_id)
        if not db.query(User).filter(User.user_id == user_id).first():
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        db.add(
            HouseholdMember(
                household_id=household.household_id,
                user_id=user_id,
                scope_mode=_validate_scope_mode(member["scope_mode"]),
            )
        )
    db.commit()
    return {"household_id": household.household_id, "status": "ok"}


@router.put("/households/{household_id}")
def admin_update_household(
    household_id: int, payload: HouseholdUpdate, db: Session = Depends(get_db)
):
    household = (
        db.query(Household).filter(Household.household_id == household_id).first()
    )
    if not household:
        raise HTTPException(status_code=404, detail="Household not found")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data:
        household.name = data["name"]
    if "is_active" in data:
        household.is_active = data["is_active"]
    if "shared_domains" in data:
        household.shared_domains = ",".join(data["shared_domains"] or ["all"])
    db.commit()
    return {"status": "ok"}


@router.put("/households/{household_id}/members/{user_id}")
def admin_update_member(
    household_id: int,
    user_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
):
    member = (
        db.query(HouseholdMember)
        .filter(
            HouseholdMember.household_id == household_id,
            HouseholdMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.scope_mode = _validate_scope_mode(payload.scope_mode)
    db.commit()
    return {"status": "ok"}


@router.delete("/households/{household_id}/members/{user_id}")
def admin_remove_member(
    household_id: int, user_id: int, db: Session = Depends(get_db)
):
    member = (
        db.query(HouseholdMember)
        .filter(
            HouseholdMember.household_id == household_id,
            HouseholdMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(member)
    db.commit()
    return {"status": "ok"}
