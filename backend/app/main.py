"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from .config import settings
from .routes import chat, users

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI Health Coach API for Disha",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router)
app.include_router(users.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Disha AI Health Coach API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    from datetime import datetime, timezone
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
