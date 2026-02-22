# Specification: Session Schemas

## Requirements

### Requirement: SessionResponse Schema
The system SHALL provide a Pydantic schema for session response validation.

#### Scenario: Schema definition
- **WHEN** application is started
- **THEN** a SessionResponse Pydantic model is available in app/schemas/session.py

#### Scenario: Required fields
- **WHEN** a SessionResponse is created
- **THEN** it includes session_id (UUID) and created_at (datetime) fields, both required

#### Scenario: Session ID field
- **WHEN** SessionResponse contains session_id
- **THEN** it is a valid UUID4 type that can be serialized to string

#### Scenario: Creation timestamp field
- **WHEN** SessionResponse contains created_at
- **THEN** it is a datetime object serialized as ISO 8601 string in JSON

#### Scenario: JSON serialization
- **WHEN** a SessionResponse is serialized to JSON
- **THEN** session_id appears as string UUID and created_at as ISO 8601 timestamp

#### Scenario: Schema validation
- **WHEN** invalid data is used to create SessionResponse
- **THEN** Pydantic raises ValidationError with clear error messages

### Requirement: SessionCreate Schema
The system SHALL provide a schema for session creation requests.

#### Scenario: Empty request schema
- **WHEN** a session creation request is received
- **THEN** SessionCreate schema allows empty request body (no required fields)

#### Scenario: Optional fields support
- **WHEN** SessionCreate schema is used
- **THEN** any future optional fields can be added without breaking existing clients

#### Scenario: Request validation
- **WHEN** request data is validated against SessionCreate
- **THEN** no validation errors occur for empty body or empty JSON object

### Requirement: FastAPI Integration
The system SHALL integrate schemas with FastAPI request/response handlers.

#### Scenario: Response model annotation
- **WHEN** session creation endpoint is defined
- **THEN** SessionResponse is used as response_model in FastAPI

#### Scenario: Automatic response validation
- **WHEN** endpoint returns session data
- **THEN** FastAPI automatically validates against SessionResponse schema

#### Scenario: OpenAPI documentation
- **WHEN** Swagger/OpenAPI documentation is generated
- **THEN** SessionResponse schema is documented with correct fields and types

#### Scenario: Type hints
- **WHEN** session endpoint receives FastAPI Depends(get_db)
- **THEN** type hints are available for IDE autocompletion

### Requirement: Error Response Schema
The system SHALL provide consistent error response format.

#### Scenario: Error message structure
- **WHEN** an error occurs (e.g., 404, 500)
- **THEN** error response includes detail message with explanation

#### Scenario: HTTP exception handling
- **WHEN** endpoint raises HTTPException
- **THEN** FastAPI returns proper status code with detail message

#### Scenario: Validation error format
- **WHEN** request validation fails
- **THEN** response includes list of validation errors with field names and messages

### Requirement: Schema Documentation
The system SHALL provide clear documentation of schemas.

#### Scenario: Field descriptions
- **WHEN** schema fields are defined
- **THEN** they include descriptions for API documentation

#### Scenario: Example values
- **WHEN** OpenAPI docs are generated
- **THEN** examples of response values are shown (e.g., session_id: "550e8400-e29b-41d4-a716-446655440000")

#### Scenario: Type clarity
- **WHEN** schema fields are documented
- **THEN** types are clear (UUID as string, datetime as ISO 8601 string)
