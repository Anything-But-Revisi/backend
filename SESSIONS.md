# Anonymous Sessions Implementation Guide

## Overview

This document describes the implementation of the anonymous sessions system for SafeSpace backend. The system provides privacy-first session management using UUID4 identifiers and hard delete capability for user data removal.

## Architecture

### Database Layer

**Session Model** (`app/models/session.py`):
- UUID4 primary key (non-sequential, cryptographically random)
- Created timestamp (UTC)
- Minimal data model (zero PII - privacy-first design)
- SQLAlchemy ORM with PostgreSQL support

```python
class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### API Layer

**Endpoints** (`app/api/v1/sessions.py`):

1. **POST /api/v1/sessions** - Create Session
   - Status: 201 Created
   - Request: Empty body (or `{}`)
   - Response: `{session_id: UUID, created_at: datetime}`
   - Generates UUID4 and persists to database

2. **DELETE /api/v1/sessions/{session_id}** - Delete Session
   - Status: 204 No Content
   - Hard delete (permanent, irreversible)
   - User control over data removal (panic button)
   - Returns 404 if session not found

### Validation Layer

**Pydantic Schemas** (`app/schemas/session.py`):

- `SessionCreate`: Empty schema for POST requests
- `SessionResponse`: Response model with `session_id` (UUID) and `created_at` (datetime)
- `from_model()`: Converts ORM models to API responses

## API Documentation

### Create Session

```bash
curl -X POST http://localhost:8000/api/v1/sessions
```

**Response (201)**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-02-21T10:30:45.123456"
}
```

**Error Responses**:
- `503 Service Unavailable`: Database connection failed

### Delete Session

```bash
curl -X DELETE http://localhost:8000/api/v1/sessions/550e8400-e29b-41d4-a716-446655440000
```

**Response (204)**: No content

**Error Responses**:
- `404 Not Found`: Session doesn't exist
- `422 Unprocessable Entity`: Invalid UUID format
- `503 Service Unavailable`: Database connection failed

## Feature Implementation

### Privacy-First Design

1. **UUID4 Identifiers**: Non-sequential, cryptographically random
   - Prevents client-side prediction
   - No information leakage about session count/order
   - Follows industry standard for anonymous systems

2. **Minimal Data Model**: Only 2 columns (id, created_at)
   - No PII stored (names, emails, IP addresses, etc.)
   - No chat history in core session model
   - Easy to understand data retention

3. **Hard Delete Strategy**: Permanent, irreversible removal
   - User control over data via POST /api/v1/sessions/{id}
   - No soft deletes (recovery not possible)
   - Panic button for immediate data removal
   - Clear deletion guarantees

### Error Handling

- **404 Not Found**: Returned when session doesn't exist in delete requests
- **422 Unprocessable Entity**: Invalid UUID format (FastAPI auto-validation)
- **503 Service Unavailable**: Database connection failures
- All errors logged with appropriate severity (INFO, WARNING, ERROR)

### Logging

Session operations logged at appropriate levels:
- **DEBUG**: Operation start (`Creating new session...`, `Deleting session...`)
- **INFO**: Successful operations (`Session created successfully`, `Session deleted successfully`)
- **WARNING**: Resource not found (`Session not found for deletion`)
- **ERROR**: Exception details (`Failed to create/delete session`, `Database unavailable`)

## Integration

### FastAPI Setup

Sessions router registered in `app/main.py`:

```python
from app.api.v1.sessions import router as sessions_router

app.include_router(sessions_router, prefix="/api/v1")
```

This makes endpoints available at `/api/v1/sessions` and `/api/v1/sessions/{session_id}`.

### Database Integration

- Uses existing AsyncSession dependency from `app/database.get_db()`
- Async/await pattern for non-blocking operations
- Automatic connection pooling via SQLAlchemy
- Transaction management (commit/rollback)

## Testing

### Test Coverage

1. **Model Tests** (`tests/test_session_model.py`):
   - UUID4 generation
   - Timestamp creation
   - Field validation
   - Minimal data model verification

2. **Schema Tests** (`tests/test_session_schemas.py`):
   - Request/response validation
   - UUID and datetime parsing
   - from_model() conversion
   - JSON serialization

3. **Endpoint Tests** (`tests/test_session_endpoints.py`):
   - POST /sessions: 201 status, UUID generation
   - DELETE /sessions/{id}: 204 status, 404 on missing
   - Error handling (422 for invalid UUID)
   - OpenAPI documentation

### Running Tests

```bash
# Run all session tests
pytest tests/test_session_*.py -v

# Run specific test file
pytest tests/test_session_endpoints.py -v

# Run with coverage
pytest tests/test_session_*.py --cov=app
```

## Database Schema

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

No additional indexes on minimal model (primary key index sufficient).

### Scalability

- UUID4 natural distribution (no hotspots)
- Single table (no joins)
- Fast point lookups (PK index on id)
- Easy sharding/partitioning by id if needed

## Configuration

Session endpoints use existing database configuration:
- `DB_HOST`: Database hostname
- `DB_PORT`: Database port
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_POOL_MIN_SIZE`: Minimum connections (default: 10)
- `DB_POOL_MAX_SIZE`: Maximum connections (default: 20)

See `.env.example` for full configuration template.

## Security Considerations

1. **UUID4 Randomness**: Cryptographically random, not guessable
2. **No PII**: Session model contains no personal information
3. **HTTPS Recommended**: Transmitted session IDs should use HTTPS in production
4. **Rate Limiting**: Not implemented (consider for production)
5. **CORS**: Not configured (consider for production if frontend on different origin)

## Future Enhancements

1. **Rate Limiting**: Prevent session creation DoS attacks
2. **Session Expiration**: Auto-delete after N days of inactivity
3. **Session Metadata**: Links to chat history (separate table)
4. **Audit Logging**: Track creation/deletion for compliance
5. **Metrics**: Count active sessions, average lifetime, etc.

## Troubleshooting

### Session Creation Fails

1. Check database is running: `curl http://localhost:8000/health/db`
2. Check environment variables in `.env` file
3. Check logs for specific error message
4. Verify database tables created: `SELECT * FROM sessions;`

### Delete Returns 404

1. Verify session ID is correct (copy from create response)
2. Check UUID format is valid (case-insensitive)
3. Session may already be deleted (hard delete)

### 503 Service Unavailable

1. Database connection issue
2. Check database host/port configuration
3. Check network connectivity to database
4. Check database logs for connection errors

## References

- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [FastAPI Dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [UUID Standards](https://en.wikipedia.org/wiki/Universally_unique_identifier)
- [Privacy-First Design Patterns](https://www.privacybydesign.ca/)
