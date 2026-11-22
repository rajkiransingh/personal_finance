from sqlalchemy.orm import Session

from backend.models.investments.stock import Dividends
from backend.schemas.investments.dividend_schema import DividendCreate, DividendUpdate
from backend.services.scope import apply_scope, require_owner


def get_all_dividends(db: Session, scope=None):
    return apply_scope(db.query(Dividends), Dividends, scope).all()


def get_dividend_by_user(db: Session, user_id: int, scope=None):
    require_owner(user_id, scope)
    return apply_scope(db.query(Dividends), Dividends, scope).filter(
        Dividends.investor == user_id
    ).all()


def get_dividend(db: Session, dividend_id: int, scope=None):
    return apply_scope(db.query(Dividends), Dividends, scope).filter(
        Dividends.id == dividend_id
    ).first()


def create_dividend(db: Session, dividend_data: DividendCreate):
    new_dividend = Dividends(**dividend_data.dict())
    db.add(new_dividend)
    db.commit()
    db.refresh(new_dividend)
    return new_dividend


def update_dividend(db: Session, dividend_id: int, dividend_data: DividendUpdate, scope=None):
    dividend = get_dividend(db, dividend_id, scope)
    if dividend:
        for key, value in dividend_data.dict(exclude_unset=True).items():
            if key != "investor":
                setattr(dividend, key, value)
        db.commit()
        db.refresh(dividend)
    return dividend


def delete_dividend(db: Session, dividend_id: int, scope=None):
    dividend = get_dividend(db, dividend_id, scope)
    if dividend:
        from backend.summarizing import revert_dividend_summary

        revert_dividend_summary.revert(db, dividend)
        db.delete(dividend)
        db.commit()
    return dividend
