# api/core/config.py
import os 
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from functools import lru_cache

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Stock Data API"
    PROJECT_DESCRIPTION: str = "A modular API to fetch stock data from Polygon.io"
    PROJECT_VERSION: str = "0.1.0"
    
    # Polygon.io Settings
    POLYGON_API_KEY: str = os.getenv("POLYGON_API_KEY", "")
    POLYGON_BASE_URL: str = "https://api.polygon.io"
    
    # CORS Settings
    CORS_ORIGINS: list = ["*"]  # Update this in production
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings as a singleton.
    
    Returns:
        Application settings
    """
    return Settings()