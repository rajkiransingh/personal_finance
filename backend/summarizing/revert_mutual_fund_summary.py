from sqlalchemy.orm import Session
from backend.models.investments.mutual_fund import (
    MutualFundSummary,
    MutualFundInvestment,
)
from backend.summarizing.revert_utils import delete_related_income
import datetime
from decimal import Decimal
from datetime import UTC


def revert(db: Session, investment: MutualFundInvestment):
    fund = (
        db.query(MutualFundSummary)
        .filter(
            MutualFundSummary.investor_id == investment.investor,
            MutualFundSummary.scheme_code == investment.scheme_code,
            MutualFundSummary.fund_name == investment.fund_name,
        )
        .first()
    )

    if not fund:
        return

    qty = Decimal(str(investment.unit_quantity))
    avg_price = Decimal(str(fund.average_price_per_unit))

    if investment.transaction_type == "BUY":
        # Revert Buy: Remove qty and cost using average price for stability
        cost_to_remove = qty * avg_price

        fund.total_quantity = float(Decimal(str(fund.total_quantity)) - qty)
        fund.total_cost = float(Decimal(str(fund.total_cost)) - cost_to_remove)

    elif investment.transaction_type == "SELL":
        # Revert Sell: Add back qty and cost
        cost_to_add = qty * avg_price

        fund.total_quantity = float(Decimal(str(fund.total_quantity)) + qty)
        fund.total_cost = float(Decimal(str(fund.total_cost)) + cost_to_add)

        # Revert Income (Source ID 5 for Mutual Fund)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=5,
            amount=investment.total_amount_after_sale,
            earned_date=(
                investment.investment_date.date()
                if hasattr(investment.investment_date, "date")
                else investment.investment_date
            ),
        )

    # Recalculate Average
    total_q = Decimal(str(fund.total_quantity))
    total_c = Decimal(str(fund.total_cost))

    if total_q > 0:
        fund.average_price_per_unit = float(total_c / total_q)
    else:
        fund.average_price_per_unit = 0.0
        fund.total_cost = 0.0

    fund.last_updated = datetime.datetime.now(UTC)
