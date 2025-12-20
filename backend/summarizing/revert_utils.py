from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.models.earnings.income import Income


def delete_related_income(
    db: Session, user_id: int, source_id: int, amount: float, earned_date: date
):
    """
    Finds and deletes a matching Income entry.
    Used when reverting 'Sell' or 'Dividend' transactions.
    Matches by user_id, source_id, amount, and date.
    Deletes only one entry to avoid over-deletion if duplicates exist.
    """
    # Allow some flexibility in date? No, strict matching for now as creation uses exact date.
    income_entry = (
        db.query(Income)
        .filter(
            Income.user_id == user_id,
            Income.source_id == source_id,
            Income.amount == amount,
            func.date(Income.earned_date) == earned_date,
        )
        .first()
    )

    if income_entry:
        db.delete(income_entry)
        # We generally don't commit here, let the caller commit the whole transaction
