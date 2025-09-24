from typing import Optional

from pydantic import constr

from backend.schemas.investments.common import InvestmentBase


# INPUT SCHEMA - for creating new real estate investments
class RealEstateInvestmentCreate(InvestmentBase):
    property_name: constr(max_length=50)  # type: ignore
    property_type: constr(max_length=20)  # type: ignore
    property_location: constr(max_length=50)  # type: ignore
    area_in_sqyds: float
    initial_price_per_sqyds: float
    # Optional fields that might be calculated
    current_price_per_sqyds: Optional[float] = None


# RESPONSE SCHEMA - for returning real estate investment data
class RealEstateInvestmentResponse(InvestmentBase):
    id: int  # Include the ID in response
    property_name: constr(max_length=50)  # type: ignore
    property_type: constr(max_length=20)  # type: ignore
    property_location: constr(max_length=50)  # type: ignore
    area_in_sqyds: float
    initial_price_per_sqyds: float
    # Optional fields that might be calculated
    current_price_per_sqyds: Optional[float] = None
