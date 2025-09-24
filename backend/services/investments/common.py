from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionInvestment
from backend.models.investments.crypto import CryptoInvestment
from backend.models.investments.mutual_fund import MutualFundInvestment
from backend.models.investments.real_estate import RealEstateInvestment
from backend.models.investments.stock import StockInvestment
from backend.schemas.investments.common import InvestmentUpdate


def get_all_investments(investment_type: str, db: Session):
    if investment_type == "stock":
        return db.query(StockInvestment).all()
    elif investment_type == "mutual fund":
        return db.query(MutualFundInvestment).all()
    elif investment_type == "bullion":
        return db.query(BullionInvestment).all()
    elif investment_type == "real estate":
        return db.query(RealEstateInvestment).all()
    elif investment_type == "crypto":
        return db.query(CryptoInvestment).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def get_investment_by_user(investment_type: str, db: Session, user_id: int):
    if investment_type == "stock":
        return db.query(StockInvestment).filter(StockInvestment.investor == user_id).all()
    elif investment_type == "mutual fund":
        return db.query(MutualFundInvestment).filter(MutualFundInvestment.investor == user_id).all()
    elif investment_type == "bullion":
        return db.query(BullionInvestment).filter(BullionInvestment.investor == user_id).all()
    elif investment_type == "real estate":
        return db.query(RealEstateInvestment).filter(RealEstateInvestment.investor == user_id).all()
    elif investment_type == "crypto":
        return db.query(CryptoInvestment).filter(CryptoInvestment.investor == user_id).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def get_investment_by_id(investment_type: str, db: Session, investment_id: int):
    if investment_type == "stock":
        return db.query(StockInvestment).filter(StockInvestment.id == investment_id).first()
    elif investment_type == "mutual fund":
        return db.query(MutualFundInvestment).filter(MutualFundInvestment.id == investment_id).first()
    elif investment_type == "bullion":
        return db.query(BullionInvestment).filter(BullionInvestment.id == investment_id).first()
    elif investment_type == "real estate":
        return db.query(RealEstateInvestment).filter(RealEstateInvestment.id == investment_id).first()
    elif investment_type == "crypto":
        return db.query(CryptoInvestment).filter(CryptoInvestment.id == investment_id).first()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def update_investment(investment_type: str, investment_id: int, update_data: InvestmentUpdate, db: Session):
    """
    Updates only the provided fields for the investment transaction while keeping other values unchanged.
    """
    if investment_type == "stock":
        investment = db.query(StockInvestment).filter(StockInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "mutual fund":
        investment = db.query(MutualFundInvestment).filter(MutualFundInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "bullion":
        investment = db.query(BullionInvestment).filter(BullionInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "real estate":
        investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "crypto":
        investment = db.query(CryptoInvestment).filter(CryptoInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

    # Apply updates only if the field is provided
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(investment, key, value)

    db.commit()
    db.refresh(investment)

    return investment


def delete_investment(investment_type: str, investment_id: int, db: Session):
    if investment_type == "stock":
        investment = db.query(StockInvestment).filter(StockInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "mutual fund":
        investment = db.query(MutualFundInvestment).filter(MutualFundInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "bullion":
        investment = db.query(BullionInvestment).filter(BullionInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "real estate":
        investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "crypto":
        investment = db.query(CryptoInvestment).filter(CryptoInvestment.id == investment_id).first()
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

    db.delete(investment)
    db.commit()
    return investment
