from sqlalchemy.orm import Session

from backend.models.expenses.expense import Expense
from backend.schemas.expense_schema import ExpenseCreate, ExpenseUpdate


def get_all_expenses(db: Session):
    return db.query(Expense).all()


def get_expenses_by_user(db: Session, user_id: int):
    return db.query(Expense).filter(Expense.user_id == user_id).all()


def get_expense(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.expense_id == expense_id).first()


def create_expense(db: Session, expense: ExpenseCreate):
    new_expense = Expense(**expense.dict())
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense


def update_expense(db: Session, expense_id: int, expense: ExpenseUpdate):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if db_expense:
        for key, value in expense.dict(exclude_unset=True).items():
            setattr(db_expense, key, value)
        db.commit()
        db.refresh(db_expense)
    return db_expense


def delete_expense(db: Session, expense_id: int):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    if db_expense:
        db.delete(db_expense)
        db.commit()
    return db_expense
