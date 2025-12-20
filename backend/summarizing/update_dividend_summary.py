from datetime import date
from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.stock import DividendSummary
from backend.schemas.investments.dividend_schema import DividendCreate


def update(db: Session, investment: DividendCreate):
    dividend = (
        db.query(DividendSummary)
        .filter(
            DividendSummary.investor == investment.investor,
            DividendSummary.stock_symbol == investment.stock_symbol,
        )
        .first()
    )

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    if dividend:
        dividend.total_amount += investment.amount
    else:
        new_summary = DividendSummary(
            investor=investment.investor,
            currency_id=investment.currency_id,
            region_id=investment.region_id,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_amount=investment.amount,
        )
        db.add(new_summary)

    # Create Income entry for ALL dividend transactions
    income = Income(
        user_id=investment.investor,
        source_id=4,
        amount=investment.amount,
        currency=currency_map[investment.currency_id],
        earned_date=investment.received_date or date.today(),  # type: ignore
    )
    db.add(income)

    db.commit()
