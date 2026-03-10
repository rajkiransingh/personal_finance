from datetime import date
from sqlalchemy.orm import Session
from decimal import Decimal
import datetime

from backend.models.earnings.income import Income
from backend.models.investments.mutual_fund import MutualFundSummary
from backend.schemas.investments.mutual_fund_schema import MutualFundInvestmentCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: MutualFundInvestmentCreate):
    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    fund = (
        db.query(MutualFundSummary)
        .filter(
            MutualFundSummary.investor_id == investment.investor,
            MutualFundSummary.scheme_code == investment.scheme_code,
            MutualFundSummary.fund_name == investment.fund_name,
        )
        .first()
    )

    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    if fund:
        if investment.transaction_type == "BUY":
            fund.total_quantity = Decimal(str(fund.total_quantity)) + Decimal(
                str(investment.unit_quantity)
            )
            # Add cost in INR
            fund.total_cost = Decimal(str(fund.total_cost)) + (
                Decimal(str(investment.total_invested_amount)) * conversion_rate
            )
        elif investment.transaction_type == "SELL":
            fund.total_quantity = Decimal(str(fund.total_quantity)) - Decimal(
                str(investment.unit_quantity)
            )
            # When selling, we remove the proportional cost at current average price
            fund.total_cost = Decimal(str(fund.total_cost)) - (
                Decimal(str(investment.unit_quantity))
                * Decimal(str(fund.average_price_per_unit))
            )

            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=5,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today(),  # type: ignore
            )
            db.add(income)

        fund.average_price_per_unit = (
            float(fund.total_cost) / float(fund.total_quantity)
            if fund.total_quantity > 0
            else Decimal("0")
        )
        fund.last_updated = datetime.datetime.utcnow()
    else:
        # Adding new fund
        total_quantity = Decimal(str(investment.unit_quantity))
        total_cost_inr = (
            Decimal(str(investment.total_invested_amount)) * conversion_rate
        )

        new_fund = MutualFundSummary(
            investor_id=investment.investor,
            scheme_code=investment.scheme_code,
            fund_name=investment.fund_name,
            total_quantity=float(total_quantity),
            total_cost=float(total_cost_inr),
            average_price_per_unit=float(total_cost_inr / total_quantity),
            last_updated=datetime.datetime.utcnow(),
        )
        db.add(new_fund)
    db.commit()
