from fastapi import FastAPI
from backend.routes import user_routes
from backend.routes import income_routes
from backend.routes import expense_routes
from backend.routes import investment_routes
from backend.routes import investment_summary_routes
from utilities.get_exchange_rates import get_exchange_rates
from utilities.get_mf_rates import get_mutual_fund_rates
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

app.include_router(user_routes.router)
app.include_router(income_routes.router)
app.include_router(expense_routes.router)
app.include_router(investment_routes.router)
app.include_router(investment_summary_routes.router)

@app.get("/")
def health_check():
    return {"message": "API is running!"}

exchange_rate = get_exchange_rates("PLN","INR")
print(exchange_rate)

mf_rates = get_mutual_fund_rates("122639")
print(mf_rates.get("nav"))
       