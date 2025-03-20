from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.services.db_services import get_db
from backend.services.user_services import get_user
from backend.services.income_services import get_all_incomes, get_income, get_income_by_user, create_income, update_income, delete_income
from backend.schemas.income_schemas import IncomeCreate, IncomeUpdate, IncomeResponse
from typing import List

router = APIRouter(prefix="/income", tags=["Income"])

@router.get("/", response_model=List[IncomeResponse])
def read_all_incomes(db: Session = Depends(get_db)):
    incomes = get_all_incomes(db)
    return incomes

@router.get("/user/{user_id}", response_model=List[IncomeResponse])
def read_incomes_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = get_income_by_user(db, user_id)
    if not incomes:
        raise HTTPException(status_code=404, detail="No incomes found for this user")
    return incomes

@router.get("/{income_id}", response_model=IncomeResponse)
def read_income(income_id: int, db: Session = Depends(get_db)):
    income = get_income(db, income_id)
    if not income:
        raise HTTPException(status_code=404, detail="Income not found")
    return income

@router.post("/", response_model=IncomeResponse)
def add_income(income_data: IncomeCreate, db: Session = Depends(get_db)):
    return create_income(db, income_data)

@router.put("/{income_id}", response_model=IncomeResponse)
def modify_income(income_id: int, income_data: IncomeUpdate, db: Session = Depends(get_db)):
    updated_income = update_income(db, income_id, income_data)
    if not updated_income:
        raise HTTPException(status_code=404, detail="Income not found")
    return updated_income

@router.delete("/{income_id}")
def remove_income(income_id: int, db: Session = Depends(get_db)):
    deleted_income = delete_income(db, income_id)
    if not deleted_income:
        raise HTTPException(status_code=404, detail="Income not found")
    return {"message": "Income deleted successfully"}
