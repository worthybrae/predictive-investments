# api/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router as api_router

# Load environment variables
load_dotenv()

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # App settings from environment variables with defaults
    project_name = os.getenv("PROJECT_NAME", "Stock Data API")
    project_description = os.getenv("PROJECT_DESCRIPTION", "A modular API to fetch stock data from Polygon.io")
    project_version = os.getenv("PROJECT_VERSION", "0.1.0")
    api_prefix = os.getenv("API_PREFIX", "/api/v1")
    
    # CORS settings
    cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
    
    application = FastAPI(
        title=project_name,
        description=project_description,
        version=project_version,
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    application.include_router(api_router, prefix=api_prefix)
    
    @application.get("/", tags=["status"])
    async def root():
        """API health check endpoint."""
        return {
            "status": "online",
            "message": f"{project_name} is running",
            "version": project_version
        }
    
    return application

app = create_application()