import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL (Update with your actual MySQL credentials)
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Authentication / identity -------------------------------------------------
# Local passwords are the default. Setting AUTH_PROVIDER=oidc switches the
# login flow to an OIDC provider (e.g. Authentik) without any schema change.
AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "local").strip().lower()
SECRET_KEY = os.getenv("SECRET_KEY", "")
SESSION_COOKIE = os.getenv("SESSION_COOKIE", "mp_session")
VIEW_COOKIE = os.getenv("VIEW_COOKIE", "mp_view")
CSRF_COOKIE = os.getenv("CSRF_COOKIE", "mp_csrf")
CSRF_HEADER = "X-CSRF-Token"
COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").strip().lower() == "true"
SESSION_TTL_HOURS = int(os.getenv("SESSION_TTL_HOURS", "12"))

# OIDC settings (only used when AUTH_PROVIDER=oidc)
OIDC_ISSUER = os.getenv("OIDC_ISSUER", "")
OIDC_CLIENT_ID = os.getenv("OIDC_CLIENT_ID", "")
OIDC_CLIENT_SECRET = os.getenv("OIDC_CLIENT_SECRET", "")
OIDC_REDIRECT_URI = os.getenv("OIDC_REDIRECT_URI", "")
OIDC_ADMIN_GROUP = os.getenv("OIDC_ADMIN_GROUP", "mera-paisa-admin")

# Frontend origins allowed to call the API with credentials.
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://localhost:3001"
    ).split(",")
    if origin.strip()
]
