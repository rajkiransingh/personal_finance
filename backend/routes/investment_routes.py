from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models import models
from backend.services.db_services import get_db
from backend.schemas.investment_schemas import InvestmentCreate, InvestmentUpdate, InvestmentResponse
from backend.services.user_services import get_user
from backend.services.investment_services import get_all_investments, get_investment, get_investment_by_user, create_investment, update_investment, delete_investment

import backend.summarizing.investment as investment
import backend.summarizing.investment_summary as investment_summary


router = APIRouter(prefix="/investment", tags=["Investment"])

@router.get("/", response_model=list[InvestmentResponse])
def read_all_investments(db: Session = Depends(get_db)):
    investments = get_all_investments(db)
    return investments

@router.get("/user/{user_id}", response_model=list[InvestmentResponse])
def read_investments_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    investment = get_investment_by_user(db, user_id)
    if not investment:
        raise HTTPException(status_code=404, detail="No investments found for this user")
    return investment

@router.get("/{investment_id}", response_model=InvestmentResponse)
def read_investment(investment_id: int, db: Session = Depends(get_db)):
    investment = get_investment(db, investment_id)
    return investment

@router.post("/", response_model=InvestmentResponse)
def add_investment_transaction(investment_data: InvestmentCreate, db: Session = Depends(get_db)):
    #return create_investment(investment_data, db)
    new_investment = investment.create(investment_data, db)
    
    investment_summary.update(new_investment, db)
    return new_investment

@router.put("/{investment_id}", response_model=InvestmentResponse)
def update_investment_api(investment_id: int, investment_data: InvestmentUpdate, db: Session = Depends(get_db)):
    updated_investment = update_investment(investment_id, investment_data, db)
    if not updated_investment:
        raise HTTPException(status_code=404, detail="Income not found")
    return updated_investment

@router.delete("/{investment_id}", response_model=dict)
def delete_investment_api(investment_id: int, db: Session = Depends(get_db)):
    deleted_investment = delete_investment(investment_id,db)
    if not deleted_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted successfully"}