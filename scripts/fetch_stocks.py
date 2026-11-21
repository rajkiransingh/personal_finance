import sys

# Add the app root directory to Python path
sys.path.insert(0, "/app")

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import (
    get_investments_symbols,
    get_dividends_data,
)
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher
from utilities.common.app_config import config

logger = config.setup_logger("scripts.fetch_stocks")
db: Session = next(get_db())

# ---------------------------------------------------------------------------
# Pre-flight: ensure forex rates are in Redis before running stock updates.
# Stock prices may be quoted in USD or PLN; without valid forex rates the INR
# conversion silently falls back to 1.0, corrupting current_total_value and ROI.
# ---------------------------------------------------------------------------
_REQUIRED_FOREX_KEYS = ["forex::USD-INR", "forex::PLN-INR", "forex::USD-PLN"]
_redis = config.redis_client()
_missing_forex = [k for k in _REQUIRED_FOREX_KEYS if not _redis.exists(k)]
if _missing_forex:
    logger.warning(
        f"⚠️  Forex cache keys missing: {_missing_forex}. "
        "Triggering on-demand forex fetch before stock updates to avoid 1.0 fallback."
    )
    from utilities.forex_exchange_rate_fetcher import ForexExchangeRateFetcher as fEx, forexFetcher
    fEx.get_exchange_rates(forexFetcher, "USD", "INR")
    fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
    fEx.get_exchange_rates(forexFetcher, "USD", "PLN")
    logger.info("✅ Forex rates fetched and cached. Proceeding with stock updates.")

# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
dividends_data = get_dividends_data(db)

# Extracting investment specific data from the DB
common_stock_list = all_investment_data.get("common_stocks", {})
dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})

try:
    # Get stock prices (checks Redis first; only calls API for symbols not present in Redis)
    common_stock_prices = sPF.get_stock_prices_in_bulk(
        stockFetcher, common_stock_list
    )
    dividend_stock_prices = sPF.get_stock_prices_in_bulk(
        stockFetcher, dividend_stock_list
    )

    # update the investment and summary
    if common_stock_prices and common_stock_prices.get("data"):
        sPF.update_stock_investments(stockFetcher, db, common_stock_prices)
        sPF.update_stock_summary(stockFetcher, db, common_stock_prices)

    if dividend_stock_prices and dividend_stock_prices.get("data"):
        sPF.update_stock_investments(
            stockFetcher, db, dividend_stock_prices, dividends_data
        )
        sPF.update_stock_summary(
            stockFetcher, db, dividend_stock_prices, dividends_data
        )

except Exception as e:
    logger.error(f"Critical error in fetch_stocks script: {e}", exc_info=True)
finally:
    db.close()
