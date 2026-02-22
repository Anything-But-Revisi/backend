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

## Sexual Violence Report Generation API

Generate formal Sexual Violence Complaint Forms (FORMULIR PENGADUAN KEKERASAN SEKSUAL) from structured incident data using Gemini LLM integration.

### Create Report
```bash
POST /api/v1/sessions/{session_id}/report

{
  "location": "kampus",
  "perpetrator": "lecturer",
  "description": "inappropriate comments",
  "evidence": "witness",
  "user_goal": "document safely"
}
```

Response (201):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "location": "kampus",
  "perpetrator": "lecturer",
  "description": "inappropriate comments",
  "evidence": "witness",
  "user_goal": "document safely",
  "generated_document": "## FORMULIR PENGADUAN KEKERASAN SEKSUAL\n\n### I. IDENTIFIKASI KEBUTUHAN\n...",
  "created_at": "2026-02-21T10:30:45.123456"
}
```

**Request Fields (Enums):**
- `location`: "public space" | "online" | "kampus" | "sekolah" | "workplace"
- `perpetrator`: "supervisor" | "colleague" | "lecturer" | "client" | "stranger"
- `description`: "inappropriate comments" | "unwanted physical touch" | "repeated pressure" | "threat or coercion" | "digital harassment"
- `evidence`: "messages" | "emails" | "witness" | "none"
- `user_goal`: "understand the risk" | "document safely" | "consider reporting" | "explore options"

### Retrieve Report
```bash
GET /api/v1/sessions/{session_id}/report
```

Response (200):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "location": "kampus",
  "perpetrator": "lecturer",
  "description": "inappropriate comments",
  "evidence": "witness",
  "user_goal": "document safely",
  "generated_document": "## FORMULIR PENGADUAN KEKERASAN SEKSUAL\n...",
  "created_at": "2026-02-21T10:30:45.123456"
}
```

**Notes:**
- Reports are scoped to sessions and automatically deleted when parent session is deleted (cascade delete)
- If Gemini report generation fails, report data is preserved with `generated_document=null` (POST returns 500)
- Generated reports use fixed structure: I. Identifikasi Kebutuhan, II. Identifikasi Pelaku, III. Kronologi Kejadian, IV. Bukti Terlampir
- Reports are generated in Indonesian using first-person narrative perspective

## Project Structure

```
app/
  main.py                - FastAPI application with health check and router registration
  config.py              - Environment configuration and database credentials management
  database.py            - PostgreSQL connection pool and session management
  models/
    session.py           - Anonymous session SQLAlchemy ORM model (UUID pk)
    report.py            - Sexual violence incident report SQLAlchemy ORM model
  schemas/
    session.py           - Pydantic validation schemas for sessions
    report.py            - Pydantic validation schemas for reports with Enum fields
  services/
    report.py            - Report generation service using Gemini LLM
  api/
    v1/
      sessions.py        - FastAPI session endpoints (POST create, DELETE remove)
      report.py          - FastAPI report endpoints (POST create, GET retrieve)
tests/
  test_config.py         - Configuration module tests
  test_database.py       - Database integration tests  
  test_health_check.py   - Health endpoint tests
  test_session_model.py  - Session ORM model tests
  test_session_schemas.py - Session Pydantic schema tests
  test_session_endpoints.py - Session API endpoint tests
  test_report_model.py   - Report ORM model and relationship tests
  test_report_schemas.py - Report Pydantic schema and Enum validation tests
  test_report_service.py - Report generation service tests with mocked Gemini API
  test_report_endpoints.py - Report API endpoint integration tests
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
| `GOOGLE_API_KEY` | (required for reports) | Google Generative AI API key for Gemini LLM integration |

**Important:** To enable report generation, set `GOOGLE_API_KEY` environment variable with your Gemini API credentials from [Google AI Studio](https://ai.google.dev/)

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
- ✅ Sexual violence report generation using Gemini LLM
- ✅ Report creation with structured incident data (location, perpetrator, description, evidence, user_goal Enums)
- ✅ Automatic generation of formal complaint form narratives in Indonesian
- ✅ Report retrieval endpoint (`GET /api/v1/sessions/{session_id}/report`)
- ✅ Session-scoped report management with cascade delete
- ✅ Nullable generated_document field for resilience on LLM failures

## Troubleshooting

For database connection issues, see [SETUP.md - Troubleshooting section](SETUP.md#troubleshooting)

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy AsyncIO](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
