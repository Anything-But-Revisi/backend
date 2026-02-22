## ADDED Requirements

### Requirement: POST Report Creation Endpoint
The system SHALL provide a POST /api/v1/sessions/{session_id}/report endpoint that accepts a ReportCreate JSON payload, validates input, saves to database, generates report narrative via Gemini, updates generated_document field, and returns ReportResponse.

#### Scenario: Create report with valid input and generate narrative
- **WHEN** POST /api/v1/sessions/{session_id}/report receives valid ReportCreate payload with session_id="123", location="kampus", perpetrator="lecturer", description="inappropriate comments", evidence="witness", user_goal="document safely"
- **THEN** endpoint returns HTTP 201 with ReportResponse including populated generated_document field

#### Scenario: Invalid Enum values are rejected at API boundary
- **WHEN** POST request contains location="invalid_value"
- **THEN** endpoint returns HTTP 422 with validation error message

#### Scenario: Non-existent session returns 404
- **WHEN** POST /api/v1/sessions/invalid-session-id/report is called
- **THEN** endpoint returns HTTP 404 with error message

#### Scenario: Report saves to database even if Gemini fails
- **WHEN** Gemini API call fails during report generation
- **THEN** endpoint returns HTTP 500 error, but structured report data (location, perpetrator, etc.) is already saved to database with generated_document=null

### Requirement: GET Report Retrieval Endpoint
The system SHALL provide a GET /api/v1/sessions/{session_id}/report endpoint that returns the existing report for a given session or 404 if not found.

#### Scenario: Retrieve existing report
- **WHEN** GET /api/v1/sessions/{session_id}/report is called for a session with an existing report
- **THEN** endpoint returns HTTP 200 with ReportResponse including generated_document

#### Scenario: No report exists for session
- **WHEN** GET /api/v1/sessions/{session_id}/report is called for a session without a report
- **THEN** endpoint returns HTTP 404 with error message

#### Scenario: Non-existent session returns 404
- **WHEN** GET /api/v1/sessions/invalid-session-id/report is called
- **THEN** endpoint returns HTTP 404 with error message

### Requirement: Session ID Validation
The system SHALL validate that the provided session_id exists and belongs to a valid session before creating or retrieving reports.

#### Scenario: Endpoint verifies session existence
- **WHEN** any report endpoint is called with session_id
- **THEN** endpoint queries sessions table to verify session exists before proceeding
