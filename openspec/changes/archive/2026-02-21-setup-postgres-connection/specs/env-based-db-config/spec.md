# Specification: Environment-Based Database Configuration

## ADDED Requirements

### Requirement: Environment Variable Configuration for Database Credentials
The system SHALL read database credentials from environment variables instead of hardcoding them.

#### Scenario: Load database host from environment
- **WHEN** application starts
- **THEN** database host is loaded from `DB_HOST` environment variable

#### Scenario: Load database port from environment
- **WHEN** application starts
- **THEN** database port is loaded from `DB_PORT` environment variable

#### Scenario: Load database name from environment
- **WHEN** application starts
- **THEN** database name is loaded from `DB_NAME` environment variable

#### Scenario: Load database username from environment
- **WHEN** application starts
- **THEN** database username is loaded from `DB_USER` environment variable

#### Scenario: Load database password from environment
- **WHEN** application starts
- **THEN** database password is loaded from `DB_PASSWORD` environment variable

### Requirement: .env File Support
The system SHALL support loading environment variables from a .env file in the project root directory during development.

#### Scenario: Load .env file on startup
- **WHEN** the application starts in development mode
- **THEN** environment variables from `.env` file are loaded into the process environment

#### Scenario: .env file not in production
- **WHEN** application runs in production
- **THEN** environment variables are read from actual OS/container environment (not from .env file)

#### Scenario: Missing .env file in development
- **WHEN** .env file is not present
- **THEN** application falls back to OS environment variables

### Requirement: Validation of Required Credentials
The system SHALL validate that all required database credentials are provided.

#### Scenario: Missing required environment variable
- **WHEN** a required environment variable (DB_HOST, DB_USER, DB_PASSWORD, etc.) is missing
- **THEN** application fails with a clear error message indicating which variable is missing

#### Scenario: Invalid environment variable format
- **WHEN** an environment variable has invalid format (e.g., port is not a number)
- **THEN** application fails with a clear error message during startup

#### Scenario: All required credentials present
- **WHEN** all required environment variables are properly configured
- **THEN** database connection can be established

### Requirement: Sensitive Credential Protection
The system SHALL protect sensitive credentials from exposure in logs and error messages.

#### Scenario: Password not logged
- **WHEN** database operations are logged
- **THEN** database password never appears in plain text in logs

#### Scenario: Connection string sanitized in errors
- **WHEN** a connection error occurs
- **THEN** error message displays sanitized connection string without password

### Requirement: Configuration Module API
The system SHALL provide a clean API for accessing configuration values in the application.

#### Scenario: Get database URL from config
- **WHEN** application code needs the database connection URL
- **THEN** config module provides `get_database_url()` function returning valid connection string

#### Scenario: Get pool settings from config
- **WHEN** application code needs pool configuration
- **THEN** config module provides `get_pool_config()` function returning pool settings as dict
