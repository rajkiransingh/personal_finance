from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.investments.common import InvestmentUpdate
from backend.schemas.investments.real_estate_schema import (
    RealEstateInvestmentResponse,
    RealEstateInvestmentCreate,
    RealEstateUpdateResponse,
)
from backend.services.auth import get_data_scope
from backend.services.db_services import get_db
from backend.services.scope import require_owner
from backend.services.investments.common import (
    get_all_investments,
    get_investment_by_user,
    get_investment_by_id,
    update_investment,
    delete_investment,
)
from backend.services.investments.real_estate import create_property
from backend.services.user_services import get_user
from backend.summarizing import update_real_estate_summary
from utilities.real_estate_price_updater import update_real_estate_investment

router = APIRouter(prefix="/investment/real-estate", tags=["Investment"])


@router.get("", response_model=list[RealEstateInvestmentResponse])
def read_all_investments(db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    investments = get_all_investments("real estate", db, scope)
    if not investments:
        raise HTTPException(
            status_code=404, detail="No investments found for any user on this platform"
        )
    return investments


@router.get("/user/{user_id}", response_model=list[RealEstateInvestmentResponse])
def read_investments_by_user(user_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    require_owner(user_id, scope)
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    investment = get_investment_by_user("real estate", db, user_id, scope)
    if not investment:
        raise HTTPException(
            status_code=404, detail="No investments found for this user"
        )
    return investment


@router.get("/{investment_id}", response_model=RealEstateInvestmentResponse)
def read_investment(investment_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    investment = get_investment_by_id("real estate", db, investment_id, scope)
    return investment


@router.post("", response_model=RealEstateInvestmentResponse)
def add_investment_transaction(
    investment_data: RealEstateInvestmentCreate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    investment_data.investor = scope[0] if scope else investment_data.investor
    new_investment = create_property(db, investment_data)
    update_real_estate_summary.update(db, investment_data)
    return new_investment


@router.put("/{investment_id}", response_model=InvestmentUpdate)
def update_investment_api(
    investment_id: int, investment_data: InvestmentUpdate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    updated_investment = update_investment(
        "real estate", investment_id, investment_data, db
    )
    if not updated_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    update_real_estate_summary.update(db, updated_investment)
    return updated_investment


@router.put("/{investment_id}/price", response_model=RealEstateUpdateResponse)
def update_property_price(
    investment_id: int, investment_data: InvestmentUpdate, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)
):
    return update_real_estate_investment(db, investment_id, investment_data)


@router.delete("/{investment_id}", response_model=dict)
def delete_investment_api(investment_id: int, db: Session = Depends(get_db), scope: list[int] = Depends(get_data_scope)):
    deleted_investment = delete_investment("real estate", investment_id, db, scope)
    if not deleted_investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    return {"message": "Investment deleted successfully"}
