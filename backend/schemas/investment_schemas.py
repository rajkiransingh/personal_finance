from pydantic import BaseModel, constr
from datetime import date
from typing import Optional

class InvestmentBase(BaseModel):
    investment_type_id: int
    investment_subcategory_id: Optional[int] = None
    investment_name: constr(max_length=50)
    investment_amount: float
    purchased_quantity: float
    unit_id: int
    investor: int
    investment_date: Optional[date] = None
    currency_id: Optional[int] = None
    transaction_type: constr(max_length=10)

class InvestmentCreate(InvestmentBase):
    pass

class InvestmentUpdate(BaseModel):
    id: Optional[int] = None
    investment_type_id: Optional[int] = None
    investment_subcategory_id: Optional[int] = None
    investment_name: Optional[constr(max_length=50)] = None
    investment_amount: Optional[float] = None
    purchased_quantity: Optional[float] = None
    unit_id: Optional[int] = None
    investor: Optional[int] = None
    initial_value: Optional[float] = None
    investment_date: Optional[date] = None
    currency_id: Optional[int] = None
    transaction_type: constr(max_length=10)

    class Config:
        orm_mode = True

class InvestmentResponse(InvestmentBase):
    id: int

    class Config:
        from_attributes = True