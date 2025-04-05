from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.StockInvestment):
    stock = db.query(models.StockSummary).filter(
        models.StockSummary.investor_id == investment.investor,
        models.StockSummary.stock_symbol == investment.stock_symbol
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
            # Record income from sale
            income = models.Income(
                user_id=investment.investor,
                source_id=8,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today() # type: ignore
            )
        db.add(income)

        stock.average_price_per_unit = stock.total_cost / stock.total_quantity if stock.total_quantity > 0 else 0
        stock.last_updated = datetime.datetime.utcnow()
    else:
        new_stock = models.StockSummary(
            investor_id=investment.investor,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_quantity=investment.stock_quantity,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount / investment.stock_quantity
        )
        db.add(new_stock)

    db.commit()