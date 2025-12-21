import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.cryptocurrency_rate_fetcher import (
    CryptoCurrencyRateFetcher as crF,
    CryptoFetcher,
)
from utilities.common.app_config import config
from utilities.fetch_overall_investment_data import get_investments_symbols

# Add the app root directory to Python path
sys.path.insert(0, "/app")

logger = config.setup_logger("scripts.fetch_crypto")
db: Session = next(get_db())

# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
crypto_coin_list = all_investment_data["crypto"]

try:
    cryData = crF.fetch_cryptocurrency_data_in_usd(CryptoFetcher, crypto_coin_list)

    if cryData and cryData.get("data"):
        crF.update_crypto_investments(CryptoFetcher, db, cryData)
        crF.update_crypto_summary(CryptoFetcher, db, cryData)
    else:
        logger.warning("No valid crypto data fetched. Skipping updates.")

except Exception as e:
    logger.error(f"Critical error in fetch_crypto script: {e}", exc_info=True)
