from sqlalchemy.orm import Session

from backend.models.investments.stock import Dividends
from backend.schemas.investments.dividend_schema import DividendCreate, DividendUpdate

def get_all_dividends(db: Session):
    return db.query(Dividends).all()

def get_dividend_by_user(db: Session, user_id: int):
    return db.query(Dividends).filter(Dividends.investor == user_id).all()

def get_dividend(db: Session, dividend_id: int):
    return db.query(Dividends).filter(Dividends.id == dividend_id).first()

def create_dividend(db: Session, dividend_data: DividendCreate):
    new_dividend = Dividends(**dividend_data.dict())
    db.add(new_dividend)
    db.commit()
    db.refresh(new_dividend)
    return new_dividend

def update_dividend(db: Session, dividend_id: int, dividend_data: DividendUpdate):
    dividend = db.query(Dividends).filter(Dividends.id == dividend_id).first()
    if dividend:
        for key, value in dividend_data.dict(exclude_unset=True).items():
            setattr(dividend, key, value)
        db.commit()
        db.refresh(dividend)
    return dividend

def delete_dividend(db: Session, dividend_id: int):
    dividend = db.query(Dividends).filter(Dividends.id == dividend_id).first()
    if dividend:
        db.delete(dividend)
        db.commit()
    return dividend
