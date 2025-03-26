from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.Investment):
    bullion = db.query(models.StockSummary).filter(
        models.BullionSummary.investor_id == investment.investor,
        models.BullionSummary.investment_type == investment.investment_subcategory_id
    ).first()

    if bullion:
        if investment.transaction_type == "BUY":
            bullion.total_quantity += investment.quantity
            bullion.total_cost += investment.amount
        elif investment.transaction_type == "SELL":
            bullion.total_quantity -= investment.quantity
            bullion.total_cost -= (bullion.average_price * investment.quantity)

        bullion.average_price = bullion.total_cost / bullion.total_quantity if bullion.total_quantity > 0 else 0
        bullion.last_updated = datetime.datetime.utcnow()
    else:
        new_bullion = models.StockSummary(
            investor_id=investment.investor,
            stock_name=investment.investment_name,
            total_quantity=investment.purchased_quantity,
            total_cost=investment.investment_amount,
            average_price=investment.investment_amount / investment.purchased_quantity
        )
        db.add(new_bullion)

    db.commit()