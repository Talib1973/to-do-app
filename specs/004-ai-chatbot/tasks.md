# Tasks: AI Chatbot for Task Management

**Feature**: 004-ai-chatbot
**Date**: 2026-02-07
**Branch**: `004-ai-chatbot`
**References**: [spec.md](./spec.md), [plan.md](./plan.md), [data-model.md](./data-model.md)

## Overview

This document breaks down the AI Chatbot feature into executable, dependency-ordered tasks organized by user story priority. The implementation follows the layered approach: Foundation → Core → Integration, with each user story representing an independently testable increment.

---

## Task Summary

| Phase | User Story | Task Count | Parallel Tasks |
|-------|------------|------------|----------------|
| Phase 1: Setup | - | 3 | 2 |
| Phase 2: Foundation | - | 6 | 4 |
| Phase 3: US1 | Natural Language Task Creation (P1) | 8 | 5 |
| Phase 4: US6 | Conversation Continuity (P2) | 4 | 3 |
| Phase 5: US2 | Conversational Task Queries (P2) | 2 | 2 |
| Phase 6: US3-5 | Full CRUD via Chat (P3-P5) | 3 | 3 |
| Phase 7: Polish | Cross-Cutting Concerns | 3 | 2 |
| **Total** | **6 User Stories** | **29** | **21** |

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (US1) = Natural Language Task Creation
**Iteration 1**: Add Phase 4 (US6) + Phase 5 (US2) = Conversation queries and continuity
**Iteration 2**: Add Phase 6 (US3-5) = Full CRUD operations

---

## Phase 1: Setup (Environment & Dependencies)

**Goal**: Install dependencies and configure environment for AI chatbot development.

**Prerequisites**: None (starting point)

**Tasks**:

- [ ] T001 [P] Install backend AI dependencies in backend/requirements.txt (openai-agents-sdk, mcp, fastmcp)
- [ ] T002 [P] Install frontend chat dependencies in frontend/package.json (@openai/chatkit)
- [ ] T003 Configure environment variables in backend/.env (AI_PROVIDER, OPENROUTER_API_KEY or OPENAI_API_KEY, AI_MODEL)

**Completion Criteria**:
- Dependencies installed without errors
- Environment variables configured with valid API keys
- `pip list` shows openai-agents-sdk, mcp, fastmcp
- `npm list` shows @openai/chatkit

---

## Phase 2: Foundation (Database Schema & Models)

**Goal**: Create database schema for conversations and messages with proper indexes and relationships.

**Prerequisites**: Phase 1 complete

**Blocking For**: All user stories (US1-US6)

**Tasks**:

- [ ] T004 [P] Create Conversation model in backend/src/models/conversation.py with SQLModel (id, user_id, created_at, updated_at, relationships)
- [ ] T005 [P] Create Message model in backend/src/models/message.py with SQLModel (id, conversation_id, user_id, role, content, created_at, relationships)
- [ ] T006 [P] Update User model in backend/src/models/user.py to add conversations and messages relationships
- [ ] T007 [P] Create Alembic migration for conversations table with indexes (user_id, user_id+updated_at composite)
- [ ] T008 Create Alembic migration for messages table with composite index (user_id, conversation_id, created_at)
- [ ] T009 Run migrations and verify tables created with correct indexes in database

**Completion Criteria**:
- `conversations` table exists with indexes: id (PK), user_id, (user_id, updated_at)
- `messages` table exists with composite index: (user_id, conversation_id, created_at)
- Foreign keys enforced: messages.conversation_id → conversations.id, messages.user_id → users.id
- SQLModel models pass validation tests
- Query: `EXPLAIN SELECT * FROM messages WHERE user_id=? AND conversation_id=? ORDER BY created_at` uses composite index

---

## Phase 3: User Story 1 - Natural Language Task Creation (P1 - MVP)

**Goal**: Users can create tasks by telling the chatbot what they need to remember.

**Prerequisites**: Phase 2 complete (database schema ready)

**Independent Test Criteria**:
- Send message "I need to buy groceries" → verify task created in database with title "Buy groceries"
- Send message "Add a task to call mom tonight" → verify task created with title "Call mom tonight"
- Check database: task exists with correct user_id, title, completed=false

**Tasks**:

### MCP Tools Layer

