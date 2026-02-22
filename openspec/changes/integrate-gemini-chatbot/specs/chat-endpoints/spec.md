# Specification: Chat Endpoints

## ADDED Requirements

### Requirement: Message Send Endpoint
The system SHALL provide a POST endpoint to send user messages and receive AI responses.

#### Scenario: POST request to send message
- **WHEN** a POST request is made to `/api/v1/sessions/{session_id}/chat`
- **THEN** the endpoint accepts a JSON body with "message" field and returns HTTP 200 OK

#### Scenario: User message validation
- **WHEN** a message is sent
- **THEN** the message content must be non-empty string with length > 0 and <= 4096 characters

#### Scenario: Session validation before message
- **WHEN** a message is sent for a session_id
- **THEN** the endpoint verifies the session exists; returns 404 if not found

#### Scenario: Message broadcast to Gemini
- **WHEN** a user message is received
- **THEN** the prior conversation history is retrieved and the new message is sent to Gemini with full context

#### Scenario: Response saving to database
- **WHEN** Gemini returns a response
- **THEN** both the user message and model response are persisted to the messages table in order

#### Scenario: Response format
- **WHEN** the endpoint returns success
- **THEN** the response is a single message object with role="model", content (string), created_at (datetime)

#### Scenario: Empty message rejection
- **WHEN** a message request contains empty string or whitespace-only content
- **THEN** endpoint returns HTTP 422 Unprocessable Entity with validation error

### Requirement: Message History Retrieval Endpoint
The system SHALL provide a GET endpoint to retrieve full conversation history.

#### Scenario: GET request for history
- **WHEN** a GET request is made to `/api/v1/sessions/{session_id}/chat`
- **THEN** the endpoint returns HTTP 200 OK with full message history

#### Scenario: Session history access
- **WHEN** history is requested for a session_id
- **THEN** all messages for that session are returned in chronological order (by created_at)

#### Scenario: History response format
- **WHEN** history is returned
- **THEN** response includes session_id and messages array, each message with id, role, content, created_at

#### Scenario: Empty history
- **WHEN** a session has no messages
- **THEN** the messages array is empty (not null)

#### Scenario: Session not found in history
- **WHEN** history is requested for non-existent session_id
- **THEN** endpoint returns HTTP 404 Not Found

### Requirement: Session ID Path Parameter Validation
The system SHALL validate session_id is a proper UUID.

#### Scenario: Valid UUID in path
- **WHEN** session_id is a valid UUID format in the request path
- **THEN** the endpoint processes the request normally

#### Scenario: Invalid UUID format
- **WHEN** session_id is not a valid UUID format
- **THEN** endpoint returns HTTP 422 Unprocessable Entity with validation error

#### Scenario: Invalid UUID rejection
- **WHEN** invalid UUIDs are rejected
- **THEN** no database queries are attempted for malformed IDs

### Requirement: Endpoint Response Headers
The system SHALL include appropriate headers in responses.

#### Scenario: Content-Type header
- **WHEN** a response is sent
- **THEN** Content-Type header is "application/json"

#### Scenario: Cache control for history
- **WHEN** GET /api/v1/sessions/{session_id}/chat is requested
- **THEN** Cache-Control header indicates data can be cached by client (no sensitive info)

### Requirement: Error Response Consistency
The system SHALL return consistent error response format.

#### Scenario: Error response format
- **WHEN** an error occurs (4xx or 5xx)
- **THEN** response includes a detail field with human-readable error message

#### Scenario: 400 series errors
- **WHEN** request is invalid (422 validation error)
- **THEN** response includes list of validation errors with field names and messages

#### Scenario: 500 series errors
- **WHEN** server error occurs
- **THEN** response includes detail message and HTTP 500 status; no sensitive stack traces
