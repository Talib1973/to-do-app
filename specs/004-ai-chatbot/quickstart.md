# Quickstart Guide: AI Chatbot Development

**Feature**: 004-ai-chatbot
**Date**: 2026-02-07
**Audience**: Developers implementing the AI chatbot feature
**Prerequisites**: Familiarity with FastAPI, Next.js, PostgreSQL, and Python async programming

## Overview

This guide helps developers set up a local development environment for the AI Chatbot feature, test the implementation, and understand the component interactions.

---

## Environment Setup

### 1. Install Dependencies

**Backend** (`/backend`):

```bash
cd backend
pip install openai-agents-sdk mcp fastmcp
```

**Frontend** (`/frontend`):

```bash
cd frontend
npm install @openai/chatkit
```

### 2. Configure Environment Variables

Create or update `/backend/.env`:

```env
# Existing variables
DATABASE_URL=postgresql://user:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-jwt-secret-key

# NEW: AI Provider Configuration
AI_PROVIDER=openrouter  # or "openai"
OPENROUTER_API_KEY=sk-or-v1-...  # If using OpenRouter
OPENAI_API_KEY=sk-...  # If using OpenAI
AI_MODEL=anthropic/claude-3.5-haiku  # For OpenRouter, or gpt-4o-mini for OpenAI
```

**Environment Variable Guide**:

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `AI_PROVIDER` | Yes | Which AI service to use | `openrouter` or `openai` |
| `OPENROUTER_API_KEY` | If using OpenRouter | OpenRouter API key | `sk-or-v1-...` |
| `OPENAI_API_KEY` | If using OpenAI | OpenAI API key | `sk-...` |
| `AI_MODEL` | No | Model to use (defaults vary by provider) | `anthropic/claude-3.5-haiku` |

**Cost-Effective Setup** (Recommended):
- Use `AI_PROVIDER=openrouter`
- Use `AI_MODEL=anthropic/claude-3.5-haiku` (~$0.25 per 1M tokens)
- Alternative: `meta-llama/llama-3.1-8b-instruct` (~$0.06 per 1M tokens)

**Production Setup**:
- Use `AI_PROVIDER=openai`
- Use `AI_MODEL=gpt-4o-mini` for balance of cost and capability
- Or `gpt-4o` for maximum capability

### 3. Database Migration

Run Alembic migration to create new tables:

```bash
cd backend
alembic revision --autogenerate -m "Add conversations and messages tables"
alembic upgrade head
```

**Verify Migration**:

```bash
psql $DATABASE_URL -c "\dt"
```

Expected output should include:
```
conversations
messages
tasks
users
```

---

## Development Workflow

### Phase 1: Database Layer

**Goal**: Verify conversation and message models work correctly.

1. **Create Models** (`/backend/src/models/conversation.py`, `/backend/src/models/message.py`):
   - Define SQLModel classes with proper foreign keys
   - Add composite indexes as specified in [data-model.md](./data-model.md)

2. **Test Database Operations**:

```python
# backend/tests/test_db_operations.py
import pytest
from src.models.conversation import Conversation
from src.models.message import Message

@pytest.mark.asyncio
async def test_create_conversation(db_session, test_user):
    """Verify conversation creation."""
    conversation = Conversation(user_id=test_user.id)
    db_session.add(conversation)
    await db_session.commit()
    await db_session.refresh(conversation)

    assert conversation.id is not None
    assert conversation.user_id == test_user.id

@pytest.mark.asyncio
async def test_add_message(db_session, test_conversation):
    """Verify message creation."""
    message = Message(
        conversation_id=test_conversation.id,
        user_id=test_conversation.user_id,
        role="user",
        content="Test message"
    )
    db_session.add(message)
    await db_session.commit()

    assert message.id is not None
    assert message.role == "user"
```

Run tests:
```bash
pytest backend/tests/test_db_operations.py -v
```

---

### Phase 2: MCP Tools

**Goal**: Implement and test MCP tools independently from AI agent.

1. **Create MCP Server** (`/backend/src/ai/mcp_server.py`):
   - Import fastmcp
   - Define 5 tools using `@mcp.tool()` decorator
   - Follow contracts in [mcp-tools.md](./contracts/mcp-tools.md)

2. **Test MCP Tools Directly**:

```python
# backend/tests/test_mcp_tools.py
import pytest
from src.ai.tools import add_task, list_tasks, complete_task

@pytest.mark.asyncio
async def test_add_task_tool(db_session, test_user):
    """Test add_task MCP tool."""
    result = await add_task(
        user_id=test_user.id,
        title="Test Task",
        description="Test Description"
    )

    assert result["status"] == "success"
    assert result["data"]["title"] == "Test Task"
    assert result["error"] is None

@pytest.mark.asyncio
async def test_list_tasks_user_scoping(db_session, test_user, other_user):
    """Verify user scoping in list_tasks."""
    # Create task for test_user
    await add_task(test_user.id, "User 1 Task", "")

    # Create task for other_user
    await add_task(other_user.id, "User 2 Task", "")

    # List tasks for test_user
    result = await list_tasks(test_user.id, "all")

    # Should only return test_user's task
    assert len(result["data"]) == 1
    assert result["data"][0]["title"] == "User 1 Task"
```

Run tests:
```bash
pytest backend/tests/test_mcp_tools.py -v
```

---

### Phase 3: AI Agent Integration

**Goal**: Set up OpenAI Agents SDK and connect to MCP tools.

1. **Create Agent Handler** (`/backend/src/ai/agent.py`):
   - Initialize OpenAI client with configurable base_url
   - Load conversation history from database
   - Register MCP tools
   - Process user message
   - Return assistant response

2. **Test Agent Locally** (without full API):

```python
# backend/tests/test_agent.py
import pytest
from src.ai.agent import run_agent

@pytest.mark.asyncio
async def test_agent_add_task(db_session, test_user, test_conversation):
    """Test agent interprets 'add task' command."""
    user_message = "I need to buy groceries tomorrow"

    response = await run_agent(
        user_id=test_user.id,
        conversation_id=test_conversation.id,
        user_message=user_message,
        conversation_history=[]
    )

    # Verify assistant response mentions task creation
    assert "added" in response["content"].lower() or "created" in response["content"].lower()

    # Verify add_task tool was called
    assert any(call["tool"] == "add_task" for call in response["tool_calls"])

@pytest.mark.asyncio
async def test_agent_list_tasks(db_session, test_user, test_conversation):
    """Test agent interprets 'show tasks' command."""
    # Add some tasks first
    await add_task(test_user.id, "Task 1", "")
    await add_task(test_user.id, "Task 2", "")

    user_message = "Show me all my tasks"

    response = await run_agent(
        user_id=test_user.id,
        conversation_id=test_conversation.id,
        user_message=user_message,
        conversation_history=[]
    )

    # Verify list_tasks tool was called
    assert any(call["tool"] == "list_tasks" for call in response["tool_calls"])

    # Verify response mentions both tasks
    assert "Task 1" in response["content"]
    assert "Task 2" in response["content"]
```

Run tests:
```bash
pytest backend/tests/test_agent.py -v
```

**Important**: These tests will make real API calls to OpenAI/OpenRouter. Monitor usage and costs.

---

### Phase 4: Chat API Endpoint

**Goal**: Implement POST `/api/{user_id}/chat` endpoint with full lifecycle.

1. **Create Endpoint** (`/backend/src/api/chat.py`):
   - JWT authentication
   - User ID validation
   - Conversation creation/loading
   - Message persistence
   - Agent invocation
   - Response formatting

2. **Test Endpoint**:

```python
# backend/tests/test_chat_endpoint.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_chat_endpoint_new_conversation(client: AsyncClient, auth_headers):
    """Test creating new conversation."""
    response = await client.post(
        "/api/550e8400-e29b-41d4-a716-446655440000/chat",
        headers=auth_headers,
        json={
            "conversation_id": None,
            "message": "I need to buy groceries"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "conversation_id" in data
    assert data["message"]["role"] == "assistant"
    assert len(data["tool_calls"]) > 0

@pytest.mark.asyncio
async def test_chat_endpoint_existing_conversation(client, auth_headers, test_conversation):
    """Test continuing existing conversation."""
    response = await client.post(
        f"/api/{test_conversation.user_id}/chat",
        headers=auth_headers,
        json={
            "conversation_id": str(test_conversation.id),
            "message": "What tasks do I have?"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert data["conversation_id"] == str(test_conversation.id)

@pytest.mark.asyncio
async def test_chat_endpoint_user_mismatch(client, auth_headers, other_user):
    """Test 403 when route user_id doesn't match JWT."""
    response = await client.post(
        f"/api/{other_user.id}/chat",  # Different user in route
        headers=auth_headers,  # JWT for test_user
        json={
            "conversation_id": None,
            "message": "Test"
        }
    )

    assert response.status_code == 403
```