- [ ] T010 [P] [US1] Create MCP tool `add_task` in backend/src/ai/tools.py (accepts user_id, title, description; returns task data or error)
- [ ] T011 [P] [US1] Create MCP tool `list_tasks` in backend/src/ai/tools.py (accepts user_id, status filter; returns array of tasks)
- [ ] T012 [P] [US1] Create MCP server initialization in backend/src/ai/mcp_server.py (register tools with @mcp.tool() decorator)

### AI Agent Layer

- [ ] T013 [P] [US1] Create AI agent handler in backend/src/ai/agent.py (initializes OpenAI Agents SDK, loads conversation history, registers MCP tools)
- [ ] T014 [US1] Configure agent system prompt in backend/src/ai/agent.py (defines task management domain, explains MCP tools, instructs on natural language interpretation)

### Chat API Layer

- [ ] T015 [P] [US1] Create chat request/response schemas in backend/src/schemas/chat.py (ChatRequest, ChatResponse, MessageSchema)
- [ ] T016 [US1] Create POST /api/{user_id}/chat endpoint in backend/src/api/chat.py (JWT auth, user validation, conversation creation, message persistence, agent invocation)
- [ ] T017 [US1] Add chat routes to FastAPI app in backend/src/main.py

**Completion Criteria (US1)**:
- MCP tools (add_task, list_tasks) callable and return correct responses
- AI agent interprets "I need to buy groceries" and calls add_task MCP tool
- POST /api/{user_id}/chat accepts message, returns assistant response
- Database contains: new conversation, user message, assistant message, new task
- Integration test: `curl -X POST /api/{user_id}/chat -H "Authorization: Bearer {jwt}" -d '{"message":"Add task to buy milk"}' → 200 OK, task created`

---

## Phase 4: User Story 6 - Conversation Continuity (P2)

**Goal**: Users can resume conversations across sessions with full history.

**Prerequisites**: Phase 3 complete (chat endpoint functional)

**Independent Test Criteria**:
- Create conversation, send 3 messages, close browser
- Reopen browser, navigate to chat with conversation_id
- Verify all 3 message pairs (user + assistant) are displayed
- Send new message → verify it appends to existing conversation

**Tasks**:

### Frontend Chat UI

- [ ] T018 [P] [US6] Create ChatInterface component in frontend/src/components/chat/ChatInterface.tsx (displays messages, handles input, calls chat API)
- [ ] T019 [P] [US6] Create ChatMessage component in frontend/src/components/chat/ChatMessage.tsx (renders user/assistant messages with styling)
- [ ] T020 [P] [US6] Create ChatInput component in frontend/src/components/chat/ChatInput.tsx (message input field, send button, loading state)
- [ ] T021 [US6] Create chat page in frontend/src/app/chat/page.tsx (protected route, loads conversation history on mount, manages conversation_id)

**Completion Criteria (US6)**:
- Frontend loads conversation history from database via GET /api/{user_id}/chat/{conversation_id}
- Messages displayed chronologically with visual distinction (user on right, assistant on left)
- Page refresh preserves conversation history
- Browser close + reopen loads same conversation (if conversation_id in URL or localStorage)
- New message appends to existing conversation without creating duplicate

---

## Phase 5: User Story 2 - Conversational Task Queries (P2)

**Goal**: Users can ask chatbot to show their tasks using natural language.

**Prerequisites**: Phase 3 complete (add_task and list_tasks MCP tools exist)

**Independent Test Criteria**:
- Create 3 pending tasks and 2 completed tasks
- Send message "What are my pending tasks?" → verify chatbot lists only 3 pending tasks
- Send message "Show all tasks" → verify chatbot lists all 5 tasks
- Send message "What have I finished?" → verify chatbot lists only 2 completed tasks

**Tasks**:

- [ ] T022 [P] [US2] Enhance agent system prompt in backend/src/ai/agent.py to handle task query patterns ("show tasks", "what's pending", "list completed")
- [ ] T023 [P] [US2] Add chat API methods to frontend API client in frontend/src/lib/api/chat.ts (sendMessage, loadConversation)

**Completion Criteria (US2)**:
- AI agent interprets "Show my tasks" and calls list_tasks(user_id, "all")
- AI agent interprets "What's pending?" and calls list_tasks(user_id, "pending")
- AI agent formats task list in natural language response (not raw JSON)
- Frontend displays assistant response with task list
- Integration test: Send "Show tasks" → response contains task titles

---

