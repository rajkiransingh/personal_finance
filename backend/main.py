import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.raiden_integration import raiden_client
from backend.routes import dashboard_routes, portfolio_routes
from backend.routes import (
    expense_routes,
    investment_summary_routes,
    user_routes,
    income_routes,
)
from backend.routes import transaction_import_routes, protected_instrument_routes
from backend.routes.analytics import score_routes
from backend.routes.categories import category_routes
from backend.routes.configurations import config_routes
from backend.routes.investments import (
    stock as stock_route,
    mutual_fund as mf_route,
    bullion as bullion_route,
    real_estate as re_route,
    crypto as crypto_route,
    dividend as dividend_route,
)
from backend.services.db_services import get_db
from scripts.fetch_mutual_funds import mutual_funds_list
from scripts.fetch_stocks import (
    common_stock_prices,
    dividend_stock_prices,
    dividends_data,
    dividend_stock_list,
)
from utilities.analytics.balancing_screener import BalancingScreener, balancingScreener
from utilities.analytics.stock_analyzer import get_stock_score
from utilities.analytics.stock_merger import StockMerger as sM, stockMerger
from utilities.common.app_config import config
from utilities.dashboard.dashboard_calculation_helper import DashboardDataCalculator
from utilities.dashboard.dashboard_calculation_helper import dashboardDataCalculator
from utilities.fetch_overall_investment_data import (
    get_investments_symbols,
)
from utilities.forex_exchange_rate_fetcher import (
    ForexExchangeRateFetcher as fF,
    forexFetcher,
)
from utilities.metal_rate_fetcher import MetalRateFetcher as mRF, bullionFetcher
from utilities.mutual_fund_price_fetcher import (
    MutualFundPriceFetcher as mfF,
    mutualFundFetcher,
)
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher

# Set up centralized logger for main application
logger = config.setup_logger("api.main")


def safe_float(value, default=0.0):
    """
    Safely convert a value to float.
    Returns default if conversion fails or value is None/'N/A'.
    """
    try:
        if value in [None, "N/A", "NaN", "-", "", "nan"]:
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def startup_logic():
    logger.info("=" * 60)
    logger.info("Starting application logic...")
    raiden_client.send_event(
        "scheduler_started", {"message": "Financer startup logic beginning"}
    )
    logger.info("=" * 60)
    try:
        db: Session = next(get_db())

        # Fetch exchange rates
        fF.get_exchange_rates(forexFetcher, "USD", "INR")
        fF.get_exchange_rates(forexFetcher, "PLN", "INR")
        fF.get_exchange_rates(forexFetcher, "USD", "PLN")

        # Get all investment data and stock prices upfront
        all_investment_data = get_investments_symbols(db)

        # Extracting investment specific data from the DB
        common_stock_list = all_investment_data.get("common_stocks", {})
        sPF.update_stock_summary(stockFetcher, db, common_stock_prices)
        sPF.update_stock_summary(
            stockFetcher, db, dividend_stock_prices, dividends_data
        )

        logger.info(f"Mutual Fund list: {mutual_funds_list}")
        mf_data = mfF.get_mutual_fund_rates_bulk(mutualFundFetcher, mutual_funds_list)
        mfF.update_mutual_fund_investments(mutualFundFetcher, db, mf_data)
        mfF.update_mutual_fund_summary(mutualFundFetcher, db, mf_data)

        bullion_data = {
            "Gold": mRF.get_gold_rate(bullionFetcher),
            "Silver": mRF.get_silver_rate(bullionFetcher),
        }
        mRF.update_bullion_investments(bullionFetcher, db, bullion_data)
        mRF.update_bullion_summary(bullionFetcher, db, bullion_data)
        DashboardDataCalculator.get_investment_data(dashboardDataCalculator)
        out = BalancingScreener.run_cycle(balancingScreener)
        logger.info("Portfolio Rebalancing Plan:")
        logger.info(json.dumps(out, indent=2))

        common_stock_list.extend(dividend_stock_list)

        sM.merge_stock_lists(stockMerger)
        sM.merge_with_ticker_data(stockMerger, db)
        get_stock_score()

        raiden_client.send_event("scheduler_completed", {"status": "success"})

    except Exception as e:
        raiden_client.send_event("scheduler_failed", {"error": str(e)})
        logger.error(f"Error executing startup logic: {e}", exc_info=True)
        # We catch exceptions to prevent app startup failure if logic is buggy

    logger.info("=" * 60)
    logger.info("Startup logic completed successfully")
    logger.info("=" * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Register with Raiden and start heartbeat
    raiden_client.register()
    raiden_client.start_heartbeat()

    startup_logic()
    yield
    raiden_client.stop_heartbeat()
    logger.info("Shutting down application...")


app = FastAPI(lifespan=lifespan)

api_router = APIRouter(prefix="/api")
api_router.include_router(user_routes.router)
api_router.include_router(income_routes.router)
api_router.include_router(expense_routes.router)
api_router.include_router(stock_route.router)
api_router.include_router(mf_route.router)
api_router.include_router(bullion_route.router)
api_router.include_router(re_route.router)
api_router.include_router(crypto_route.router)
api_router.include_router(investment_summary_routes.router)
api_router.include_router(dividend_route.router)
api_router.include_router(dashboard_routes.router)
api_router.include_router(portfolio_routes.router)
api_router.include_router(config_routes.router)
api_router.include_router(category_routes.router)
api_router.include_router(score_routes.router)
api_router.include_router(transaction_import_routes.router)
api_router.include_router(protected_instrument_routes.router)

app.include_router(api_router)

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
