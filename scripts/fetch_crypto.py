import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.get_crypto_rates import fetch_cryptocurrency_data
from utilities.update_investments import get_data_from_investments

# Add the app root directory to Python path
sys.path.insert(0, '/app')

db: Session = next(get_db())
# Get all investment data and stock prices upfront
all_investment_data = get_data_from_investments(db)
crypto_coin_list = all_investment_data['crypto']
fetch_cryptocurrency_data(crypto_coin_list)