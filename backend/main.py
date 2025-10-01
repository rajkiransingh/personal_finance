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
