from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic for validation and type checking
    """
    #Security
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int = 30
    REFRESH_TOKEN_EXPRIRE_DAYS:int =7

    #redis cache
    REDIS_HOST:str
    REDIS_PORT:int
    REDIS_USR:str
    REDIS_PWD:str

    # Application
    APP_NAME: str = "API Prod"
    DEBUG: bool = False

    class Config:
        env_file = ".env"
        case_sesitive = True

@lru_cache
def get_settings() -> Settings:
    """
    Cache settings to avoid reading .env file repeatedly.
    lru_cache ensures we only create one Settings instance.
    """
    return Settings()