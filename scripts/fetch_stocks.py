import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import get_investments_symbols, get_dividends_data
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher

# Add the app root directory to Python path
sys.path.insert(0, '/app')

db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
dividends_data = get_dividends_data(db)

# Extracting investment specific data from the DB
common_stock_list = all_investment_data.get("common_stocks", {})
dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})

# Get the latest stock prices
common_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, common_stock_list)
dividend_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, dividend_stock_list)

# update the investment and summary
sPF.update_stock_investments(stockFetcher, db, common_stock_prices)
sPF.update_stock_investments(stockFetcher, db, dividend_stock_prices, dividends_data)

sPF.update_stock_summary(stockFetcher, db, common_stock_prices)
sPF.update_stock_summary(stockFetcher, db, dividend_stock_prices, dividends_data)
