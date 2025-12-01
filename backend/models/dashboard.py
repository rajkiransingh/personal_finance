from typing import List

from pydantic import BaseModel


class IncomeYTD(BaseModel):
    income: float
    income_last_year_to_date: float
    change: float


class ExpenseYTD(BaseModel):
    expense: float
    expense_last_year_to_date: float
    average_expense: float
    change: float
    expense_ratio: float


class InvestmentYTD(BaseModel):
    investment: float
    investment_last_year_to_date: float
    average_investment: float
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


class DashboardResponse(BaseModel):
    cash_balance: float
    emergency_coverage: float
    income_ytd: IncomeYTD
    expense_avg: ExpenseYTD
    investment_avg: InvestmentYTD
    total_returns: float
    average_roi: float
    savings_ytd: float
    savings_rate: float
    assets: Assets
    net_worth: float
    spending_categories: List[Spending]
    investment_returns: InvestmentReturns
