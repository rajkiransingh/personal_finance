import logging

from fastapi import APIRouter, Depends, HTTPException
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


# Get all the data related to mera paisa dashboard
@router.get("/users")
async def get_available_users():
    db: Session = next(get_db())
    db.expire_all()
    return db.query(User).all()


@router.post("/users")
async def add_user(user_data: dict, db: Session = Depends(get_db)):
    new_user = User(name=user_data.get("name"))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.name = user_data.get("name", user.name)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.get("/income-sources")
async def get_income_sources():
    db: Session = next(get_db())
    return db.query(IncomeSource).all()


@router.post("/income-sources")
async def add_income_sources(income_source_data: dict, db: Session = Depends(get_db)):
    new_source = IncomeSource(name=income_source_data.get("name"), description=income_source_data.get("description"))
    db.add(new_source)
    db.commit()
    db.refresh(new_source)
    return new_source


@router.put("/income-sources/{income_source_id}")
async def update_income_source(income_source_id: int, income_source_data: dict, db: Session = Depends(get_db)):
    income_source = db.query(IncomeSource).filter(IncomeSource.income_source_id == income_source_id).first()
    if not income_source:
        raise HTTPException(status_code=404, detail="Income Source not found")
    income_source.name = income_source_data.get("name", income_source.name)
    income_source.description = income_source_data.get("description", income_source.description)
    db.commit()
    db.refresh(income_source)
    return income_source


@router.delete("/income-sources/{income_source_id}")
async def delete_income_source(income_source_id: int, db: Session = Depends(get_db)):
    income_source = db.query(IncomeSource).filter(IncomeSource.income_source_id == income_source_id).first()
    if not income_source:
        raise HTTPException(status_code=404, detail="Income Source not found")
    db.delete(income_source)
    db.commit()
    return {"message": "Income Source deleted successfully"}


@router.get("/expense-category")
async def get_expense_category():
    db: Session = next(get_db())
    return db.query(ExpenseCategory).all()


@router.post("/expense-category")
async def add_expense_category(expense_category_data: dict, db: Session = Depends(get_db)):
    new_category = ExpenseCategory(name=expense_category_data.get("name"),
                                   description=expense_category_data.get("description"))
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/expense-category/{expense_category_id}")
async def update_expense_category(expense_category_id: int, expense_category_data: dict, db: Session = Depends(get_db)):
    expense_category = db.query(ExpenseCategory).filter(
        ExpenseCategory.expense_category_id == expense_category_id).first()
    if not expense_category:
        raise HTTPException(status_code=404, detail="Expense Category not found")
    expense_category.name = expense_category_data.get("name", expense_category.name)
    expense_category.description = expense_category_data.get("description", expense_category.description)
    db.commit()
    db.refresh(expense_category)
    return expense_category


@router.delete("/expense-category/{expense_category_id}")
async def delete_expense_category(expense_category_id: int, db: Session = Depends(get_db)):
    expense_category = db.query(ExpenseCategory).filter(
        ExpenseCategory.expense_category_id == expense_category_id).first()
    if not expense_category:
        raise HTTPException(status_code=404, detail="Expense Category not found")
    db.delete(expense_category)
    db.commit()
    return {"message": "Expense Category deleted successfully"}


@router.get("/investment-category")
async def get_investment_category():
    db: Session = next(get_db())
    return db.query(InvestmentCategory).all()


@router.post("/investment-category")
async def add_investment_category(investment_category_data: dict, db: Session = Depends(get_db)):
    new_category = InvestmentCategory(investment_type=investment_category_data.get("investment_type"))
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category


@router.put("/investment-category/{investment_category_id}")
async def update_investment_category(investment_category_id: int, investment_category_data: dict,
                                     db: Session = Depends(get_db)):
    investment_category = db.query(InvestmentCategory).filter(
        InvestmentCategory.id == investment_category_id).first()
    if not investment_category:
        raise HTTPException(status_code=404, detail="Investment Category not found")
    investment_category.investment_type = investment_category_data.get("investment_type",
                                                                       investment_category.investment_type)
    db.commit()
    db.refresh(investment_category)
    return investment_category


@router.delete("/investment-category/{investment_category_id}")
async def delete_investment_category(investment_category_id: int, db: Session = Depends(get_db)):
    investment_category = db.query(InvestmentCategory).filter(
        InvestmentCategory.id == investment_category_id).first()
    if not investment_category:
        raise HTTPException(status_code=404, detail="Investment Category not found")
    db.delete(investment_category)
    db.commit()
    return {"message": "Investment Category deleted successfully"}


@router.get("/investment-subcategory")
async def get_investment_subcategory():
    db: Session = next(get_db())
    return db.query(InvestmentSubCategory).all()


