## Why

Sexual violence survivors often struggle to document their experiences in formal, professional language. Providing an LLM-powered template generator helps survivors transform structured input (location, perpetrator type, incident description, evidence, goals) into a formal "Sexual Violence Complaint Form" that is ready for submission to authorities, HR, or organizational bodies. This empowers survivors to document safely and clarifies reporting options without professional intermediaries.

## What Changes

- Create a new Report (Pelaporan) domain with Pydantic schema validation
- Add database support for storing structured reports with cascading session deletion
- Integrate Gemini 2.5 Flash LLM to generate formal report narratives
- Expose FastAPI endpoints for creating and retrieving reports
- Generate reports in Indonesian using "FORMULIR PENGADUAN KEKERASAN SEKSUAL" structure with system prompt injection

## Capabilities

### New Capabilities
- `report-schema`: Pydantic schema (ReportCreate) with strict Enum validation for location, perpetrator type, description, evidence, and user goals
- `report-database-model`: Database model for reports table with FK to sessions, cascade delete, and generated_document field
- `report-gemini-service`: LLM service function to generate formal report drafts using Context Injection with fixed system prompt structure
- `report-endpoints`: FastAPI endpoints for creating reports (POST) and retrieving existing reports (GET) by session_id

### Modified Capabilities
- `session-api-integration`: Requires new report endpoints integrated into session-scoped routing

## Impact

- New package dependency: Google Generative AI (gemini-2.5-flash) for report generation
- New database table: `reports` with FK constraint to `sessions.id`
- New service module: `app/services/report.py`
- New endpoint module: `app/api/v1/report.py`
- New schema module: `app/schemas/report.py`
- Session deletion will cascade to reports (orphaned reports cannot exist)
- Report generation requires Gemini API key in environment variables
