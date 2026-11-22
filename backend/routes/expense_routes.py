from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.expense_schema import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from backend.services.auth import get_data_scope
from backend.services.db_services import get_db
from backend.services.scope import require_owner
from backend.services.expense_services import (
    get_all_expenses,
    get_expenses_by_user,
    get_expense,
    create_expense,
    update_expense,
    delete_expense,
)
from backend.services.user_services import get_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", response_model=List[ExpenseResponse])
def read_all_expenses(db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    expenses = get_all_expenses(db, scope)
    return expenses


@router.get("/user/{user_id}", response_model=List[ExpenseResponse])
def read_incomes_by_user(user_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    require_owner(user_id, scope)
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    incomes = get_expenses_by_user(db, user_id, scope)
    if not incomes:
        raise HTTPException(status_code=404, detail="No spendings found for this user")
    return incomes


@router.get("/{expense_id}", response_model=ExpenseResponse)
def read_expense(expense_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    expense = get_expense(db, expense_id, scope)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("", response_model=ExpenseResponse)
def add_expense(expense: ExpenseCreate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    expense.user_id = scope[0] if scope else expense.user_id
    return create_expense(db, expense)


@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_existing_expense(
    expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    updated_expense = update_expense(db, expense_id, expense, scope)
    if not updated_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return updated_expense


@router.delete("/{expense_id}")
def remove_expense(expense_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    deleted_expense = delete_expense(db, expense_id, scope)
    if not deleted_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"message": "Expense deleted successfully"}
