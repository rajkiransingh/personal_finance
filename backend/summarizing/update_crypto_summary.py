from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.Investment):
    coin = db.query(models.StockSummary).filter(
        models.CryptoSummary.investor_id == investment.investor,
        models.CryptoSummary.coin_name == investment.investment_name
    ).first()

    if coin:
        if investment.transaction_type == "BUY":
            coin.total_quantity += investment.quantity
            coin.total_cost += investment.amount
        elif investment.transaction_type == "SELL":
            coin.total_quantity -= investment.quantity
            coin.total_cost -= (coin.average_price * investment.quantity)

        coin.average_price = coin.total_cost / coin.total_quantity if coin.total_quantity > 0 else 0
        coin.last_updated = datetime.datetime.utcnow()
    else:
        new_coin = models.StockSummary(
            investor_id=investment.investor,
            stock_name=investment.investment_name,
            total_quantity=investment.purchased_quantity,
            total_cost=investment.investment_amount,
            average_price=investment.investment_amount / investment.purchased_quantity
        )
        db.add(new_coin)

    db.commit()