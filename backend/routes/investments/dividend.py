from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.investments.dividend_schema import (
    DividendCreate,
    DividendUpdate,
    DividendResponse,
    DividendAnalyticsResponse,
)
from backend.services.auth import get_data_scope
from backend.services.db_services import get_db
from backend.services.scope import require_owner
from backend.services.investments.dividend import (
    get_all_dividends,
    get_dividend_by_user,
    get_dividend,
    create_dividend,
    delete_dividend,
    update_dividend,
)
from backend.services.user_services import get_user
from backend.summarizing import update_dividend_summary
from utilities.common.base_fetcher import BaseFetcher

router = APIRouter(prefix="/dividends", tags=["Income"])
converter = BaseFetcher("dividends.routes", "dividends")
CURRENCY_CODES = {1: "INR", 2: "PLN", 3: "USD"}


@router.get("", response_model=List[DividendResponse])
def read_all_dividends(db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    dividends = get_all_dividends(db, scope)
    return dividends


@router.get("/user/{user_id}", response_model=List[DividendResponse])
def read_dividends_by_user(user_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    require_owner(user_id, scope)
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    dividends = get_dividend_by_user(db, user_id, scope)
    if not dividends:
        raise HTTPException(status_code=404, detail="No dividends found for this user")
    return dividends


@router.get("/analytics", response_model=List[DividendAnalyticsResponse])
def read_dividend_analytics(db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    """All dividend entries with their INR equivalent for the detail screen."""
    rows = get_all_dividends(db, scope)
    result = []
    for row in rows:
        code = CURRENCY_CODES.get(row.currency_id, "INR")
        rate = converter.get_conversion_rate_against_inr(code)
        result.append(
            {
                "id": row.id,
                "stock_symbol": row.stock_symbol,
                "stock_name": row.stock_name,
                "amount": row.amount,
                "currency_code": code,
                "date": row.received_date,
                "value_inr": round(float(row.amount or 0) * rate, 2),
            }
        )
    return result


@router.get("/{dividend_id}", response_model=DividendResponse)
def read_income(dividend_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    dividend = get_dividend(db, dividend_id, scope)
    if not dividend:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return dividend


@router.post("", response_model=DividendResponse)
def add_income(dividend_data: DividendCreate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    dividend_data.investor = scope[0] if scope else dividend_data.investor
    dividend = create_dividend(db, dividend_data)
    update_dividend_summary.update(db, dividend_data)
    return dividend


@router.put("/{dividend_id}", response_model=DividendResponse)
def modify_income(
    dividend_id: int, dividend_data: DividendUpdate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    updated_dividend = update_dividend(db, dividend_id, dividend_data, scope)
    if not updated_dividend:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return updated_dividend


@router.delete("/{dividend_id}")
def remove_income(dividend_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    deleted_income = delete_dividend(db, dividend_id, scope)
    if not deleted_income:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return {"message": "Dividend deleted successfully"}
