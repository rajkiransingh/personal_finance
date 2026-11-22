"""Pluggable identity providers.

Local passwords are used today. The OIDC provider speaks standard
Authorization Code + PKCE discovery/JWKS, so moving to Authentik later is a
configuration change (AUTH_PROVIDER=oidc) rather than a rewrite of auth code.
"""

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlencode

import jwt
import requests
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend import config
from backend.models.user import User
from backend.services.auth import verify_password


class IdentityProvider(Protocol):
    def authenticate_password(
        self, db: Session, email: str, password: str
    ) -> User | None: ...

    def authorization_url(self, state: str, code_challenge: str) -> str | None: ...

    def complete_login(
        self, db: Session, code: str, code_verifier: str
    ) -> User | None: ...


class LocalIdentityProvider:
    def authenticate_password(self, db, email, password):
        user = (
            db.query(User)
            .filter(User.email == email, User.auth_provider == "local")
            .first()
        )
        if user and user.is_active and verify_password(password, user.password_hash):
            return user
        return None

    def authorization_url(self, state, code_challenge):
        return None

    def complete_login(self, db, code, code_verifier):
        raise HTTPException(status_code=400, detail="OIDC is not configured")


@dataclass
class OidcIdentityProvider:
    issuer: str = config.OIDC_ISSUER
    client_id: str = config.OIDC_CLIENT_ID
    client_secret: str = config.OIDC_CLIENT_SECRET
    redirect_uri: str = config.OIDC_REDIRECT_URI

    def _discovery(self) -> dict:
        response = requests.get(
            f"{self.issuer.rstrip('/')}/.well-known/openid-configuration",
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def authorization_url(self, state, code_challenge):
        discovery = self._discovery()
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile groups",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{discovery['authorization_endpoint']}?{urlencode(params)}"

    def complete_login(self, db, code, code_verifier):
        discovery = self._discovery()
        token_response = requests.post(
            discovery["token_endpoint"],
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code_verifier": code_verifier,
            },
            timeout=10,
        )
        token_response.raise_for_status()
        id_token = token_response.json().get("id_token")
        if not id_token:
            raise HTTPException(status_code=401, detail="OIDC did not return an id_token")

        jwks_client = jwt.PyJWKClient(discovery["jwks_uri"])
        signing_key = jwks_client.get_signing_key_from_jwt(id_token)
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=self.client_id,
            issuer=self.issuer,
            options={"verify_at_hash": False},
        )

        sub = claims.get("sub")
        email = claims.get("email")
        if not sub:
            raise HTTPException(status_code=401, detail="OIDC token has no subject")

        user = db.query(User).filter(User.external_sub == sub).first()
        if not user and email:
            user = db.query(User).filter(User.email == email).first()
        if not user:
            groups = claims.get("groups") or []
            role = "admin" if config.OIDC_ADMIN_GROUP in groups else "user"
            user = User(
                name=claims.get("name") or email or sub,
                email=email,
                role=role,
                auth_provider="oidc",
                external_sub=sub,
                is_active=True,
            )
            db.add(user)
        else:
            user.external_sub = sub
            user.auth_provider = "oidc"
        db.commit()
        db.refresh(user)
        return user


def get_identity_provider() -> IdentityProvider:
    if config.AUTH_PROVIDER == "oidc":
        if not all(
            (config.OIDC_ISSUER, config.OIDC_CLIENT_ID, config.OIDC_REDIRECT_URI)
        ):
            raise HTTPException(
                status_code=500, detail="OIDC is enabled but not configured"
            )
        return OidcIdentityProvider()
    return LocalIdentityProvider()


__all__ = ["IdentityProvider", "LocalIdentityProvider", "OidcIdentityProvider", "get_identity_provider"]
