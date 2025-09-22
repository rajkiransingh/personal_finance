from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.schemas.investment_schemas import MutualFundInvestmentResponse, InvestmentUpdate
from backend.services.db_services import get_db
from backend.services.user_services import get_user
from backend.services.investment_services import get_all_investments, get_investment_by_user, get_investment_by_id, create_mutual_fund, update_investment, delete_investment
from backend.summarizing import update_mutual_fund_summary

router = APIRouter(prefix="/investment/mutual-fund", tags=["Investment"])
@router.get("/", response_model=list[MutualFundInvestmentResponse])
def read_all_investments(db: Session = Depends(get_db)):
    investments = get_all_investments("mutual fund", db)
    if not investments:
        raise HTTPException(status_code=404, detail="No investments found for any user on this platform")
    return investments

@router.get("/user/{user_id}", response_model=list[MutualFundInvestmentResponse])
def read_investments_by_user(user_id: int, db: Session = Depends(get_db)):
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    investment = get_investment_by_user("mutual fund", db, user_id)
    if not investment:
        raise HTTPException(status_code=404, detail="No investments found for this user")
    return investment

@router.get("/{investment_id}", response_model=MutualFundInvestmentResponse)
def read_investment(investment_id: int, db: Session = Depends(get_db)):
    investment = get_investment_by_id("mutual fund", db, investment_id)
    return investment

@router.post("/", response_model=MutualFundInvestmentResponse)
def add_investment_transaction(investment_data: MutualFundInvestmentResponse, db: Session = Depends(get_db)):
    new_investment = create_mutual_fund(investment_data, db)
    update_mutual_fund_summary.update(db, investment_data)
    return new_investment

@router.put("/{investment_id}", response_model=InvestmentUpdate)
def update_investment_api(investment_id: int, investment_data: InvestmentUpdate, db: Session = Depends(get_db)):
    updated_investment = update_investment("mutual fund", investment_id, investment_data, db)
    if not updated_investment:
        raise HTTPException(status_code=404, detail="Income not found")
    return updated_investment

@router.delete("/{investment_id}", response_model=dict)
def delete_investment_api(investment_id: int, db: Session = Depends(get_db)):
    deleted_investment = delete_investment("mutual fund", investment_id,db)
    if not deleted_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted successfully"}