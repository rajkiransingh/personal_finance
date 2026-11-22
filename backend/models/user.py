from sqlalchemy import Boolean, Column, DateTime, Integer, String

from backend.services.db_services import Base


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    # Identity / authorization. email and password_hash are nullable so OIDC
    # provisioned accounts (and legacy rows) can exist without a local password.
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(20), nullable=False, default="user", server_default="user")
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    auth_provider = Column(
        String(20), nullable=False, default="local", server_default="local"
    )
    external_sub = Column(String(255), unique=True, nullable=True)
    must_change_password = Column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    last_login_at = Column(DateTime, nullable=True)
