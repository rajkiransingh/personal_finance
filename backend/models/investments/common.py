from sqlalchemy import Column, Integer, String, ForeignKey

from backend.services.db_services import Base


class InvestmentCategory(Base):
    __tablename__ = "investment_category"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_type = Column(String(255), nullable=False)


class InvestmentSubCategory(Base):
    __tablename__ = "investment_subcategory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_subcategory_name = Column(String(255), nullable=False)
    category_id = Column(Integer, ForeignKey("investment_category.id"), nullable=False)


class TransactionType(Base):
    __tablename__ = "transaction_types"
    transaction_type_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_name = Column(String(50), nullable=False, unique=True)
