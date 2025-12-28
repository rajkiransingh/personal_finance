from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from backend.services.db_services import Base


class MonthlyFinancialData(Base):
    __tablename__ = "monthly_financial_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    total_income = Column(Float, nullable=False)
    total_expenditure = Column(Float, nullable=False)
    investment_type = Column(Float, nullable=False)
    investment_amount = Column(Float, nullable=False)
    net_worth = Column(Float, nullable=False)


class StockTransactions(Base):
    __tablename__ = "stock_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    stock_name = Column(String(255), nullable=False)
    transaction_type_id = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)


class MutualFundTransactions(Base):
    __tablename__ = "mutual_fund_transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    mutual_fund_name = Column(String(255), nullable=False)
    transaction_type_id = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Float, nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
