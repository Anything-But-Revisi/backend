# Design: Google Gemini Chatbot Integration

## Context

SafeSpace provides anonymous session infrastructure with database persistence. Users need an AI-powered companion for emotional support conversations. Google Gemini (gemini-2.5-flash-lite) is a capable, fast, and cost-effective LLM suitable for real-time chat applications. The integration must maintain session anonymity, preserve conversation context, and provide empathetic responses.

Current state:
- PostgreSQL with async SQLAlchemy connection pool (app/database.py)
- Anonymous sessions with UUID4 identifiers (app/models/session.py)
- FastAPI application with dependency injection (app/main.py)
- API versioning under /api/v1/

## Goals / Non-Goals

**Goals:**
- Integrate Gemini API for multi-turn conversations with session context
- Store message history (user and model) in database for context retrieval
- Provide empathetic system prompts configurable per conversation
- Enable stateless endpoint design using session_id for all context
- Maintain anonymity (no user identification in messages or logs)
- Provide GET endpoint to retrieve full conversation history
- Support fast response times by leveraging gemini-2.5-flash-lite model

**Non-Goals:**
- Real-time streaming to frontend (return complete response after API call)
- Fine-tuning or custom model training
- Multi-language support (English only initially)
- Voice/audio input (text only)
- Integration with payment/billing systems
- User authentication beyond session_id validation
- Message editing/deletion endpoints (immutable conversation history)
- Rate limiting per user (out of scope, consider future enhancement)

## Decisions

### 1. Message Storage Architecture
**Decision**: Store ALL messages (user and model) in a single `messages` table with role field.

**Rationale**: 
- Simplicity: Single table reduces schema complexity and query count
- Flexibility: role field enables future analytics on user vs model behavior
- Performance: Index on (session_id, created_at) enables efficient history retrieval
- Immutability: Append-only design prevents accidental overwrite

**Alternatives Considered**:
- Separate tables for user/model messages: More normalized but adds JOIN complexity
- NoSQL document store: Would require changing database architecture mid-project

### 2. Context Retrieval Strategy
**Decision**: Fetch entire message history per request, send to Gemini in single conversation turn.

**Rationale**:
- Gemini API accepts full conversation history in request (no session state on API side)
- Avoids complexity of maintaining conversation state in API
- Respects anonymity: Each request is independent, all context is local
- Scales well: No server-side session state to manage

**Alternatives Considered**:
- Maintain conversation state server-side with Gemini: Adds complexity, requires session management
- Limit history to N most recent messages: May lose important context for longer conversations

### 3. System Prompt Configuration
**Decision**: Store base system prompt as constant in code; allow per-request override via optional endpoint parameter.

**Rationale**:
- Sensible default for all users (empathetic, non-judgmental companion)
- No database queries needed for prompt retrieval
- Future extensibility: Could store custom prompts per session_id if needed
- Security: Centralized prompt prevents injection attacks

**System Prompt**:
```
You are SafeSpace, an empathetic emotional support companion. 
Your role is to:
- Validate and reflect feelings without judgment
- Ask clarifying questions to understand the user better
- Offer supportive perspectives, not medical advice
- Maintain absolute confidentiality
- Respond with warmth, understanding, and patience

Never:
- Attempt to diagnose or prescribe treatment
- Make decisions for the user
- Share advice that contradicts professional help
- Dismiss or minimize feelings
```

**Alternatives Considered**:
- Full system prompt in database: Adds complexity for minimal benefit
- Multiple personas switchable per session: Out of scope, future enhancement

### 4. API Endpoint Design
**Decision**: Two endpoints only - POST for sending/receiving and GET for history.

**Rationale**:
- Simplicity: Users send message, receive response in single request/response cycle
- Alignment: Matches REST conventions (POST for write, GET for read)
- No streaming: Simpler to implement, acceptable latency for most use cases
- Response format: POST returns latest model response + user knows they're in conversation

**POST Request/Response**:
```json
POST /api/v1/sessions/{session_id}/chat
{ "message": "I feel anxious about tomorrow" }
→ 200 OK
{ "session_id": "...", "role": "model", "content": "...", "created_at": "..." }
```

**GET Response**:
```json
GET /api/v1/sessions/{session_id}/chat
→ 200 OK
{
  "session_id": "...",
  "messages": [
    { "role": "user", "content": "...", "created_at": "..." },
    { "role": "model", "content": "...", "created_at": "..." },
    ...
  ]
}
```

**Alternatives Considered**:
- WebSocket for streaming: More complex, not needed for MVP
- Single endpoint with method dispatch: Less REST-compliant
- Separate endpoints for create/update/delete: Overengineered for current scope

### 5. Error Handling Strategy
**Decision**: Gemini API errors return 503, validation errors return 422, session not found returns 404.

**Rationale**:
- Follows HTTP semantics: 503 for service unavailable, 422 for validation, 404 for resource not found
- User experience: Clear distinction between client error, server error, and API error
- Frontend handling: Client can retry 503, fix request on 422, ask user to verify session_id on 404

**Alternatives Considered**:
- All errors as 500: Loses semantic information for frontend
- Expose raw Gemini errors: May leak implementation details

### 6. Dependency Management
**Decision**: Add google-generativeai to requirements.txt; no async wrapper (use sync SDK in async context).

**Rationale**:
- google-generativeai is officially maintained, well-documented
- Sync SDK in async endpoint: Acceptable because Gemini calls are I/O-bound, not compute-bound
- Alternative: Write custom async wrapper - adds complexity for marginal benefit

**Alternatives Considered**:
- Use REST API directly: More control but manual request handling
- Create async wrapper: Over-engineered for initial integration

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **Gemini API rate limits**: High message volume could hit API quotas | Monitor usage; implement rate limiting in future phase |
| **Large conversation history**: Long chats mean large context sent to API | Limit older messages or summarize history in future enhancement |
| **Sync SDK in async endpoint**: Could block event loop | Accept for MVP; profile performance; upgrade if needed |
| **API key exposure**: GOOGLE_API_KEY in environment | Standard practice; use secrets management in production |
| **Message privacy**: All messages stored in database | User controls deletion via session delete; document data retention |
| **Context window size**: Gemini has finite context (100K tokens) | Not a concern for typical chats; monitor token usage |
| **No streaming**: User waits for full response | Acceptable latency; streaming is future enhancement |

## Deployment Plan

1. **Phase 1 - Code Complete**: Implement message model, endpoints, and Gemini integration
2. **Phase 2 - Testing**: Unit tests, integration tests, manual API testing
3. **Phase 3 - Configuration**: Add GOOGLE_API_KEY to .env.example and production secrets
4. **Phase 4 - Documentation**: Update README with chat API examples
5. **Phase 5 - Deployment**: Deploy to staging, verify with sample conversations, then production

**Rollback**: Remove `/chat` routes from router in app/api/v1/; messages table persists but is not used.

## Open Questions

1. Should we implement conversation summarization for very long chats? (Future enhancement)
2. What is acceptable response latency for typical queries? (Need to measure with gemini-2.5-flash-lite)
3. Should chat history be visible in user's session, or only to them? (No visibility restrictions initially)
4. Do we need moderation/safety filtering? (Gemini has built-in safety features; document for users)
5. Should deleted sessions cascade-delete messages? (Yes, implement as foreign key cascade)
