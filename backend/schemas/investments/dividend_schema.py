from pydantic import BaseModel, constr
from datetime import date
from typing import Optional


class DividendBase(BaseModel):
    investor: int
    region_id: Optional[int]
    currency_id: Optional[int]
    stock_symbol: constr(max_length=10)  # type: ignore
    stock_name: Optional[constr(max_length=50)]  # type: ignore
    amount: float
    received_date: date

    class Config:
        from_attributes = True  # Enable ORM mode


class DividendCreate(DividendBase):
    pass


class DividendUpdate(BaseModel):
    id: int
    stock_symbol: constr(max_length=10)  # type: ignore
    amount: float
    received_date: date


class DividendResponse(DividendBase):
    id: int

    class Config:
        from_attributes = True
