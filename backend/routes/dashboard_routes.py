import logging

from fastapi import APIRouter

from backend.models.dashboard import DashboardResponse
from utilities.dashboard.dashboard_calculation_helper import DashboardDataCalculator as ddc, dashboardDataCalculator

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Get all the data related to mera paisa dashboard
@router.get("/", response_model=DashboardResponse)
async def get_dashboard():
    return ddc.get_investment_data(dashboardDataCalculator)
