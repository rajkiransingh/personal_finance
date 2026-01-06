from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date

from backend.services.db_services import Base


class ProtectedInstrument(Base):
    __tablename__ = "protected_instruments"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    name = Column(String(255), nullable=False)  # LIC, Sukanya, Insurance
    provider = Column(String(255), nullable=True)  # LIC, SBI, HDFC
    category = Column(String(255), nullable=False)  # insurance | savings | pension

    frequency = Column(String(50), nullable=True)  # Yearly, Half Yearly, Monthly
    contribution = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    maturity_date = Column(Date, nullable=True)

    guaranteed_amount = Column(Float, nullable=True)
    notes = Column(String(255), nullable=True)
