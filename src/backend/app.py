"""FastAPI application - minimal demo version"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.core.config import settings
from src.backend.api import v1_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    # Create FastAPI app
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
        max_age=settings.cors.max_age,
    )

    # Include API router
    app.include_router(v1_router, prefix="/api")

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "Demo API",
            "version": settings.app.version,
            "status": "running",
        }

    # Health check
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app


# Create app instance
app = create_app()
