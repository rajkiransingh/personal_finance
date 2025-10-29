from typing import Dict

from pydantic import BaseModel


class SubAllocation(BaseModel):
    current_value: float
    ideal_value: float
    gap: float
    target_pct_of_total: float


class Category(BaseModel):
    current_value: float
    ideal_value: float
    gap: float
    current_pct: float
    target_pct: float
    status: str
    sub_allocations: Dict[str, SubAllocation]


class Summary(BaseModel):
    positive_gap_total: float
    negative_gap_total: float
    inflow_sufficient: bool


class RebalancePlan(BaseModel):
    ETFs: float
    MutualFunds: float
    Stocks: float
    Metals: float
    RealEstate: float
    Crypto: float


class PortfolioUpdate(BaseModel):
    total_value: float
    categories: Dict[str, Category]
    summary: Summary
    next_monthly_sip: float
    rebalance_plan: RebalancePlan


class PortfolioResponse(BaseModel):
    total_value: float
    categories: Dict[str, Category]
    summary: Summary
    next_monthly_sip: float
    rebalance_plan: RebalancePlan
