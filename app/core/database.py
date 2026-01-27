"""
Database connection management.

This module configures:
- Async SQLAlchemy engine
- Session factory for creating database sessions
- FastAPI dependency for dependency injection
- Functions to create/drop/check tables

Uses async/await for non-blocking operations and better performance.
"""

from typing import AsyncGenerator, Set
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy import text, inspect

# Import settings and models
from app.core.config import settings
from app.models.base import Base
from app.models.database import Seller, Customer, Product, Order, OrderProduct  # noqa: F401


# Async SQLAlchemy Engine
# Responsible for managing connections to the database
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=settings.DB_POOL_RECYCLE,
)


# Session factory to create async sessions
# A session represents a "conversation" with the database
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Objects remain accessible after commit
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get a database session.

    This function is used as a dependency in FastAPI endpoints to
    provide a database session that is automatically closed at the
    end of the request.

    Usage example in an endpoint:
        from fastapi import Depends
        from sqlalchemy import select

        @router.get("/sellers")
        async def get_sellers(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Seller))
            return result.scalars().all()

    Yields:
        AsyncSession: Configured database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables() -> None:
    """
    Creates all tables in the database.

    This function should be called at application startup
    to ensure all tables exist.

    IMPORTANT: This only creates tables that don't exist.
    For changes to existing tables, use migrations (Alembic).

    Raises:
        Exception: If table creation fails

    Usage:
        from app.core.database import create_tables
        await create_tables()
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise


async def drop_tables() -> None:
    """
    Drops all tables from the database.

    ⚠️ WARNING: This function deletes ALL data!
    Use only in development/testing environments.

    Raises:
        Exception: If table deletion fails

    Usage:
        from app.core.database import drop_tables
        await drop_tables()
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        print("🗑️  All tables dropped successfully!")
    except Exception as e:
        print(f"❌ Error dropping tables: {e}")
        raise


async def test_connection() -> bool:
    """
    Tests the connection to the database.

    Returns:
        bool: True if connection successful, False otherwise

    Usage:
        from app.core.database import test_connection
        is_connected = await test_connection()
    """
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            result.scalar()
        print("✅ Database connection successful!")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        # Hide password from URL when displaying
        safe_url = (
            settings.DATABASE_URL.split("@")[1]
            if "@" in settings.DATABASE_URL
            else "unknown"
        )
        print(f"   Target: {safe_url}")
        return False


async def get_existing_tables() -> Set[str]:
    """
    Returns the set of existing table names in the database.

    Returns:
        Set[str]: Set of table names that currently exist

    Usage:
        tables = await get_existing_tables()
        print(f"Existing tables: {tables}")
    """
    try:
        async with engine.connect() as conn:

            def get_tables(connection):
                inspector = inspect(connection)
                return set(inspector.get_table_names())

            return await conn.run_sync(get_tables)
    except Exception as e:
        print(f"❌ Error getting table list: {e}")
        return set()


async def check_tables_exist() -> bool:
    """
    Checks if all required tables exist in the database.

    Returns:
        bool: True if all required tables exist, False otherwise

    Usage:
        all_exist = await check_tables_exist()
        if not all_exist:
            await create_tables()
    """
    required_tables = {"seller", "customer", "product", "order", "order_product"}

    try:
        existing_tables = await get_existing_tables()
        missing_tables = required_tables - existing_tables

        if not missing_tables:
            print("✅ All required tables exist")
            return True
        else:
            print(f"⚠️  Missing tables: {', '.join(sorted(missing_tables))}")
            return False

    except Exception as e:
        print(f"❌ Error checking tables: {e}")
        return False


async def init_db(force_recreate: bool = False, auto_seed: bool = False) -> None:
    """
    Initialize the database: test connection and create tables if needed.

    This is a convenience function that combines connection test and table creation.
    Safe to call multiple times - won't recreate existing tables unless force_recreate=True.

    Args:
        force_recreate: If True, drops and recreates all tables (DELETES ALL DATA!)
        auto_seed: If True, populates database with sample data after creation

    Raises:
        Exception: If connection fails or table creation fails

    Usage:
        # Normal initialization (safe)
        await init_db()

        # Force recreate (DANGEROUS - deletes all data!)
        await init_db(force_recreate=True)

        # Create and seed with sample data
        await init_db(force_recreate=True, auto_seed=True)
    """
    print("=" * 60)
    print("🔍 Initializing database...")
    print("=" * 60)

    # Test connection
    if not await test_connection():
        raise Exception("❌ Failed to connect to database. Check your DATABASE_URL.")

    # Handle force recreate
    if force_recreate:
        print("\n⚠️  WARNING: Dropping all tables (force_recreate=True)")
        await drop_tables()
        print("\n📋 Creating tables...")
        await create_tables()
        print("✅ Database initialized with fresh tables!")

        # Seed if requested
        if auto_seed:
            from app.core.seed import seed_database

            async with AsyncSessionLocal() as db:
                await seed_database(db)

        return

    # Check if tables exist
    tables_exist = await check_tables_exist()

    if not tables_exist:
        print("\n📋 Creating missing tables...")
        await create_tables()

        # Seed if requested and tables were just created
        if auto_seed:
            from app.core.seed import seed_database

            async with AsyncSessionLocal() as db:
                await seed_database(db)
    else:
        print("ℹ️  All tables already exist, skipping creation")

    print("\n" + "=" * 60)
    print("✅ Database initialized successfully!")
    print("=" * 60)


async def close_db() -> None:
    """
    Closes all database connections and disposes of the engine.

    Should be called during application shutdown.

    Usage:
        from app.core.database import close_db
        await close_db()
    """
    await engine.dispose()
    print("🔌 Database connections closed")
