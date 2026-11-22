"""Access-control and preference models.

`households` lets an admin grant one user a combined view of two accounts
(typically a couple managing money together). `household_members.scope_mode`
is per member, so the sharing can be one-way: one partner can opt into the
household view while the other always sees personal data only.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from backend.services.db_services import Base


class Household(Base):
    __tablename__ = "households"

    household_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    # JSON list of data domains shared in the household view. Defaults to all
    # personal domains; kept as text so no MySQL-specific JSON type is needed.
    shared_domains = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True, server_default="1")
    created_at = Column(DateTime, nullable=True)


class HouseholdMember(Base):
    __tablename__ = "household_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    household_id = Column(
        Integer, ForeignKey("households.household_id"), nullable=False
    )
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    # 'self' = personal view only; 'household' = may switch to combined view.
    scope_mode = Column(
        String(20), nullable=False, default="self", server_default="self"
    )


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    theme = Column(String(20), nullable=True)
    filters = Column(Text, nullable=True)
    strategies = Column(Text, nullable=True)
    page_size = Column(Integer, nullable=True)
    updated_at = Column(DateTime, nullable=True)
