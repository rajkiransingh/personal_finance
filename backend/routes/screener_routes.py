import logging

from fastapi import APIRouter
from sqlalchemy.orm import Session

from backend.models.Screener import RedisDataResponse
from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import get_investments_symbols
from utilities.stock_price_fetcher import StockPriceFetcher as sPF, stockFetcher

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/screener", tags=["screener"])


# Get all the data related to stock screening & Discovery
@router.post("/fetch-stock-strategy-data", response_model=RedisDataResponse)
async def get_stock_screening_data():
    response_data = {}
    db: Session = next(get_db())
    # Get all investment data and stock prices upfront
    all_investment_data = get_investments_symbols(db)

    # Extracting investment specific data from the DB
    common_stock_list = all_investment_data.get("common_stocks", {})
    dividend_stock_list = all_investment_data.get("stocks_with_dividends", {})

    common_stock_list.extend(dividend_stock_list)

    for item in ["NIFTYBEES", "SILVERCASE", "MOMENTUM50"]:
        if item in common_stock_list:
            common_stock_list.remove(item)

    # Entire data similar to what is stored in Redis can be fetched using this stored_data variable below
    stock_data = sPF.get_stock_prices_in_bulk(stockFetcher, common_stock_list)
    for stock in stock_data:
        pe = stock['trailingPE']
        pb = stock['priceToBook']
        debtToEquity = stock['debtToEquity']
        promoterHolding = stock['heldPercentInsiders'] * 100
        marketCap = stock['marketCap']

        opm = stock['operatingMargins'] * 100
        npm = stock['profitMargins'] * 100

        eBIT = stock['operatingMargins'] * stock['totalRevenue']

    return RedisDataResponse(stocks=stock_data)
