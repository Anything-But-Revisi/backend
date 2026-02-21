## ADDED Requirements

### Requirement: ReportCreate Pydantic Schema
The system SHALL provide a ReportCreate Pydantic schema that validates structured report form input with strict Enum types for location, perpetrator type, incident description, evidence, and user goal.

#### Scenario: Valid report creation with all required Enum fields
- **WHEN** a user submits a report form with valid Enum values (location=public space, perpetrator=colleague, description=inappropriate comments, evidence=messages, user_goal=document safely)
- **THEN** ReportCreate schema validates successfully and creates a schema instance

#### Scenario: Invalid location value is rejected
- **WHEN** a user submits location="invalid_location"
- **THEN** Pydantic validation fails with error message indicating valid options: public space, online, kampus, sekolah, workplace

#### Scenario: Invalid perpetrator value is rejected
- **WHEN** a user submits perpetrator="invalid_perpetrator"
- **THEN** Pydantic validation fails with error message indicating valid options: supervisor, colleague, lecturer, client, stranger

#### Scenario: Invalid description value is rejected
- **WHEN** a user submits description="invalid_description"
- **THEN** Pydantic validation fails with error message indicating valid options: inappropriate comments, unwanted physical touch, repeated pressure, threat or coercion, digital harassment

#### Scenario: Invalid evidence value is rejected
- **WHEN** a user submits evidence="invalid_evidence"
- **THEN** Pydantic validation fails with error message indicating valid options: messages, emails, witness, none

#### Scenario: Invalid user goal value is rejected
- **WHEN** a user submits user_goal="invalid_goal"
- **THEN** Pydantic validation fails with error message indicating valid options: understand the risk, document safely, consider reporting, explore options

### Requirement: ReportResponse Schema
The system SHALL provide a ReportResponse schema for API responses that includes all input fields plus id, session_id, generated_document, and created_at.

#### Scenario: Report response includes all fields
- **WHEN** a report is retrieved from the API
- **THEN** ReportResponse includes: id, session_id, location, perpetrator, description, evidence, user_goal, generated_document, created_at