## Phase 6: User Story 3-5 - Full CRUD via Chat (P3-P5)

**Goal**: Users can complete, update, and delete tasks via natural language.

**Prerequisites**: Phase 3 complete (MCP server and agent functional)

**Independent Test Criteria**:
- US3: Send "I finished buying groceries" → verify task marked complete in database
- US4: Send "Change task 1 to 'Call mom at 6pm'" → verify task title updated
- US5: Send "Delete the meeting task" → verify task removed from database

**Tasks**:

- [ ] T024 [P] [US3] Create MCP tool `complete_task` in backend/src/ai/tools.py (accepts user_id, task_id; marks task complete)
- [ ] T025 [P] [US4] Create MCP tool `update_task` in backend/src/ai/tools.py (accepts user_id, task_id, optional title/description; updates task)
- [ ] T026 [P] [US5] Create MCP tool `delete_task` in backend/src/ai/tools.py (accepts user_id, task_id; removes task)

**Completion Criteria (US3-5)**:
- AI agent interprets "Mark task 3 done" and calls complete_task(user_id, 3)
- AI agent interprets "Change task to X" and calls update_task(user_id, task_id, "X")
- AI agent interprets "Delete task Y" and calls delete_task(user_id, task_id)
- Multi-step tool chains work: "I finished groceries" → list_tasks (to find task) → complete_task
- Database updates reflect task status changes, title updates, deletions

---

## Phase 7: Polish & Cross-Cutting Concerns

**Goal**: Error handling, user experience improvements, and deployment readiness.

**Prerequisites**: Phase 6 complete (all user stories functional)

**Tasks**:

- [ ] T027 [P] Add error handling to chat endpoint for AI API failures (500 with user-friendly message), rate limits (503), invalid JWT (401)
- [ ] T028 [P] Add link to chat page from dashboard in frontend/src/app/dashboard/page.tsx
- [ ] T029 Update backend README with environment variable documentation and chat endpoint usage

**Completion Criteria (Polish)**:
- AI API down → user sees "I'm having trouble right now. Please try again in a moment."
- Invalid JWT → 401 Unauthorized
- User ID mismatch (route vs JWT) → 403 Forbidden
- Chat page accessible from dashboard navigation
- README documents AI_PROVIDER, OPENROUTER_API_KEY, OPENAI_API_KEY variables

---

## Dependency Graph

```text
Phase 1 (Setup)
    ↓
Phase 2 (Foundation: Database Schema)
    ↓
    ├──→ Phase 3 (US1: Natural Language Task Creation) ← MVP COMPLETE
    │         ↓
    │    ├──→ Phase 4 (US6: Conversation Continuity)
    │    │         ↓
    │    ├──→ Phase 5 (US2: Conversational Task Queries)
    │    │         ↓
    │    └──→ Phase 6 (US3-5: Full CRUD via Chat)
    │              ↓
    └────────→ Phase 7 (Polish & Error Handling)
```

**Blocking Relationships**:
- Phase 2 blocks all user stories (database schema required)
- Phase 3 (US1) blocks all subsequent phases (core MCP tools + chat endpoint required)
- Phase 4, 5, 6 are independent (can be implemented in any order after US1)

**Parallel Opportunities Within Phases**:
- Phase 1: T001, T002 can run in parallel (different files)
- Phase 2: T004, T005, T006, T007 can run in parallel (different files)
- Phase 3: T010, T011, T012, T013, T015 can run in parallel (different modules)
- Phase 4: T018, T019, T020 can run in parallel (different components)
- Phase 6: T024, T025, T026 can run in parallel (different tools, same file but separate functions)

---

## Parallel Execution Examples

### Backend Team Workflow (Phase 2 + 3)

**Week 1: Foundation (Phase 2)**
```bash
Developer A: T004 + T007 (Conversation model + migration)
Developer B: T005 + T008 (Message model + migration)
Developer C: T006 (Update User model)
Join: T009 (Run migrations together)
```

**Week 2: MCP Tools & Agent (Phase 3)**
```bash
Developer A: T010 + T011 (add_task, list_tasks tools)
Developer B: T012 + T013 (MCP server, AI agent)
Developer C: T015 (Chat schemas)
Join: T016 + T017 (Chat endpoint + routes integration)
```

### Frontend Team Workflow (Phase 4)

