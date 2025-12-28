from pydantic import BaseModel
from datetime import datetime


class IncomeBase(BaseModel):
    user_id: int
    source_id: int
    amount: float
    currency: str
    earned_date: datetime


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    income_id: int
    amount: float
    currency: str
    earned_date: datetime


class IncomeResponse(IncomeBase):
    income_id: int

    class Config:
        from_attributes = True
