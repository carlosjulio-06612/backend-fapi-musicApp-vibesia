from app.models.User import User
from app.core.config import settings
from functools import wraps
from fastapi import HTTPException, status, Depends

def is_admin_user(user: User) -> bool:
    """
    Checks if a user is an administrator based on various criteria.
    """
    if user.email and user.email.lower() in {email.lower() for email in settings.ADMIN_EMAILS}:
        return True
    
    if hasattr(user, 'username') and user.username in settings.ADMIN_USERNAMES:
        return True
    
    if user.user_id in settings.ADMIN_USER_IDS:
        return True
    
    return False

def require_admin_permission(user: User) -> None:
    """
    Helper function that raises an exception if the user is not an admin.
    """
    if not is_admin_user(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required to perform this action."
        )

# --- Alternative Decorator ---
def admin_required(func):
    """
    Decorator to protect endpoints, requiring administrator permissions.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Find the 'current_user' parameter in the decorated function's arguments
        current_user: User = kwargs.get('current_user')
        if not current_user:
            # This case should ideally be handled by a dependency first
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
            
        require_admin_permission(current_user)
        return func(*args, **kwargs)
    return wrapper