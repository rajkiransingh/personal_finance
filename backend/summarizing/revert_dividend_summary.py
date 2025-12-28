from sqlalchemy.orm import Session
from backend.models.investments.stock import DividendSummary, Dividends
from backend.summarizing.revert_utils import delete_related_income


def revert(db: Session, investment: Dividends):
    summary = (
        db.query(DividendSummary)
        .filter(
            DividendSummary.investor == investment.investor,
            DividendSummary.stock_symbol == investment.stock_symbol,
        )
        .first()
    )

    if summary:
        summary.total_amount -= float(investment.amount)
        # If total goes to < 0 (unlikely unless data error), we leave it.

    # Revert Income (Source ID 4 for Dividend)
    delete_related_income(
        db,
        user_id=investment.investor,
        source_id=4,
        amount=investment.amount,
        earned_date=(
            investment.received_date.date()
            if hasattr(investment.received_date, "date")
            else investment.received_date
        ),
    )
