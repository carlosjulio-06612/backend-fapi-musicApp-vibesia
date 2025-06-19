from typing import Set
import os
from pydantic_settings import BaseSettings

class AdminSettings(BaseSettings):
    # Option 1: List of administrator emails
    ADMIN_EMAILS: Set[str] = {
        "admin@vibesia.com",
        "superuser@vibesia.com",
        "manager@vibesia.com"
    }
    
    # Option 2: List of administrator usernames
    ADMIN_USERNAMES: Set[str] = {
        "admin",
        "superuser",
        "artist_manager"
    }
    
    # Option 3: List of administrator user IDs
    ADMIN_USER_IDS: Set[int] = {22, 23, 24}  # Admin user IDs
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = 'ignore'

# Global settings instance
admin_settings = AdminSettings()