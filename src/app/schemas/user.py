from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime, date
from typing import Optional 

class UserBase(BaseModel):
    username: str
    email: str

    @validator("email")
    def email_must_not_contain_spaces(cls, v):
        """validate that email does not contain spaces"""
        if ' ' in v:
            raise ValueError("email must not contain spaces")
        return v

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    user_id: int
    is_active: bool
    registration_date: date
    preferences: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    password_changed_at: Optional[datetime] = None

class UserListResponse(BaseModel):
    users: list[UserResponse]
    total: int
    page: int
    per_page: int

class UserStatusResponse(BaseModel):
    user_id: int
    username: str
    is_active: bool