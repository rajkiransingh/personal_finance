from sqlalchemy.orm import Session
from backend.models.investments.bullion import BullionSummary, BullionInvestment
from backend.summarizing.revert_utils import delete_related_income
import datetime


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

    qty = float(investment.quantity_in_grams)

    if investment.transaction_type == "BUY":
        bullion.total_quantity -= qty
        bullion.total_cost -= float(investment.total_invested_amount)

    elif investment.transaction_type == "SELL":
        avg_price = bullion.average_price_per_unit
        cost_to_add = qty * avg_price

        bullion.total_quantity += qty
        bullion.total_cost += cost_to_add

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

    if bullion.total_quantity > 0:
        bullion.average_price_per_unit = bullion.total_cost / bullion.total_quantity
    else:
        bullion.average_price_per_unit = 0.0

    bullion.last_updated = datetime.datetime.utcnow()
