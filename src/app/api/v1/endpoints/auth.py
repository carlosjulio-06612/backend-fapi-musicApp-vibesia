# --- START OF FILE auth.py (CORRECTED) ---

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.token import Token

router = APIRouter()

@router.post("/login", response_model=Token, tags=["Authentication"])
def login_for_access_token(
    db: Session = Depends(deps.get_db_session),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    token_data = {
        "sub": user.email,
        "user_id": str(user.user_id)
    }

    access_token = security.create_access_token(
        data=token_data, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }