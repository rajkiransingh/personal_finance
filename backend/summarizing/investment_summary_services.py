from sqlalchemy.orm import Session

from backend.models.investments.bullion import BullionSummary
from backend.models.investments.crypto import CryptoSummary
from backend.models.investments.mutual_fund import MutualFundSummary
from backend.models.investments.real_estate import RealEstateSummary
from backend.models.investments.stock import StockSummary
from backend.services.scope import apply_scope, require_owner


def _all(db, model, scope):
    return apply_scope(db.query(model), model, scope).all()


def _by_user(db, model, user_id, scope):
    require_owner(user_id, scope)
    return apply_scope(db.query(model), model, scope).filter(
        model.investor_id == user_id
    ).all()


def get_all_stocks_investment_summary(db: Session, scope=None):
    return _all(db, StockSummary, scope)


def get_stocks_by_user(db: Session, user_id: int, scope=None):
    return _by_user(db, StockSummary, user_id, scope)


def get_all_mutualfunds_investment_summary(db: Session, scope=None):
    return _all(db, MutualFundSummary, scope)


def get_mutualfunds_by_user(db: Session, user_id: int, scope=None):
    return _by_user(db, MutualFundSummary, user_id, scope)


def get_all_crypto_investment_summary(db: Session, scope=None):
    return _all(db, CryptoSummary, scope)


def get_crypto_by_user(db: Session, user_id: int, scope=None):
    return _by_user(db, CryptoSummary, user_id, scope)


def get_all_realestate_investment_summary(db: Session, scope=None):
    return _all(db, RealEstateSummary, scope)


def get_realestate_by_user(db: Session, user_id: int, scope=None):
    return _by_user(db, RealEstateSummary, user_id, scope)


def get_all_bullion_investment_summary(db: Session, scope=None):
    return _all(db, BullionSummary, scope)


def get_bullion_by_user(db: Session, user_id: int, scope=None):
    return _by_user(db, BullionSummary, user_id, scope)
