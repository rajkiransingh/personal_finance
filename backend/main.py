import logging

from fastapi import FastAPI

from backend.routes import expense_routes, investment_summary_routes, \
    user_routes, income_routes
from backend.routes.investments import stock as stock_route, mutual_fund as mf_route, bullion as bullion_route, \
    real_estate as re_route, crypto as crypto_route, dividend as dividend_route

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

# db: Session = next(get_db())
# # Get all investment data and stock prices upfront
# all_investment_data = get_data_from_investments(db)
#
# # Extracting investment specific data from the DB
# common_stock_list = all_investment_data.get("common_stocks", {})
# dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})
# mutual_funds_list = all_investment_data['mutual_funds']
# crypto_coin_list = all_investment_data['crypto']
#
# # Get All the dividends data
# dividends_data = get_all_dividends(db)
#
# # Get the latest prices and NAVs
# logger.info(f"Common Stock List: {common_stock_list}")
# logger.info(f"Dividend Stock List: {dividend_stock_list}")
# # common_stock_prices = get_stock_prices_in_bulk(common_stock_list)
# dividend_stock_prices = get_stock_prices_in_bulk(dividend_stock_list)
#
# logger.info(f"Mutual Fund list: {mutual_funds_list}")
#
# fetch_cryptocurrency_data(crypto_coin_list)
# get_gold_rate()
# get_silver_rate()
# All_mutual_fund_data = get_mutual_fund_rates_bulk(mutual_funds_list)
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
