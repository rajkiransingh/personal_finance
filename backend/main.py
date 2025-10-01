import logging

from fastapi import FastAPI
from sqlalchemy.orm import Session

from backend.routes import expense_routes, investment_summary_routes, \
    user_routes, income_routes
from backend.routes.investments import stock as stock_route, mutual_fund as mf_route, bullion as bullion_route, \
    real_estate as re_route, crypto as crypto_route, dividend as dividend_route
from backend.services.db_services import get_db
from backend.services.dividend_summary import get_all_dividends
from utilities.cryptocurrency_rate_fetcher import CryptoCurrencyRateFetcher as crF, CryptoFetcher
from utilities.forex_exchange_rate_fetcher import ForexExchangeRateFetcher as fEx, forexFetcher
from utilities.metal_rate_fetcher import MetalRateFetcher as mRF, bullionFetcher
from utilities.mutual_fund_price_fetcher import MutualFundPriceFetcher as mfF, mutualFundFetcher
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher
from utilities.update_investments import get_data_from_investments

# Initialize logging
logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(income_routes.router)
app.include_router(expense_routes.router)
app.include_router(stock_route.router)
app.include_router(mf_route.router)
app.include_router(bullion_route.router)
app.include_router(re_route.router)
app.include_router(crypto_route.router)
app.include_router(investment_summary_routes.router)
app.include_router(dividend_route.router)


@app.get("/")
def health_check():
    return {"message": "API is running!"}


db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_data_from_investments(db)

# Extracting investment specific data from the DB
common_stock_list = all_investment_data.get("common_stocks", {})
dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})
mutual_funds_list = all_investment_data['mutual_funds']
crypto_coin_list = all_investment_data['crypto']

# Get All the dividends data
dividends_data = get_all_dividends(db)

# Get Forex Data
fEx.get_exchange_rates(forexFetcher, "USD", "INR")
fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
fEx.get_exchange_rates(forexFetcher, "USD", "PLN")

# Get the latest prices and NAVs
logger.info(f"Common Stock List: {common_stock_list}")
logger.info(f"Dividend Stock List: {dividend_stock_list}")
common_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, common_stock_list)
dividend_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, dividend_stock_list)

logger.info(f"Mutual Fund list: {mutual_funds_list}")

mfF.get_mutual_fund_rates_bulk(mutualFundFetcher, mutual_funds_list)

cryData = crF.fetch_cryptocurrency_data_in_usd(CryptoFetcher, crypto_coin_list)
crF.update_crypto_investments(CryptoFetcher, db, cryData)
crF.update_crypto_summary(CryptoFetcher, db, cryData)

bullion_data = {"Gold": mRF.get_gold_rate(bullionFetcher), "Silver": mRF.get_silver_rate(bullionFetcher)}
mRF.update_bullion_investments(bullionFetcher, db, bullion_data)
mRF.update_bullion_summary(bullionFetcher, db, bullion_data)
