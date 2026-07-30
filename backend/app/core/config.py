import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "DunderHunt API"
    VERSION: str = "0.1.0"
    
    # DB configuration (default to local sqlite async)
    DATABASE_URL: str = "sqlite+aiosqlite:///./dunderhunt.db"
    REDIS_URL: str = ""
    
    # LLM configuration
    LLM_PROVIDER: str = "mock"  # "mock", "gemini", "openai", "anthropic"
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
