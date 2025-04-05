from fastapi import FastAPI
from backend.routes import user_routes
from backend.routes import income_routes
from backend.routes import expense_routes
from backend.routes import stock_investment_routes, mutual_fund_investment_routes, bullion_investment_routes, real_estate_investment_routes, crypto_investment_routes
from backend.routes import investment_summary_routes
from utilities.get_exchange_rates import get_exchange_rates
from utilities.get_mf_rates import get_mutual_fund_rates
from utilities.get_current_metal_rates import get_current_metal_rates
from utilities.get_stock_prices import get_stock_prices
import logging


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

@app.get("/")
def health_check():
    return {"message": "API is running!"}

exchange_rate = get_exchange_rates("PLN","INR")
print(exchange_rate)

mf_rates = get_mutual_fund_rates("122639")
print(mf_rates.get("nav"))

gold_rate = get_current_metal_rates("Gold")
print(f'This is the gold rate of the day: {gold_rate}')

silver_rate = get_current_metal_rates("Silver")
print(f'This is the silver rate of the day: {silver_rate}')

all_stock_data = get_stock_prices({"HDFCBANK"})
for stock, data in all_stock_data.items():
    print(data['currentPrice'])




