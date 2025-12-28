from sqlalchemy.orm import Session
from backend.models.investments.stock import StockSummary, StockInvestment
from backend.summarizing.revert_utils import delete_related_income
import datetime


def revert(db: Session, investment: StockInvestment):
    stock = (
        db.query(StockSummary)
        .filter(
            StockSummary.investor_id == investment.investor,
            StockSummary.stock_symbol == investment.stock_symbol,
        )
        .first()
    )

    if not stock:
        # If summary doesn't exist, we can't revert anything.
        # This could happen if summary was manually deleted?
        return

    if investment.transaction_type == "BUY":
        # Logic: Reduce quantity and cost
        # If we remove the only transaction, summary might go to 0/0.

        stock.total_quantity -= float(investment.stock_quantity)
        stock.total_cost -= float(investment.total_invested_amount)

        # Recalculate Average
        if stock.total_quantity > 0:
            stock.average_price_per_unit = stock.total_cost / stock.total_quantity
        else:
            stock.average_price_per_unit = 0.0
            # Optional: If qty is 0, should we delete summary?
            # Keeping it is safer for history, but cost/qty 0 is fine.

    elif investment.transaction_type == "SELL":
        # Logic: Add back quantity.
        # Add back Cost.
        # Issue: We don't know exact cost basis removed.
        # Approximation: Use Current Average Price * Quantity.
        # This assumes the "un-sold" shares have the same cost profile as current holdings.

        cost_to_add = float(investment.stock_quantity) * stock.average_price_per_unit

        stock.total_quantity += float(investment.stock_quantity)
        stock.total_cost += cost_to_add

        # Average Price should technically remain same (x/y = (x+c)/(y+q) if c/q = x/y)
        # So no need to update average_price_per_unit, but updating it won't hurt to be precise.
        if stock.total_quantity > 0:
            stock.average_price_per_unit = stock.total_cost / stock.total_quantity

        # Revert Income (Source ID 8 for Stock)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=8,
            amount=investment.total_amount_after_sale,
            earned_date=(
                investment.investment_date.date()
                if hasattr(investment.investment_date, "date")
                else investment.investment_date
            ),
        )

    stock.last_updated = datetime.datetime.utcnow()
