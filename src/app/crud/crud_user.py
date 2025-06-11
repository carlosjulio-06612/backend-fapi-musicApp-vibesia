from typing import Any, Dict, Optional, Union
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from datetime import datetime

from app.core.security import verify_password, get_password_hash
from app.crud.base import CRUDBase
from app.models.User import User as UserModel
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[UserModel, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[UserModel]:
        return db.query(UserModel).filter(UserModel.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> UserModel:
        if self.get_by_email(db, email=obj_in.email):
            raise HTTPException(status_code=400, detail="Email already registered.")
        if self.get_by_username(db, username=obj_in.username):
            raise HTTPException(status_code=400, detail="Username already taken.")
        
        create_data = obj_in.model_dump()
        
        db_obj = UserModel(
            email=create_data["email"],
            username=create_data["username"],
            hashed_password=get_password_hash(create_data["password"])
        )
        db.add(db_obj)
        db.flush()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: UserModel, obj_in: Union[UserUpdate, Dict[str, Any]]) -> UserModel:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            update_data["hashed_password"] = hashed_password
            update_data["password_changed_at"] = datetime.utcnow()
            del update_data["password"]
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[UserModel]:
        user = self.get_by_email(db, email=email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def deactivate(self, db: Session, *, user_id: int) -> UserModel:
        user = self.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        user.is_active = False
        db.add(user)
        db.flush()
        db.refresh(user)
        return user
    
    def reactivate(self, db: Session, *, user_id: int) -> UserModel:
        user = db.query(self.model).filter(self.model.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        user.is_active = True
        db.add(user)
        db.flush()
        db.refresh(user)
        return user

    def delete_permanently(self, db: Session, *, user_id: int) -> bool:
        user = self.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        self.remove(db=db, id=user_id)
        return True

    def get_multi_paginated(self, db: Session, *, page: int = 1, per_page: int = 10, search: Optional[str] = None) -> Dict[str, Any]:
        skip = (page - 1) * per_page
        query = db.query(self.model)
        if search:
            query = query.filter(or_(self.model.email.ilike(f"%{search}%"), self.model.username.ilike(f"%{search}%")))
        total = query.count()
        users = query.offset(skip).limit(per_page).all()
        pages = (total + per_page - 1) // per_page
        return {"users": users, "total": total, "page": page, "per_page": per_page, "pages": pages}

user = CRUDUser(UserModel)