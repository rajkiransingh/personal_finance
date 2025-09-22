from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.routes import user_routes
from backend.routes import income_routes
from backend.routes import expense_routes
from backend.routes import stock_investment_routes, mutual_fund_investment_routes, bullion_investment_routes, real_estate_investment_routes, crypto_investment_routes, dividend_routes
from backend.routes import investment_summary_routes
from backend.services.db_services import get_db
from utilities.get_crypto_rates import fetch_cryptocurrency_data
from utilities.get_current_metal_rates import get_gold_rate, get_silver_rate
# from utilities.get_exchange_rates import get_exchange_rates
from utilities.get_stock_prices import get_stock_prices_in_bulk
from utilities.get_mf_rates import get_mutual_fund_rates_bulk, get_mutual_fund_nav_dict
from utilities.update_investments import get_data_from_investments
# from utilities.update_investment_summary import get_data_from_investment_summary
from backend.services.dividend_service import get_all_dividends
import logging
# import requests
import json


# Initialize logging
logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(income_routes.router)
app.include_router(expense_routes.router)
app.include_router(stock_investment_routes.router)
app.include_router(mutual_fund_investment_routes.router)
app.include_router(bullion_investment_routes.router)
app.include_router(real_estate_investment_routes.router)
app.include_router(crypto_investment_routes.router)
app.include_router(investment_summary_routes.router)
app.include_router(dividend_routes.router)

# All the Mutual Funds can be checked in here: https://www.amfiindia.com/spages/NAVAll.txt

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

# Get the latest prices and NAVs
logger.info(f"Common Stock List: {common_stock_list}")
logger.info(f"Dividend Stock List: {dividend_stock_list}")
# common_stock_prices = get_stock_prices_in_bulk(common_stock_list)
dividend_stock_prices = get_stock_prices_in_bulk(dividend_stock_list)

logger.info(f"Mutual Fund list: {mutual_funds_list}")

fetch_cryptocurrency_data(crypto_coin_list)
get_gold_rate()
get_silver_rate()
#All_mutual_fund_data = get_mutual_fund_rates_bulk(mutual_funds_list)
# mf_navs = get_mutual_fund_nav_dict(All_mutual_fund_data)
# logger.info(f"MF NAVs: {mf_navs}")

# update_stock_prices(db, common_stock_prices, dividend_stock_prices, dividends_data)
# print("**************************** Some New Lines ************************")
# #update_mutual_fund_values(db, mf_navs)


# # Get the latest prices and NAVs
# logger.info(f"Common Stock Summary List: {common_stock_list}")
# logger.info(f"Dividend Stock Summary List: {dividend_stock_list}")
# #logger.info(f"Mutual Fund Summary List: {mutual_funds_list}")
# logger.info(f"Common Bulk Price Summary: {common_stock_prices}")
# logger.info(f"Dividend Bulk Price Summary: {dividend_stock_prices}")

