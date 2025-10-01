from datetime import datetime, UTC

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.real_estate import RealEstateInvestment, RealEstateSummary
from backend.schemas.investments.common import InvestmentUpdate


def update_real_estate_investment(db: Session, investment_id: int, investment_data: InvestmentUpdate):
    current_price_per_sqyds = investment_data.current_price_per_sqyds
    real_estate_investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == investment_id).first()

    if not real_estate_investment:
        raise HTTPException(status_code=404, detail="Property investment not found")

    # Calculate the data:
    today = datetime.now(UTC)
    current_value = current_price_per_sqyds * real_estate_investment.area_in_sqyds
    days_invested = (today.date() - real_estate_investment.investment_date).days
    years = days_invested / 365.0
    initial_investment = real_estate_investment.total_invested_amount

    # Update current value
    real_estate_investment.current_price_per_sqyds = current_price_per_sqyds
    real_estate_investment.current_total_value = current_value
    real_estate_investment.return_on_investment = ((current_value - initial_investment) / initial_investment) * 100
    real_estate_investment.xirr = (((current_value / initial_investment) ** (
            1 / years)) - 1) * 100 if years > 0 else 0.0

    db.commit()
    db.refresh(real_estate_investment)
    update_real_estate_summary(db, investment_id, investment_data)
    return real_estate_investment


def update_real_estate_summary(db: Session, investment_id: int, investment_data: InvestmentUpdate):
    current_price_per_sqyds = investment_data.current_price_per_sqyds
    real_estate_investment = db.query(RealEstateInvestment).filter(RealEstateInvestment.id == investment_id).first()
    real_estate_summary = db.query(RealEstateSummary).filter(
        RealEstateSummary.investor_id == real_estate_investment.investor,
        RealEstateSummary.property_name == real_estate_investment.property_name).first()

    if not real_estate_summary:
        raise HTTPException(status_code=404, detail="Property investment not found")

    # Calculate the data:
    today = datetime.now(UTC)
    current_value = current_price_per_sqyds * real_estate_investment.area_in_sqyds
    days_invested = (today.date() - real_estate_investment.investment_date).days
    years = days_invested / 365.0
    initial_investment = real_estate_investment.total_invested_amount

    # Update current value
    real_estate_summary.current_price_per_unit = current_price_per_sqyds
    real_estate_summary.current_value = current_value
    real_estate_summary.roi = ((current_value - initial_investment) / initial_investment) * 100
    real_estate_summary.xirr = (((current_value / initial_investment) ** (
            1 / years)) - 1) * 100 if years > 0 else 0.0
    real_estate_summary.last_updated = today.now(UTC)

    db.commit()
    db.refresh(real_estate_summary)
