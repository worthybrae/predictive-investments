# api/dependencies.py
from fastapi import Depends, HTTPException, status
from api.core.config import get_settings, Settings
from api.core.exceptions import ConfigurationException

async def get_api_key(settings: Settings = Depends(get_settings)):
    """
    Dependency to validate that the Polygon.io API key is configured.
    
    Returns:
        The API key if it exists
        
    Raises:
        ConfigurationException: If the API key is not set
    """
    if not settings.POLYGON_API_KEY:
        raise ConfigurationException(detail="Polygon.io API key not configured")
    
    return settings.POLYGON_API_KEY

async def get_settings_dependency():
    """
    Get application settings.
    
    Returns:
        Application settings
    """
    return get_settings()