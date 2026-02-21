# Tasks: Google Gemini Chatbot Integration

## 1. Database Schema and ORM

- [x] 1.1 Create SQLAlchemy Message model in app/models/message.py
- [x] 1.2 Define columns: id (UUID pk), session_id (UUID fk), role (String), content (Text), created_at (DateTime)
- [x] 1.3 Add table name `messages` and proper SQLAlchemy configurations
- [x] 1.4 Configure foreign key constraint from session_id to sessions table
- [x] 1.5 Add cascade delete for messages when session is deleted
- [x] 1.6 Add database indexes on (session_id, created_at) for efficient querying
- [x] 1.7 Test Message model instantiation and field access

## 2. Environment Configuration

- [x] 2.1 Add GOOGLE_API_KEY to .env.example with description
- [x] 2.2 Update app/config.py to load GOOGLE_API_KEY from environment
- [x] 2.3 Add validation for GOOGLE_API_KEY (warn if missing, allow graceful degradation)
- [x] 2.4 Create helper function to initialize Gemini client with proper error handling
- [x] 2.5 Test configuration loading with and without GOOGLE_API_KEY

## 3. Gemini SDK Integration

- [ ] 3.1 Install google-generativeai package (add to requirements.txt)
- [ ] 3.2 Create app/services/gemini.py module for Gemini client operations
- [ ] 3.3 Initialize GenerativeModel with "gemini-2.5-flash" model
- [ ] 3.4 Implement system prompt constant with empathetic companion instructions
- [ ] 3.5 Create function to call Gemini API with message history context
- [ ] 3.6 Implement error handling for API failures, rate limits, missing key
- [ ] 3.7 Test Gemini API calls with sample conversations

## 4. Message Pydantic Schemas

- [ ] 4.1 Create app/schemas/message.py module
- [ ] 4.2 Define MessageCreate schema (for POST requests, with "message" field)
- [ ] 4.3 Define MessageResponse schema (id, session_id, role, content, created_at)
- [ ] 4.4 Add field descriptions and example values for OpenAPI docs
- [ ] 4.5 Add validation for message length (non-empty, <= 4096 chars)
- [ ] 4.6 Create ChatHistoryResponse schema (session_id, messages array)

## 5. Chat Endpoints Implementation

- [ ] 5.1 Create app/api/v1/chat.py route file for chat endpoints
- [ ] 5.2 Implement POST /api/v1/sessions/{session_id}/chat endpoint
- [ ] 5.3 Add message validation and session existence check
- [ ] 5.4 Retrieve prior message history from database for context
- [ ] 5.5 Call Gemini API with message history and new user message
- [ ] 5.6 Save both user message and model response to database
- [ ] 5.7 Return model response with 200 OK status
- [ ] 5.8 Add error handling (404 for missing session, 422 for validation, 503 for API errors)
- [ ] 5.9 Implement GET /api/v1/sessions/{session_id}/chat endpoint
- [ ] 5.10 Retrieve all messages for session in chronological order
- [ ] 5.11 Return messages array with 200 OK status
- [ ] 5.12 Handle 404 for non-existent sessions

## 6. Route Registration and Integration

- [ ] 6.1 Create APIRouter for chat endpoints in app/api/v1/chat.py
- [ ] 6.2 Import and include router in app/main.py with prefix /api/v1
- [ ] 6.3 Verify routes appear in OpenAPI documentation at /docs
- [ ] 6.4 Add tags to chat endpoints for documentation organization
- [ ] 6.5 Test endpoint paths through FastAPI application

## 7. Database Integration

- [ ] 7.1 Extend app/database.py to create Message table on startup (add to Base.metadata.create_all)
- [ ] 7.2 Verify message model is imported in database initialization
- [ ] 7.3 Test table creation with fresh database
- [ ] 7.4 Test foreign key constraint enforcement
- [ ] 7.5 Test cascade delete (delete session → delete messages)

## 8. Logging and Monitoring

- [ ] 8.1 Add debug-level logging for Gemini API calls (input/output summary)
- [ ] 8.2 Add info-level logging for successful message creation
- [ ] 8.3 Add warning-level logging for API errors
- [ ] 8.4 Verify logs don't contain sensitive data (no full messages, no API keys)
- [ ] 8.5 Test log output format and readability

## 9. Unit Testing

- [ ] 9.1 Create tests/test_message_model.py with Message ORM tests
- [ ] 9.2 Test message table creation and foreign key constraints
- [ ] 9.3 Test message model instantiation, serialization, and field access
- [ ] 9.4 Create tests/test_message_schemas.py with Pydantic schema tests
- [ ] 9.5 Test MessageCreate schema validation (empty/valid/invalid message)
- [ ] 9.6 Test MessageResponse schema with ORM conversion
- [ ] 9.7 Create tests/test_gemini_service.py for Gemini integration
- [ ] 9.8 Test Gemini API calls with mock responses
- [ ] 9.9 Test error handling (missing key, API failures, rate limits)
- [ ] 9.10 Test system prompt initialization

## 10. Integration Testing

- [ ] 10.1 Create tests/test_chat_endpoints.py with API integration tests
- [ ] 10.2 Test POST /api/v1/sessions/{session_id}/chat full flow
- [ ] 10.3 Test message save to database and retrieval
- [ ] 10.4 Test GET /api/v1/sessions/{session_id}/chat history retrieval
- [ ] 10.5 Test chronological ordering of messages
- [ ] 10.6 Test 404 for non-existent session
- [ ] 10.7 Test 422 validation error for invalid message
- [ ] 10.8 Test 422 for invalid session_id UUID format
- [ ] 10.9 Test cascade delete (delete session → delete message history)
- [ ] 10.10 Test concurrent requests to same session

## 11. API Documentation

- [ ] 11.1 Add docstrings to Message ORM model
- [ ] 11.2 Add docstrings to all endpoint functions
- [ ] 11.3 Verify OpenAPI schema generation includes chat endpoints
- [ ] 11.4 Verify request/response schemas appear in /docs
- [ ] 11.5 Add example curl commands to README for chat API
- [ ] 11.6 Document POST /api/v1/sessions/{session_id}/chat endpoint
- [ ] 11.7 Document GET /api/v1/sessions/{session_id}/chat endpoint
- [ ] 11.8 Create GEMINI.md documentation file with usage examples

## 12. Privacy and Security Verification

- [ ] 12.1 Verify no PII is stored in message content (system design enforces this)
- [ ] 12.2 Verify no personal data in error messages or logs
- [ ] 12.3 Verify GOOGLE_API_KEY is never logged or exposed
- [ ] 12.4 Verify cascade delete removes all user data with session
- [ ] 12.5 Verify endpoint requires valid session_id (validate UUID)
- [ ] 12.6 Test message privacy (messages only accessible via session history)

## 13. Integration with Existing Systems

- [ ] 13.1 Verify PostgreSQL connection pool works with new message model
- [ ] 13.2 Verify health check endpoint still works
- [ ] 13.3 Test sessions and chat endpoints together
- [ ] 13.4 Verify no conflicts with existing database models
- [ ] 13.5 Load test endpoints with concurrent chat requests
- [ ] 13.6 Verify message table scales efficiently with many messages

## 14. Final Validation

- [ ] 14.1 Run all tests locally (unit + integration)
- [ ] 14.2 Verify OpenAPI documentation is complete and accurate
- [ ] 14.3 Manual testing of complete chat flow
- [ ] 14.4 Test error scenarios (missing session, API down, invalid input)
- [ ] 14.5 Code review for style, best practices, and documentation
- [ ] 14.6 Verify all environment variables documented in .env.example
