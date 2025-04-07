from sqlalchemy.orm import Session
from backend.models import models
import datetime

def update(db: Session, investment: models.RealEstateInvestment):
    property = db.query(models.RealEstateSummary).filter(
        models.RealEstateSummary.investor_id == investment.investor,
        models.RealEstateSummary.property_type == investment.investment_subcategory_id,
        models.RealEstateSummary.property_name == investment.property_name,
        models.RealEstateSummary.property_location == investment.property_location,
        models.RealEstateSummary.property_type == investment.property_type
    ).first()

    currency_map = {
        1: "INR",
        2: "PLN",
        3: "USD"
    }

    if property:
        if investment.transaction_type == "BUY":
            property.total_quantity += investment.area_in_sqyds
            property.total_cost += investment.total_invested_amount
        elif investment.transaction_type == "SELL":
            property.total_quantity -= investment.area_in_sqyds
            property.total_cost -= (property.average_price_per_unit * investment.area_in_sqyds)

            currency = currency_map.get(investment.currency_id, "INR")
            # Record income from sale
            income = models.Income(
                user_id=investment.investor,
                source_id=10,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today() # type: ignore
            )
        db.add(income)

        property.average_price_per_unit = property.total_cost / property.total_quantity if property.total_quantity > 0 else 0
        property.last_updated = investment.investment_date or date.today() # type: ignore
    else:
        new_property = models.RealEstateSummary(
            investor_id=investment.investor,
            property_type=investment.investment_subcategory_id,
            property_name=investment.property_name,
            property_location=investment.property_location,
            total_quantity=investment.area_in_sqyds,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount / investment.area_in_sqyds,
            last_updated=investment.investment_date or date.today() # type: ignore
        )
        db.add(new_property)

    db.commit()