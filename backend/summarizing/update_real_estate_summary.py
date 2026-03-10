from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.real_estate import RealEstateSummary
from backend.schemas.investments.real_estate_schema import RealEstateInvestmentCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: RealEstateInvestmentCreate):
    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    property_to_update = (
        db.query(RealEstateSummary)
        .filter(
            RealEstateSummary.investor_id == investment.investor,
            RealEstateSummary.property_type == investment.investment_subcategory_id,
            RealEstateSummary.property_name == investment.property_name,
            RealEstateSummary.property_location == investment.property_location,
        )
        .first()
    )

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    if property_to_update:
        if investment.transaction_type == "BUY":
            property_to_update.total_quantity = Decimal(
                str(property_to_update.total_quantity)
            ) + Decimal(str(investment.area_in_sqyds))
            # Add cost in INR
            property_to_update.total_cost = Decimal(
                str(property_to_update.total_cost)
            ) + (Decimal(str(investment.total_invested_amount)) * conversion_rate)
        elif investment.transaction_type == "SELL":
            property_to_update.total_quantity = Decimal(
                str(property_to_update.total_quantity)
            ) - Decimal(str(investment.area_in_sqyds))
            # When selling, we remove the proportional cost at current average price
            property_to_update.total_cost = Decimal(
                str(property_to_update.total_cost)
            ) - (
                                                    Decimal(str(property_to_update.average_price_per_unit))
                                                    * Decimal(str(investment.area_in_sqyds))
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
            float(property_to_update.total_cost / property_to_update.total_quantity)
            if property_to_update.total_quantity > 0
            else 0
        )
        property_to_update.last_updated = date.today()
    else:
        # Adding new real estate entry
        total_quantity = Decimal(str(investment.area_in_sqyds))
        total_cost_inr = (
                Decimal(str(investment.total_invested_amount)) * conversion_rate
        )

        new_property = RealEstateSummary(
            investor_id=investment.investor,
            property_type=investment.investment_subcategory_id,
            property_name=investment.property_name,
            property_location=investment.property_location,
            total_quantity=float(total_quantity),
            total_cost=float(total_cost_inr),
            average_price_per_unit=float(total_cost_inr / total_quantity),
            last_updated=date.today(),
        )
        db.add(new_property)

    db.commit()
