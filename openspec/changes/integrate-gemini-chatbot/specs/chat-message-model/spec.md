# Specification: Chat Message Model

## ADDED Requirements

### Requirement: Message Table Structure
The system SHALL provide persistent storage for chat messages linked to sessions.

#### Scenario: Message table creation
- **WHEN** database schema is initialized
- **THEN** a `messages` table exists with id, session_id, role, content, created_at columns

#### Scenario: Foreign key to sessions
- **WHEN** a message record is created
- **THEN** session_id must reference a valid session id in the sessions table (foreign key constraint)

#### Scenario: Immutable message records
- **WHEN** a message is persisted to the database
- **THEN** only id, session_id, role, content, and created_at are stored; no update operations are supported

### Requirement: SQLAlchemy Message ORM Model
The system SHALL provide an SQLAlchemy ORM model for message operations.

#### Scenario: Message model class
- **WHEN** application imports the message model
- **THEN** a Message class exists with proper SQLAlchemy configuration and Base inheritance

#### Scenario: Model attributes
- **WHEN** a Message instance is created
- **THEN** it has id (UUID primary key), session_id (UUID foreign key), role (string), content (text), and created_at (datetime) attributes

#### Scenario: Role field enumeration
- **WHEN** a message role value is set
- **THEN** it must be either "user" or "model" (enumerated values)

#### Scenario: Message indexing
- **WHEN** retrieving messages for a session
- **THEN** database indexes on (session_id, created_at) enable efficient querying

### Requirement: Message Cascade Deletion
The system SHALL handle message cleanup when sessions are deleted.

#### Scenario: Session deletion cascades to messages
- **WHEN** a session is deleted via DELETE /api/v1/sessions/{session_id}
- **THEN** all messages linked to that session are also deleted (cascade delete)

#### Scenario: Orphaned messages prevention
- **WHEN** database enforces foreign key constraints
- **THEN** no message can exist without a valid corresponding session

### Requirement: Message Serialization
The system SHALL convert message records to API-compatible format.

#### Scenario: ORM to dictionary conversion
- **WHEN** a Message object is serialized
- **THEN** it includes all fields: id, session_id, role, content, created_at

#### Scenario: Timestamp formatting
- **WHEN** created_at is serialized to JSON
- **THEN** it is formatted as ISO 8601 string (e.g., "2026-02-21T12:00:00")
