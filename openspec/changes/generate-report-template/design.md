## Context

The system currently has sessions management and users can securely document their experiences. We are adding report generation capability to transform structured form input into formal report narratives using Gemini 2.5 Flash LLM. This feature sits alongside the chat and session subsystems and requires database, schema, service, and API layers.

Current architecture:
- FastAPI application with modular API versioning (v1)
- SQLAlchemy ORM with PostgreSQL backend
- Pydantic for request/response validation
- Gemini integration for chat functionality

## Goals / Non-Goals

**Goals:**
- Enable survivors to generate formal report narratives from structured input using LLM
- Maintain referential integrity between sessions and reports (cascade delete on session removal)
- Provide strict input validation via Pydantic Enum types
- Use system prompt injection to ensure consistent report structure (SEXUAL VIOLENCE COMPLAINT FORM)
- Expose REST endpoints for creating and retrieving reports scoped to sessions
- Generate Indonesian-language formal reports

**Non-Goals:**
- Automatic submission to authorities or external systems
- Multi-language support beyond Indonesian
- Report templates or customization beyond the fixed form structure
- Email delivery or notification on report creation
- Report versioning or editing of existing reports
- Integration with external case management systems

## Decisions

### Decision 1: System Prompt Structure (Context Injection)
**Choice**: Use fixed system prompt injected into Gemini API call that enforces "FORMULIR PENGADUAN KEKERASAN SEKSUAL" structure with sections: Identifikasi Kebutuhan, Identifikasi Pelaku, Kronologi Kejadian, Bukti Terlampir.

**Rationale**: 
- System prompts ensure consistent output format across all report generations
- Fixed structure matches official complaint form expectations
- Context injection prevents prompt injection attacks and ensures deterministic output
- Reduces need for post-processing or output parsing

**Alternatives considered**:
- Fine-tuned model: Requires large dataset and longer training cycle
- Few-shot prompting: Less reliable than system prompts; inconsistent formatting
- Template-based generation: Inflexible, doesn't leverage LLM narrative capability

### Decision 2: Cascade Delete for Reports
**Choice**: Set database FK constraint to `sessions.id` with `ondelete=CASCADE`.

**Rationale**:
- Reports are meaningless without their parent session context
- Simplifies session deletion logic; no orphaned report records
- Maintains data consistency without manual cleanup

**Alternatives considered**:
- Soft delete (mark as deleted): Adds complexity; reports are not sensitive enough for archival
- Manual deletion handler: Error-prone; could leave orphaned records

### Decision 3: Enum Validation at Schema Layer
**Choice**: Define Pydantic Enum types for location, perpetrator, description, evidence, user_goal in ReportCreate schema.

**Rationale**:
- Strict validation prevents invalid states at API boundary
- Enum values are limited and well-defined per specification
- Reduces LLM prompt complexity (fewer free-text fields to handle)
- Provides clear contract between frontend and backend

**Alternatives considered**:
- String validation with regex: Error-prone; doesn't convey semantic meaning
- Free-text input: Increases LLM complexity; inconsistent outputs

### Decision 4: Service Function vs Inline Endpoint Logic
**Choice**: Create dedicated `app/services/report.py` with `generate_report_draft()` function called by endpoint.

**Rationale**:
- Separates business logic from HTTP handling
- Allows reuse across multiple endpoints or contexts
- Testable independently of FastAPI
- Follows existing pattern (e.g., `app/services/gemini.py` for chat)

### Decision 5: Nullable generated_document Field
**Choice**: Store report data even if Gemini generation fails; keep generated_document as nullable.

**Rationale**:
- Preserves structured form input regardless of LLM availability
- Allows user to retry generation or manually complete later
- Provides audit trail of report intent even without narrative

**Alternatives considered**:
- Fail request if generation fails: Loses user input on API/LLM errors
- Make generated_document required: Brittle; breaks if LLM is unavailable

## Risks / Trade-offs

[Risk] **Gemini API Rate Limiting** → Will implement exponential backoff + retry logic in generate_report_draft(); inform users of potential delays during high-load periods.

[Risk] **LLM Output Inconsistency** → Mitigated by system prompt injection and temperature=0.3 (low creativity); may occasionally produce slightly different structures despite prompt constraints.

[Risk] **Large generated_document Field Size** → Mitigated by: (a) Text column supports up to 1GB in PostgreSQL, (b) Gemini outputs are typically 2-5KB, (c) Can archive old reports if needed.

[Risk] **Session Deletion Cascade Impact** → Users cannot recover deleted reports; mitigated by: (a) soft-delete session first if audit trail needed, (b) database backups.

[Trade-off] **Context Injection vs Token Usage** → System prompt + context requires more tokens than streaming to file; acceptable trade-off for deterministic structure.

## Migration Plan

1. Create new database migration to add `reports` table with FK to `sessions`
2. Deploy updated schema and service files
3. Deploy new API endpoints at `/api/v1/sessions/{session_id}/report`
4. Verify Gemini API connectivity and credentials
5. Run smoke tests: POST a sample report, verify generated_document is populated
6. Rollback: Requires schema rollback (drop reports table) if issues detected

## Open Questions

1. Should report creation return immediately with `generated_document=null`, then update asynchronously via background task, or wait for Gemini response synchronously? (Answer: Synchronous for MVP; document timeout risk)
2. Should we log generated prompts and LLM responses for debugging? (Answer: Log to structured logs, exclude sensitive content)
3. Rate limiting: How many reports per user/session? (Answer: No explicit limit for MVP; use Gemini's built-in quotas)
