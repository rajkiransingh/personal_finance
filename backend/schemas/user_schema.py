from pydantic import BaseModel
from typing import Optional


# Schema for creating a user
class UserCreate(BaseModel):
    name: str  # Matches DB column


# Schema for updating a user (partial update allowed)
class UserUpdate(BaseModel):
    name: Optional[str] = None  # Allows partial updates


# Schema for returning user data
class UserResponse(BaseModel):
    user_id: int
    name: str

    class Config:
        from_attributes = True


# Schema for returning multiple users
class UsersResponse(BaseModel):
    users: list[UserResponse]

    class Config:
        from_attributes = True


# Schema for returning a single user
class SingleUserResponse(BaseModel):
    user: UserResponse

    class Config:
        from_attributes = True
