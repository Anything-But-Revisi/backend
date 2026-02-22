"""
Configuration module for SafeSpace backend.
Handles environment variables and application settings.
"""

import os
import logging
from typing import Optional, Dict
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file (if it exists)
load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration from environment variables."""
    
    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "5432"))
        self.name = os.getenv("DB_NAME", "safespace_dev")
        self.user = os.getenv("DB_USER", "postgres")
        self.password = os.getenv("DB_PASSWORD", "")
        self.pool_min_size = int(os.getenv("DB_POOL_MIN_SIZE", "10"))
        self.pool_max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))
        self.query_timeout = int(os.getenv("DB_QUERY_TIMEOUT", "30"))
        self.connection_timeout = int(os.getenv("DB_CONNECTION_TIMEOUT", "10"))
        
        # Validate required credentials
        self._validate_credentials()
    
    def _validate_credentials(self) -> None:
        """Validate that all required database credentials are set."""
        required_fields = {
            "DB_HOST": self.host,
            "DB_PORT": str(self.port),
            "DB_NAME": self.name,
            "DB_USER": self.user,
            "DB_PASSWORD": self.password,
        }
        
        missing_fields = [key for key, value in required_fields.items() if not value]
        
        if missing_fields:
            error_msg = f"Missing required environment variables: {', '.join(missing_fields)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def get_database_url(self) -> str:
        """
        Build the PostgreSQL database URL for async connections.
        Returns URL in format: postgresql+asyncpg://user:password@host:port/database
        """
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.name}"
        )
    
    def get_sanitized_url(self) -> str:
        """
        Get database URL with password masked for logging/error messages.
        Returns URL with password replaced with asterisks.
        """
        return (
            f"postgresql+asyncpg://{self.user}:***@"
            f"{self.host}:{self.port}/{self.name}"
        )
    
    def get_pool_config(self) -> Dict[str, int]:
        """
        Get connection pool configuration as a dictionary.
        Returns dict with min_size and max_size.
        """
        return {
            "min_size": self.pool_min_size,
            "max_size": self.pool_max_size,
            "command_timeout": self.connection_timeout,
        }


class AppConfig:
    """Application-level configuration."""
    
    def __init__(self):
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.host = os.getenv("APP_HOST", "0.0.0.0")
        self.port = int(os.getenv("APP_PORT", "8000"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.debug = self.environment == "development"


class GeminiConfig:
    """Google Generativeai API configuration."""
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", "")
        self._validate_api_key()
    
    def _validate_api_key(self) -> None:
        """
        Validate that GOOGLE_API_KEY is set.
        Logs warning if missing, but doesn't block application startup
        (chat endpoints will return 503 if key is missing).
        """
        if not self.api_key:
            logger.warning(
                "GOOGLE_API_KEY not configured. "
                "Chat endpoints will be unavailable. "
                "Set GOOGLE_API_KEY environment variable to enable Gemini integration."
            )
    
    def is_configured(self) -> bool:
        """Check if API key is configured and available."""
        return bool(self.api_key)


@lru_cache(maxsize=1)
def get_db_config() -> DatabaseConfig:
    """
    Get database configuration singleton.
    Uses caching to ensure config is loaded only once.
    """
    return DatabaseConfig()


@lru_cache(maxsize=1)
def get_app_config() -> AppConfig:
    """
    Get application configuration singleton.
    Uses caching to ensure config is loaded only once.
    """
    return AppConfig()


@lru_cache(maxsize=1)
def get_gemini_config() -> GeminiConfig:
    """
    Get Gemini API configuration singleton.
    Uses caching to ensure config is loaded only once.
    """
    return GeminiConfig()


def validate_config() -> bool:
    """
    Validate all configuration on startup.
    Returns True if all configuration is valid.
    Raises exceptions if configuration is invalid.
    """
    try:
        get_db_config()
        get_app_config()
        get_gemini_config()  # Validate but don't fail if missing (graceful degradation)
        logger.info("Configuration validation passed")
        return True
    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        raise