@router.post("/investment-subcategory")
async def add_investment_sub_category(investment_sub_category_data: dict, db: Session = Depends(get_db)):
    new_sub_category = InvestmentSubCategory(
        investment_subcategory_name=investment_sub_category_data.get("investment_subcategory_name"),
        category_id=investment_sub_category_data.get("category_id"))
    db.add(new_sub_category)
    db.commit()
    db.refresh(new_sub_category)
    return new_sub_category


@router.put("/investment-subcategory/{investment_subcategory_id}")
async def update_investment_subcategory(investment_subcategory_id: int, investment_subcategory_data: dict,
                                        db: Session = Depends(get_db)):
    investment_subcategory = db.query(InvestmentSubCategory).filter(
        InvestmentSubCategory.id == investment_subcategory_id).first()
    if not investment_subcategory:
        raise HTTPException(status_code=404, detail="Investment Sub Category not found")
    investment_subcategory.category_id = investment_subcategory_data.get("category_id",
                                                                         investment_subcategory.category_id)
    investment_subcategory.investment_subcategory_name = investment_subcategory_data.get("investment_subcategory_name",
                                                                                         investment_subcategory.investment_subcategory_name)
    db.commit()
    db.refresh(investment_subcategory)
    return investment_subcategory


@router.delete("/investment-subcategory/{investment_subcategory_id}")
async def delete_investment_subcategory(investment_subcategory_id: int, db: Session = Depends(get_db)):
    investment_subcategory = db.query(InvestmentSubCategory).filter(
        InvestmentSubCategory.id == investment_subcategory_id).first()
    if not investment_subcategory:
        raise HTTPException(status_code=404, detail="Investment Sub Category not found")
    db.delete(investment_subcategory)
    db.commit()
    return {"message": "Investment Category deleted successfully"}


@router.get("/currencies")
async def get_currencies():
    db: Session = next(get_db())
    return db.query(Currencies).all()


@router.post("/currencies")
async def add_currencies(currency_data: dict, db: Session = Depends(get_db)):
    new_currency = Currencies(currency_code=currency_data.get("currency_code"),
                              currency_name=currency_data.get("currency_name"))
    db.add(new_currency)
    db.commit()
    db.refresh(new_currency)
    return new_currency


@router.put("/currencies/{currency_id}")
async def update_currency(currency_id: int, currency_data: dict, db: Session = Depends(get_db)):
    currency = db.query(Currencies).filter(Currencies.currency_id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    currency.currency_code = currency_data.get("currency_code", currency.currency_code)
    currency.currency_name = currency_data.get("currency_name", currency.currency_name)
    db.commit()
    db.refresh(currency)
    return currency


@router.delete("/currencies/{currency_id}")
async def delete_currency(currency_id: int, db: Session = Depends(get_db)):
    currency = db.query(Currencies).filter(Currencies.currency_id == currency_id).first()
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    db.delete(currency)
    db.commit()
    return {"message": "Currency deleted successfully"}


@router.get("/region")
async def get_region():
    db: Session = next(get_db())
    return db.query(Regions).all()


@router.post("/region")
async def add_region(region_data: dict, db: Session = Depends(get_db)):
    new_region = Regions(region_name=region_data.get("region_name"),
                         currency_id=region_data.get("currency_id"))
    db.add(new_region)
    db.commit()
    db.refresh(new_region)
    return new_region


@router.put("/region/{region_id}")
async def update_region(region_id: int, region_data: dict, db: Session = Depends(get_db)):
    region = db.query(Regions).filter(Regions.region_id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    region.region_name = region_data.get("region_name", region.region_name)
    region.currency_id = region_data.get("currency_id", region.currency_id)
    db.commit()
    db.refresh(region)
    return region


@router.delete("/region/{region_id}")
async def delete_region(region_id: int, db: Session = Depends(get_db)):
    region = db.query(Regions).filter(Regions.region_id == region_id).first()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    db.delete(region)
    db.commit()
    return {"message": "Region deleted successfully"}


@router.get("/units")
async def get_units():
    db: Session = next(get_db())
    return db.query(Unit).all()


@router.post("/units")
async def add_unit(unit_data: dict, db: Session = Depends(get_db)):
    new_unit = Unit(unit_name=unit_data.get("unit_name"))
    db.add(new_unit)
    db.commit()
    db.refresh(new_unit)
    return new_unit


@router.put("/units/{unit_id}")
async def update_unit(unit_id: int, unit_data: dict, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    unit.unit_name = unit_data.get("unit_name", unit.unit_name)
    db.commit()
    db.refresh(unit)
    return unit


@router.delete("/units/{unit_id}")
async def delete_unit(unit_id: int, db: Session = Depends(get_db)):
    unit = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not unit:
        raise HTTPException(status_code=404, detail="Unit not found")
    db.delete(unit)
    db.commit()
    return {"message": "Unit deleted successfully"}
