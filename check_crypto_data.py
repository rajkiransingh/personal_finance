import sys

# Add project root to path
sys.path.append("/home/rajkiran/github/personal_finance")

from backend.services.db_services import SessionLocal
from backend.models.investments.crypto import CryptoSummary


def check_data():
    db = SessionLocal()
    try:
        summaries = db.query(CryptoSummary).all()
        print(f"Found {len(summaries)} crypto summaries.")
        for s in summaries:
            # Using str() for Decimal to avoid formatting issues in print
            print(
                f"Symbol: {s.coin_symbol}, Qty: {s.total_quantity}, Cost: {s.total_cost}, Current Value: {s.current_value}, Last Updated: {s.last_updated}"
            )
    except Exception as e:
        print(f"Error checking data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_data()
