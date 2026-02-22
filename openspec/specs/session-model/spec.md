# Specification: Session Data Model

## Requirements

### Requirement: Session Table Structure
The system SHALL provide a persistent session storage model with UUID-based identifiers and creation timestamps.

#### Scenario: Session table creation
- **WHEN** database migrations are applied
- **THEN** a `sessions` table is created with columns for id, created_at

#### Scenario: UUID primary key
- **WHEN** a new session is created
- **THEN** the session id is a UUID4 primary key, unique across all sessions

#### Scenario: Creation timestamp
- **WHEN** a session is created
- **THEN** created_at is automatically set to current UTC timestamp

#### Scenario: No personally identifiable data
- **WHEN** a session record is examined
- **THEN** no user identification data exists in the record (only id and timestamp)

### Requirement: SQLAlchemy ORM Model
The system SHALL provide an SQLAlchemy ORM model mapping to the sessions table.

#### Scenario: Model class definition
- **WHEN** application imports the session model
- **THEN** a Session class exists with proper SQLAlchemy configuration

#### Scenario: Model attributes
- **WHEN** a Session instance is created
- **THEN** it has id (UUID primary key) and created_at (datetime) attributes

#### Scenario: Model serialization
- **WHEN** a Session object is converted to dictionary
- **THEN** it includes id and created_at in the output

#### Scenario: Immutable after creation
- **WHEN** a session is persisted to database
- **THEN** only the id and created_at fields exist; no update operations are supported in the model

### Requirement: Database Session Dependency
The system SHALL integrate with the existing database connection pool for session operations.

#### Scenario: Use existing connection pool
- **WHEN** session model operations occur
- **THEN** they use the AsyncSession from app/database.py dependency injection

#### Scenario: Transaction handling
- **WHEN** a session record is created or deleted
- **THEN** database transaction is committed and any errors are rolled back

#### Scenario: Connection cleanup
- **WHEN** session operations complete
- **THEN** database connections are returned to the pool
