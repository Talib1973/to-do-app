# Chat Endpoint Contract

**Feature**: 004-ai-chatbot
**Date**: 2026-02-07
**Status**: Design
**References**: [spec.md](../spec.md), [data-model.md](../data-model.md)

## Overview

The chat endpoint enables authenticated users to send messages to the AI chatbot and receive conversational responses. The endpoint manages conversation creation, message persistence, AI agent invocation, and response delivery.

---

## Endpoint: Send Message

### Request

**Method**: `POST`
**Path**: `/api/{user_id}/chat`

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | UUID | Yes | User identifier (MUST match JWT user_id) |

**Headers**:

| Header | Required | Value | Description |
|--------|----------|-------|-------------|
| Authorization | Yes | Bearer {token} | JWT token containing user_id claim |
| Content-Type | Yes | application/json | Request payload format |

**Request Body**:

```json
{
  "conversation_id": "uuid | null",
  "message": "string"
}
```

**Request Schema**:

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| conversation_id | UUID \| null | No | Must be owned by authenticated user if provided | Existing conversation ID or null for new conversation |
| message | string | Yes | 1-10000 characters, non-empty | User's message text |

**Example Request**:

```http
POST /api/550e8400-e29b-41d4-a716-446655440000/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": "Show me all my pending tasks"
}
```

**Example Request (New Conversation)**:

```http
POST /api/550e8400-e29b-41d4-a716-446655440000/chat HTTP/1.1
Host: api.example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "conversation_id": null,
  "message": "I need to buy groceries tomorrow"
}
```

---

### Response

**Success Response (200 OK)**:

```json
{
  "conversation_id": "uuid",
  "message": {
    "id": "uuid",
    "role": "assistant",
    "content": "string",
    "created_at": "ISO 8601 timestamp"
  },
  "tool_calls": [
    {
      "tool": "string",
      "parameters": {},
      "result": {}
    }
  ]
}
```

**Response Schema**:

| Field | Type | Description |
|-------|------|-------------|
| conversation_id | UUID | Conversation ID (newly created if was null in request) |
| message | object | AI assistant's response message |
| message.id | UUID | Message identifier |
| message.role | string | Always "assistant" |
| message.content | string | AI assistant's natural language response |
| message.created_at | string | ISO 8601 timestamp when response was created |
| tool_calls | array | List of MCP tools invoked by AI agent (for debugging/transparency) |
| tool_calls[].tool | string | Tool name (e.g., "add_task", "list_tasks") |
| tool_calls[].parameters | object | Parameters passed to tool |
| tool_calls[].result | object | Tool response data |

**Example Success Response**:

```json
{
  "conversation_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "message": {
    "id": "8d4f8390-3b16-42f3-9c21-5f8e7a6b4c2d",
    "role": "assistant",
    "content": "You have 3 pending tasks:\n1. Buy groceries (ID: 123)\n2. Call mom (ID: 456)\n3. Finish project report (ID: 789)\n\nWould you like to mark any of these as complete?",
    "created_at": "2026-02-07T14:32:15Z"
  },
  "tool_calls": [
    {
      "tool": "list_tasks",
      "parameters": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "pending"
      },
      "result": {
        "status": "success",
        "data": [
          {"id": "123", "title": "Buy groceries", "completed": false},
          {"id": "456", "title": "Call mom", "completed": false},
          {"id": "789", "title": "Finish project report", "completed": false}
        ]
      }
    }
  ]
}
```

---

### Error Responses

#### 400 Bad Request - Invalid Input

```json
{
  "detail": "Message cannot be empty"
}
```

**Triggers**:
- `message` field is empty or whitespace
- `message` exceeds 10000 characters
- `conversation_id` is invalid UUID format
- Missing required field

---

#### 401 Unauthorized - Missing or Invalid JWT

```json
{
  "detail": "Authentication required"
}
```

**Triggers**:
- Missing `Authorization` header
- Invalid JWT token
- Expired JWT token
- JWT signature verification fails

---

#### 403 Forbidden - User ID Mismatch

```json
{
  "detail": "User ID in route does not match authenticated user"
}
```

**Triggers**:
- `user_id` in route path does not match `user_id` from JWT token
- Attempting to access another user's conversation

---

#### 404 Not Found - Conversation Not Found

```json
{
  "detail": "Conversation not found or does not belong to user"
}
```

**Triggers**:
- `conversation_id` provided but doesn't exist
- `conversation_id` exists but belongs to different user

---

#### 500 Internal Server Error - AI API Failure

```json
{
  "detail": "I'm having trouble processing your request right now. Please try again in a moment."
}
```

**Triggers**:
- OpenAI or OpenRouter API is unavailable
- OpenAI or OpenRouter API returns error
- Database connection failure
- Unexpected server exception

---

#### 503 Service Unavailable - Rate Limit

```json
{
  "detail": "AI service is temporarily rate-limited. Please try again in 30 seconds."
}
```

**Triggers**:
- OpenAI or OpenRouter API returns 429 Too Many Requests
- Rate limit on AI provider account exceeded

---

## Business Logic

### Request Lifecycle

1. **Authentication** (GATE):
   - Extract JWT token from `Authorization: Bearer {token}` header
   - Verify JWT signature using `BETTER_AUTH_SECRET`
   - Extract `user_id` from token's `sub` claim
   - Verify `user_id` in route matches `user_id` from JWT
   - If any check fails → return 401 or 403

