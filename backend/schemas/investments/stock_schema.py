from typing import Optional

from pydantic import constr

from backend.schemas.investments.common import InvestmentBase


# INPUT SCHEMA - for creating new stock investments
class StockInvestmentCreate(InvestmentBase):
    stock_symbol: constr(max_length=10)  # type: ignore
    stock_name: Optional[constr(max_length=50)] = None  # type: ignore
    initial_price_per_stock: float
    stock_quantity: float
    # Optional fields that might be calculated
    current_price_per_stock: Optional[float] = None
    dividend_paying: bool = False


# RESPONSE SCHEMA - for returning stock investment data
class StockInvestmentResponse(InvestmentBase):
    id: int  # Include the ID in response
    stock_symbol: constr(max_length=10)  # type: ignore
    stock_name: Optional[constr(max_length=50)] = None  # type: ignore
    initial_price_per_stock: float
    stock_quantity: float
    current_price_per_stock: Optional[float] = None
    dividend_paying: bool = False
