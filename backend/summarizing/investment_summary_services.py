from sqlalchemy.orm import Session
from backend.models.models import StockSummary, MutualFundSummary, CryptoSummary, RealEstateSummary, BullionSummary

def get_all_stocks_investment_summary(db: Session):
    return db.query(StockSummary).all()

def get_stocks_by_user(db: Session, user_id: int):
    return db.query(StockSummary).filter(StockSummary.investor_id == user_id).all()

def get_all_mutualfunds_investment_summary(db: Session):
    return db.query(MutualFundSummary).all()

def get_mutualfunds_by_user(db: Session, user_id: int):
    return db.query(MutualFundSummary).filter(StockSummary.investor_id == user_id).all()

def get_all_crypto_investment_summary(db: Session):
    return db.query(CryptoSummary).all()

def get_crypto_by_user(db: Session, user_id: int):
    return db.query(CryptoSummary).filter(CryptoSummary.investor_id == user_id).all()

def get_all_realestate_investment_summary(db: Session):
    return db.query(RealEstateSummary).all()

def get_realestate_by_user(db: Session, user_id: int):
    return db.query(RealEstateSummary).filter(RealEstateSummary.investor_id == user_id).all()

def get_all_bullion_investment_summary(db: Session):
    return db.query(BullionSummary).all()

def get_bullion_by_user(db: Session, user_id: int):
    return db.query(BullionSummary).filter(BullionSummary.investor_id == user_id).all()
