from sqlalchemy.orm import Session
from backend.models.investments.crypto import CryptoSummary, CryptoInvestment
from backend.summarizing.revert_utils import delete_related_income
import datetime
from decimal import Decimal
from datetime import UTC


def revert(db: Session, investment: CryptoInvestment):
    coin = (
        db.query(CryptoSummary)
        .filter(
            CryptoSummary.investor_id == investment.investor,
            CryptoSummary.coin_symbol == investment.coin_symbol,
            CryptoSummary.crypto_name == investment.crypto_name,
        )
        .first()
    )

    if not coin:
        return

    qty = Decimal(str(investment.coin_quantity))
    avg_price = Decimal(str(coin.average_price_per_unit))

    if investment.transaction_type == "BUY":
        # DECISION: To ensure average price stability (least damage), we remove Cost = Quantity * AvgPrice.
        cost_to_remove = qty * avg_price

        coin.total_quantity = float(Decimal(str(coin.total_quantity)) - qty)
        coin.total_cost = float(Decimal(str(coin.total_cost)) - cost_to_remove)

    elif investment.transaction_type == "SELL":
        # Un-Sell: Add back quantity.
        # Add back Cost = Quantity * Current Avg Price.
        cost_to_add = qty * avg_price

        coin.total_quantity = float(Decimal(str(coin.total_quantity)) + qty)
        coin.total_cost = float(Decimal(str(coin.total_cost)) + cost_to_add)

        # Revert Income (Source ID 9 for Crypto)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=9,
            amount=investment.total_amount_after_sale,
            earned_date=(
                investment.investment_date.date()
                if hasattr(investment.investment_date, "date")
                else investment.investment_date
            ),
        )

    if Decimal(str(coin.total_quantity)) > 0:
        coin.average_price_per_unit = float(
            Decimal(str(coin.total_cost)) / Decimal(str(coin.total_quantity))
        )
    else:
        coin.average_price_per_unit = 0
        coin.total_cost = 0

    coin.last_updated = datetime.datetime.now(UTC)