**Parallel Component Development**
```bash
Developer A: T018 (ChatInterface component)
Developer B: T019 (ChatMessage component)
Developer C: T020 (ChatInput component)
Join: T021 (Integrate components in chat page)
```

### Full Stack Parallel Development

**Backend & Frontend in Parallel (After Phase 3)**
```bash
Backend Team: Phase 6 (T024, T025, T026 - additional MCP tools)
Frontend Team: Phase 4 (T018-T021 - chat UI components)
Integration: Both teams join for testing after completion
```

---

## Testing Strategy

### Contract Tests (MCP Tools)

**Test each MCP tool independently** (after Phase 3, before Phase 5-6):
```python
def test_add_task_tool():
    result = await add_task(user_id, "Test Task", "Description")
    assert result["status"] == "success"
    assert result["data"]["title"] == "Test Task"

def test_list_tasks_user_scoping():
    # Create task for user A
    await add_task(user_a_id, "User A Task", "")
    # Create task for user B
    await add_task(user_b_id, "User B Task", "")
    # List tasks for user A
    result = await list_tasks(user_a_id, "all")
    # Should only return user A's task
    assert len(result["data"]) == 1
    assert result["data"][0]["title"] == "User A Task"
```

### Integration Tests (Chat Endpoint)

**Test full request/response lifecycle** (after Phase 3):
```python
def test_chat_endpoint_creates_task():
    response = client.post(
        f"/api/{user_id}/chat",
        headers={"Authorization": f"Bearer {jwt}"},
        json={"conversation_id": None, "message": "Add task to buy milk"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    # Verify task created in database
    task = db.query(Task).filter_by(user_id=user_id, title="Buy milk").first()
    assert task is not None
```

### Authorization Tests

**Verify user scoping** (after Phase 3):
```python
def test_cross_user_conversation_access():
    # User A creates conversation
    conv = create_conversation(user_a_id)
    # User B tries to access User A's conversation
    response = client.post(
        f"/api/{user_b_id}/chat",
        headers={"Authorization": f"Bearer {user_b_jwt}"},
        json={"conversation_id": conv.id, "message": "Test"}
    )
    # Should get 404 (conversation not found for user B)
    assert response.status_code == 404
```

### Performance Tests

**Measure response times** (after Phase 4):
```python
def test_message_history_load_performance():
    # Create conversation with 100 messages
    conv = create_conversation(user_id)
    for i in range(100):
        create_message(conv.id, user_id, f"Message {i}")

    # Measure query time
    start = time.time()
    messages = db.query(Message).filter_by(
        user_id=user_id, conversation_id=conv.id
    ).order_by(Message.created_at).all()
    duration = time.time() - start

    # Should complete in <100ms
    assert duration < 0.1
    assert len(messages) == 100
```

---

## Implementation Strategy

### MVP Approach (Fastest Path to Value)

**Goal**: Ship natural language task creation ASAP

**Scope**: Phase 1 + Phase 2 + Phase 3 (US1 only)

**Timeline**: ~1-2 weeks
- Week 1: Backend (Database schema, MCP tools, AI agent, chat endpoint)
- Week 2: Frontend (Basic chat UI, API integration, testing)

**Deliverable**: Users can open chat interface, type "I need to buy groceries", and see task created

**Validation**: Integration test passes, manual smoke test works, deployed to staging

---

### Iteration 1: Conversation Experience

**Goal**: Add conversation persistence and task queries

**Scope**: Phase 4 (US6) + Phase 5 (US2)

**Timeline**: ~1 week
- Phase 4: Conversation history loading, persistent UI state (3 days)
- Phase 5: Enhanced agent prompt for task queries (2 days)

**Deliverable**: Users can resume conversations and ask "Show my tasks"

**Validation**: Conversation persists across sessions, task queries work correctly

---

### Iteration 2: Full CRUD Operations

**Goal**: Complete all task management operations via chat

**Scope**: Phase 6 (US3-5)

**Timeline**: ~3 days
- Implement 3 additional MCP tools (complete, update, delete)
- Test multi-step tool chains (e.g., "I finished groceries" → list → complete)

**Deliverable**: Users can manage entire task lifecycle via chat

**Validation**: All CRUD operations work via natural language

---

### Iteration 3: Polish & Production

**Goal**: Error handling, UX improvements, deployment

**Scope**: Phase 7 (Polish)

**Timeline**: ~2-3 days
- Error handling for AI API failures, invalid auth
- Dashboard navigation link
- Documentation updates

