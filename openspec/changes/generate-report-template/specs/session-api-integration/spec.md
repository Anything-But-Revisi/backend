## MODIFIED Requirements

### Requirement: FastAPI Router Setup
The system SHALL register session endpoints and session-scoped report endpoints with FastAPI application.

#### Scenario: Router creation
- **WHEN** application starts
- **THEN** a FastAPI APIRouter for sessions is created in app/api/v1/sessions.py and a report router is created in app/api/v1/report.py

#### Scenario: Route registration
- **WHEN** FastAPI app initializes
- **THEN** session routes are registered with the main app with prefix `/api/v1` AND report routes are registered with prefix `/api/v1/sessions`

#### Scenario: Route discovery
- **WHEN** Swagger/OpenAPI documentation is accessed
- **THEN** session endpoints AND report endpoints appear in `/api/docs` with correct paths

### Requirement: Report Endpoints Registration
The system SHALL register report endpoints as sub-routes under sessions with proper versioning.

#### Scenario: Report endpoints paths
- **WHEN** routes are registered
- **THEN** POST `/api/v1/sessions/{session_id}/report` and GET `/api/v1/sessions/{session_id}/report` are available

#### Scenario: Report endpoints documentation
- **WHEN** Swagger documentation is accessed
- **THEN** report endpoints are grouped under sessions and documented with request/response schemas
