from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.Investment):
    property = db.query(models.StockSummary).filter(
        models.RealEstateSummary.investor_id == investment.investor,
        models.RealEstateSummary.property_type == investment.investment_subcategory_id,
        models.RealEstateSummary.property_name == investment.investment_name
    ).first()

    if property:
        if investment.transaction_type == "BUY":
            property.total_quantity += investment.quantity
            property.total_cost += investment.amount
        elif investment.transaction_type == "SELL":
            property.total_quantity -= investment.quantity
            property.total_cost -= (property.average_price * investment.quantity)

        property.average_price = property.total_cost / property.total_quantity if property.total_quantity > 0 else 0
        property.last_updated = datetime.datetime.utcnow()
    else:
        new_property = models.StockSummary(
            investor_id=investment.investor,
            stock_name=investment.investment_name,
            total_quantity=investment.purchased_quantity,
            total_cost=investment.investment_amount,
            average_price=investment.investment_amount / investment.purchased_quantity
        )
        db.add(new_property)

    db.commit()