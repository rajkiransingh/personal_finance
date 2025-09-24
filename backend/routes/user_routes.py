import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from backend.services.db_services import get_db
from backend.services.user_services import get_user, get_user_id_by_name, create_user, update_user, delete_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["Users"])


# Create a new user
@router.post("/", response_model=UserResponse)
def create_user_api(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)


# Get a user by ID
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_api(user_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching user with ID: {user_id}")
    logger.debug(f"User ID: {user_id}")
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return user
    except Exception as e:
        logger.exception("Exception occurred while fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Get user_id by name
@router.get("/username/{name}", response_model=UserResponse)
async def get_user_id_by_name_api(name: str, db: Session = Depends(get_db)):
    logger.info(f"Fetching user with name: {name}")
    logger.debug(f"User name: {name}")
    user = get_user_id_by_name(db, name)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        return user
    except Exception as e:
        logger.exception("Exception occurred while fetching user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Update a user by ID
@router.put("/{user_id}", response_model=UserResponse)
def update_user_api(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    updated_user = update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


# Delete a user by ID
@router.delete("/{user_id}")
def delete_user_api(user_id: int, db: Session = Depends(get_db)):
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
