from typing import List, Optional

from pydantic import BaseModel


class IncomeYTD(BaseModel):
    income: float
    income_last_year_to_date: float
    average_income: float
    active_months: int
    last_month: Optional[str]
    change: float


class ExpenseYTD(BaseModel):
    expense: float
    expense_last_year_to_date: float
    average_expense: float
    active_months: int
    last_month: Optional[str]
    change: float
    expense_ratio: float


class InvestmentYTD(BaseModel):
    investment: float
    investment_last_year_to_date: float
    average_investment: float
    active_months: int
    last_month: Optional[str]
    active_sip_count: int
    change: float
    investment_ratio: float


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


class Spending(BaseModel):
    category: str
    amount: float


class DividendYear(BaseModel):
    year: str
    amount: float


class DividendStock(BaseModel):
    name: str
    amount: float


class CashFlowForecast(BaseModel):
    inflow: float
    outflow: float
    net_savings: float


class LiabilityEntry(BaseModel):
    name: str
    value: float


class InvestmentBreakdown(BaseModel):
    name: str
    total_cost: float
    current_value: float
    gain: float
    xirr: float


class DashboardResponse(BaseModel):
    cash_balance: float
    emergency_coverage: float
    emergency_fund_required: float
    emergency_monthly_average: float
    total_invested_cost: float
    income_ytd: IncomeYTD
    expense_avg: ExpenseYTD
    investment_avg: InvestmentYTD
    total_returns: float
    total_return_pct: float
    invested_current_value: float
    investment_breakdown: List[InvestmentBreakdown]
    average_roi: float
    savings_ytd: float
    savings_rate: float
    forecast: CashFlowForecast
    assets: Assets
    total_assets: float
    total_liabilities: float
    liability_breakdown: List[LiabilityEntry]
    net_worth: float
    spending_categories: List[Spending]
    dividend_yearly: List[DividendYear]
    dividend_top_stocks: List[DividendStock]
    investment_returns: InvestmentReturns
