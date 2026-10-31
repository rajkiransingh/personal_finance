import sys

# Add the app root directory to Python path
sys.path.insert(0, "/app")

from utilities.forex_exchange_rate_fetcher import (
    ForexExchangeRateFetcher as fEx,
    forexFetcher,
)
from utilities.common.app_config import config

logger = config.setup_logger("scripts.fetch_forex")

try:
    # Force refresh Forex Data from open exchange API
    fEx.get_exchange_rates(forexFetcher, "USD", "INR", force_refresh=True)
    fEx.get_exchange_rates(forexFetcher, "PLN", "INR", force_refresh=True)
    fEx.get_exchange_rates(forexFetcher, "USD", "PLN", force_refresh=True)

except Exception as e:
    logger.error(f"Critical error in fetch_forex script: {e}", exc_info=True)
