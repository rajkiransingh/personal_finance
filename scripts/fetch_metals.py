import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.metal_rate_fetcher import MetalRateFetcher as mRF, bullionFetcher

# Add the app root directory to Python path
sys.path.insert(0, '/app')

db: Session = next(get_db())

grate = mRF.get_gold_rate(bullionFetcher)
srate = mRF.get_silver_rate(bullionFetcher)

mRF.update_bullion_investments(bullionFetcher, db, "Gold", grate)
mRF.update_bullion_investments(bullionFetcher, db, "Silver", srate)
