from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

from backend.services.db_services import Base


class Expense(Base):
    __tablename__ = "expense"
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    category_id = Column(
        Integer, ForeignKey("expense_category.expense_category_id"), nullable=False
    )
    amount = Column(Float, nullable=False)
    currency = Column(String(255), nullable=False)
    spent_date = Column(DateTime, nullable=False)


class ExpenseCategory(Base):
    __tablename__ = "expense_category"
    expense_category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)


class Liabilities(Base):
    __tablename__ = "liabilities"
    liability_id = Column(Integer, primary_key=True, autoincrement=True)
    liability_type = Column(String(255), nullable=False)


class LiabilitySubCategory(Base):
    __tablename__ = "liability_subcategory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    liability_id = Column(Integer, ForeignKey("liabilities.liability_id"), nullable=False)


class LiabilityValue(Base):
    __tablename__ = "liability_value"
    id = Column(Integer, primary_key=True, autoincrement=True)
    liability_id = Column(Integer, ForeignKey("liabilities.liability_id"), nullable=False)
    value = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="INR")
    comment = Column(String(255), nullable=False, default="")
    date = Column(DateTime, nullable=False)
