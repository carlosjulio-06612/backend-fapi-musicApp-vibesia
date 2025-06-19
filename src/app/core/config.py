from typing import List, Set
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # --- Project Settings ---
    PROJECT_NAME: str = "MusicApp - Vibesia"
    API_V1_STR: str = "/api/v1"
    
    # --- Database Settings ---
    DATABASE_URL: str
    
    # --- Security & JWT Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60 
    
    # --- CORS Settings ---
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
    ]
    ADMIN_EMAILS: Set[str]
    ADMIN_USERNAMES: Set[str]
    ADMIN_USER_IDS: Set[int]

 
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True, 
        env_file_encoding='utf-8'
    )


settings = Settings()