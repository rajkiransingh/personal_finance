import sys
from datetime import date

# Add project root to path
sys.path.append("/home/rajkiran/github/personal_finance")

from backend.services.db_services import SessionLocal
from backend.models.investments.crypto import CryptoSummary, CryptoInvestment
from backend.schemas.investments.crypto_schema import CryptoInvestmentCreate
from backend.summarizing import update_crypto_summary, revert_crypto_summary


def test_crypto_revert():
    db = SessionLocal()
    try:
        investor_id = 1
        coin_symbol = "REVERT_BTC"
        crypto_name = "Revert Bitcoin"

        # Clean up existing
        db.query(CryptoSummary).filter(
            CryptoSummary.coin_symbol == coin_symbol
        ).delete()
        db.query(CryptoInvestment).filter(
            CryptoInvestment.coin_symbol == coin_symbol
        ).delete()
        db.commit()

        # 1. Buy
        investment = CryptoInvestmentCreate(
            investor=investor_id,
            coin_symbol=coin_symbol,
            crypto_name=crypto_name,
            coin_quantity=0.1,
            total_invested_amount=8000.0,  # 8000 INR
            currency_id=1,  # INR
            investment_date=date.today(),
            transaction_type="BUY",
        )

        update_crypto_summary.update(db, investment)

        # Get the investment record created (update script commits)
        inv_record = (
            db.query(CryptoInvestment)
            .filter(CryptoInvestment.coin_symbol == coin_symbol)
            .first()
        )

        summary = (
            db.query(CryptoSummary)
            .filter(CryptoSummary.coin_symbol == coin_symbol)
            .first()
        )
        print(
            f"Summary after BUY: Qty={summary.total_quantity}, Cost={summary.total_cost}"
        )

        # 2. Revert Buy
        revert_crypto_summary.revert(db, inv_record)
        db.commit()

        summary = (
            db.query(CryptoSummary)
            .filter(CryptoSummary.coin_symbol == coin_symbol)
            .first()
        )
        print(
            f"Summary after REVERT BUY: Qty={summary.total_quantity}, Cost={summary.total_cost}"
        )

        if abs(summary.total_quantity) < 0.00000001 and abs(summary.total_cost) < 0.01:
            print("✅ Crypto Revert Test (BUY) Passed!")
        else:
            print("❌ Crypto Revert Test (BUY) Failed!")

    except Exception as e:
        print(f"❌ Crypto Revert Test Failed with Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_crypto_revert()
