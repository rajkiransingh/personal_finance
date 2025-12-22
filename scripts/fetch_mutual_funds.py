from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import get_investments_symbols
from utilities.mutual_fund_price_fetcher import (
    MutualFundPriceFetcher as mfF,
    mutualFundFetcher,
)
from utilities.common.app_config import config

logger = config.setup_logger("scripts.fetch_mutual_funds")
db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
mutual_funds_list = all_investment_data["mutual_funds"]

try:
    mf_data = mfF.get_mutual_fund_rates_bulk(mutualFundFetcher, mutual_funds_list)

    if mf_data and mf_data.get("data"):
        mfF.update_mutual_fund_investments(mutualFundFetcher, db, mf_data)
        mfF.update_mutual_fund_summary(mutualFundFetcher, db, mf_data)
    else:
        logger.warning("No valid mutual fund data fetched. Skipping updates.")

except Exception as e:
    logger.error(f"Critical error in fetch_mutual_funds script: {e}", exc_info=True)
