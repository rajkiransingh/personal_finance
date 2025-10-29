import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.cryptocurrency_rate_fetcher import CryptoCurrencyRateFetcher as crF, CryptoFetcher
from utilities.fetch_overall_investment_data import get_investments_symbols

# Add the app root directory to Python path
sys.path.insert(0, '/app')

db: Session = next(get_db())

# Get all investment data and stock prices upfront
all_investment_data = get_investments_symbols(db)
crypto_coin_list = all_investment_data['crypto']

cryData = crF.fetch_cryptocurrency_data_in_usd(CryptoFetcher, crypto_coin_list)
crF.update_crypto_investments(CryptoFetcher, db, cryData)
crF.update_crypto_summary(CryptoFetcher, db, cryData)
