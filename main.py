"""
Wrapper for running the application from the root directory.
This allows VS Code debug to work with 'main:app'.
"""

from app.main import app  # noqa: F401

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
