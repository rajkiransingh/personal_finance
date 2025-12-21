import sys

from utilities.forex_exchange_rate_fetcher import (
    ForexExchangeRateFetcher as fEx,
    forexFetcher,
)
from utilities.common.app_config import config

sys.path.insert(0, "/app")

logger = config.setup_logger("scripts.fetch_forex")

try:
    # Get Forex Data
    fEx.get_exchange_rates(forexFetcher, "USD", "INR")
    fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
    fEx.get_exchange_rates(forexFetcher, "USD", "PLN")

except Exception as e:
    logger.error(f"Critical error in fetch_forex script: {e}", exc_info=True)
