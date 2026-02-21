"""
Database connection management module for SafeSpace.
Handles connection pool initialization, management, and cleanup.
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import text

from app.config import get_db_config

# --- PINDAHKAN IMPORT INI KE SINI (DI LUAR FUNGSI) ---
# Memastikan semua model terdaftar di Base.metadata sebelum aplikasi menyala
from app.models.session import Base, Session
from app.models.message import Message 
from app.models.report import Report
# -----------------------------------------------------

logger = logging.getLogger(__name__)

# Global database engine instance
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


async def init_database() -> None:
    """
    Initialize the database connection pool.
    Called during application startup.
    Creates the async engine and session factory.
    """
    global _engine, _session_factory
    
    if _engine is not None:
        logger.warning("Database already initialized")
        return
    
    try:
        db_config = get_db_config()
        database_url = db_config.get_database_url()
        pool_config = db_config.get_pool_config()
        
        logger.info(f"Initializing database connection pool to {db_config.get_sanitized_url()}")
        
        # Create async engine with connection pooling
        _engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            poolclass=QueuePool,
            pool_size=pool_config["min_size"],
            max_overflow=pool_config["max_size"] - pool_config["min_size"],
            pool_timeout=db_config.connection_timeout,
            pool_pre_ping=True,  # Test connections before using them
            pool_recycle=3600,  # Recycle connections after 1 hour
            connect_args={
                "timeout": db_config.connection_timeout,
                "command_timeout": db_config.query_timeout,
            },
        )
        
        # Create session factory
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        # --- HAPUS IMPORT LOKAL DI SINI KARENA SUDAH DIPINDAH KE ATAS ---
        # (Cukup jalankan create_all saja)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created/verified successfully")
            
        logger.info("Database connection pool initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database() -> None:
    """
    Close the database connection pool.
    Called during application shutdown.
    Properly disposes of all connections.
    """
    global _engine, _session_factory
    
    if _engine is None:
        logger.warning("Database was not initialized")
        return
    
    try:
        logger.info("Closing database connection pool")
        await _engine.dispose()
        _engine = None
        _session_factory = None
        logger.info("Database connection pool closed successfully")
    except Exception as e:
        logger.error(f"Error closing database: {e}")
        raise


def get_engine() -> AsyncEngine:
    """
    Get the global database engine instance.
    Raises RuntimeError if database is not initialized.
    """
    if _engine is None:
        raise RuntimeError(
            "Database engine not initialized. Call init_database() during startup."
        )
    return _engine


def get_session_factory() -> async_sessionmaker:
    """
    Get the global session factory instance.
    Raises RuntimeError if database is not initialized.
    """
    if _session_factory is None:
        raise RuntimeError(
            "Session factory not initialized. Call init_database() during startup."
        )
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for acquiring a database session.
    Automatically handles session creation, cleanup, and error handling.
    
    Usage:
        async with get_db_session() as session:
            result = await session.execute(query)
    """
    if _session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_database() during startup."
        )
    
    async_session = _session_factory()
    try:
        yield async_session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await async_session.rollback()
        raise
    finally:
        await async_session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session injection.
    
    Usage in route:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(query)
    """
    async with get_db_session() as session:
        yield session


async def check_database_connection() -> bool:
    """
    Check if the database connection is working.
    Returns True if connection is successful, False otherwise.
    Used for health checks.
    """
    if _engine is None:
        logger.warning("Database engine not initialized")
        return False
    
    try:
        async with _engine.connect() as connection:
            # Execute a simple query to verify connection using text()
            await connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False