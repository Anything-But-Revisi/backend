# Specification: Gemini SDK Integration

## ADDED Requirements

### Requirement: Google Generativeai SDK Initialization
The system SHALL initialize the Gemini API client with proper credentials.

#### Scenario: API key from environment
- **WHEN** the application starts
- **THEN** GOOGLE_API_KEY is read from environment variables

#### Scenario: SDK client creation
- **WHEN** the API key is available
- **THEN** a google.generativeai.GenerativeModel is created and configured

#### Scenario: Model selection
- **WHEN** the Gemini client is initialized
- **THEN** the model is set to "gemini-2.5-flash-lite" for optimal speed and cost

#### Scenario: Graceful key missing handling
- **WHEN** GOOGLE_API_KEY is not set
- **THEN** application startup logs a warning and disables chat endpoints (or returns 503 on chat requests)

### Requirement: System Prompt Configuration
The system SHALL configure Gemini with empathetic companion system instructions.

#### Scenario: Default system prompt
- **WHEN** the Gemini model is initialized
- **THEN** a system prompt is set instructing the model to be an empathetic, non-judgmental emotional support companion

#### Scenario: System instruction content
- **WHEN** the system prompt is applied
- **THEN** it includes directives to validate feelings, avoid judgment, never prescribe medical advice, and maintain confidentiality

#### Scenario: Prompt immutability
- **WHEN** the system prompt is loaded
- **THEN** it cannot be modified per-request (only by application restart or via admin configuration)

### Requirement: Conversation Context Handling
The system SHALL maintain conversation history for context in API calls.

#### Scenario: Message history formatting
- **WHEN** preparing a Gemini API request
- **THEN** previous messages from the session are formatted with role ("user" or "model") and content

#### Scenario: Complete history inclusion
- **WHEN** a user sends a message
- **THEN** ALL prior messages in the session history are included in the API request for full context

#### Scenario: Role mapping
- **WHEN** messages are sent to Gemini API
- **THEN** "user" messages are labeled as user role and "model" messages are labeled as model role

### Requirement: API Request and Response Handling
The system SHALL handle Gemini API requests and responses correctly.

#### Scenario: Message send request
- **WHEN** a user message is processed
- **THEN** a request is sent to Gemini API with full conversation history plus new user message

#### Scenario: Text response extraction
- **WHEN** a response is received from Gemini
- **THEN** the text content is extracted from the API response object

#### Scenario: Response validation
- **WHEN** a Gemini response is received
- **THEN** it contains at least one text candidate with content (no empty responses)

### Requirement: Error Handling
The system SHALL handle API failures gracefully.

#### Scenario: API unavailable
- **WHEN** Gemini API is unreachable or returns an error
- **THEN** the endpoint returns HTTP 503 Service Unavailable with error details

#### Scenario: Rate limiting
- **WHEN** Gemini API returns rate limit error
- **THEN** the endpoint returns HTTP 503 and includes retry-after information if available

#### Scenario: Invalid API key
- **WHEN** API key is missing or invalid and chat is requested
- **THEN** the endpoint returns HTTP 503 with instruction to configure GOOGLE_API_KEY

#### Scenario: Malformed response
- **WHEN** Gemini returns an unexpected response format
- **THEN** the application logs the error and returns HTTP 500 Internal Server Error
