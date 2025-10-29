import logging

from fastapi import APIRouter

from backend.models.Portfolio import PortfolioResponse
from utilities.analytics.balancing_screener import BalancingScreener as bS, balancingScreener

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio", tags=["portfolio"])


# Get all the data related to mera paisa dashboard
@router.get("/", response_model=PortfolioResponse)
async def get_portfolio():
    return bS.run_cycle(balancingScreener)
