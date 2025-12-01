import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.services.db_services import get_db
from utilities.analytics.stock_analyzer import get_stock_score

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["categories"])


# Get all the data related to mera paisa dashboard
@router.get("/score")
async def get_stock_scores():
    return get_stock_score()


@router.post("/users")
async def add_user(user_data: dict, db: Session = Depends(get_db)):
    new_user = User(name=user_data.get("name"))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
