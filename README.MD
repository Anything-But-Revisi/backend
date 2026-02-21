# BACKEND - HACKTON

SafeSpace backend - Secure anonymous chatbot with PostgreSQL persistence

## Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- Virtual environment tools

### Setup Instructions

1. **Activate virtual environment:**
   - Windows PowerShell: `.\\.venv\\Scripts\\Activate.ps1`
   - macOS/Linux bash: `source .venv/bin/activate`

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database:**
   - Copy `.env.example` to `.env`
   - Edit `.env` with your PostgreSQL credentials
   - Ensure PostgreSQL is running locally or update `DB_HOST` if remote
   
   See [SETUP.md](SETUP.md) for detailed database configuration

4. **Run the server:**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

5. **Test the application:**
   - Main endpoint: `http://127.0.0.1:8000/`
   - Health check: `http://127.0.0.1:8000/health/db`
   - API documentation: `http://127.0.0.1:8000/docs`

## Database Setup

The application uses PostgreSQL for persistent storage. 

**Quick database setup (development):**
```bash
# Create database and user
psql -U postgres -c "CREATE DATABASE safespace_dev;"
psql -U postgres -c "CREATE USER safespace_dev WITH PASSWORD 'your_password';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE safespace_dev TO safespace_dev;"

# Update .env with credentials
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=safespace_dev
# DB_USER=safespace_dev
# DB_PASSWORD=your_password
```

For detailed setup instructions including production deployment, see [SETUP.md](SETUP.md)

## Health Check

Verify database connectivity:
```bash
curl http://localhost:8000/health/db
```

Response when healthy:
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2026-02-21T10:30:45.123456",
  "connection_pool": {
    "total": 20,
    "available": 18
  }
}
```

## Anonymous Sessions API

Create and manage anonymous user sessions with UUID4 identifiers:

### Create Session
```bash
POST /api/v1/sessions
```
Response (201):
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-21T10:30:45.123456"
}
```

### Delete Session
```bash
DELETE /api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
```
Response (204): No content

See [SESSIONS.md](SESSIONS.md) for detailed session API documentation, architecture, and security considerations.

## Project Structure

```
app/
  main.py                - FastAPI application with health check endpoints
  config.py              - Environment configuration and database credentials management
  database.py            - PostgreSQL connection pool and session management
  models/
    session.py           - Anonymous session SQLAlchemy ORM model (UUID pk)
  schemas/
    session.py           - Pydantic validation schemas for sessions
  api/
    v1/
      sessions.py        - FastAPI session endpoints (POST create, DELETE remove)
tests/
  test_config.py         - Configuration module tests
  test_database.py       - Database integration tests  
  test_health_check.py   - Health endpoint tests
  test_session_model.py  - Session ORM model tests
  test_session_schemas.py - Session Pydantic schema tests
  test_session_endpoints.py - Session API endpoint tests
.env.example             - Environment variable template (copy to .env)
SETUP.md                 - Detailed database setup and troubleshooting guide
SESSIONS.md              - Anonymous session system documentation
requirements.txt         - Python dependencies
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_config.py
```

## Environment Variables

See `.env.example` for all available options. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | localhost | PostgreSQL host |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | safespace_dev | Database name |
| `DB_USER` | postgres | Database username |
| `DB_PASSWORD` | (required) | Database password |
| `DB_POOL_MIN_SIZE` | 10 | Min connection pool size |
| `DB_POOL_MAX_SIZE` | 20 | Max connection pool size |
| `APP_HOST` | 0.0.0.0 | Application listen address |
| `APP_PORT` | 8000 | Application port |

## Current Features

- ✅ FastAPI framework setup
- ✅ PostgreSQL async connection pool
- ✅ Environment-based configuration with `.env` support
- ✅ Health check endpoint (`/health/db`)
- ✅ Secure credential management (no hardcoded passwords)
- ✅ Connection pooling with configurable sizes
- ✅ Automatic startup/shutdown connection lifecycle
- ✅ Comprehensive logging and error handling
- ✅ Anonymous session management (UUID4 identifiers, privacy-first design)
- ✅ Session creation endpoint (`POST /api/v1/sessions`)
- ✅ Session deletion endpoint (`DELETE /api/v1/sessions/{session_id}`)
- ✅ Hard delete strategy (permanent user data removal)

## Troubleshooting

For database connection issues, see [SETUP.md - Troubleshooting section](SETUP.md#troubleshooting)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy AsyncIO](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
