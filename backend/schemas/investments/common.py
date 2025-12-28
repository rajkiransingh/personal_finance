from pydantic import BaseModel, constr
from datetime import date
from typing import Optional


# Base Model for Investment is defined here
class InvestmentBase(BaseModel):
    investor: int
    currency_id: Optional[int] = None
    region_id: Optional[int] = None
    investment_type_id: int
    investment_subcategory_id: Optional[int] = None
    transaction_type: constr(max_length=10)  # type: ignore
    total_invested_amount: float
    investment_date: Optional[date] = None
    current_total_value: Optional[float] = None
    total_amount_after_sale: Optional[float] = None
    return_on_investment: Optional[float] = None
    xirr: Optional[float] = None

    class Config:
        from_attributes = True  # Enable ORM mode


## Update Investment Models are defined below
class InvestmentUpdate(BaseModel):
    id: Optional[int] = None
    investor: Optional[int] = None
    currency_id: Optional[int] = None
    region_id: Optional[int] = None
    investment_type_id: Optional[int] = None
    investment_subcategory_id: Optional[int] = None
    transaction_type: Optional[constr(max_length=10)] = None  # type: ignore
    investment_name: Optional[constr(max_length=50)] = None  # type: ignore
    total_invested_amount: Optional[float] = None
    investment_date: Optional[date] = None
    current_total_value: Optional[float] = None
    total_amount_after_sale: Optional[float] = None
    return_on_investment: Optional[float] = None
    xirr: Optional[float] = None
    stock_symbol: Optional[constr(max_length=10)] = None  # type: ignore
    stock_name: Optional[constr(max_length=50)] = None  # type: ignore
    initial_price_per_stock: Optional[float] = None
    stock_quantity: Optional[float] = None
    current_price_per_stock: Optional[float] = None
    dividend_paying: Optional[bool] = None
    scheme_code: Optional[constr(max_length=20)] = None  # type: ignore
    mutual_fund_name: Optional[constr(max_length=50)] = None  # type: ignore
    initial_price_per_unit: Optional[float] = None
    unit_quantity: Optional[float] = None
    current_price_per_unit: Optional[float] = None
    metal_name: Optional[constr(max_length=10)] = None  # type: ignore
    initial_price_per_gram: Optional[float] = None
    quantity_in_grams: Optional[float] = None
    current_price_per_gram: Optional[float] = None
    property_name: Optional[constr(max_length=50)] = None  # type: ignore
    property_type: Optional[constr(max_length=20)] = None  # type: ignore
    property_location: Optional[constr(max_length=50)] = None  # type: ignore
    area_in_sqyds: Optional[float] = None
    initial_price_per_sqyds: Optional[float] = None
    current_price_per_sqyds: Optional[float] = None
    coin_symbol: Optional[constr(max_length=10)] = None  # type: ignore
    coin_name: Optional[constr(max_length=20)] = None  # type: ignore
    initial_price_per_coin: Optional[float] = None
    coin_quantity: Optional[float] = None
    current_price_per_coin: Optional[float] = None

    class Config:
        orm_mode = True
