from datetime import date
from sqlalchemy.orm import Session
import datetime

from backend.models.earnings.income import Income
from backend.models.investments.bullion import BullionSummary
from backend.schemas.investments.bullion_schema import BullionInvestmentCreate


def update(db: Session, investment: BullionInvestmentCreate):
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
            bullion.total_quantity += investment.quantity_in_grams
            bullion.total_cost += investment.total_invested_amount
        elif investment.transaction_type == "SELL":
            bullion.total_quantity -= investment.quantity_in_grams
            bullion.total_cost -= (
                bullion.average_price_per_unit * investment.quantity_in_grams
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
            bullion.total_cost / bullion.total_quantity
            if bullion.total_quantity > 0
            else 0
        )
        bullion.last_updated = datetime.datetime.utcnow()
    else:
        new_bullion = BullionSummary(
            investor_id=investment.investor,
            investment_type=investment.investment_subcategory_id,
            metal_name=investment.metal_name,
            total_quantity=investment.quantity_in_grams,
            total_cost=investment.total_invested_amount,
            average_price_per_unit=investment.total_invested_amount
            / investment.quantity_in_grams,
            last_updated=datetime.datetime.utcnow(),
        )
        db.add(new_bullion)

    db.commit()
