from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from backend.services.db_services import Base

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    

class Unit(Base):
    __tablename__ = "units"
    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String(50), nullable=False, unique=True)

class TransactionType(Base):
    __tablename__ = "transaction_types"
    transaction_type_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_name = Column(String(50), nullable=False, unique=True)

class IncomeSource(Base):
    __tablename__ = "income_source"
    income_source_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

class ExpenseCategory(Base):
    __tablename__ = "expense_category"
    expense_category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)

class InvestmentCategory(Base):
    __tablename__ = "investment_category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_type = Column(String(255), nullable=False)

class InvestmentSubCategory(Base):
    __tablename__ = "investment_subcategory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_subcategory_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("investment_category.id"), nullable=False)

class Currencies(Base):
    __tablename__ = "currencies"
    currency_id = Column(Integer, primary_key=True, autoincrement=True)
    currency_name = Column(String(50), nullable=False, unique=True)
    currency_code = Column(String(3), nullable=False, unique=True)

class CurrencyConversion(Base):
    __tablename__ = "currency_conversion"
    conversion_id = Column(Integer, primary_key=True, autoincrement=True)
    from_currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    to_currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    conversion_rate = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class Regions(Base):
    __tablename__ = "regions"
    region_id = Column(Integer, primary_key=True, autoincrement=True)
    region_name = Column(String(255), nullable=False, unique=True)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)

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

class StockSummary(Base):
    __tablename__ = "stock_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    stock_name = Column(String(255), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_or_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class MutualFundSummary(Base):
    __tablename__ = "mutual_fund_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    mutual_fund_name = Column(String(255), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_or_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)
    

class CryptoSummary(Base):
    __tablename__ = "crypto_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    coin_name = Column(String(255), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    total_cost = Column(Integer, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_or_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class Real_Estate_Summary(Base):
    __tablename__ = "real_estate_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    property_name = Column(String(255), nullable=False)
    property_type = Column(String(255), nullable=False)
    property_location = Column(String(255), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    units = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    total_cost = Column(Integer, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_or_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class bullion_summary(Base):
    __tablename__ = "bullion_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    investment_type = Column(String(255), nullable=False)
    total_quantity = Column(Integer, nullable=False)
    units = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    total_cost = Column(Integer, nullable=False)
    average_price_per_unit = Column(Float, nullable=False)
    current_price_per_unit = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    profit_or_loss = Column(Float, nullable=False)
    profit_or_loss_percentage = Column(Float, nullable=False)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)

class Investment(Base):
    __tablename__ = "investment"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_type_id = Column(Integer, ForeignKey("investment_category.id"), nullable=False)
    investment_subcategory_id = Column(Integer, ForeignKey("investment_subcategory.id"), nullable=False)
    investment_name = Column(String(255), nullable=False)
    investment_amount = Column(Float, nullable=False)
    purchased_quantity = Column(Integer, nullable=False)
    unit_id = Column(Integer, ForeignKey("units.unit_id"), nullable=False)
    investor = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    investment_date = Column(DateTime, nullable=False)
    region_id = Column(Integer, ForeignKey("regions.region_id"), nullable=False)
    currency_id = Column(Integer, ForeignKey("currencies.currency_id"), nullable=False)
    initial_value = Column(Float, nullable=False)
    current_value = Column(Float, nullable=False)
    return_on_investment = Column(Float, nullable=False)
    transaction_type = Column(String(10), nullable=False)

class Assets(Base):
    __tablename__ = "assets"
    asset_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(255), nullable=False)

class AssetSubCategory(Base):
    __tablename__ = "asset_sub_category"
    asset_sub_category_id = Column(Integer, primary_key=True, autoincrement=True)
    asset_sub_category_name = Column(String(255), nullable=False)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

class AssetValue(Base):
    __tablename__ = "asset_value"
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)
    value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

class Liabilities(Base):
    __tablename__ = "liabilities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(255), nullable=False)

class LiabilitySubCategory(Base):
    __tablename__ = "liability_subcategory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    liability_id = Column(Integer, ForeignKey("liabilities.id"), nullable=False)

class LiabilityValue(Base):
    __tablename__ = "liability_value"
    id = Column(Integer, primary_key=True, autoincrement=True)
    liability_id = Column(Integer, ForeignKey("liabilities.id"), nullable=False)
    value = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)

class Income(Base):
    __tablename__ = "income"
    income_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    source_id = Column(Integer, ForeignKey("income_source.income_source_id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(255), nullable=False)
    earned_date = Column(DateTime, nullable=False)

class Expense(Base):
    __tablename__ = "expense"
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(Integer, ForeignKey("expense_category.expense_category_id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(255), nullable=False)
    spent_date = Column(DateTime, nullable=False)

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