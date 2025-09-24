from typing import Optional

from pydantic import constr

from backend.schemas.investments.common import InvestmentBase


# INPUT SCHEMA - for creating new bullion investments
class BullionInvestmentCreate(InvestmentBase):
    metal_name: constr(max_length=10)  # type: ignore
    initial_price_per_gram: float
    quantity_in_grams: float
    # Optional fields that might be calculated
    current_price_per_gram: Optional[float] = None


# RESPONSE SCHEMA - for returning bullion investment data
class BullionInvestmentResponse(InvestmentBase):
    id: int  # Include the ID in response
    metal_name: constr(max_length=10)  # type: ignore
    initial_price_per_gram: float
    quantity_in_grams: float
    current_price_per_gram: Optional[float] = None
