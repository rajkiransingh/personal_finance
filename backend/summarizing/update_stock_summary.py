from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.Investment):
    stock = db.query(models.StockSummary).filter(
        models.StockSummary.investor_id == investment.investor,
        models.StockSummary.stock_name == investment.investment_name
    ).first()

    if stock:
        if investment.transaction_type == "BUY":
            stock.total_quantity += investment.quantity
            stock.total_cost += investment.amount
        elif investment.transaction_type == "SELL":
            stock.total_quantity -= investment.quantity
            stock.total_cost -= (stock.average_price * investment.quantity)

        stock.average_price = stock.total_cost / stock.total_quantity if stock.total_quantity > 0 else 0
        stock.last_updated = datetime.datetime.utcnow()
    else:
        new_stock = models.StockSummary(
            investor_id=investment.investor,
            stock_name=investment.investment_name,
            total_quantity=investment.purchased_quantity,
            total_cost=investment.investment_amount,
            average_price=investment.investment_amount / investment.purchased_quantity
        )
        db.add(new_stock)

    db.commit()