Run tests:
```bash
pytest backend/tests/test_chat_endpoint.py -v
```

---

### Phase 5: Frontend Integration

**Goal**: Build ChatKit-based UI connected to backend.

1. **Create Chat Components** (`/frontend/src/components/chat/`):
   - `ChatInterface.tsx` - Main chat container
   - `ChatMessage.tsx` - Message display component
   - `ChatInput.tsx` - Message input field

2. **Create Chat Page** (`/frontend/src/app/chat/page.tsx`):
   - Protected route (requires authentication)
   - Loads conversation history on mount
   - Sends messages to `/api/{user_id}/chat`
   - Displays AI responses

3. **Test Frontend Locally**:

```bash
cd frontend
npm run dev
```

Navigate to `http://localhost:3000/chat` and:
1. Log in with test user
2. Send message: "I need to buy groceries"
3. Verify AI response appears
4. Check developer tools network tab → verify API call to `/api/{user_id}/chat`
5. Refresh page → verify conversation persists

---

## Manual Testing Scenarios

### Scenario 1: Natural Language Task Creation

**Steps**:
1. Open chat interface
2. Send message: "Add a task to buy groceries"
3. Verify response: "I've added 'Buy groceries' to your tasks"
4. Open task list page → verify task appears

**Expected Behavior**:
- Chat endpoint creates new conversation (if first message)
- AI agent calls `add_task` MCP tool
- Task appears in database with correct user_id
- Conversation and messages persisted

---

### Scenario 2: Conversational Task Queries

**Steps**:
1. Create 3 tasks (2 pending, 1 completed)
2. Send message: "What are my pending tasks?"
3. Verify response lists only 2 pending tasks
4. Send message: "Show all tasks"
5. Verify response lists all 3 tasks

**Expected Behavior**:
- AI agent calls `list_tasks` with appropriate filter
- Response is conversational (not raw JSON)
- Conversation context is maintained

---

### Scenario 3: Task Completion via Chat

**Steps**:
1. Create task "Buy groceries"
2. Send message: "I'm done with buying groceries"
3. Verify response: "Great! I've marked 'Buy groceries' as complete"
4. Check task list → verify task marked complete

**Expected Behavior**:
- AI agent calls `list_tasks` to find task
- AI agent calls `complete_task` with correct task_id
- Database updated correctly

---

### Scenario 4: Conversation Continuity

**Steps**:
1. Start new conversation, send message
2. Copy conversation_id from response
3. Close browser
4. Reopen browser, navigate to chat with conversation_id in URL
5. Verify previous messages are loaded

**Expected Behavior**:
- All messages loaded from database
- Conversation context available to AI agent
- New messages append to existing conversation

---

### Scenario 5: User Authorization

**Steps**:
1. Log in as User A
2. Create conversation, note conversation_id
3. Log out
4. Log in as User B
5. Attempt to access User A's conversation_id

**Expected Behavior**:
- 404 error (conversation not found)
- User B cannot see User A's messages
- Database queries filtered by user_id

---

## Debugging Tips

### Issue: AI agent not calling tools

**Symptoms**: Agent responds with text but doesn't create/update tasks

**Debug Steps**:
1. Check system prompt includes tool descriptions
2. Verify MCP tools registered correctly: `print(agent.tools)`
3. Check OpenAI/OpenRouter API logs for tool call attempts
4. Try more explicit user message: "Use the add_task tool to create a task called X"

---

### Issue: 401 Unauthorized on chat endpoint

**Symptoms**: Frontend gets 401 error when sending message

**Debug Steps**:
1. Verify JWT token in localStorage: `localStorage.getItem('access_token')`
2. Check token expiration: Decode JWT and inspect `exp` claim
3. Verify `Authorization: Bearer {token}` header sent
4. Check backend JWT verification uses correct `BETTER_AUTH_SECRET`

---

### Issue: Conversation not persisting

**Symptoms**: Messages disappear on page refresh

**Debug Steps**:
1. Check database: `SELECT * FROM conversations WHERE user_id = ...`
2. Check database: `SELECT * FROM messages WHERE conversation_id = ...`
3. Verify frontend stores `conversation_id` in state/URL
4. Check network tab: Is `conversation_id` sent in subsequent requests?

