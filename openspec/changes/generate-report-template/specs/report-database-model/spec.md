## ADDED Requirements

### Requirement: Reports Database Table with Session Foreign Key
The system SHALL create a reports table in PostgreSQL with columns for all Enum fields, generated_document (nullable Text), created_at timestamp, session_id foreign key with cascade delete, and appropriate indexes.

#### Scenario: Reports table is created with all required columns
- **WHEN** database migration is executed
- **THEN** reports table exists with columns: id (PK), session_id (FK), location (String), perpetrator (String), description (String), evidence (String), user_goal (String), generated_document (Text nullable), created_at (DateTime)

#### Scenario: Foreign key constraint enforces referential integrity
- **WHEN** attempting to create a report with non-existent session_id
- **THEN** database rejects the insert with foreign key constraint violation

#### Scenario: Cascade delete removes reports when session is deleted
- **WHEN** a session is deleted
- **THEN** all reports associated with that session are automatically deleted

#### Scenario: Report record is created with valid Enum values
- **WHEN** Report model is instantiated with valid location, perpetrator, description, evidence, user_goal values
- **THEN** record can be committed to database without validation errors

### Requirement: Report Model Relationships
The system SHALL define a Report SQLAlchemy ORM model with a back-reference relationship to Session.

#### Scenario: Report model has relationship to parent session
- **WHEN** a Report instance is loaded from database
- **THEN** accessing report.session returns the associated Session object
