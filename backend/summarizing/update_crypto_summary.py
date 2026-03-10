from datetime import date
from decimal import Decimal
import datetime
from sqlalchemy.orm import Session

from backend.models.earnings.income import Income
from backend.models.investments.crypto import CryptoSummary
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def update(db: Session, investment: CryptoInvestmentCreate):
    # Get conversion rate to INR
    conversion_rate = get_conversion_rate_to_inr(investment.currency_id)

    coin = (
        db.query(CryptoSummary)
        .filter(
            CryptoSummary.investor_id == investment.investor,
            CryptoSummary.coin_symbol == investment.coin_symbol,
            CryptoSummary.crypto_name == investment.crypto_name,
        )
        .first()
    )

    if coin:
        if investment.transaction_type == "BUY":
            coin.total_quantity = float(
                Decimal(str(coin.total_quantity))
                + Decimal(str(investment.coin_quantity))
            )
            # Add cost in INR
            coin.total_cost = float(
                Decimal(str(coin.total_cost))
                + Decimal(str(investment.total_invested_amount)) * conversion_rate
            )
        elif investment.transaction_type == "SELL":
            coin.total_quantity = float(
                Decimal(str(coin.total_quantity))
                - Decimal(str(investment.coin_quantity))
            )
            # When selling, we remove the proportional cost at current average price
            coin.total_cost = float(
                Decimal(str(coin.total_cost))
                - Decimal(str(coin.average_price_per_unit))
                * Decimal(str(investment.coin_quantity))
            )

            # Record earnings from sale
            currency_map = {1: "INR", 2: "PLN", 3: "USD"}
            currency = currency_map.get(investment.currency_id, "INR")
            income = Income(
                user_id=investment.investor,
                source_id=9,
                amount=investment.total_amount_after_sale,
                currency=currency,
                earned_date=investment.investment_date or date.today(),  # type: ignore
            )
            db.add(income)

        if coin.total_quantity > 0:
            coin.average_price_per_unit = float(
                Decimal(str(coin.total_cost)) / Decimal(str(coin.total_quantity))
            )
        else:
            coin.average_price_per_unit = 0
            coin.total_cost = 0

        coin.last_updated = datetime.datetime.utcnow()
    else:
        # Adding new coin
        total_quantity = Decimal(str(investment.coin_quantity))
        total_cost_inr = (
            Decimal(str(investment.total_invested_amount)) * conversion_rate
        )

        new_coin = CryptoSummary(
            investor_id=investment.investor,
            coin_symbol=investment.coin_symbol,
            crypto_name=investment.crypto_name,
            total_quantity=float(total_quantity),
            total_cost=float(total_cost_inr),
            average_price_per_unit=float(total_cost_inr / total_quantity),
            last_updated=datetime.datetime.utcnow(),
        )
        db.add(new_coin)

    db.commit()
