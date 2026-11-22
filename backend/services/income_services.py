from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.schemas.income_schema import IncomeCreate, IncomeUpdate
from backend.services.scope import apply_scope, require_owner


def get_all_incomes(db: Session, scope=None):
    return apply_scope(db.query(Income), Income, scope).all()


def get_income_by_user(db: Session, user_id: int, scope=None):
    require_owner(user_id, scope)
    return apply_scope(db.query(Income), Income, scope).filter(
        Income.user_id == user_id
    ).all()


def get_income(db: Session, income_id: int, scope=None):
    return apply_scope(db.query(Income), Income, scope).filter(
        Income.income_id == income_id
    ).first()


def create_income(db: Session, income_data: IncomeCreate):
    new_income = Income(**income_data.dict())
    db.add(new_income)
    db.commit()
    db.refresh(new_income)
    return new_income


def update_income(db: Session, income_id: int, income_data: IncomeUpdate, scope=None):
    income = get_income(db, income_id, scope)
    if income:
        for key, value in income_data.dict(exclude_unset=True).items():
            if key != "user_id":
                setattr(income, key, value)
        db.commit()
        db.refresh(income)
    return income


def delete_income(db: Session, income_id: int, scope=None):
    income = get_income(db, income_id, scope)
    if income:
        db.delete(income)
        db.commit()
    return income
