# Design: PostgreSQL Connection Setup

## Context

SafeSpace is a FastAPI-based backend application that requires persistent storage for anonymous user chatbot sessions. Currently, the application has no database integration. We need to establish a PostgreSQL connection layer that is:
- Secure (no hardcoded credentials)
- Efficient (connection pooling)
- Reliable (health checks and proper initialization)
- Production-ready for session persistence

The application structure includes `app/main.py` as the entry point and will need new modules for configuration and database management.

## Goals / Non-Goals

**Goals:**
- Establish a secure PostgreSQL connection using environment-based configuration
- Implement connection pooling to efficiently manage database resources
- Create health check mechanisms to verify database availability on startup and runtime
- Provide a clean, reusable database session interface for the FastAPI application
- Support graceful connection cleanup on application shutdown

**Non-Goals:**
- Creating database schemas or tables (handled in separate specs)
- ORM model definitions (handled in separate specs)
- User authentication or authorization logic
- Data migration from other sources

## Decisions

### Decision 1: Async PostgreSQL Driver
**Choice**: Use `asyncpg` instead of `psycopg2-binary`

**Rationale**: 
- `asyncpg` is async-native and integrates seamlessly with FastAPI's async/await model
- Provides better performance with connection pooling
- Non-blocking I/O prevents thread context switching overhead

**Alternative Considered**:
- `psycopg2-binary` with thread pooling: Simpler but blocks threads and less efficient

### Decision 2: SQLAlchemy for Connection Management
**Choice**: Use SQLAlchemy Core (not ORM) with `create_async_engine` for connection pooling

**Rationale**:
- Built-in connection pooling with configurable pool size
- Proper resource management and connection recycling
- Can upgrade to ORM later if needed without refactoring connection logic

**Alternative Considered**:
- Raw asyncpg pool: More control but requires manual connection management

### Decision 3: Environment Configuration
**Choice**: Use `python-dotenv` to load `.env` file with explicit environment variable requirements

**Rationale**:
- Simple, standard approach for environment-based configuration
- `.env` stored locally, not committed to git (added to `.gitignore`)
- Clear documentation of required environment variables
- Production uses actual environment variables

**Alternative Considered**:
- Pydantic Settings: More complex, unnecessary for this use case

### Decision 4: Health Check Endpoint
**Choice**: Create `/health/db` endpoint that queries database connectivity

**Rationale**:
- Allows monitoring systems to verify database availability
- Separate from general `/health` endpoint for granular monitoring
- Lightweight query (e.g., `SELECT 1`) to minimize overhead

**Alternative Considered**:
- Check only on startup: Doesn't detect runtime disconnections

## Risks / Trade-offs

**Risk 1: Connection Pool Exhaustion**
- **Problem**: Rapid requests could exhaust connection pool if connections aren't released
- **Mitigation**: Configure appropriate pool size, implement query timeouts, use context managers for connection handling

**Risk 2: .env File Exposure**
- **Problem**: Developer accidentally commits .env file with credentials
- **Mitigation**: Pre-commit hooks, clear .gitignore rules, documentation on environment setup

**Risk 3: Database Connection During Startup**
- **Problem**: Application fails if database is unavailable at startup
- **Mitigation**: Implement retry logic with exponential backoff, clear error messages in logs

**Trade-off 1: asyncpg Learning Curve**
- **Trade**: Team needs to learn asyncpg API vs psycopg2
- **Worth It Because**: Performance gains and async/await consistency outweigh learning curve

**Trade-off 2: Configuration Complexity**
- **Trade**: More configuration steps for developers vs hardcoding
- **Worth It Because**: Security benefits are critical for production

## Migration Plan

1. **Phase 1 - Setup** (this change):
   - Create configuration module with environment variable management
   - Set up SQLAlchemy async engine with connection pool
   - Implement health check endpoint

2. **Phase 2 - Integration** (follow-up change):
   - Add database session dependency injection to FastAPI
   - Create database initialization scripts
   - Integrate with session management system

3. **Phase 3 - Testing**:
   - Integration tests with test database
   - Connection pool behavior tests

**Deployment Steps**:
1. Ensure PostgreSQL server is running and accessible
2. Set required environment variables (host, port, database, username, password)
3. Deploy application - connection pool initializes on startup
4. Verify health check endpoint returns 200 OK
5. Rollback: Set environment variable to previous database or use database replica

## Open Questions

- What pool size should we start with? (Suggestion: 10-20 connections)
- Should we implement connection timeout / idle timeout settings initially?
- Do we need separate read/write connection pools, or is one pool sufficient?
- What logging level for database connection events?
