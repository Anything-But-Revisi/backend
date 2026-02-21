"""
SafeSpace Backend - FastAPI Application
Main application entry point with database integration.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager

from app.config import validate_config, get_db_config
from app.database import (
    init_database,
    close_database,
    check_database_connection,
    get_engine,
)
from app.api.v1.sessions import router as sessions_router
from app.api.v1.chat import router as chat_router  # <--- IMPORT ROUTER CHAT DITAMBAHKAN DI SINI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def startup_event() -> None:
    """
    Application startup event handler.
    Validates configuration and initializes database connection.
    """
    logger.info("Starting SafeSpace backend application...")
    
    try:
        # Validate configuration
        validate_config()
        logger.info("Configuration validated successfully")
        
        # Initialize database with retry logic
        max_retries = 3
        retry_delay = 1  # Start with 1 second
        
        for attempt in range(1, max_retries + 1):
            try:
                await init_database()
                logger.info("Database initialized successfully")
                
                # Verify database connection
                is_healthy = await check_database_connection()
                if is_healthy:
                    logger.info("Database health check passed")
                    break
                else:
                    raise Exception("Database health check failed")
                    
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(
                        f"Database connection attempt {attempt}/{max_retries} failed: {e}. "
                        f"Retrying in {retry_delay} seconds..."
                    )
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(
                        f"Failed to initialize database after {max_retries} attempts: {e}"
                    )
                    raise
        
        logger.info("SafeSpace backend started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


async def shutdown_event() -> None:
    """
    Application shutdown event handler.
    Properly closes database connections.
    """
    logger.info("Shutting down SafeSpace backend application...")
    
    try:
        await close_database()
        logger.info("Database connection closed successfully")
        logger.info("SafeSpace backend shut down gracefully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    await startup_event()
    yield
    # Shutdown
    await shutdown_event()


# Create FastAPI application with lifespan handler
app = FastAPI(
    title="SafeSpace Backend",
    description="Secure anonymous chatbot backend with PostgreSQL persistence",
    version="1.0.0",
    lifespan=lifespan,
)

# Include API routers
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")  # <--- ROUTER CHAT DIDAFTARKAN DI SINI


@app.get("/")
async def read_root() -> Dict[str, str]:
    """Root endpoint - health indicator."""
    return {"message": "SafeSpace backend is running", "version": "1.0.0"}


@app.get("/health/db")
async def health_check_db() -> Dict[str, Any]:
    """
    Database health check endpoint.
    Verifies database connectivity and returns connection pool status.
    
    Returns:
        - status: "healthy" if database is accessible, "unhealthy" otherwise
        - database: "connected" or "disconnected"
        - timestamp: ISO format timestamp
        - connection_pool: Current pool statistics
        - error: (optional) Error message if unhealthy
    """
    logger.info("Database health check requested")
    
    try:
        # Try to get connection with timeout (diperpanjang menjadi 10 detik)
        is_healthy = await asyncio.wait_for(
            check_database_connection(),
            timeout=10.0  # <--- SUDAH DIPERBARUI
        )
        
        if not is_healthy:
            logger.warning("Database health check failed")
            raise HTTPException(
                status_code=503,
                detail={
                    "status": "unhealthy",
                    "database": "disconnected",
                    "error": "Database query failed",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
        
        # Get engine for pool info
        engine = get_engine()
        pool = engine.pool
        
        # Check pool status
        if hasattr(pool, "size"):
            pool_info = {
                "total": pool.size(),
                "available": pool.checkedout(),
            }
        else:
            pool_info = {
                "total": "unknown",
                "available": "unknown",
            }
        
        response = {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "connection_pool": pool_info,
        }
        
        logger.info("Database health check passed")
        return response
        
    except asyncio.TimeoutError:
        logger.error("Database health check timed out")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": "Health check query timeout (> 10 seconds)", # <--- SUDAH DIPERBARUI
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )