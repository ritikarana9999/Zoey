"""
Application configuration using Pydantic Settings.
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://smartcart:smartcart_secret@localhost:5432/smartcart"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenAI
    openai_api_key: str = ""

    # App
    environment: str = "development"
    debug: bool = True

    # CORS
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Forecasting
    forecast_horizon_days: int = 30
    min_history_days: int = 14

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
