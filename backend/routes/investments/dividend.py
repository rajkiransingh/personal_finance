from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.investments.dividend_schema import DividendCreate, DividendUpdate, DividendResponse
from backend.services.db_services import get_db
from backend.services.investments.dividend import get_all_dividends, get_dividend_by_user, get_dividend, \
    create_dividend, delete_dividend, update_dividend
from backend.services.user_services import get_user
from backend.summarizing import update_dividend_summary

router = APIRouter(prefix="/dividends", tags=["Income"])


@router.get("/", response_model=List[DividendResponse])
def read_all_dividends(db: Session = Depends(get_db)):
    dividends = get_all_dividends(db)
    return dividends


@router.get("/user/{user_id}", response_model=List[DividendResponse])
def read_dividends_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    dividends = get_dividend_by_user(db, user_id)
    if not dividends:
        raise HTTPException(status_code=404, detail="No dividends found for this user")
    return dividends


@router.get("/{dividend_id}", response_model=DividendResponse)
def read_income(dividend_id: int, db: Session = Depends(get_db)):
    dividend = get_dividend(db, dividend_id)
    if not dividend:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return dividend


@router.post("/", response_model=DividendResponse)
def add_income(dividend_data: DividendCreate, db: Session = Depends(get_db)):
    dividend = create_dividend(db, dividend_data)
    update_dividend_summary.update(db, dividend_data)
    return dividend


@router.put("/{dividend_id}", response_model=DividendResponse)
def modify_income(dividend_id: int, dividend_data: DividendUpdate, db: Session = Depends(get_db)):
    updated_dividend = update_dividend(db, dividend_id, dividend_data)
    if not updated_dividend:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return updated_dividend


@router.delete("/{dividend_id}")
def remove_income(dividend_id: int, db: Session = Depends(get_db)):
    deleted_income = delete_dividend(db, dividend_id)
    if not deleted_income:
        raise HTTPException(status_code=404, detail="Dividend not found")
    return {"message": "Dividend deleted successfully"}
