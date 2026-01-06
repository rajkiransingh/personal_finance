from datetime import date
from typing import Optional

from pydantic import BaseModel


class ProtectedInstrumentBase(BaseModel):
    user_id: int
    policy_number: str
    name: str
    provider: Optional[str] = None
    category: str
    frequency: Optional[str] = None
    contribution: float
    start_date: date
    maturity_date: Optional[date] = None
    guaranteed_amount: Optional[float] = None
    notes: Optional[str] = None


class ProtectedInstrumentCreate(ProtectedInstrumentBase):
    pass


class ProtectedInstrumentUpdate(BaseModel):
    policy_number: str = None
    name: Optional[str] = None
    provider: Optional[str] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    contribution: Optional[float] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    guaranteed_amount: Optional[float] = None
    notes: Optional[str] = None


class ProtectedInstrumentResponse(ProtectedInstrumentBase):
    id: int

    class Config:
        from_attributes = True
