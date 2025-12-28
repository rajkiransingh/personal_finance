from pydantic import BaseModel

from typing import Optional


class DividendSummary(BaseModel):
    investor_id: int
    currency_id: Optional[int]
    region_id: Optional[int]
    stock_symbol: str
    stock_name: Optional[str]
    total_amount: float

    class Config:
        from_attributes = True  # Enable ORM mode


# 1️⃣ Dividend Summary Schema
class DividendSummaryResponse(DividendSummary):
    pass
