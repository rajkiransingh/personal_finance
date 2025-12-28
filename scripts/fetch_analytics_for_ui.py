import sys

from sqlalchemy.orm import Session

from backend.services.db_services import get_db
from utilities.analytics.balancing_screener import BalancingScreener as bS, balancingScreener
from utilities.analytics.stock_analyzer import get_stock_score
from utilities.analytics.stock_merger import StockMerger as sM, stockMerger
from utilities.common.app_config import config
from utilities.dashboard.dashboard_calculation_helper import DashboardDataCalculator as dDC, dashboardDataCalculator

sys.path.insert(0, "/app")

logger = config.setup_logger("scripts.fetch_analytics_for_ui")
db: Session = next(get_db())

try:
    # Get Dashboard data
    test_dashboard = dDC.get_investment_data(
        dashboardDataCalculator
    )

    bS.run_cycle(balancingScreener)

    sM.merge_stock_lists(stockMerger)
    sM.merge_with_ticker_data(stockMerger, db)
    get_stock_score()

except Exception as e:
    logger.error(f"Critical error in fetch analytics for UI script: {e}", exc_info=True)
