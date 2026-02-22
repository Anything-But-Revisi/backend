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
from sqlalchemy.pool import QueuePool
from sqlalchemy import text

from app.config import get_db_config

# Import model agar terdaftar di Base.metadata sebelum aplikasi menyala
from app.models.session import Base, Session
from app.models.message import Message 
from app.models.report import Report

logger = logging.getLogger(__name__)

# Global database engine instance
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker] = None


async def init_database() -> None:
    """
    Initialize the database connection pool.
    Slightly modified to handle table creation errors gracefully.
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
        
        # Inisialisasi engine dengan pool configuration sesuai ConfigMap
        _engine = create_async_engine(
            database_url,
            echo=False,
            poolclass=QueuePool,
            pool_size=pool_config["min_size"],
            max_overflow=pool_config["max_size"] - pool_config["min_size"],
            pool_timeout=db_config.connection_timeout,
            pool_pre_ping=True,  # Memastikan koneksi sehat sebelum digunakan
            pool_recycle=3600,
            connect_args={
                "timeout": db_config.connection_timeout,
                "command_timeout": db_config.query_timeout,
            },
        )
        
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
        
        # Menangani pembuatan tabel dengan Try-Except agar tidak memicu CrashLoopBackOff
        # jika user database tidak memiliki izin CREATE
        try:
            async with _engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables verified successfully")
        except Exception as table_err:
            logger.warning(f"Skipping table creation/verification: {table_err}")
            
        logger.info("Database connection pool initialized successfully")
        
    except Exception as e:
        logger.error(f"Critical error during database initialization: {e}")
        raise


async def close_database() -> None:
    """
    Close the database connection pool during application shutdown.
    """
    global _engine, _session_factory
    
    if _engine is None:
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
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


def get_session_factory() -> async_sessionmaker:
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized")
    return _session_factory


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager untuk memastikan session selalu ditutup (mencegah pool exhaustion).
    """
    if _session_factory is None:
        raise RuntimeError("Database not initialized")
    
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
    Dependency injection untuk FastAPI routes.
    """
    async with get_db_session() as session:
        yield session


# async def check_database_connection() -> bool:
#     """
#     Fungsi krusial untuk Liveness/Readiness probe di Kubernetes.
#     """
#     if _engine is None:
#         return False
    
#     try:
#         async with _engine.connect() as connection:
#             await connection.execute(text("SELECT 1"))
#             return True
#     except Exception as e:
#         logger.error(f"Database health check failed: {e}")
#         return False