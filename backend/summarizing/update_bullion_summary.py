from datetime import date
from sqlalchemy.orm import Session
from decimal import Decimal
import datetime

from backend.models.earnings.income import Income
from backend.models.investments.bullion import BullionSummary
from backend.schemas.investments.bullion_schema import BullionInvestmentCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: BullionInvestmentCreate):
    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    bullion = (
        db.query(BullionSummary)
        .filter(
            BullionSummary.investor_id == investment.investor,
            BullionSummary.investment_type == investment.investment_subcategory_id,
        )
        .first()
    )

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    if bullion:
        if investment.transaction_type == "BUY":
            bullion.total_quantity = Decimal(str(bullion.total_quantity)) + Decimal(
                str(investment.quantity_in_grams)
            )
            # Add cost in INR
            bullion.total_cost = Decimal(str(bullion.total_cost)) + (
                Decimal(str(investment.total_invested_amount)) * conversion_rate
            )
        elif investment.transaction_type == "SELL":
            bullion.total_quantity = Decimal(str(bullion.total_quantity)) - Decimal(
                str(investment.quantity_in_grams)
            )
            # When selling, we remove the proportional cost at current average price
            bullion.total_cost = Decimal(str(bullion.total_cost)) - (
                Decimal(str(bullion.average_price_per_unit))
                * Decimal(str(investment.quantity_in_grams))
            )

            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=11,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today(),  # type: ignore
            )
            db.add(income)

        bullion.average_price_per_unit = (
            float(bullion.total_cost / bullion.total_quantity)
            if bullion.total_quantity > 0
            else 0
        )
        bullion.last_updated = datetime.datetime.utcnow()
    else:
        # Adding new bullion entry
        total_quantity = Decimal(str(investment.quantity_in_grams))
        total_cost_inr = (
            Decimal(str(investment.total_invested_amount)) * conversion_rate
        )

        new_bullion = BullionSummary(
            investor_id=investment.investor,
            investment_type=investment.investment_subcategory_id,
            metal_name=investment.metal_name,
            total_quantity=float(total_quantity),
            total_cost=float(total_cost_inr),
            average_price_per_unit=float(total_cost_inr / total_quantity),
            last_updated=datetime.datetime.utcnow(),
        )
        db.add(new_bullion)

    db.commit()
