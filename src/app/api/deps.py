from typing import Optional, Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.config import settings
from app.crud.crud_user import user as user_crud
from app.models.User import User as UserModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

def get_db_session() -> Generator[Session, None, None]:
    print("\n[DEBUG] 1. Creating DB session.")
    db = SessionLocal()
    try:
        yield db
    finally:
        print("[DEBUG] 10. Committing transaction.")
        db.commit()
        print("[DEBUG] 11. Closing DB session.")
        db.close()

def set_audit_context_and_get_user(
    request: Request,
    db: Session = Depends(get_db_session),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[UserModel]:
    
    print("[DEBUG] 2. Entering audit context dependency.")
    
    if hasattr(request.state, 'current_user_from_audit'):
        print("[DEBUG] 2.1. User already processed for this request. Skipping.")
        return request.state.current_user_from_audit
    
    db_user = None
    if token:
        print("[DEBUG] 3. Bearer token found. Attempting to decode.")
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_email: Optional[str] = payload.get("sub")
            print(f"[DEBUG] 4. Token decoded. Email found: {user_email}")
            
            if user_email:
                print(f"[DEBUG] 5. Fetching user '{user_email}' from database...")
                db_user = user_crud.get_by_email(db, email=user_email)
                request.state.current_user_from_audit = db_user
            else:
                print("[DEBUG] 4.1. FAIL: Token payload does not contain 'sub' (email) field.")
                request.state.current_user_from_audit = None

        except (JWTError, AttributeError) as e:
            print(f"[DEBUG] 3.1. FAIL: Token is invalid or an error occurred. Detail: {e}")
            request.state.current_user_from_audit = None
    else:
        print("[DEBUG] 3. No token found in request.")
        request.state.current_user_from_audit = None
        
    user_agent = request.headers.get("user-agent", "")
    api_endpoint = request.url.path
    request_id = request.headers.get("x-request-id", "")
    
    app_user_id = str(db_user.user_id) if db_user and db_user.user_id else ""
    app_user_email = db_user.email if db_user and db_user.email else ""
    app_user_role = db_user.role if db_user and hasattr(db_user, 'role') and db_user.role else ""

    print("[DEBUG] 6. Setting audit variables in DB session.")
    db.execute(text("SET LOCAL audit.app_user_id = :val"), {'val': app_user_id})
    db.execute(text("SET LOCAL audit.app_user_email = :val"), {'val': app_user_email})
    db.execute(text("SET LOCAL audit.app_user_role = :val"), {'val': app_user_role})
    db.execute(text("SET LOCAL audit.user_agent = :val"), {'val': user_agent})
    db.execute(text("SET LOCAL audit.api_endpoint = :val"), {'val': api_endpoint})
    db.execute(text("SET LOCAL audit.request_id = :val"), {'val': request_id})
    print(f"[DEBUG] 7. AUDIT CONTEXT ESTABLISHED for user: {app_user_email or 'Anonymous'}")

    return db_user


def get_current_user(
    db_user: Optional[UserModel] = Depends(set_audit_context_and_get_user)
) -> UserModel:
    print("[DEBUG] 8. Checking for current user.")
    if db_user is None:
        print("[DEBUG] 8.1. FAIL: No valid user found. Raising 401 Unauthorized.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    print(f"[DEBUG] 8.2. SUCCESS: Valid user '{db_user.email}' confirmed.")
    return db_user

def get_current_active_user(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    print("[DEBUG] 9. Checking if current user is active.")
    if not current_user.is_active:
        print("[DEBUG] 9.1. FAIL: User is inactive. Raising 400 Bad Request.")
        raise HTTPException(status_code=status.HTTP_400, detail="Inactive user")
    
    print("[DEBUG] 9.2. SUCCESS: User is active.")
    return current_user