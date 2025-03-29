import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings"""
    APP_NAME: str = "Crypto Exchange Comparison API"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/crypto_exchange")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"

settings = Settings() 