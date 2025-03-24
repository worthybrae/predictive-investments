# api/dependencies.py
import os
from fastapi import HTTPException, status
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def get_api_key():
    """
    Dependency to validate that the Polygon.io API key is configured.
    
    Returns:
        The API key if it exists
        
    Raises:
        HTTPException: If the API key is not set
    """
    api_key = os.getenv("POLYGON_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Polygon.io API key not configured"
        )
    
    return api_key

# Add these dependencies for AI services
async def get_openai_api_key():
    """
    Dependency to validate that the OpenAI API key is configured.
    
    Returns:
        The API key if it exists
        
    Raises:
        HTTPException: If the API key is not set
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OpenAI API key not configured"
        )
    
    return api_key

async def get_perplexity_api_key():
    """
    Dependency to validate that the Perplexity API key is configured.
    
    Returns:
        The API key if it exists
        
    Raises:
        HTTPException: If the API key is not set
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Perplexity API key not configured"
        )
    
    return api_key