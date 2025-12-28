from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionInvestment
from backend.schemas.investments.bullion_schema import BullionInvestmentCreate


def create_bullion(db: Session, bullion_data: BullionInvestmentCreate):
    if bullion_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if bullion_data.transaction_type == "SELL":
        total_holdings = (
            db.query(BullionInvestment)
            .filter(
                BullionInvestment.investor == bullion_data.investor,
                BullionInvestment.metal_name == bullion_data.metal_name,
                BullionInvestment.investment_subcategory_id
                == bullion_data.investment_subcategory_id,
            )
            .all()
        )

        total_quantity = sum(holding.quantity_in_grams for holding in total_holdings)

        if bullion_data.quantity_in_grams > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = BullionInvestment(
        investor=bullion_data.investor,
        currency_id=bullion_data.currency_id,
        investment_type_id=bullion_data.investment_type_id,
        investment_subcategory_id=bullion_data.investment_subcategory_id,
        transaction_type=bullion_data.transaction_type,
        metal_name=bullion_data.metal_name,
        initial_price_per_gram=bullion_data.initial_price_per_gram,
        quantity_in_grams=bullion_data.quantity_in_grams,
        total_invested_amount=bullion_data.total_invested_amount,
        total_amount_after_sale=bullion_data.total_amount_after_sale,
        investment_date=bullion_data.investment_date or date.today(),
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
