"""Login, session, view switching and personal preferences."""

import base64
import hashlib
import json
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend import config
from backend.models.access import UserPreference
from backend.services.auth import (
    create_session_token,
    get_current_user,
    get_view_mode,
    hash_password,
    household_for_user,
    user_payload,
    verify_password,
)
from backend.services.db_services import get_db
from backend.services.identity_provider import get_identity_provider

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class ViewRequest(BaseModel):
    view: str  # 'personal' | 'household'


class PreferencesUpdate(BaseModel):
    theme: str | None = None
    filters: dict | None = None
    strategies: dict | None = None
    page_size: int | None = None


def set_session_cookies(response, user) -> None:
    response.set_cookie(
        config.SESSION_COOKIE,
        create_session_token(user),
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        max_age=config.SESSION_TTL_HOURS * 3600,
        path="/",
    )
    response.set_cookie(
        config.CSRF_COOKIE,
        secrets.token_urlsafe(32),
        httponly=False,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        max_age=config.SESSION_TTL_HOURS * 3600,
        path="/",
    )


def clear_session_cookies(response) -> None:
    for name in (config.SESSION_COOKIE, config.CSRF_COOKIE, config.VIEW_COOKIE):
        response.delete_cookie(name, path="/")


@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    provider = get_identity_provider()
    user = provider.authenticate_password(db, request.email.strip(), request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    user.last_login_at = datetime.utcnow()
    db.commit()
    response = JSONResponse(
        user_payload(user, db, "personal")
    )
    set_session_cookies(response, user)
    response.set_cookie(
        config.VIEW_COOKIE,
        "personal",
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        max_age=config.SESSION_TTL_HOURS * 3600,
        path="/",
    )
    return response


@router.get("/me")
def me(
    request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return user_payload(user, db, get_view_mode(request))


@router.post("/logout")
def logout():
    response = JSONResponse({"status": "ok"})
    clear_session_cookies(response)
    return response


@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    http_request: Request,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.auth_provider != "local":
        raise HTTPException(status_code=400, detail="Password is managed by the SSO provider")
    if len(request.new_password) < 10:
        raise HTTPException(status_code=400, detail="Use at least 10 characters")
    if not verify_password(request.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = hash_password(request.new_password)
    user.must_change_password = False
    db.commit()
    db.refresh(user)
    # Returning the fresh principal lets the UI route an admin to /admin even
    # if the page opened before the session had finished loading.
    return user_payload(user, db, get_view_mode(http_request))


@router.post("/view")
def set_view(
    request: ViewRequest,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if request.view not in ("personal", "household"):
        raise HTTPException(status_code=400, detail="Unknown view")
    if request.view == "household" and not household_for_user(db, user.user_id):
        raise HTTPException(
            status_code=403, detail="Household view is not enabled for this account"
        )
    response = JSONResponse({"status": "ok", "view": request.view})
    response.set_cookie(
        config.VIEW_COOKIE,
        request.view,
        httponly=True,
        samesite="lax",
        secure=config.COOKIE_SECURE,
        max_age=config.SESSION_TTL_HOURS * 3600,
        path="/",
    )
    return response


@router.get("/preferences")
def get_preferences(user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user.user_id)
        .first()
    )
    if not row:
        return {"theme": None, "filters": {}, "strategies": {}, "page_size": None}
    return {
        "theme": row.theme,
        "filters": json.loads(row.filters) if row.filters else {},
        "strategies": json.loads(row.strategies) if row.strategies else {},
        "page_size": row.page_size,
    }


@router.put("/preferences")
def put_preferences(
    update: PreferencesUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    row = (
        db.query(UserPreference)
        .filter(UserPreference.user_id == user.user_id)
        .first()
    )
    if not row:
        row = UserPreference(user_id=user.user_id)
        db.add(row)
    if update.theme is not None:
        row.theme = update.theme
    if update.filters is not None:
        row.filters = json.dumps(update.filters)
    if update.strategies is not None:
        row.strategies = json.dumps(update.strategies)
    if update.page_size is not None:
        row.page_size = update.page_size
    row.updated_at = datetime.utcnow()
    db.commit()
    return {"status": "ok"}


# --- OIDC / Authentik ---------------------------------------------------------
@router.get("/oidc/login")
def oidc_login():
    provider = get_identity_provider()
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).decode().rstrip("=")
    state = secrets.token_urlsafe(24)
    authorization_url = provider.authorization_url(state, challenge)
    if not authorization_url:
        raise HTTPException(status_code=400, detail="OIDC is not configured")
    response = RedirectResponse(authorization_url, status_code=307)
    for name, value in (
        ("mp_oidc_state", state),
        ("mp_oidc_verifier", verifier),
    ):
        response.set_cookie(
            name, value, httponly=True, samesite="lax",
            secure=config.COOKIE_SECURE, max_age=600, path="/",
        )
    return response


@router.get("/oidc/callback")
def oidc_callback(
    request: Request, db: Session = Depends(get_db)
):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    expected_state = request.cookies.get("mp_oidc_state")
    verifier = request.cookies.get("mp_oidc_verifier")
    if not code or not state or state != expected_state or not verifier:
        raise HTTPException(status_code=401, detail="Invalid OIDC callback")
    user = get_identity_provider().complete_login(db, code, verifier)
    if not user or not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")

    response = RedirectResponse("/", status_code=307)
    set_session_cookies(response, user)
    response.set_cookie(
        config.VIEW_COOKIE, "personal", httponly=True, samesite="lax",
        secure=config.COOKIE_SECURE,
        max_age=config.SESSION_TTL_HOURS * 3600, path="/",
    )
    response.delete_cookie("mp_oidc_state", path="/")
    response.delete_cookie("mp_oidc_verifier", path="/")
    return response
