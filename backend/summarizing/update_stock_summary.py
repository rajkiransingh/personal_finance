from datetime import date
from sqlalchemy.orm import Session
from decimal import Decimal
import datetime

from backend.models.earnings.income import Income
from backend.models.investments.stock import StockSummary
from backend.schemas.investments.stock_schema import StockInvestmentCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: StockInvestmentCreate):
    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    stock = (
        db.query(StockSummary)
        .filter(
            StockSummary.investor_id == investment.investor,
            StockSummary.stock_symbol == investment.stock_symbol,
        )
        .first()
    )

    currency_map = {1: "INR", 2: "PLN", 3: "USD"}

    if stock:
        if investment.transaction_type == "BUY":
            stock.total_quantity = Decimal(str(stock.total_quantity)) + Decimal(
                str(investment.stock_quantity)
            )
            # Add cost in INR
            stock.total_cost = Decimal(str(stock.total_cost)) + (
                Decimal(str(investment.total_invested_amount)) * conversion_rate
            )
        elif investment.transaction_type == "SELL":
            stock.total_quantity = Decimal(str(stock.total_quantity)) - Decimal(
                str(investment.stock_quantity)
            )
            # When selling, we remove the proportional cost at current average price
            stock.total_cost = Decimal(str(stock.total_cost)) - (
                Decimal(str(investment.stock_quantity))
                * Decimal(str(stock.average_price_per_unit))
            )

            currency = currency_map.get(investment.currency_id, "INR")
            # Record earnings from sale
            income = Income(
                user_id=investment.investor,
                source_id=8,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today(),  # type: ignore
            )
            db.add(income)

        stock.average_price_per_unit = (
            float(stock.total_cost / stock.total_quantity)
            if stock.total_quantity > 0
            else 0
        )
        stock.last_updated = datetime.datetime.utcnow()
        stock.dividend_paying = investment.dividend_paying
    else:
        # Adding new stock
        total_quantity = Decimal(str(investment.stock_quantity))
        total_cost_inr = (
            Decimal(str(investment.total_invested_amount)) * conversion_rate
        )

        new_stock = StockSummary(
            investor_id=investment.investor,
            stock_symbol=investment.stock_symbol,
            stock_name=investment.stock_name,
            total_quantity=float(total_quantity),
            total_cost=float(total_cost_inr),
            average_price_per_unit=float(total_cost_inr / total_quantity),
            last_updated=datetime.datetime.utcnow(),
            dividend_paying=investment.dividend_paying,
        )
        db.add(new_stock)

    db.commit()
