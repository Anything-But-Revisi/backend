"""
SafeSpace Backend - FastAPI Application
Main application entry point with database integration and CORS support.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <-- ADDED
from contextlib import asynccontextmanager

from app.config import validate_config, get_db_config
from app.database import (
    init_database,
    close_database,
    check_database_connection,
    get_engine,
)
from app.api.v1.sessions import router as sessions_router
from app.api.v1.chat import router as chat_router 
from app.api.v1.report import router as report_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def startup_event() -> None:
    logger.info("Starting SafeSpace backend application...")
    try:
        validate_config()
        logger.info("Configuration validated successfully")
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(1, max_retries + 1):
            try:
                await init_database()
                logger.info("Database initialized successfully")
                
                is_healthy = await check_database_connection()
                if is_healthy:
                    logger.info("Database health check passed")
                    break
                else:
                    raise Exception("Database health check failed")
                    
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Database connection attempt {attempt}/{max_retries} failed: {e}. Retrying...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to initialize database after {max_retries} attempts: {e}")
                    raise
        
        logger.info("SafeSpace backend started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


async def shutdown_event() -> None:
    logger.info("Shutting down SafeSpace backend application...")
    try:
        await close_database()
        logger.info("Database connection closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_event()
    yield
    await shutdown_event()


# Create FastAPI application
app = FastAPI(
    title="SafeSpace Backend",
    description="Secure anonymous chatbot backend with PostgreSQL persistence",
    version="1.0.0",
    lifespan=lifespan,
)

# --- CORS MIDDLEWARE CONFIGURATION ---
# Mengizinkan frontend untuk mengakses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Untuk hackathon, kita izinkan semua agar cepat. 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(report_router, prefix="/api/v1")


@app.get("/")
async def read_root() -> Dict[str, str]:
    return {"message": "SafeSpace backend is running", "version": "1.0.0"}


@app.get("/health/db")
async def health_check_db() -> Dict[str, Any]:
    logger.info("Database health check requested")
    try:
        is_healthy = await asyncio.wait_for(
            check_database_connection(),
            timeout=10.0
        )
        
        if not is_healthy:
            raise HTTPException(status_code=503, detail="Database query failed")
        
        engine = get_engine()
        pool = engine.pool
        pool_info = {"total": pool.size(), "available": pool.checkedout()} if hasattr(pool, "size") else "unknown"
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "connection_pool": pool_info,
        }
    except Exception as e:
        logger.error(f"Database health check error: {e}")
        raise HTTPException(status_code=503, detail=str(e))