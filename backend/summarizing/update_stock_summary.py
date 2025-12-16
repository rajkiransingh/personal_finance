from datetime import date
from sqlalchemy.orm import Session
import datetime

from backend.models.earnings.income import Income
from backend.models.investments.stock import StockSummary
from backend.schemas.investments.stock_schema import StockInvestmentCreate


def update(db: Session, investment: StockInvestmentCreate):
    stock = db.query(StockSummary).filter(
        StockSummary.investor_id == investment.investor,
        StockSummary.stock_symbol == investment.stock_symbol
    ).first()

    currency_map = {
        1: "INR",
        2: "PLN",
        3: "USD"
    }

    if stock:
        if investment.transaction_type == "BUY":
            stock.total_quantity += investment.stock_quantity
            stock.total_cost += investment.total_invested_amount
        elif investment.transaction_type == "SELL":
            stock.total_quantity -= investment.stock_quantity
            stock.total_cost -= (stock.average_price_per_unit * investment.stock_quantity)
            
            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=8,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today() # type: ignore
            )
            db.add(income)

        stock.average_price_per_unit = stock.total_cost / stock.total_quantity if stock.total_quantity > 0 else 0
        stock.last_updated = datetime.datetime.utcnow()
        stock.dividend_paying = investment.dividend_paying
    else:
        new_stock = StockSummary(
            investor_id=investment.investor,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_quantity=investment.stock_quantity,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount / investment.stock_quantity,
            last_updated = datetime.datetime.utcnow(),
            dividend_paying=investment.dividend_paying
        )
        db.add(new_stock)

    db.commit()