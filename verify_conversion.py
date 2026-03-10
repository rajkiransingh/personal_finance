import sys
from decimal import Decimal
from datetime import date

# Add project root to path
sys.path.append("/home/rajkiran/github/personal_finance")

from backend.services.db_services import SessionLocal
from backend.models.investments.crypto import CryptoSummary
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate
from backend.summarizing import update_crypto_summary
from backend.summarizing.currency_util import get_conversion_rate_to_inr


def test_crypto_conversion():
    db = SessionLocal()
    try:
        # Mock a USD crypto investment
        # Rate for USD-INR is usually around 80+
        usd_rate = get_conversion_rate_to_inr(3)
        print(f"Current USD-INR Rate: {usd_rate}")

        investor_id = 1
        coin_symbol = "VERIFY_BTC"
        crypto_name = "Verify Bitcoin"

        # Clean up existing if any
        db.query(CryptoSummary).filter(
            CryptoSummary.coin_symbol == coin_symbol
        ).delete()
        db.commit()

        investment = CryptoInvestmentCreate(
            investor=investor_id,
            coin_symbol=coin_symbol,
            crypto_name=crypto_name,
            coin_quantity=0.1,
            total_invested_amount=1000.0,  # 1000 USD
            currency_id=3,  # USD
            investment_date=date.today(),
            transaction_type="BUY",
        )

        update_crypto_summary.update(db, investment)

        summary = (
            db.query(CryptoSummary)
            .filter(CryptoSummary.coin_symbol == coin_symbol)
            .first()
        )

        expected_cost = Decimal("1000.0") * usd_rate
        actual_cost = Decimal(str(summary.total_cost))

        print(f"Expected Cost (INR): {expected_cost}")
        print(f"Actual Cost (INR): {actual_cost}")

        if abs(expected_cost - actual_cost) < 1:
            print("✅ Crypto Conversion Test Passed!")
        else:
            print("❌ Crypto Conversion Test Failed!")

    finally:
        db.close()


if __name__ == "__main__":
    test_crypto_conversion()
