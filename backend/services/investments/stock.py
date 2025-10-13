from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.investments.stock import StockInvestment
from backend.schemas.investments.stock_schema import StockInvestmentCreate


def create_stock(db: Session, stock_data: StockInvestmentCreate):
    if stock_data.transaction_type not in ["BUY", "SELL"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # If selling, check available holdings
    if stock_data.transaction_type == "SELL":
        total_holdings = db.query(StockInvestment).filter(
            StockInvestment.investor == stock_data.investor,
            StockInvestment.stock_symbol == stock_data.stock_symbol
        ).all()

        total_quantity = sum(holding.stock_quantity for holding in total_holdings)

        if stock_data.stock_quantity > total_quantity:
            raise HTTPException(status_code=400, detail="Insufficient holdings to sell")

    # Create transaction
    new_transaction = StockInvestment(
        investor=stock_data.investor,
        currency_id=stock_data.currency_id,
        investment_type_id=stock_data.investment_type_id,
        investment_subcategory_id=stock_data.investment_subcategory_id,
        transaction_type=stock_data.transaction_type,
        stock_symbol=stock_data.stock_symbol,
        stock_name=stock_data.stock_name,
        initial_price_per_stock=stock_data.initial_price_per_stock,
        stock_quantity=stock_data.stock_quantity,
        total_invested_amount=stock_data.total_invested_amount,
        total_amount_after_sale=stock_data.total_amount_after_sale,
        investment_date=stock_data.investment_date or date.today(),
        dividend_paying=int(stock_data.dividend_paying)
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction
