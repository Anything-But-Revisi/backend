"""
Unit tests for configuration module.
Tests environment variable loading, validation, and credential handling.
"""

import os
import pytest
from unittest.mock import patch

from app.config import (
    DatabaseConfig,
    AppConfig,
    get_db_config,
    get_app_config,
    validate_config,
)


class TestDatabaseConfig:
    """Tests for DatabaseConfig class."""
    
    def test_valid_config_loading(self):
        """Test that valid configuration loads without errors."""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
        }):
            # Clear cache
            get_db_config.cache_clear()
            config = get_db_config()
            
            assert config.host == "localhost"
            assert config.port == 5432
            assert config.name == "testdb"
            assert config.user == "testuser"
            assert config.password == "testpass"
    
    def test_missing_required_field(self):
        """Test that missing required fields raise ValueError."""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            # Missing DB_PASSWORD
        }, clear=True):
            get_db_config.cache_clear()
            with pytest.raises(ValueError, match="Missing required environment variables"):
                DatabaseConfig()
    
    def test_default_values(self):
        """Test that default values are applied when not provided."""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
        }):
            get_db_config.cache_clear()
            config = get_db_config()
            
            assert config.pool_min_size == 10  # default
            assert config.pool_max_size == 20  # default
            assert config.query_timeout == 30  # default
            assert config.connection_timeout == 10  # default
    
    def test_get_database_url(self):
        """Test that database URL is correctly formatted."""
        with patch.dict(os.environ, {
            "DB_HOST": "db.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
        }):
            get_db_config.cache_clear()
            config = get_db_config()
            
            url = config.get_database_url()
            assert url == "postgresql+asyncpg://testuser:testpass@db.example.com:5432/testdb"
    
    def test_get_sanitized_url(self):
        """Test that password is masked in sanitized URL."""
        with patch.dict(os.environ, {
            "DB_HOST": "db.example.com",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "supersecretpassword",
        }):
            get_db_config.cache_clear()
            config = get_db_config()
            
            sanitized = config.get_sanitized_url()
            assert "supersecretpassword" not in sanitized
            assert "***" in sanitized
            assert "testuser" in sanitized
            assert "db.example.com" in sanitized
    
    def test_get_pool_config(self):
        """Test that pool configuration is correctly returned."""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
            "DB_POOL_MIN_SIZE": "5",
            "DB_POOL_MAX_SIZE": "25",
            "DB_CONNECTION_TIMEOUT": "15",
        }):
            get_db_config.cache_clear()
            config = get_db_config()
            pool_config = config.get_pool_config()
            
            assert pool_config["min_size"] == 5
            assert pool_config["max_size"] == 25
            assert pool_config["command_timeout"] == 15


class TestAppConfig:
    """Tests for AppConfig class."""
    
    def test_default_app_config(self):
        """Test that AppConfig loads with defaults."""
        with patch.dict(os.environ, {}, clear=True):
            get_app_config.cache_clear()
            config = get_app_config()
            
            assert config.environment == "development"
            assert config.host == "0.0.0.0"
            assert config.port == 8000
            assert config.log_level == "INFO"
            assert config.debug is True
    
    def test_custom_app_config(self):
        """Test that custom AppConfig values are loaded."""
        with patch.dict(os.environ, {
            "ENVIRONMENT": "production",
            "APP_HOST": "127.0.0.1",
            "APP_PORT": "9000",
            "LOG_LEVEL": "DEBUG",
        }):
            get_app_config.cache_clear()
            config = get_app_config()
            
            assert config.environment == "production"
            assert config.host == "127.0.0.1"
            assert config.port == 9000
            assert config.log_level == "DEBUG"
            assert config.debug is False  # not development


class TestConfigValidation:
    """Tests for configuration validation."""
    
    def test_validate_config_success(self):
        """Test that validation passes with valid config."""
        with patch.dict(os.environ, {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "testdb",
            "DB_USER": "testuser",
            "DB_PASSWORD": "testpass",
        }):
            get_db_config.cache_clear()
            get_app_config.cache_clear()
            
            result = validate_config()
            assert result is True
    
    def test_validate_config_failure(self):
        """Test that validation fails with missing config."""
        with patch.dict(os.environ, {}, clear=True):
            get_db_config.cache_clear()
            get_app_config.cache_clear()
            
            with pytest.raises(ValueError):
                validate_config()
