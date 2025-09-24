from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean

from backend.services.db_services import Base

class StockInvestment(Base):
    __tablename__ = "stock_investment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    investment_type_id = Column(Integer, ForeignKey("investment_category.id"), nullable=False)
    investment_subcategory_id = Column(Integer, ForeignKey("investment_subcategory.id"), nullable=False)
    transaction_type = Column(String(10), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(50), nullable=False)
    initial_price_per_stock = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    total_invested_amount = Column(Float, nullable=False)
    investment_date = Column(DateTime, nullable=False)
    current_price_per_stock = Column(Float, nullable=False)
    current_total_value = Column(Float, nullable=False)
    total_amount_after_sale = Column(Float, nullable=False)
    return_on_investment = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    dividend_paying = Column(Boolean, nullable=False)

class StockSummary(Base):
    __tablename__ = "stock_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    stock_symbol = Column(String(10), nullable=False)
    stock_name = Column(String(255), nullable=False)
    total_quantity = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
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