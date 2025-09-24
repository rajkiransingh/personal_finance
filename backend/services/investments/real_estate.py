from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.real_estate import RealEstateInvestment
from backend.schemas.investments.real_estate_schema import RealEstateInvestmentCreate


def create_property(db: Session, property_data: RealEstateInvestmentCreate):
    if property_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if property_data.transaction_type == "SELL":
        total_holdings = db.query(RealEstateInvestment).filter(
            RealEstateInvestment.investor == property_data.investor,
            RealEstateInvestment.property_type == property_data.property_type,
            RealEstateInvestment.property_location == property_data.property_location,
            RealEstateInvestment.investment_subcategory_id == property_data.investment_subcategory_id
        ).all()

        total_quantity = sum(holding.area_in_sqyds for holding in total_holdings)

        if property_data.area_in_sqyds > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = RealEstateInvestment(
        investor=property_data.investor,
        currency_id=property_data.currency_id,
        investment_type_id=property_data.investment_type_id,
        investment_subcategory_id=property_data.investment_subcategory_id,
        transaction_type=property_data.transaction_type,
        property_name=property_data.property_name,
        property_type=property_data.property_type,
        property_location=property_data.property_location,
        initial_price_per_sqyds=property_data.initial_price_per_sqyds,
        area_in_sqyds=property_data.area_in_sqyds,
        total_invested_amount=property_data.total_invested_amount,
        total_amount_after_sale=property_data.total_amount_after_sale,
        investment_date=property_data.investment_date or date.today()
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
