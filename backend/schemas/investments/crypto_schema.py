from typing import Optional

from pydantic import constr

from backend.schemas.investments.common import InvestmentBase


# INPUT SCHEMA - for creating new crypto investments
class CryptoInvestmentCreate(InvestmentBase):
    coin_symbol: constr(max_length=10)  # type: ignore
    crypto_name: constr(max_length=20)  # type: ignore
    initial_price_per_coin: float
    coin_quantity: float
    # Optional fields that might be calculated
    current_price_per_coin: Optional[float] = None


# RESPONSE SCHEMA - for returning crypto investment data
class CryptoInvestmentResponse(InvestmentBase):
    id: int  # Include the ID in response
    coin_symbol: constr(max_length=10)  # type: ignore
    crypto_name: constr(max_length=20)  # type: ignore
    initial_price_per_coin: float
    coin_quantity: float
    current_price_per_coin: Optional[float] = None
