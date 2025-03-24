# api/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import get_settings
from api.routes import router as api_router
from api.middleware.rate_limiter import PolygonRateLimiter

def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    settings = get_settings()
    
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
    )
    
    # Add CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add rate limiter middleware for Polygon API
    application.add_middleware(PolygonRateLimiter)
    
    # Include API routes
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    @application.get("/", tags=["status"])
    async def root():
        """API health check endpoint."""
        return {
            "status": "online",
            "message": f"{settings.PROJECT_NAME} is running",
            "version": settings.PROJECT_VERSION
        }
    
    return application

app = create_application()