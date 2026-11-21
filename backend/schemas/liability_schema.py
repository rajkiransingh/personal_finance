from datetime import date as Date

from pydantic import BaseModel


class LiabilityTypeCreate(BaseModel):
    liability_type: str


class LiabilityTypeResponse(BaseModel):
    liability_id: int
    liability_type: str

    class Config:
        from_attributes = True


class LiabilityValueCreate(BaseModel):
    liability_id: int
    value: float
    currency: str = "INR"
    comment: str = ""
    date: Date


class LiabilityValueUpdate(BaseModel):
    liability_id: int | None = None
    value: float | None = None
    currency: str | None = None
    comment: str | None = None
    date: Date | None = None


class LiabilityValueResponse(BaseModel):
    id: int
    liability_id: int
    value: float
    currency: str
    comment: str
    date: Date
    liability_type: str | None = None
    value_inr: float | None = None

    class Config:
        from_attributes = True
