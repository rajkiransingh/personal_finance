from sqlalchemy.orm import Session
from backend.models.investments.crypto import CryptoSummary, CryptoInvestment
from backend.summarizing.revert_utils import delete_related_income
import datetime


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

    if investment.transaction_type == "BUY":
        # Note: Crypto uses a conversion rate for cost in 'update'.
        # But 'total_invested_amount' in DB should be in uniform currency?
        # Let's check update_crypto_summary.py.
        # It converts: coin.total_cost += investment.total_invested_amount * conversion_rate
        # But Investment record stores total_invested_amount (original currency).
        # PROBLEM: We need the conversion rate used at time of Buy!
        # We don't have it stored.
        # Approximation: We have to re-fetch current conversion rate? NO, that's wrong.
        # Check CryptoInvestment model. Does it store 'invested_value_in_base_currency'?
        # It has 'total_invested_amount'.

        # Assumption: For now, assuming INR (conv=1) or we accept slight drift.
        # Improving: We can try to use average price?
        # coin.total_cost -= (investment.coin_quantity * coin.average_price_per_unit)
        # This is symmetric to Sell logic. "Un-buying" at current average price.
        # This keeps the average price constant, which is... okay?
        # Actually, if you Un-Buy, you want to remove the specific cost that was added.
        # But we don't know it because of FX.
        # Let's use the 'current avg price' approximation for BUY revert as well?
        # No, Un-Buying should ideally remove the exact cost.
        # If we assume mostly INR, we can use `total_invested_amount`.
        # Given the complexity, we'll try to use the cost from Avg Price to keep stability.

        # DECISION: To ensure average price stability (least damage), we remove Cost = Quantity * AvgPrice.
        # This effectively treats the removed Buy as an "Average Buy".

        cost_to_remove = float(investment.coin_quantity) * coin.average_price_per_unit

        coin.total_quantity -= float(investment.coin_quantity)
        coin.total_cost -= cost_to_remove

        # Avg Price stays same.

    elif investment.transaction_type == "SELL":
        # Un-Sell: Add back quantity.
        # Add back Cost = Quantity * Current Avg Price.

        cost_to_add = float(investment.coin_quantity) * coin.average_price_per_unit

        coin.total_quantity += float(investment.coin_quantity)
        coin.total_cost += cost_to_add

        # Revert Income (Source ID 9 for Crypto)
        delete_related_income(
            db,
            user_id=investment.investor,
            source_id=9,
            amount=investment.total_amount_after_sale,
            earned_date=investment.investment_date.date()
            if hasattr(investment.investment_date, "date")
            else investment.investment_date,
        )

    if coin.total_quantity > 0:
        coin.average_price_per_unit = coin.total_cost / coin.total_quantity
    else:
        coin.average_price_per_unit = 0

    coin.last_updated = datetime.datetime.utcnow()
