from pydantic import BaseModel
from datetime import datetime

class InvestmentSummaryBase(BaseModel):
    investor_id: int
    total_quantity: float
    total_cost: float
    average_price_per_unit: float
    current_price_per_unit: float
    current_value: float
    profit_or_loss: float
    profit_loss_percentage: float
    roi: float
    xirr: float
    last_updated: datetime

    class Config:
        from_attributes = True  # Enable ORM mode

# 1️⃣ Mutual Fund Summary Schema
class MutualFundSummaryResponse(InvestmentSummaryBase):
    fund_name: str

# 2️⃣ Stock Summary Schema
class StockSummaryResponse(InvestmentSummaryBase):
    stock_name: str

# 3️⃣ Crypto Summary Schema
class CryptoSummaryResponse(InvestmentSummaryBase):
    coin_name: str

# 4️⃣ Bullion Summary Schema
class BullionSummaryResponse(InvestmentSummaryBase):
    investment_type: int
    units: int

# 5️⃣ Real Estate Summary Schema
class RealEstateSummaryResponse(InvestmentSummaryBase):
    property_name: str
    property_type: int
    property_location: str
    units: int
