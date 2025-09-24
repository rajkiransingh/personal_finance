import logging
import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from backend.services.investments.dividend import get_all_dividends
from utilities.stock_price_fetcher import get_stock_prices_in_bulk
from utilities.update_investments import get_data_from_investments

# Add the app root directory to Python path
sys.path.insert(0, '/app')

# Initialize logging
logger = logging.getLogger(__name__)

db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_data_from_investments(db)
# Get All the dividends data
dividends_data = get_all_dividends(db)

# Extracting investment specific data from the DB
common_stock_list = all_investment_data.get("common_stocks", {})
dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})

# Get the latest prices and NAVs
logger.info(f"Common Stock List: {common_stock_list}")
logger.info(f"Dividend Stock List: {dividend_stock_list}")

# common_stock_prices = get_stock_prices_in_bulk(common_stock_list)
dividend_stock_prices = get_stock_prices_in_bulk(dividend_stock_list)
