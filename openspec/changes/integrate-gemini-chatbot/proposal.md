# Proposal: Integrate Google Gemini Chatbot

## Why

SafeSpace currently provides anonymous session infrastructure but lacks an AI companion to deliver empathetic, responsive emotional support. Integrating Google Gemini (gemini-2.5-flash-lite model) enables the platform to provide real-time, context-aware emotional support conversations that validate user feelings and maintain session history. This is essential for SafeSpace's core mission of providing accessible mental health support.

## What Changes

- Add **message storage system** with SQLAlchemy ORM model linking messages to anonymous sessions
- Add **Google Gemini API integration** using google-generativeai SDK with system prompts for empathetic companion behavior
- Add **chat endpoints** for sending messages and retrieving conversation history
- Add **environment-based credential management** for GOOGLE_API_KEY
- Add **context-aware conversations** leveraging session message history for coherent multi-turn chat
- Extend **existing session infrastructure** to support chat message operations

## Capabilities

### New Capabilities
- `chat-message-model`: SQLAlchemy message model with session linking, role (user/model), content, and timestamps
- `gemini-sdk-integration`: Google Generativeai client initialization, model configuration, and API calls with system instructions
- `chat-endpoints`: FastAPI routes for sending user messages and retrieving chat history with session context
- `empathetic-companion-instructions`: System prompt configuration for Gemini to act as non-judgmental emotional support companion
- `chat-history-retrieval`: Database queries to fetch conversation context and message history for sessions

### Modified Capabilities
- `postgres-connection`: Extend database configuration to support chat message model (already async-ready, no requirement changes needed)
- `initial-fastapi-hello-endpoint`: Add new chat endpoints alongside existing hello world endpoint

## Impact

- **Database**: New `messages` table with foreign key to `sessions` table; requires async ORM integration with existing connection pool
- **APIs**: Two new versioned endpoints under `/api/v1/sessions/{session_id}/chat` (POST for sending, GET for history)
- **Dependencies**: Add `google-generativeai` library to requirements.txt
- **Configuration**: Add `GOOGLE_API_KEY` environment variable to `.env`
- **Architecture**: Stateless endpoint design using session_id for context; message history retrieved per-request for context-awareness
- **Security**: API key management via environment variables; user anonymity preserved (no identification in messages)
