# PostgreSQL Database Setup Guide

This guide explains how to set up and configure the PostgreSQL database connection for SafeSpace backend.

## Prerequisites

- PostgreSQL 12+ installed and running
- Python 3.9+
- Virtual environment activated

## Environment Variables

The application requires the following environment variables to connect to PostgreSQL. Create a `.env` file in the project root:

```bash
# Database host (default: localhost)
DB_HOST=localhost

# Database port (default: 5432)
DB_PORT=5432

# Database name
DB_NAME=safespace_dev

# Database username
DB_USER=postgres

# Database password
DB_PASSWORD=your_secure_password_here

# Connection pool - minimum size (default: 10)
DB_POOL_MIN_SIZE=10

# Connection pool - maximum size (default: 20)
DB_POOL_MAX_SIZE=20

# Query timeout in seconds (default: 30)
DB_QUERY_TIMEOUT=30

# Connection timeout in seconds (default: 10)
DB_CONNECTION_TIMEOUT=10
```

Copy `.env.example` to `.env` and update with your actual values:

```bash
cp .env.example .env
# Edit .env with your database credentials
```

## Local Development Setup

### Step 1: Install PostgreSQL

**On macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**On Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Step 2: Create Development Database

Connect to PostgreSQL as the default user:

```bash
psql -U postgres
```

Create a new database and user:

```sql
CREATE DATABASE safespace_dev;
CREATE USER safespace_dev WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE safespace_dev TO safespace_dev;
```

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy and configure the `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=safespace_dev
DB_USER=safespace_dev
DB_PASSWORD=your_secure_password_here
```

### Step 5: Verify Connection

Run the application and check the database health endpoint:

```bash
uvicorn app.main:app --reload
```

In another terminal, test the health check:

```bash
curl http://localhost:8000/health/db
```

Expected response when database is connected:
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

## Connection Pool Configuration

The application uses SQLAlchemy's connection pooling with the following strategy:

### Default Settings

- **Minimum connections**: 10 (configurable via `DB_POOL_MIN_SIZE`)
- **Maximum connections**: 20 (configurable via `DB_POOL_MAX_SIZE`)
- **Connection timeout**: 10 seconds (configurable via `DB_CONNECTION_TIMEOUT`)
- **Query timeout**: 30 seconds (configurable via `DB_QUERY_TIMEOUT`)

### Tuning the Pool Size

Adjust pool size based on:
- **Concurrent users**: Higher concurrent users → larger pool
- **Database resources**: Limited server resources → smaller pool
- **Application workload**: IO-heavy → larger pool

Example for high-concurrency scenario:
```
DB_POOL_MIN_SIZE=20
DB_POOL_MAX_SIZE=50
```

Example for development:
```
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=10
```

### Pool Features

- **Connection recycling**: Connections are recycled every 1 hour to prevent stale connections
- **Health checking**: Connections are tested before use (`pool_pre_ping=True`)
- **Connection timeout**: Configurable timeout for acquiring connections
- **Automatic cleanup**: Connections are properly closed on application shutdown

## Health Checks

### Database Health Endpoint

The application provides a health check endpoint to verify database connectivity:

**Endpoint**: `GET /health/db`

**Response when healthy (200 OK):**
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

**Response when unhealthy (503 Service Unavailable):**
```json
{
  "status": "unhealthy",
  "database": "disconnected",
  "error": "Connection refused",
  "timestamp": "2026-02-21T10:30:45.123456"
}
```

### Monitoring

Monitor health checks using:

```bash
# Single check
curl http://localhost:8000/health/db

# Continuous monitoring (every 5 seconds)
watch -n 5 'curl -s http://localhost:8000/health/db | jq'

# With logging
curl -v http://localhost:8000/health/db
```

## Troubleshooting

### Connection Refused

**Error**: `Connection refused on localhost:5432`

**Solutions**:
1. Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
2. Check host/port in `.env` are correct
3. Restart PostgreSQL service

### Authentication Failed

**Error**: `authentication failed for user "safespace_dev"`

**Solutions**:
1. Verify credentials in `.env`
2. Check user exists: `psql -U postgres -c "\du"`
3. Reset password: `ALTER USER safespace_dev WITH PASSWORD 'newpassword';`

### Connection Pool Exhausted

**Error**: `QueuePool timeout of 10 seconds exceeded`

**Solutions**:
1. Increase `DB_POOL_MAX_SIZE` in `.env`
2. Lower `DB_CONNECTION_TIMEOUT` to fail faster
3. Check for connection leaks in application code
4. Verify no long-running queries

### Timeout Issues

**Error**: `Health check query timeout (> 3 seconds)`

**Solutions**:
1. Check database server load: `SELECT count(*) FROM pg_stat_activity;`
2. Increase timeouts: `DB_QUERY_TIMEOUT=60`
3. Check network latency to database
4. Verify database server has adequate resources

### .env File Not Found

**Error**: `No environment variables found`

**Solution**:
```bash
cp .env.example .env
# Edit .env with your values
```

## Production Deployment

For production deployments:

1. **Use strong passwords**: Generate with `openssl rand -base64 32`
2. **Set ENVIRONMENT variable**: `ENVIRONMENT=production`
3. **Adjust pool sizes**: Based on expected load
4. **Use managed database**: Consider AWS RDS, Azure Database, Google Cloud SQL
5. **Enable SSL connections**: Set SSL mode in connection string
6. **Monitor health endpoint**: Set up alerts on `/health/db`
7. **Database backups**: Configure automated backups
8. **Connection pooling**: Consider using PgBouncer for additional pooling layer

### Example Production .env

```
ENVIRONMENT=production
DB_HOST=safespace-db.c9akciq32.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=safespace
DB_USER=safespace_admin
DB_PASSWORD=<strong_generated_password>
DB_POOL_MIN_SIZE=20
DB_POOL_MAX_SIZE=50
DB_QUERY_TIMEOUT=60
DB_CONNECTION_TIMEOUT=10
LOG_LEVEL=WARNING
```

## Development Tips

### Reset Development Database

```bash
# Drop database
dropdb safespace_dev

# Recreate
createdb safespace_dev
psql -U safespace_dev -d safespace_dev < schema.sql
```

### View Active Connections

```bash
psql -U postgres -c "SELECT * FROM pg_stat_activity WHERE datname='safespace_dev';"
```

### Check Pool Status

The health endpoint shows current pool statistics:
```bash
curl http://localhost:8000/health/db | jq '.connection_pool'
```

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLAlchemy AsyncIO Documentation](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
