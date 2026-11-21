import sys

# Add the app root directory to Python path
sys.path.insert(0, "/app")

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.cryptocurrency_rate_fetcher import (
    CryptoCurrencyRateFetcher as crF,
    CryptoFetcher,
)
from utilities.common.app_config import config
from utilities.fetch_overall_investment_data import get_investments_symbols

logger = config.setup_logger("scripts.fetch_crypto")

# ---------------------------------------------------------------------------
# Pre-flight: ensure forex rates are in Redis before running crypto updates.
# Crypto prices are fetched in USD; without valid forex rates the conversion
# to INR silently falls back to 1.0, corrupting current_total_value and ROI.
# ---------------------------------------------------------------------------
_REQUIRED_FOREX_KEYS = ["forex::USD-INR", "forex::PLN-INR", "forex::USD-PLN"]
_redis = config.redis_client()
_missing_forex = [k for k in _REQUIRED_FOREX_KEYS if not _redis.exists(k)]
if _missing_forex:
    logger.warning(
        f"⚠️  Forex cache keys missing: {_missing_forex}. "
        "Triggering on-demand forex fetch before crypto updates to avoid 1.0 fallback."
    )
    from utilities.forex_exchange_rate_fetcher import ForexExchangeRateFetcher as fEx, forexFetcher
    fEx.get_exchange_rates(forexFetcher, "USD", "INR")
    fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
    fEx.get_exchange_rates(forexFetcher, "USD", "PLN")
    logger.info("✅ Forex rates fetched and cached. Proceeding with crypto updates.")
db: Session = next(get_db())

# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
crypto_coin_list = all_investment_data["crypto"]

try:
    cryData = crF.fetch_cryptocurrency_data_in_usd(
        CryptoFetcher, crypto_coin_list
    )

    if cryData and cryData.get("data"):
        crF.update_crypto_investments(CryptoFetcher, db, cryData)
        crF.update_crypto_summary(CryptoFetcher, db, cryData)
    else:
        logger.warning("No valid crypto data fetched. Skipping updates.")

except Exception as e:
    logger.error(f"Critical error in fetch_crypto script: {e}", exc_info=True)
finally:
    db.close()
