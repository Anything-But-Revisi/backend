# Design: Anonymous Sessions System

## Context

SafeSpace backend currently has PostgreSQL connectivity (setup-postgres-connection) and FastAPI framework, but no session management system. The chatbot feature requires tracking conversations per user without storing personally identifiable information. Sessions must be anonymous (identified only by UUID), immutable (no updates after creation), and completely deletable by the user at any time.

Current state:
- PostgreSQL database configured and accessible
- FastAPI application with lifespan handlers and health checks
- No session tracking or conversation persistence
- No ability for users to control their data deletion

## Goals / Non-Goals

**Goals:**
- Create privacy-first session management system using only UUID identifiers
- Implement session creation and retrieval endpoints
- Implement secure session deletion with cascading cleanup
- Provide clean API for session management in conversation context
- Ensure data immutability except for deletion
- Support future features that depend on session tracking

**Non-Goals:**
- User authentication or identification
- Session encryption (relying on database security and HTTPS)
- Session token management or expiration (out of scope)
- Conversation message storage (sessions only, no message history)
- Session analytics or metrics collection

## Decisions

### Decision 1: UUID4 for Session Identifiers
**Choice**: Use UUID4 (random) instead of UUIDs based on user data or sequential IDs

**Rationale**:
- UUID4 provides strong privacy guarantees - no information leakage about user or session order
- Non-sequential ensures no enumeration attacks
- Globally unique, no coordination needed
- Standard format used across web applications

**Alternative Considered**:
- Sequential IDs: Would allow enumeration/discovery of session IDs
- UUID5 (name-based): Would require storing identifying information
- Hash-based IDs: Unnecessary complexity

### Decision 2: SQLAlchemy ORM with Pydantic Validation
**Choice**: Use SQLAlchemy for ORM model and Pydantic for request/response schema validation

**Rationale**:
- SQLAlchemy already in use (postgres-connection), consistent with codebase
- Pydantic integrates seamlessly with FastAPI
- Type safety and automatic validation
- Can upgrade to async ORM models later if needed

**Alternative Considered**:
- Raw SQL: Less maintainable and harder to evolve
- Different ORM: Inconsistent with existing setup

### Decision 3: Soft Delete vs Hard Delete
**Choice**: Hard delete (permanent removal) with optional audit logging, no soft deletes

**Rationale**:
- User privacy principle: deletion means truly gone, not hidden
- "Panic Button" expectation - user expects complete removal
- Simplifies schema
- No privacy implications of deleted sessions remaining in database

**Alternative Considered**:
- Soft delete with extra `deleted_at` column: Violates privacy principle (data still exists)
- Audit table for deletions: Can be added later without schema changes

### Decision 4: Minimal Session Model
**Choice**: Session table with only `id` (UUID primary key) and `created_at` (timestamp)

**Rationale**:
- Enforces privacy-first design (no user data)
- Sufficient for session identification
- Timestamp useful for future analytics/cleanup policies
- No update operations needed

**Alternative Considered**:
- Add user_id field: Violates anonymity
- Add session metadata: Unnecessary complexity for MVP

### Decision 5: Endpoint Structure
**Choice**: RESTful endpoints under `/api/v1/sessions` with resource-based paths

**Rationale**:
- Consistent with RESTful conventions
- `/api/v1/` provides versioning path for future changes
- `POST /sessions` for creation, `DELETE /sessions/{id}` for deletion
- Natural mapping to HTTP verbs

**Alternative Considered**:
- Custom RPC-style endpoints: Less standard, harder to evolve
- Anonymous paths like `/api/chat-session`: Less discoverable, harder to version

## Risks / Trade-offs

**Risk 1: Accidental Session Deletion**
- **Problem**: User might accidentally delete session data with no recovery
- **Mitigation**: Clear API documentation warning about permanent deletion, optional confirmation message in client UI (not enforced server-side)

**Risk 2: Session ID Enumeration**
- **Problem**: If session IDs are predictable, attacker could enumerate all sessions
- **Mitigation**: Using UUID4 (random) prevents enumeration, rely on HTTPS to prevent ID interception

**Trade-off 1: No Session Metadata**
- **Trade**: Cannot track session source, user agent, IP, etc. without violating privacy
- **Worth It Because**: Privacy is core principle, metadata can be tracked at conversation level if needed

**Trade-off 2: Hard Delete Only**
- **Trade**: No audit trail of deleted sessions without separate logging
- **Worth It Because**: User expectation and privacy principle (data truly gone)

**Risk 3: Orphaned Session References**
- **Problem**: Other tables might reference sessions
- **Mitigation**: Use database constraints (foreign keys), cascade delete rules in schema

## Migration Plan

**Phase 1 - Schema & Models** (this change):
1. Create `sessions` table in PostgreSQL
2. Define SQLAlchemy session model
3. Create Pydantic schemas for requests/responses
4. Implement session API endpoints

**Phase 2 - Integration** (future):
1. Integrate sessions with conversation message storage
2. Add session-based conversation retrieval
3. Implement conversation deletion when session deleted

**Phase 3 - Cleanup Policies** (future):
1. Add optional session expiration based on created_at
2. Implement batch cleanup for expired sessions
3. Add metrics on session lifecycle

**Deployment Steps**:
1. Deploy database migration to create sessions table
2. Deploy application code with new endpoints
3. Verify endpoints respond correctly
4. Integration tests pass

**Rollback**:
1. Disable session endpoints (return 503)
2. Keep table intact (no data loss)
3. Revert to previous code
4. Drop table in maintenance window if needed

## Open Questions

- Should we add session expiration/TTL? (e.g., auto-delete after 30 days)
- Should we track creation IP/User-Agent separately from session model?
- Do we need rate limiting on session creation?
- Should session lookup require session_id, or should there be discovery endpoints?
- Future: Do we need session state (active, archived, etc.)?