**Deliverable**: Production-ready feature with graceful error handling

**Validation**: All error scenarios tested, deployed to production

---

## Risk Mitigation Tasks

### AI API Cost Monitoring

**Task** (after Phase 3): Implement token usage logging
```python
# In agent.py
logger.info(f"AI request: {len(conversation_history)} messages, model={AI_MODEL}")
# Log response token count from OpenAI/OpenRouter API
logger.info(f"AI response: {response.usage.total_tokens} tokens, cost=${estimated_cost}")
```

**Monitoring**: Alert if daily token usage exceeds budget

---

### Performance Optimization

**Task** (if Phase 4 performance tests fail): Implement conversation truncation
```python
# Load only last 50 messages for context
recent_messages = db.query(Message).filter_by(
    conversation_id=conversation_id
).order_by(Message.created_at.desc()).limit(50).all()
messages = list(reversed(recent_messages))
```

**Trigger**: If conversation history load time >100ms for 100+ message conversations

---

### Natural Language Accuracy Improvement

**Task** (if Phase 5 accuracy <90%): Enhance system prompt with examples
```python
system_prompt = """
You are a task management assistant. Examples of commands:
- "Add task to buy groceries" → add_task(user_id, "Buy groceries", "")
- "Show my tasks" → list_tasks(user_id, "all")
- "What's pending?" → list_tasks(user_id, "pending")
- "Mark task 3 done" → complete_task(user_id, 3)
"""
```

**Validation**: Log tool calls and manually review accuracy

---

## Deployment Checklist

**Before deploying to production**:

- [ ] All Phase 1-7 tasks completed
- [ ] Environment variables configured in deployment (AI_PROVIDER, API keys, BETTER_AUTH_SECRET)
- [ ] Database migrations applied to production database
- [ ] Composite index on messages table verified (EXPLAIN query plan)
- [ ] Integration tests passing (contract tests + chat endpoint tests)
- [ ] Authorization tests passing (cross-user protection verified)
- [ ] Performance tests passing (<3s response time for 95% of requests)
- [ ] Error handling tested (AI API down, invalid JWT, rate limits)
- [ ] Frontend deployed to Vercel with correct API_BASE_URL
- [ ] Backend deployed to Hugging Face Spaces with environment variables
- [ ] Health check endpoint returns success
- [ ] Manual smoke test: Login → Open chat → Send "Add task X" → Verify task created

---

## Success Metrics

**Post-Deployment Monitoring**:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chat adoption rate | 20% of active users try chat in first week | Analytics: unique users on /chat page |
| Task creation via chat | 10% of new tasks created via chat | Database: count tasks created via chat endpoint |
| Natural language accuracy | 90% of commands correctly interpreted | Logging: tool calls vs user intent (manual review) |
| Response time (p95) | <3 seconds | APM: chat endpoint response time distribution |
| AI API cost | <$50/month for 1000 users | OpenRouter/OpenAI billing dashboard |
| Error rate | <1% of chat requests fail | Logging: count 500/503 responses |
| Conversation continuity | 100% of conversations persist | Database: message retention validation |

---

## Task Format Validation

✅ **All tasks follow checklist format**:
- Checkbox: `- [ ]`
- Task ID: T001-T029 (sequential)
- [P] marker: 21 parallelizable tasks identified
- [Story] label: US1 (8 tasks), US6 (4 tasks), US2 (2 tasks), US3-5 (3 tasks combined)
- Description: Includes file paths and clear actions

**Total**: 29 tasks
**Parallelizable**: 21 tasks (72% can be executed in parallel)
**Story-specific**: 17 tasks (59% mapped to user stories)
**Foundation**: 9 tasks (31% setup + foundational)

---

## Next Steps

1. **Start Implementation**: Begin with Phase 1 (T001-T003) to set up environment
2. **Database Layer**: Move to Phase 2 (T004-T009) to create schema and migrations
3. **MVP Development**: Implement Phase 3 (T010-T017) for natural language task creation
4. **Test MVP**: Run integration tests, deploy to staging, validate US1 acceptance scenarios
5. **Iteration Planning**: After MVP validation, prioritize Phase 4-6 based on user feedback

**Command to track progress**: Use task management system to mark tasks complete as they're finished. Each phase completion should be validated against its completion criteria before proceeding to dependent phases.
