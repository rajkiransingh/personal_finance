from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.models import Investment
from backend.schemas.investment_schemas import InvestmentCreate
from datetime import date

def create(investment_data: InvestmentCreate, db: Session):
    """
        Handles buy and sell transactions for investments.
        - Buy transactions are added normally.
        - Sell transactions check if enough holdings exist before proceeding.
        """
    if investment_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if investment_data.transaction_type == "SELL":
        total_holdings = db.query(Investment).filter(
            Investment.investor == investment_data.investor,
            Investment.investment_name == investment_data.investment_name
        ).all()

        total_quantity = sum(holding.purchased_quantity for holding in total_holdings)

        if investment_data.purchased_quantity > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = Investment(
        investment_type_id=investment_data.investment_type_id,
        investment_subcategory_id=investment_data.investment_subcategory_id,
        investment_name=investment_data.investment_name,
        investment_amount=investment_data.investment_amount,
        purchased_quantity=investment_data.purchased_quantity,
        unit_id=investment_data.unit_id,
        investor=investment_data.investor,
        investment_date=investment_data.investment_date or date.today(),
        currency_id=investment_data.currency_id,
        transaction_type=investment_data.transaction_type,
        initial_value=investment_data.investment_amount
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction