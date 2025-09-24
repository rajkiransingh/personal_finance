from typing import Optional

from pydantic import constr

from backend.schemas.investments.common import InvestmentBase


# INPUT SCHEMA - for creating new mutual fund investments
class MutualFundInvestmentCreate(InvestmentBase):
    scheme_code: constr(max_length=20)  # type: ignore
    fund_name: constr(max_length=50)  # type: ignore
    initial_price_per_unit: float
    unit_quantity: float
    # Optional fields that might be calculated
    current_price_per_unit: Optional[float] = None


# RESPONSE SCHEMA - for returning mutual fund investment data
class MutualFundInvestmentResponse(InvestmentBase):
    id: int  # Include the ID in response
    scheme_code: constr(max_length=20)  # type: ignore
    fund_name: constr(max_length=50)  # type: ignore
    initial_price_per_unit: float
    unit_quantity: float
    current_price_per_unit: Optional[float] = None
