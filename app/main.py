"""
Main FastAPI application.

This module creates and configures the FastAPI application,
including startup/shutdown events, middleware, and routes.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import inspect
from app.core.config import settings
from app.core.database import (
    init_db,
    close_db,
    test_connection,
    engine,
)
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


@app.get("/schema")
async def get_schema():
    """
    Get database schema information.

    Returns all tables and their columns with types.
    """
    async with engine.connect() as conn:

        def get_schema_info(connection):
            inspector = inspect(connection)
            schema = {}

            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append(
                        {
                            "name": column["name"],
                            "type": str(column["type"]),
                            "nullable": column["nullable"],
                            "primary_key": column.get("primary_key", False),
                        }
                    )

                # Get foreign keys
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    foreign_keys.append(
                        {
                            "column": fk["constrained_columns"][0]
                            if fk["constrained_columns"]
                            else None,
                            "references": f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                            if fk["referred_columns"]
                            else None,
                        }
                    )

                schema[table_name] = {
                    "columns": columns,
                    "foreign_keys": foreign_keys,
                }

            return schema

        schema_info = await conn.run_sync(get_schema_info)

    return {
        "database": settings.DATABASE_URL.split("@")[1].split("/")[1]
        if "@" in settings.DATABASE_URL
        else "unknown",
        "tables": schema_info,
        "total_tables": len(schema_info),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