2. **Input Validation**:
   - Validate `message` is non-empty and ≤10000 characters
   - If `conversation_id` provided, validate UUID format
   - If validation fails → return 400

3. **Conversation Resolution**:
   - If `conversation_id` is null or not provided:
     - Create new conversation for user
     - Store in database with `user_id`, `created_at`, `updated_at`
   - If `conversation_id` provided:
     - Load conversation from database
     - Verify conversation belongs to authenticated user
     - If not found or belongs to different user → return 404

4. **Message Persistence (User Message)**:
   - Create message record with role='user', content=request.message
   - Store in database with `conversation_id`, `user_id`, `created_at`
   - Update conversation's `updated_at` timestamp

5. **Load Conversation History**:
   - Query all messages for conversation, ordered by `created_at ASC`
   - Build message array: [{role, content}, ...]

6. **AI Agent Invocation**:
   - Initialize OpenAI Agents SDK agent with conversation history
   - Provide MCP tools: add_task, list_tasks, update_task, complete_task, delete_task
   - Run agent with user's message
   - Agent may invoke 0 or more MCP tools
   - Capture tool calls for response transparency

7. **Message Persistence (Assistant Response)**:
   - Create message record with role='assistant', content=agent response
   - Store in database with `conversation_id`, `user_id`, `created_at`
   - Update conversation's `updated_at` timestamp

8. **Response Construction**:
   - Build response JSON with conversation_id, message, tool_calls
   - Return 200 OK

### Error Handling

- **AI API Failure**: Catch exceptions from OpenAI/OpenRouter SDK
  - Log error details for debugging
  - Return user-friendly 500 error message
  - Do NOT expose API keys or technical details

- **Database Failure**: Catch database exceptions
  - Log error for debugging
  - Return generic 500 error
  - Do NOT expose connection strings or schema details

- **Rate Limiting**: Catch 429 from AI provider
  - Return 503 with retry guidance
  - Log incident for monitoring

### Security Rules

- User ID MUST be extracted from JWT token only (Principle IV)
- Route parameter `user_id` MUST match JWT `user_id` (403 if mismatch)
- All database queries MUST filter by authenticated `user_id`
- Cross-user conversation access MUST be prevented
- API keys (OpenAI/OpenRouter) MUST NOT appear in responses or logs visible to users

---

## MCP Tool Invocation Flow

When AI agent interprets user message as task-related command, it invokes MCP tools:

**Example Flow**:

```
User: "I need to buy groceries tomorrow"
  ↓
Agent interprets → calls add_task MCP tool
  ↓
add_task(
  user_id="550e8400-e29b-41d4-a716-446655440000",
  title="Buy groceries tomorrow",
  description=""
)
  ↓
MCP Tool → Database INSERT INTO tasks (user_id, title, ...)
  ↓
MCP Tool returns: {status: "success", data: {id: 123, title: "Buy groceries tomorrow", ...}}
  ↓
Agent receives tool result → generates response
  ↓
Assistant: "I've added 'Buy groceries tomorrow' to your task list. Would you like to set a specific time?"
```

**Tool Call Transparency**:
Response includes `tool_calls` array showing exactly which tools were invoked. This enables:
- Debugging AI behavior
- User transparency (they know what actions were taken)
- Audit trail for security compliance

---

## Performance Requirements

| Metric | Target | Measurement Point |
|--------|--------|-------------------|
| Response Time (p95) | <3 seconds | From request received to response sent (excluding AI API latency) |
| Conversation History Load | <100ms | Database query for messages |
| Concurrent Requests | 100+ | No degradation with 100 concurrent chat sessions |
| Message Throughput | 1000+ msg/min | System-wide message processing capacity |

---

## Validation Rules

### Input Validation

```python
# Pydantic schema for request validation
class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    message: str = Field(min_length=1, max_length=10000)

    @validator('message')
    def message_not_empty(cls, v):
        if not v or v.isspace():
            raise ValueError('Message cannot be empty')
        return v.strip()
```

### Authorization Validation

```python
# JWT user_id must match route user_id
if route_user_id != jwt_user_id:
    raise HTTPException(status_code=403, detail="User ID mismatch")

# Conversation must belong to authenticated user
if conversation.user_id != jwt_user_id:
    raise HTTPException(status_code=404, detail="Conversation not found")
```

---

## Testing Scenarios

### Happy Path Tests
1. New conversation: Send message with `conversation_id=null` → verify conversation created
2. Existing conversation: Send message with valid `conversation_id` → verify message appended
3. Task creation: Send "Add task to X" → verify `add_task` tool called
4. Task listing: Send "Show my tasks" → verify `list_tasks` tool called

### Error Path Tests
1. Missing JWT → 401 Unauthorized
2. Expired JWT → 401 Unauthorized
3. User ID mismatch → 403 Forbidden
4. Invalid conversation ID → 404 Not Found
5. Cross-user conversation access → 404 Not Found
6. Empty message → 400 Bad Request
7. AI API down → 500 Internal Server Error with friendly message

### Security Tests
1. User A cannot access User B's conversation
2. JWT user_id is trusted source (route user_id ignored if mismatch)
3. Database queries filter by authenticated user_id
4. API keys not exposed in error messages

### Performance Tests
1. Load conversation with 100 messages → <100ms
2. Send message with AI response → <3 seconds (p95)
3. 100 concurrent requests → no degradation
