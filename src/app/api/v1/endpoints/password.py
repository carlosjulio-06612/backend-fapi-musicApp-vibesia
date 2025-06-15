import logging
from datetime import datetime, timezone
from urllib.parse import unquote

from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from pydantic import EmailStr, TypeAdapter
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core.config import settings
from app.core.security import (generate_password_reset_token,
                               verify_password_reset_token)
from app.schemas.password import Msg, ResetPassword
from app.schemas.token import Token as TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/recover-password/{email}", response_model=TokenResponse, tags=["Password Recovery"])
def recover_password(
    email: str,
    db: Session = Depends(deps.get_db_session),
):
    decoded_email = unquote(email)
    
    try:
        validated_email = TypeAdapter(EmailStr).validate_python(decoded_email)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    user = crud.user.get_by_email(db, email=validated_email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The user with this email does not exist.",
        )
    
    password_reset_token = generate_password_reset_token(email=validated_email)
    logger.info(f"Token generated for {validated_email}. Token starts with: {password_reset_token[:20]}...")
    
    return TokenResponse(access_token=password_reset_token, token_type="bearer")

@router.post("/reset-password", response_model=Msg, tags=["Password Recovery"])
def reset_password(
    body: ResetPassword,
    db: Session = Depends(deps.get_db_session),
):
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is invalid, expired, or has the wrong type."
        )

    user = crud.user.get_by_email(db, email=email)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive.")

    try:
        payload = jwt.decode(
            body.token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_signature": False, "verify_exp": False, "verify_nbf": False}
        )
        token_created_at = payload.get("nbf")
        if not token_created_at:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token is missing the 'nbf' (creation time) claim.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not decode token to read 'nbf': {e}")
    
    if user.password_changed_at:
        last_change_ts = user.password_changed_at.timestamp()
        if last_change_ts > token_created_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This password reset token has already been used or invalidated."
            )

    update_data = {
        "password": body.new_password,
        "password_changed_at": datetime.now(timezone.utc)
    }
    crud.user.update(db, db_obj=user, obj_in=update_data)
    
    logger.info(f"Password for '{email}' updated successfully.")
    
    return {"msg": "Password updated successfully"}