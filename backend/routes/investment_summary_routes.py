from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.services.user_services import get_user
from backend.summarizing.investment_summary_services import (
    get_all_stocks_investment_summary,
    get_stocks_by_user,
    get_all_mutualfunds_investment_summary,
    get_mutualfunds_by_user,
    get_all_crypto_investment_summary,
    get_crypto_by_user,
    get_all_realestate_investment_summary,
    get_realestate_by_user,
    get_all_bullion_investment_summary,
    get_bullion_by_user,
)

from backend.services.db_services import get_db
from backend.schemas.summaries.investment_summary_schema import (
    StockSummaryResponse,
    MutualFundSummaryResponse,
    CryptoSummaryResponse,
    RealEstateSummaryResponse,
    BullionSummaryResponse,
)

router = APIRouter(prefix="/summary", tags=["Investment"])


@router.get("/stocks", response_model=list[StockSummaryResponse])
def read_stock_summary(db: Session = Depends(get_db)):
    stock_summary = get_all_stocks_investment_summary(db)
    return stock_summary


@router.get("/stocks/user/{user_id}", response_model=list[StockSummaryResponse])
def read_stocks_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    stocks_summary = get_stocks_by_user(db, user_id)
    if not stocks_summary:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return stocks_summary


@router.get("/mutual-funds", response_model=list[MutualFundSummaryResponse])
def read_mutualfund_summary(db: Session = Depends(get_db)):
    mutualfund_summary = get_all_mutualfunds_investment_summary(db)
    return mutualfund_summary


@router.get(
    "/mutualfund/user/{user_id}", response_model=list[MutualFundSummaryResponse]
)
def read_mutualfund_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    mutualfund_summary = get_mutualfunds_by_user(db, user_id)
    if not mutualfund_summary:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return mutualfund_summary


@router.get("/crypto", response_model=list[CryptoSummaryResponse])
def read_crypto_summary(db: Session = Depends(get_db)):
    crypto_summary = get_all_crypto_investment_summary(db)
    return crypto_summary


@router.get("/crypto/user/{user_id}", response_model=list[CryptoSummaryResponse])
def read_crypto_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crypto_summary = get_crypto_by_user(db, user_id)
    if not crypto_summary:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return crypto_summary


@router.get("/real-estate", response_model=list[RealEstateSummaryResponse])
def read_realestate_summary(db: Session = Depends(get_db)):
    realestate_summary = get_all_realestate_investment_summary(db)
    return realestate_summary


@router.get(
    "/realestate/user/{user_id}", response_model=list[RealEstateSummaryResponse]
)
def read_realestate_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    realestate_summary = get_realestate_by_user(db, user_id)
    if not realestate_summary:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return realestate_summary


@router.get("/bullion", response_model=list[BullionSummaryResponse])
def read_bullion_summary(db: Session = Depends(get_db)):
    bullion_summary = get_all_bullion_investment_summary(db)
    return bullion_summary


@router.get("/bullion/user/{user_id}", response_model=list[BullionSummaryResponse])
def read_bullion_summary_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    bullion_summary = get_bullion_by_user(db, user_id)
    if not bullion_summary:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return bullion_summary


@router.get("/portfolio")
def read_portfolio_summary(db: Session = Depends(get_db)):
    """
    Get aggregated portfolio summary by category.
    Returns:
        {
            "stocks": { "total_cost": ..., "current_value": ..., "xirr": ... },
            "mutual_funds": { ... },
            "gold": { ... },
            ...
        }
    """
    from utilities.fetch_overall_investment_data import get_portfolio_summary

    return get_portfolio_summary(db)
