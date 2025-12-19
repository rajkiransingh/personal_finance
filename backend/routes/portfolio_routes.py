from fastapi import APIRouter

from backend.models.portfolio import PortfolioResponse
from utilities.analytics.balancing_screener import (
    BalancingScreener as bS,
    balancingScreener,
)
from utilities.common.app_config import config

logger = config.setup_logger("api.routes.portfolio")
router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# Get all the data related to mera paisa dashboard
@router.get("/", response_model=PortfolioResponse)
async def get_portfolio():
    return bS.run_cycle(balancingScreener)
