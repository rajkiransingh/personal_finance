from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Numeric

from backend.services.db_services import Base


class MutualFundInvestment(Base):
    __tablename__ = "mutual_fund_investment"
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
    scheme_code = Column(String(20), nullable=False)
    fund_name = Column(String(50), nullable=False)
    initial_price_per_unit = Column(Numeric(20, 8), nullable=False)
    unit_quantity = Column(Numeric(20, 8), nullable=False)
    total_invested_amount = Column(Numeric(20, 8), nullable=False)
    investment_date = Column(DateTime, nullable=False)
    current_price_per_unit = Column(Numeric(20, 8), nullable=True)
    current_total_value = Column(Numeric(20, 8), nullable=True)
    total_amount_after_sale = Column(Numeric(20, 8), nullable=True)
    return_on_investment = Column(Numeric(20, 8), nullable=True)
    XIRR = Column(Numeric(20, 8), nullable=True)


class MutualFundSummary(Base):
    __tablename__ = "mutual_fund_summary"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investor_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    scheme_code = Column(String(10), nullable=False)
    fund_name = Column(String(255), nullable=False)
    total_quantity = Column(Numeric(20, 8), nullable=False)
    total_cost = Column(Numeric(20, 8), nullable=False)
    average_price_per_unit = Column(Numeric(20, 8), nullable=False)
    current_price_per_unit = Column(Numeric(20, 8), nullable=True)
    current_value = Column(Numeric(20, 8), nullable=True)
    profit_or_loss = Column(Numeric(20, 8), nullable=True)
    profit_loss_percentage = Column(Numeric(20, 8), nullable=True)
    roi = Column(Float, nullable=False)
    xirr = Column(Float, nullable=False)
    last_updated = Column(DateTime, nullable=False)
