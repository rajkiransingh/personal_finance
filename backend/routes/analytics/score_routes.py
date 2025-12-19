import logging

from fastapi import APIRouter

from utilities.analytics.stock_analyzer import get_stock_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["categories"])


# Get all the data related to mera paisa dashboard
@router.get("/score")
async def get_stock_scores():
    return get_stock_score()
