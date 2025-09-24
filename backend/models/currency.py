from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime

from backend.services.db_services import Base


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