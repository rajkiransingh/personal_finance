import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.metal_rate_fetcher import MetalRateFetcher as mRF, bullionFetcher
from utilities.common.app_config import config

# Add the app root directory to Python path
sys.path.insert(0, "/app")

logger = config.setup_logger("scripts.fetch_metals")
db: Session = next(get_db())

try:
    bullion_data = {
        "Gold": mRF.get_gold_rate(bullionFetcher),
        "Silver": mRF.get_silver_rate(bullionFetcher),
    }

    # Filter out None values to prevent crashes in updaters
    valid_bullion_data = {k: v for k, v in bullion_data.items() if v is not None}

    if valid_bullion_data:
        mRF.update_bullion_investments(bullionFetcher, db, valid_bullion_data)
        mRF.update_bullion_summary(bullionFetcher, db, valid_bullion_data)
    else:
        logger.warning("No valid bullion data fetched. Skipping updates.")

except Exception as e:
    logger.error(f"Critical error in fetch_metals script: {e}", exc_info=True)
