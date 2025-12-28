from datetime import date
from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.real_estate import RealEstateSummary
from backend.schemas.investments.real_estate_schema import RealEstateInvestmentCreate


def update(db: Session, investment: RealEstateInvestmentCreate):
    property_to_update = (
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

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    if property_to_update:
        if investment.transaction_type == "BUY":
            property_to_update.total_quantity += investment.area_in_sqyds
            property_to_update.total_cost += investment.total_invested_amount
        elif investment.transaction_type == "SELL":
            property_to_update.total_quantity -= investment.area_in_sqyds
            property_to_update.total_cost -= (
                property_to_update.average_price_per_unit * investment.area_in_sqyds
            )

            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=10,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today(),  # type: ignore
            )
            db.add(income)

        property_to_update.average_price_per_unit = (
            property_to_update.total_cost / property_to_update.total_quantity
            if property_to_update.total_quantity > 0
            else 0
        )
        property_to_update.last_updated = investment.investment_date or date.today()  # type: ignore
    else:
        new_property = RealEstateSummary(
            investor_id=investment.investor,
            property_type=investment.investment_subcategory_id,
            property_name=investment.property_name,
            property_location=investment.property_location,
            total_quantity=investment.area_in_sqyds,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount
            / investment.area_in_sqyds,
            last_updated=investment.investment_date or date.today(),  # type: ignore
        )
        db.add(new_property)

    db.commit()
