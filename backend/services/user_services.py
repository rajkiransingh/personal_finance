from sqlalchemy.orm import Session
from backend.models.models import User
from backend.schemas.user_schema import UserCreate, UserUpdate

# Create a new user
def create_user(db: Session, user_data: UserCreate):
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Get user by ID
def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.user_id == user_id).first()

#Get user_id by name
def get_user_id_by_name(db: Session, name: str):
    return db.query(User).filter(User.name == name).first()

# Update user details
def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    for key, value in user_data.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

# Delete user
def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        return None
    db.delete(user)
    db.commit()
    return user
