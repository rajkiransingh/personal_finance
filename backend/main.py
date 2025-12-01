import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.routes import dashboard_routes, portfolio_routes, screener_routes
from backend.routes import expense_routes, investment_summary_routes, \
    user_routes, income_routes
from backend.routes.analytics import score_routes
from backend.routes.categories import category_routes
from backend.routes.configurations import config_routes
from backend.routes.investments import stock as stock_route, mutual_fund as mf_route, bullion as bullion_route, \
    real_estate as re_route, crypto as crypto_route, dividend as dividend_route
from backend.services.db_services import get_db
from utilities.analytics.balancing_screener import BalancingScreener, balancingScreener
from utilities.analytics.stock_analyzer import get_stock_score
from utilities.analytics.stock_merger import StockMerger as sM, stockMerger
from utilities.cryptocurrency_rate_fetcher import CryptoCurrencyRateFetcher as crF, CryptoFetcher
from utilities.dashboard.dashboard_calculation_helper import DashboardDataCalculator
from utilities.dashboard.dashboard_calculation_helper import dashboardDataCalculator
from utilities.fetch_overall_investment_data import get_investments_symbols, get_dividends_data, categorize_stock
from utilities.forex_exchange_rate_fetcher import ForexExchangeRateFetcher as fEx, forexFetcher
from utilities.metal_rate_fetcher import MetalRateFetcher as mRF, bullionFetcher
from utilities.mutual_fund_price_fetcher import MutualFundPriceFetcher as mfF, mutualFundFetcher
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher

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
app.include_router(dashboard_routes.router)
app.include_router(portfolio_routes.router)
app.include_router(config_routes.router)
app.include_router(category_routes.router)
app.include_router(screener_routes.router)
app.include_router(score_routes.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"message": "API is running!"}


db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)

# Extracting investment specific data from the DB
common_stock_list = all_investment_data.get("common_stocks", {})
dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})
mutual_funds_list = all_investment_data['mutual_funds']
crypto_coin_list = all_investment_data['crypto']

# Get All the dividends data
dividends_data = get_dividends_data(db)

# Get Forex Data
fEx.get_exchange_rates(forexFetcher, "USD", "INR")
fEx.get_exchange_rates(forexFetcher, "PLN", "INR")
fEx.get_exchange_rates(forexFetcher, "USD", "PLN")

# Get the latest prices and NAVs
common_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, common_stock_list)
dividend_stock_prices = sPF.get_stock_prices_in_bulk(stockFetcher, dividend_stock_list)
sPF.update_stock_investments(stockFetcher, db, common_stock_prices)
sPF.update_stock_investments(stockFetcher, db, dividend_stock_prices, dividends_data)
sPF.update_stock_summary(stockFetcher, db, common_stock_prices)
sPF.update_stock_summary(stockFetcher, db, dividend_stock_prices, dividends_data)

mf_data = mfF.get_mutual_fund_rates_bulk(mutualFundFetcher, mutual_funds_list)
mfF.update_bullion_investments(mutualFundFetcher, db, mf_data)
mfF.update_bullion_summary(mutualFundFetcher, db, mf_data)

cryData = crF.fetch_cryptocurrency_data_in_usd(CryptoFetcher, crypto_coin_list)
crF.update_crypto_investments(CryptoFetcher, db, cryData)
crF.update_crypto_summary(CryptoFetcher, db, cryData)

bullion_data = {"Gold": mRF.get_gold_rate(bullionFetcher), "Silver": mRF.get_silver_rate(bullionFetcher)}
mRF.update_bullion_investments(bullionFetcher, db, bullion_data)
mRF.update_bullion_summary(bullionFetcher, db, bullion_data)

all_data = DashboardDataCalculator.get_investment_data(dashboardDataCalculator)
out = BalancingScreener.run_cycle(balancingScreener)
print(json.dumps(out, indent=2))


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    Returns default if conversion fails or value is None/'N/A'.
    """
    try:
        if value in [None, 'N/A', 'NaN', '-', '', 'nan']:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


common_stock_list.extend(dividend_stock_list)

# keep only items that are classified as "stock"
common_stock_list = [item for item in common_stock_list if categorize_stock(item) == "stock"]

# Entire data similar to what is stored in Redis can be fetched using this stored_data variable below
stock_data = sPF.get_stock_prices_in_bulk(stockFetcher, common_stock_list)
for stock, data in stock_data['data'].items():
    price = safe_float(data.get('currentPrice'))

    # Prefer trailing EPS, fall back to forward EPS
    eps = safe_float(data.get('trailingEps')) or stock.get("epsTrailingTwelveMonths")
    if not eps or eps <= 0:
        eps = safe_float(data.get('forwardEps'))

    # PE = Earnings per Share (EPS) / Price per Share
    if eps and isinstance(eps, (int, float)) and eps > 0:
        pe = price / eps
    else:
        pe = None

    debtToEquity = safe_float(data.get('debtToEquity'))
    promoterHolding = safe_float(data.get('promoterHolding'))

sM.merge_stock_lists(stockMerger)
sM.merge_with_ticker_data(stockMerger, db)
get_stock_score()
