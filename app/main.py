"""
Main FastAPI application.

This module creates and configures the FastAPI application,
including startup/shutdown events, middleware, and routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import init_db, close_db, test_connection
from app.controller.finder import router as query_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events:
    - Startup: Initialize database and create tables
    - Shutdown: Close database connections
    """
    # Startup
    print("\n🚀 Starting application...")
    try:
        await init_db()
        print("✅ Application started successfully!\n")
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        raise

    yield

    # Shutdown
    print("\n🔌 Shutting down application...")
    await close_db()
    print("✅ Application shutdown complete\n")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Natural Language to SQL Query System using Ollama",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(query_router)


@app.get("/")
async def root():
    """
    Root endpoint - welcome message.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "description": "Convert natural language questions to SQL queries",
        "endpoints": {
            "health": "/health",
            "schema": "/schema",
            "query": "/api/query",
        },
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns application status and database connectivity.
    """
    db_connected = await test_connection()

    return {
        "status": "healthy" if db_connected else "unhealthy",
        "app_name": settings.APP_NAME,
        "debug": settings.DEBUG,
        "database": {
            "connected": db_connected,
            "url": settings.DATABASE_URL.split("@")[1]
            if "@" in settings.DATABASE_URL
            else "N/A",
        },
        "ollama": {
            "url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
