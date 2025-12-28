from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

from backend.services.db_services import Base


class Income(Base):
    __tablename__ = "income"
    income_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    source_id = Column(
        Integer, ForeignKey("income_source.income_source_id"), nullable=False
    )
    amount = Column(Float, nullable=False)
    currency = Column(String(255), nullable=False)
    earned_date = Column(DateTime, nullable=False)


class IncomeSource(Base):
    __tablename__ = "income_source"
    income_source_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)


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
