from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from backend.services.db_services import Base


class StockList(Base):
    __tablename__ = "stock_list"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20))
    name = Column(String(255))
    sector = Column(String(50))
    sub_sector = Column(String(50))
    is_active = Column(Boolean)
    last_updated = Column(DateTime)


class StocksValuableData(Base):
    __tablename__ = "stocks_valuable_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), ForeignKey("stock_list.symbol"))
    sector = Column(String(50))
    sub_sector = Column(String(50))
    date = Column(DateTime)
    market_cap = Column(Float)
    close_price = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    peg_ratio = Column(Float)
    roe = Column(Float)
    roce = Column(Float)
    debt_to_equity = Column(Float)
    promoter_holding = Column(Float)
    ebitda_margin = Column(Float)
    ev_ebitda = Column(Float)
    extra_metrics = Column(JSONB)
    updated_flag = Column(Boolean)
    created_at = Column(DateTime)
    last_updated = Column(DateTime)
