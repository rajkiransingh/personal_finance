from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionInvestment
from backend.models.investments.crypto import CryptoInvestment
from backend.models.investments.mutual_fund import MutualFundInvestment
from backend.models.investments.real_estate import RealEstateInvestment
from backend.models.investments.stock import StockInvestment
from backend.schemas.investments.common import InvestmentUpdate
from backend.services.scope import apply_scope, require_owner


def _scoped(model, db, scope):
    return apply_scope(db.query(model), model, scope)


def get_all_investments(investment_type: str, db: Session, scope=None):
    if investment_type == "stocks":
        return _scoped(StockInvestment, db, scope).all()
    elif investment_type == "mutual fund":
        return _scoped(MutualFundInvestment, db, scope).all()
    elif investment_type == "bullion":
        return _scoped(BullionInvestment, db, scope).all()
    elif investment_type == "real estate":
        return _scoped(RealEstateInvestment, db, scope).all()
    elif investment_type == "crypto":
        return _scoped(CryptoInvestment, db, scope).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def get_investment_by_user(investment_type: str, db: Session, user_id: int, scope=None):
    require_owner(user_id, scope)
    if investment_type == "stock":
        return (
            _scoped(StockInvestment, db, scope).filter(StockInvestment.investor == user_id).all()
        )
    elif investment_type == "mutual fund":
        return (
            _scoped(MutualFundInvestment, db, scope)
            .filter(MutualFundInvestment.investor == user_id)
            .all()
        )
    elif investment_type == "bullion":
        return (
            _scoped(BullionInvestment, db, scope)
            .filter(BullionInvestment.investor == user_id)
            .all()
        )
    elif investment_type == "real estate":
        return (
            _scoped(RealEstateInvestment, db, scope)
            .filter(RealEstateInvestment.investor == user_id)
            .all()
        )
    elif investment_type == "crypto":
        return (
            _scoped(CryptoInvestment, db, scope)
            .filter(CryptoInvestment.investor == user_id)
            .all()
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def get_investment_by_id(investment_type: str, db: Session, investment_id: int, scope=None):
    if investment_type == "stock":
        return (
            _scoped(StockInvestment, db, scope)
            .filter(StockInvestment.id == investment_id)
            .first()
        )
    elif investment_type == "mutual fund":
        return (
            _scoped(MutualFundInvestment, db, scope)
            .filter(MutualFundInvestment.id == investment_id)
            .first()
        )
    elif investment_type == "bullion":
        return (
            _scoped(BullionInvestment, db, scope)
            .filter(BullionInvestment.id == investment_id)
            .first()
        )
    elif investment_type == "real estate":
        return (
            _scoped(RealEstateInvestment, db, scope)
            .filter(RealEstateInvestment.id == investment_id)
            .first()
        )
    elif investment_type == "crypto":
        return (
            _scoped(CryptoInvestment, db, scope)
            .filter(CryptoInvestment.id == investment_id)
            .first()
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")


def update_investment(
    investment_type: str, investment_id: int, update_data: InvestmentUpdate, db: Session, scope=None
):
    """
    Updates only the provided fields for the investment transaction while keeping other values unchanged.
    """
    if investment_type == "stock":
        investment = (
            _scoped(StockInvestment, db, scope)
            .filter(StockInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "mutual fund":
        investment = (
            _scoped(MutualFundInvestment, db, scope)
            .filter(MutualFundInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "bullion":
        investment = (
            _scoped(BullionInvestment, db, scope)
            .filter(BullionInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "real estate":
        investment = (
            _scoped(RealEstateInvestment, db, scope)
            .filter(RealEstateInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "crypto":
        investment = (
            _scoped(CryptoInvestment, db, scope)
            .filter(CryptoInvestment.id == investment_id)
            .first()
        )
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


def delete_investment(investment_type: str, investment_id: int, db: Session, scope=None):
    if investment_type == "stock":
        investment = (
            _scoped(StockInvestment, db, scope)
            .filter(StockInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "mutual fund":
        investment = (
            _scoped(MutualFundInvestment, db, scope)
            .filter(MutualFundInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "bullion":
        investment = (
            _scoped(BullionInvestment, db, scope)
            .filter(BullionInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "real estate":
        investment = (
            _scoped(RealEstateInvestment, db, scope)
            .filter(RealEstateInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    elif investment_type == "crypto":
        investment = (
            _scoped(CryptoInvestment, db, scope)
            .filter(CryptoInvestment.id == investment_id)
            .first()
        )
        if not investment:
            raise HTTPException(status_code=404, detail="Investment not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid investment type")

    # Revert summary before deletion
    if investment_type == "stock":
        from backend.summarizing import revert_stock_summary

        revert_stock_summary.revert(db, investment)
    elif investment_type == "mutual fund":
        from backend.summarizing import revert_mutual_fund_summary

        revert_mutual_fund_summary.revert(db, investment)
    elif investment_type == "bullion":
        from backend.summarizing import revert_bullion_summary

        revert_bullion_summary.revert(db, investment)
    elif investment_type == "real estate":
        from backend.summarizing import revert_real_estate_summary

        revert_real_estate_summary.revert(db, investment)
    elif investment_type == "crypto":
        from backend.summarizing import revert_crypto_summary

        revert_crypto_summary.revert(db, investment)

    db.delete(investment)
    db.commit()
    return investment
