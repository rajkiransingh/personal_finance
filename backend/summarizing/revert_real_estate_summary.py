from sqlalchemy.orm import Session
from backend.models.investments.real_estate import (
    RealEstateSummary,
    RealEstateInvestment,
)
from backend.summarizing.revert_utils import delete_related_income
import datetime


def revert(db: Session, investment: RealEstateInvestment):
    prop = (
        db.query(RealEstateSummary)
        .filter(
            RealEstateSummary.investor_id == investment.investor,
            RealEstateSummary.property_type == investment.investment_subcategory_id,
            RealEstateSummary.property_name == investment.property_name,
            RealEstateSummary.property_location == investment.property_location,
            RealEstateSummary.property_type == investment.property_type,
        )
        .first()
    )

    if not prop:
        return

    qty = float(investment.area_in_sqyds)

    if investment.transaction_type == "BUY":
        prop.total_quantity -= qty
        prop.total_cost -= float(investment.total_invested_amount)

    elif investment.transaction_type == "SELL":
        avg_price = prop.average_price_per_unit
        cost_to_add = qty * avg_price

        prop.total_quantity += qty
        prop.total_cost += cost_to_add

        # Revert Income (Source ID 10 for Real Estate)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=10,
            amount=investment.total_amount_after_sale,
            earned_date=investment.investment_date.date()
            if hasattr(investment.investment_date, "date")
            else investment.investment_date,
        )

    if prop.total_quantity > 0:
        prop.average_price_per_unit = prop.total_cost / prop.total_quantity
    else:
        prop.average_price_per_unit = 0.0

    prop.last_updated = datetime.datetime.utcnow()
