from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
    Boolean,
    Numeric,
)

from backend.services.db_services import Base


class StockInvestment(Base):
    __tablename__ = "stock_investment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    investment_type_id = Column(
        Integer, ForeignKey("investment_category.id"), nullable=False
    )
    investment_subcategory_id = Column(
        Integer, ForeignKey("investment_subcategory.id"), nullable=False
    )
    transaction_type = Column(String(10), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    initial_price_per_stock = Column(Numeric(20, 8), nullable=False)
    stock_quantity = Column(Numeric(20, 8), nullable=False)
    total_invested_amount = Column(Numeric(20, 8), nullable=False)
    investment_date = Column(DateTime, nullable=False)
    current_price_per_stock = Column(Numeric(20, 8), nullable=True)
    current_total_value = Column(Numeric(20, 8), nullable=True)
    total_amount_after_sale = Column(Numeric(20, 8), nullable=True)
    return_on_investment = Column(Numeric(20, 8), nullable=True)
    xirr = Column(Numeric(20, 8), nullable=True)
    dividend_paying = Column(Boolean, nullable=False)


class StockSummary(Base):
    __tablename__ = "stock_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(255), nullable=False)
    total_quantity = Column(Numeric(20, 8), nullable=False)
    total_cost = Column(Numeric(20, 8), nullable=False)
    average_price_per_unit = Column(Numeric(20, 8), nullable=False)
    current_price_per_unit = Column(Numeric(20, 8), nullable=True)
    current_value = Column(Numeric(20, 8), nullable=True)
    profit_or_loss = Column(Numeric(20, 8), nullable=True)
    profit_loss_percentage = Column(Numeric(20, 8), nullable=True)
    roi = Column(Numeric(20, 8), nullable=True)
    xirr = Column(Numeric(20, 8), nullable=True)
    last_updated = Column(DateTime, nullable=False)
    dividend_paying = Column(Boolean, nullable=False)


class Dividends(Base):
    __tablename__ = "dividends"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    received_date = Column(DateTime, nullable=False)


class DividendSummary(Base):
    __tablename__ = "dividend_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    total_amount = Column(Float, nullable=False)
