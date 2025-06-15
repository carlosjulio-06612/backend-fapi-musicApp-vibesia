# --- START OF FILE users.py (CORRECTED) ---

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app import crud
from app.api import deps  # Se mantiene igual
import logging

from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.models.User import User as UserModel

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db_session)
):
    created_user = crud.user.create(db=db, obj_in=user_in)
    logger.info(f"New user registered: {created_user.user_id} - {created_user.email}")
    return created_user

@router.get("/me", response_model=UserResponse, tags=["Users"])
def read_user_me(
    current_user: UserModel = Depends(deps.get_current_active_user)
):
    return current_user

@router.put("/me", response_model=UserResponse, tags=["Users"])
def update_user_me(
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_active_user),
):
    db = Session.object_session(current_user)
    
    updated_user = crud.user.update(db=db, db_obj=current_user, obj_in=user_in)
    logger.info(f"User updated their profile: {current_user.user_id}")
    return updated_user

@router.delete("/me", response_model=dict, tags=["Users"])
def delete_current_user_permanently(
    current_user: UserModel = Depends(deps.get_current_active_user),
):
    db = Session.object_session(current_user)
    
    user_id = current_user.user_id
    username = current_user.username

    crud.user.delete_permanently(db=db, user_id=user_id)
    
    logger.info(f"User {username} (ID: {user_id}) permanently deleted their own account.")
    return {"message": "Your account has been permanently deleted.", "user_id": user_id}