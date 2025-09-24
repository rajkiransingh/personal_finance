from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InvestmentSummaryBase(BaseModel):
    investor_id: int
    total_quantity: float
    total_cost: float
    average_price_per_unit: float
    current_price_per_unit: Optional[float] = None # type: ignore
    current_value: Optional[float] = None # type: ignore
    profit_or_loss: Optional[float] = None # type: ignore
    profit_loss_percentage: Optional[float] = None # type: ignore
    roi: Optional[float] = None # type: ignore
    xirr: Optional[float] = None # type: ignore
    last_updated: datetime
    dividend_paying: bool = False

    class Config:
        from_attributes = True  # Enable ORM mode

# 1️⃣ Mutual Fund Summary Schema
class MutualFundSummaryResponse(InvestmentSummaryBase):
    scheme_code: str
    fund_name: str

# 2️⃣ Stock Summary Schema
class StockSummaryResponse(InvestmentSummaryBase):
    stock_symbol: str
    stock_name: str

# 3️⃣ Crypto Summary Schema
class CryptoSummaryResponse(InvestmentSummaryBase):
    coin_symbol: str
    crypto_name: str

# 4️⃣ Bullion Summary Schema
class BullionSummaryResponse(InvestmentSummaryBase):
    investment_type: int
    metal_name: str

# 5️⃣ Real Estate Summary Schema
class RealEstateSummaryResponse(InvestmentSummaryBase):
    property_name: str
    property_type: int
    property_location: str
