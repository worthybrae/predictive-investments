# api/core/exceptions.py
from fastapi import HTTPException, status

class PolygonAPIException(HTTPException):
    """Exception raised for errors in the Polygon.io API."""
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ConfigurationException(HTTPException):
    """Exception raised for missing configuration."""
    
    def __init__(self, detail: str = "API configuration error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)