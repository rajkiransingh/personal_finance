from typing import Dict

from pydantic import BaseModel


# Define Pydantic models for type safety and validation
class Assets(BaseModel):
    Cash: float
    Stocks: float
    Mutual_Fund: float
    Gold: float
    Silver: float
    Land: float
    Crypto: float

    class Config:
        json_schema_extra = {}


class InvestmentReturns(BaseModel):
    Stocks: float
    Mutual_Fund: float
    Gold: float
    Silver: float
    Land: float
    Crypto: float

    class Config:
        json_schema_extra = {}


class DashboardResponse(BaseModel):
    emergency_coverage: float
    total_returns: float
    average_roi: float
    assets: Assets
    investment_returns: InvestmentReturns
    spending: Dict
