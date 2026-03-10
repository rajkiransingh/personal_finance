from datetime import date
from sqlalchemy.orm import Session
from decimal import Decimal

from backend.models.earnings.income import Income
from backend.models.investments.stock import DividendSummary
from backend.schemas.investments.dividend_schema import DividendCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: DividendCreate):
    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    dividend = (
        db.query(DividendSummary)
        .filter(
            DividendSummary.investor == investment.investor,
            DividendSummary.stock_symbol == investment.stock_symbol,
        )
        .first()
    )

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    # Amount in INR
    amount_inr = Decimal(str(investment.amount)) * conversion_rate

    if dividend:
        dividend.total_amount = float(Decimal(str(dividend.total_amount)) + amount_inr)
    else:
        new_summary = DividendSummary(
            investor=investment.investor,
            currency_id=investment.currency_id,
            region_id=investment.region_id,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_amount=float(amount_inr),
        )
        db.add(new_summary)

    # Create Income entry for ALL dividend transactions
    income = Income(
        user_id=investment.investor,
        source_id=4,
        amount=investment.amount,  # Keep original amount in Income table for now as per user focus on "summary table"
        currency=currency_map.get(investment.currency_id, "INR"),
        earned_date=investment.received_date or date.today(),  # type: ignore
    )
    db.add(income)

    db.commit()
