from fastapi import APIRouter, Depends

from backend.models.dashboard import DashboardResponse
from backend.services.auth import get_data_scope
from utilities.dashboard.dashboard_calculation_helper import (
    DashboardDataCalculator as ddc,
    dashboardDataCalculator,
)
from utilities.common.app_config import config

logger = config.setup_logger("api.routes.dashboard")
router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Get all the data related to mera paisa dashboard
@router.get("", response_model=DashboardResponse)
async def get_dashboard(scope: list[int] = Depends(get_data_scope)):
    return ddc.get_investment_data(dashboardDataCalculator, scope=scope)
