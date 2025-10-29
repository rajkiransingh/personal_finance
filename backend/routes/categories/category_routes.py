import logging

from fastapi import APIRouter
from sqlalchemy.orm import Session

from backend.models.currency import Currencies, Regions
from backend.models.earnings.income import IncomeSource
from backend.models.investments.common import InvestmentCategory, InvestmentSubCategory
from backend.models.spendings.expense import ExpenseCategory
from backend.models.unit import Unit
from backend.models.user import User
from backend.services.db_services import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/categories", tags=["categories"])

db: Session = next(get_db())


# Get all the data related to mera paisa dashboard
@router.get("/users")
async def get_available_users():
    return db.query(User).all()


@router.get("/income-sources")
async def get_income_sources():
    return db.query(IncomeSource).all()


@router.get("/expense-category")
async def get_expense_category():
    return db.query(ExpenseCategory).all()


@router.get("/investment-category")
async def get_investment_category():
    return db.query(InvestmentCategory).all()


@router.get("/investment-subcategory")
async def get_investment_subcategory():
    return db.query(InvestmentSubCategory).all()


@router.get("/currencies")
async def get_currencies():
    return db.query(Currencies).all()


@router.get("/region")
async def get_region():
    return db.query(Regions).all()


@router.get("/units")
async def get_units():
    return db.query(Unit).all()
