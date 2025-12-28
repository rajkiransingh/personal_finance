from pydantic import BaseModel
from datetime import datetime


class ExpenseBase(BaseModel):
    user_id: int
    category_id: int
    amount: float
    currency: str
    spent_date: datetime


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = None
    currency: str | None = None
    spent_date: datetime | None = None


class ExpenseResponse(ExpenseBase):
    expense_id: int

    class Config:
        from_attributes = True
