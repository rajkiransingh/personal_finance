from sqlalchemy.orm import Session
from backend.models.investments.bullion import BullionSummary, BullionInvestment
from backend.summarizing.revert_utils import delete_related_income
import datetime
from decimal import Decimal
from datetime import UTC


def revert(db: Session, investment: BullionInvestment):
    bullion = (
        db.query(BullionSummary)
        .filter(
            BullionSummary.investor_id == investment.investor,
            BullionSummary.investment_type == investment.investment_subcategory_id,
        )
        .first()
    )

    if not bullion:
        return

    qty = Decimal(str(investment.quantity_in_grams))
    avg_price = Decimal(str(bullion.average_price_per_unit))

    if investment.transaction_type == "BUY":
        cost_to_remove = qty * avg_price
        bullion.total_quantity = float(Decimal(str(bullion.total_quantity)) - qty)
        bullion.total_cost = float(Decimal(str(bullion.total_cost)) - cost_to_remove)

    elif investment.transaction_type == "SELL":
        cost_to_add = qty * avg_price

        bullion.total_quantity = float(Decimal(str(bullion.total_quantity)) + qty)
        bullion.total_cost = float(Decimal(str(bullion.total_cost)) + cost_to_add)

        # Revert Income (Source ID 11 for Bullion)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=11,
            amount=investment.total_amount_after_sale,
            earned_date=(
                investment.investment_date.date()
                if hasattr(investment.investment_date, "date")
                else investment.investment_date
            ),
        )

    if Decimal(str(bullion.total_quantity)) > 0:
        bullion.average_price_per_unit = float(
            Decimal(str(bullion.total_cost)) / Decimal(str(bullion.total_quantity))
        )
    else:
        bullion.average_price_per_unit = 0.0
        bullion.total_cost = 0.0

    bullion.last_updated = datetime.datetime.now(UTC)
