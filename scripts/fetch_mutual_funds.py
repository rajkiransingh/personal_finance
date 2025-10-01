from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.fetch_overall_investment_data import get_data_from_investments
from utilities.mutual_fund_price_fetcher import MutualFundPriceFetcher as mfF, mutualFundFetcher

db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_data_from_investments(db)
mutual_funds_list = all_investment_data['mutual_funds']

mf_data = mfF.get_mutual_fund_rates_bulk(mutualFundFetcher, mutual_funds_list)
mfF.update_bullion_investments(mutualFundFetcher, db, mf_data)
mfF.update_bullion_summary(mutualFundFetcher, db, mf_data)