---

### Issue: Cross-user data leak

**Symptoms**: User A sees User B's tasks/conversations

**Debug Steps**:
1. **CRITICAL**: Immediately stop development and investigate
2. Check all MCP tools filter by `user_id`: `WHERE user_id = ?`
3. Check chat endpoint validates route `user_id` matches JWT `user_id`
4. Run authorization tests: `pytest backend/tests/test_authorization.py -v`
5. Review query logs for missing user_id filters

---

## Performance Monitoring

### Key Metrics to Track

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Chat endpoint response time | <3s (p95) | `time curl -X POST ... /chat` |
| Message history load time | <100ms | Database query logs |
| AI API response time | <2s (p95) | OpenAI/OpenRouter API logs |
| Concurrent chat sessions | 100+ | Load testing with `locust` or `k6` |

### Database Query Performance

Check slow queries:
```sql
-- PostgreSQL slow query log
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%messages%' OR query LIKE '%conversations%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

Verify index usage:
```sql
EXPLAIN ANALYZE
SELECT * FROM messages
WHERE user_id = '...' AND conversation_id = '...'
ORDER BY created_at ASC;
```

Expected: `Index Scan using messages_user_id_conversation_id_created_at_idx`

---

## Common Pitfalls

### ❌ Trusting Client-Provided user_id

**Wrong**:
```python
@router.post("/api/{user_id}/chat")
async def chat(user_id: UUID, request: ChatRequest):
    # Using route user_id directly
    conversation = await get_conversation(user_id, request.conversation_id)  # ⚠️ INSECURE
```

**Correct**:
```python
@router.post("/api/{user_id}/chat")
async def chat(user_id: UUID, request: ChatRequest, current_user: User = Depends(get_current_user)):
    # Verify route user_id matches JWT user_id
    if user_id != current_user.id:
        raise HTTPException(403, "User ID mismatch")

    # Use current_user.id from JWT
    conversation = await get_conversation(current_user.id, request.conversation_id)  # ✅ SECURE
```

---

### ❌ Forgetting to Update conversation.updated_at

**Wrong**:
```python
# Add message but don't update conversation timestamp
message = Message(...)
session.add(message)
await session.commit()
# ⚠️ Conversation updated_at is stale
```

**Correct**:
```python
message = Message(...)
session.add(message)

# Update conversation timestamp
conversation.updated_at = datetime.utcnow()
session.add(conversation)

await session.commit()  # ✅ Both updated
```

---

### ❌ Loading All Messages for Large Conversations

**Issue**: Conversations with 100+ messages slow down chat endpoint

**Solution** (Future Enhancement):
```python
# Load only recent N messages for context
recent_messages = await session.exec(
    select(Message)
    .where(Message.conversation_id == conversation_id)
    .order_by(Message.created_at.desc())
    .limit(50)  # Last 50 messages
).all()

# Reverse to chronological order
messages = list(reversed(recent_messages))
```

---

## Deployment Checklist

Before deploying to production:

- [ ] Environment variables configured (`AI_PROVIDER`, API keys)
- [ ] Database migrations applied (`alembic upgrade head`)
- [ ] Composite index on messages table created
- [ ] JWT verification secret matches between frontend and backend
- [ ] API keys stored securely (not in code)
- [ ] CORS configured for frontend domain
- [ ] Rate limiting enabled on chat endpoint
- [ ] Error logging configured (Sentry, Datadog, etc.)
- [ ] All tests passing (`pytest backend/tests/ -v`)
- [ ] Authorization tests verify user scoping
- [ ] Frontend deployed with correct `API_BASE_URL`
- [ ] Health check endpoint returns success

---

## Next Steps

After completing local development:

1. **Run Integration Tests**: `pytest backend/tests/ -v --cov`
2. **Deploy to Staging**: Test on Hugging Face Spaces (backend) and Vercel (frontend)
3. **User Acceptance Testing**: Validate all P1 user stories
4. **Performance Testing**: Load test with 100 concurrent users
5. **Security Audit**: Verify no cross-user data leaks
6. **Documentation**: Update API documentation with chat endpoint

**Ready for `/sp.tasks`**: Once quickstart scenarios work locally, proceed to task breakdown for implementation.
