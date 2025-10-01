import logging
import os
import sys

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionSummary
from backend.models.investments.crypto import CryptoSummary
from backend.models.investments.mutual_fund import MutualFundSummary
from backend.models.investments.stock import StockSummary, DividendSummary

# Create logs directory if it doesn't exist
log_dir = "./logs"
os.makedirs(log_dir, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("./logs/Investment_updater_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("investment_updater")


def get_data_from_investments(db: Session):
    return {
        "common_stocks": [s.stock_symbol for s in db.query(StockSummary).filter(or_(StockSummary.dividend_paying == 0,
                                                                                    StockSummary.dividend_paying is None)).all()],
        "stocks_with_dividends": [s.stock_symbol for s in
                                  db.query(StockSummary).filter(StockSummary.dividend_paying == 1).all()],
        "mutual_funds": [m.scheme_code for m in db.query(MutualFundSummary).all()],
        "crypto": [c.coin_symbol for c in db.query(CryptoSummary).all()],
        "bullion": list({b.metal_name for b in db.query(BullionSummary).all()})
    }


def get_dividends_data(db: Session):
    results = db.query(DividendSummary.stock_symbol, DividendSummary.total_amount).all()
    return {symbol: price for symbol, price in results}
