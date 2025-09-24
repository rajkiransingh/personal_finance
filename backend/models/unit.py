from sqlalchemy import Column, Integer, String
from backend.services.db_services import Base

class Unit(Base):
    __tablename__ = "units"
    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String(50), nullable=False, unique=True)