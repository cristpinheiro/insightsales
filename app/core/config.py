"""
Application configuration management.

Uses Pydantic Settings for type-safe configuration with automatic
validation and support for environment variables and .env files.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings.

    All settings can be overridden by environment variables.

    Usage:
        from app.core.config import settings
        print(settings.DATABASE_URL)
    """

    # Application
    APP_NAME: str = "InsightSales"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/insightsales"
    )
    DB_ECHO: bool = True
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 3600

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "insightsales-model"
    OLLAMA_TIMEOUT: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


# Global settings instance
# Import and use this in other modules
settings = Settings()


def get_safe_database_url(database_url: str) -> str:
    """
    Return a safe-to-log representation of the database URL.

    The intention is to avoid logging credentials by only returning
    the portion after the '@' if present, or 'N/A' otherwise.
    """
    if "@" in database_url:
        # Split only once, in case '@' appears elsewhere in the string.
        return database_url.split("@", 1)[1]
    return "N/A"


# Print configuration on load (debug mode only)
if settings.DEBUG:
    print("=" * 50)
    print(f"🚀 {settings.APP_NAME}")
    print(f"📊 Database: {get_safe_database_url(settings.DATABASE_URL)}")
    print(f"🤖 Ollama: {settings.OLLAMA_BASE_URL}")
    print("=" * 50)
