## 1. Database Schema & Models

- [x] 1.1 Create database migration file for reports table
- [x] 1.2 Add Report SQLAlchemy ORM model to app/models/report.py
- [x] 1.3 Create relationship from Session model to Report model with cascade delete
- [x] 1.4 Run migration to create reports table in PostgreSQL
- [x] 1.5 Verify reports table structure and foreign key constraints

## 2. Pydantic Schemas

- [x] 2.1 Create app/schemas/report.py with location Enum (public space, online, kampus, sekolah, workplace)
- [x] 2.2 Add perpetrator Enum (supervisor, colleague, lecturer, client, stranger)
- [x] 2.3 Add description Enum (inappropriate comments, unwanted physical touch, repeated pressure, threat or coercion, digital harassment)
- [x] 2.4 Add evidence Enum (messages, emails, witness, none)
- [x] 2.5 Add user_goal Enum (understand the risk, document safely, consider reporting, explore options)
- [x] 2.6 Create ReportCreate schema with all Enum fields
- [x] 2.7 Create ReportResponse schema with id, session_id, all Enum fields, generated_document, created_at
- [x] 2.8 Add validation tests for each Enum type

## 3. Gemini Service Integration

- [x] 3.1 Create app/services/report.py module
- [x] 3.2 Implement generate_report_draft(report_data: ReportCreate) → str function
- [x] 3.3 Create system prompt that enforces SEXUAL VIOLENCE COMPLAINT FORM structure (Identifikasi Kebutuhan, Identifikasi Pelaku, Kronologi Kejadian, Bukti Terlampir)
- [x] 3.4 Configure Gemini 2.5 Flash with temperature=0.3
- [x] 3.5 Ensure generated narrative uses first-person perspective ("Saya")
- [x] 3.6 Add error handling for Gemini API failures (rate limiting, timeout, auth)
- [x] 3.7 Test generate_report_draft with sample inputs
- [x] 3.8 Verify generated narrative structure matches requirements

## 4. FastAPI Endpoints

- [x] 4.1 Create app/api/v1/report.py router module
- [x] 4.2 Implement POST /api/v1/sessions/{session_id}/report endpoint
- [x] 4.3 Add request validation for Enum fields in POST endpoint
- [x] 4.4 Add session_id existence check before report creation
- [x] 4.5 Call generate_report_draft and update generated_document field
- [x] 4.6 Handle case where report generation fails but data is saved (nullable generated_document)
- [x] 4.7 Implement GET /api/v1/sessions/{session_id}/report endpoint
- [x] 4.8 Add 404 responses for missing sessions or reports
- [x] 4.9 Register report router in main FastAPI application
- [x] 4.10 Verify endpoints appear in OpenAPI documentation

## 5. Integration & Testing

- [x] 5.1 Create unit tests for Report model relationships
- [x] 5.2 Create unit tests for ReportCreate and ReportResponse schemas
- [x] 5.3 Create unit tests for generate_report_draft function
- [x] 5.4 Create integration tests for POST /api/v1/sessions/{session_id}/report
- [x] 5.5 Create integration tests for GET /api/v1/sessions/{session_id}/report
- [x] 5.6 Test Enum validation rejects invalid values
- [x] 5.7 Test cascade delete removes reports when session is deleted
- [x] 5.8 Test endpoint returns 404 for non-existent session
- [x] 5.9 Run full test suite and verify coverage

## 6. Documentation & Deployment

- [x] 6.1 Update project README with report generation feature documentation
- [x] 6.2 Document required environment variables (Gemini API key)
- [x] 6.3 Add endpoint examples to API documentation
- [x] 6.4 Verify database migration plan for production deployment
- [x] 6.5 Test report generation with real Gemini API (not mock)
- [x] 6.6 Review for security: validate Enum inputs, SQL injection prevention, LLM prompt injection
