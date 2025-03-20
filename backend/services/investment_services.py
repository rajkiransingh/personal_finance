from sqlalchemy.orm import Session
from fastapi import HTTPException
from backend.models.models import Investment
from backend.schemas.investment_schemas import InvestmentCreate, InvestmentUpdate
from datetime import date

def get_all_investments(db: Session):
    return db.query(Investment).all()

def get_investment_by_user(db: Session, user_id: int):
    return db.query(Investment).filter(Investment.investor == user_id).all()

def get_investment(db: Session, id: int):
    return db.query(Investment).filter(Investment.id == id).first()

def create_investment(investment_data: InvestmentCreate, db: Session):
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

    return {"message": f"{investment_data.transaction_type} transaction recorded", "transaction_id": new_transaction.id}

def update_investment(id: int, update_data: InvestmentUpdate, db: Session):
    """
    Updates only the provided fields for the investment transaction while keeping other values unchanged.
    """
    investment = db.query(Investment).filter(Investment.id == id).first()

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    # Apply updates only if the field is provided
    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(investment, key, value)

    db.commit()
    db.refresh(investment)

    return investment

def delete_investment(id: int, db: Session):
    investment = db.query(Investment).filter(Investment.id == id).first()
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(investment)
    db.commit()
    return investment