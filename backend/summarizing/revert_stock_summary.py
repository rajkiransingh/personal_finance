import datetime
from datetime import UTC
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.models.investments.stock import StockSummary, StockInvestment
from backend.summarizing.revert_utils import delete_related_income


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
        return

    qty = Decimal(str(investment.stock_quantity))
    avg_price = Decimal(str(stock.average_price_per_unit))

    if investment.transaction_type == "BUY":
        cost_to_remove = qty * avg_price

        stock.total_quantity = float(Decimal(str(stock.total_quantity)) - qty)
        stock.total_cost = float(Decimal(str(stock.total_cost)) - cost_to_remove)

    elif investment.transaction_type == "SELL":
        cost_to_add = qty * avg_price

        stock.total_quantity = float(Decimal(str(stock.total_quantity)) + qty)
        stock.total_cost = float(Decimal(str(stock.total_cost)) + cost_to_add)

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

    if Decimal(str(stock.total_quantity)) > 0:
        stock.average_price_per_unit = float(
            Decimal(str(stock.total_cost)) / Decimal(str(stock.total_quantity))
        )
    else:
        stock.average_price_per_unit = 0.0
        stock.total_cost = 0.0

    stock.last_updated = datetime.datetime.now(UTC)
