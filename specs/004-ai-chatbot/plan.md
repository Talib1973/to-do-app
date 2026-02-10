# Implementation Plan: AI Chatbot for Task Management

**Branch**: `004-ai-chatbot` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implement AI-powered conversational interface for task management using Model Context Protocol (MCP) server architecture. Users will interact with an AI chatbot to create, view, update, complete, and delete tasks using natural language commands. The system uses OpenAI Agents SDK for AI logic, stateless backend with database-persisted conversations, and OpenAI ChatKit for the frontend chat UI. All task operations are exposed via MCP tools, enforcing user-scoped authorization and maintaining strict security boundaries.

## Technical Context

**Language/Version**:
- Backend: Python 3.11+ (FastAPI)
- Frontend: TypeScript 5.0+ (Next.js 14 with App Router)

**Primary Dependencies**:
- Backend: FastAPI, SQLModel, OpenAI Agents SDK, MCP SDK (Official Model Context Protocol), Neon PostgreSQL driver
- Frontend: Next.js, React, OpenAI ChatKit, Tailwind CSS
- AI: OpenAI API or OpenRouter API (configurable)

**Storage**:
- PostgreSQL (Neon Serverless) with new tables: `conversations`, `messages`
- Existing table: `tasks`

**Testing**:
- Backend: pytest (contract tests for MCP tools, integration tests for chat endpoint)
- Frontend: React Testing Library (component tests for chat UI)

**Target Platform**:
- Backend: Linux server (Hugging Face Spaces deployment)
- Frontend: Vercel (Next.js deployment)

**Project Type**: Web application (monorepo with `/backend` and `/frontend`)

**Performance Goals**:
- AI response time: <3 seconds for 95% of requests (excluding network latency)
- Chat endpoint throughput: 100 concurrent conversations without degradation
- Message persistence: 100% retention across server restarts

**Constraints**:
- Stateless architecture (no in-memory conversation state)
- MCP tool interface only (AI agent cannot directly access database)
- JWT authentication required for all chat endpoints
- User-scoped authorization for all operations

**Scale/Scope**:
- Support 10,000+ users with independent conversations
- Handle conversations with hundreds of messages efficiently
- Maintain 90% accuracy for natural language interpretation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gates

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Specification-Driven Development | Approved specification exists | ✅ PASS | spec.md complete with 50 functional requirements |
| II. Security-First Architecture | JWT authentication plan defined | ✅ PASS | All chat endpoints require JWT, user_id extracted from token |
| III. Layered Implementation Order | Dependencies identified | ✅ PASS | Foundation (DB schema) → Core (MCP tools, chat endpoint) → Integration (frontend) |
| IV. Authentication & Authorization | User scoping enforced | ✅ PASS | All conversations and messages scoped to authenticated user |
| V. Technology Stack Immutability | Uses approved stack | ✅ PASS | FastAPI, SQLModel, PostgreSQL, Next.js, OpenAI Agents SDK, MCP SDK |
| VI. Monorepo Awareness | Respects layered structure | ✅ PASS | Backend changes in `/backend/src/ai/`, frontend in `/frontend/src/components/chat/` |
| VII. AI Integration Architecture | MCP architecture planned | ✅ PASS | MCP server with 5 tools, stateless design, OpenAI/OpenRouter support |
| VIII. Stateless Conversation Management | Database-backed state | ✅ PASS | conversations and messages tables, no in-memory state |
| IX. MCP Tool-Based Operations | Tools defined | ✅ PASS | 5 tools: add_task, list_tasks, update_task, complete_task, delete_task |

**Gate Result**: ✅ **PASS** - All constitutional requirements satisfied. Proceed to Phase 0 research.

### Post-Design Re-Check

**Artifacts Generated**:
- ✅ research.md (Phase 0)
- ✅ data-model.md (Phase 1)
- ✅ contracts/chat-endpoint.md (Phase 1)
- ✅ contracts/mcp-tools.md (Phase 1)
- ✅ quickstart.md (Phase 1)

**Re-validation**:

| Principle | Verification | Status | Evidence |
|-----------|--------------|--------|----------|
| I. Specification-Driven Development | All design artifacts reference spec.md | ✅ PASS | data-model.md, contracts/ all link back to spec |
| II. Security-First Architecture | User scoping enforced in data model and contracts | ✅ PASS | All tables have user_id foreign keys, all MCP tools require user_id parameter |
| III. Layered Implementation Order | Dependencies clearly documented | ✅ PASS | quickstart.md defines Phase 1 (DB) → Phase 2 (MCP) → Phase 3 (Agent) → Phase 4 (API) → Phase 5 (Frontend) |
| IV. Authentication & Authorization | JWT verification in chat endpoint contract | ✅ PASS | chat-endpoint.md specifies JWT extraction and user_id validation |
| V. Technology Stack Immutability | All dependencies from approved stack | ✅ PASS | OpenAI Agents SDK, MCP SDK, ChatKit all in constitution |
| VI. Monorepo Awareness | Clear separation of backend/frontend changes | ✅ PASS | Structure shows /backend/src/ai/ and /frontend/src/components/chat/ |
| VII. AI Integration Architecture | MCP tools follow protocol standards | ✅ PASS | mcp-tools.md defines 5 tools with JSON Schema, stateless design |
| VIII. Stateless Conversation Management | Database schema supports stateless server | ✅ PASS | data-model.md shows conversations/messages tables, no in-memory state |
| IX. MCP Tool-Based Operations | All tools enforce authorization | ✅ PASS | mcp-tools.md shows user_id parameter on every tool |

**Gate Result**: ✅ **PASS** - All design artifacts comply with constitutional requirements. Ready for `/sp.tasks`.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── ai/                    # NEW: AI chatbot feature
│   │   ├── __init__.py
│   │   ├── agent.py          # OpenAI Agents SDK agent setup
│   │   ├── mcp_server.py     # MCP server with tool definitions
│   │   └── tools.py          # MCP tool implementations
│   ├── api/
│   │   ├── auth.py           # EXISTING: Authentication endpoints
│   │   ├── tasks.py          # EXISTING: Task CRUD endpoints
│   │   ├── chat.py           # NEW: Chat endpoint
│   │   ├── errors.py         # EXISTING: Error handlers
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py           # EXISTING: User model
│   │   ├── task.py           # EXISTING: Task model
│   │   ├── conversation.py   # NEW: Conversation model
│   │   ├── message.py        # NEW: Message model
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── auth.py           # EXISTING: Auth schemas
│   │   ├── task.py           # EXISTING: Task schemas
│   │   ├── chat.py           # NEW: Chat request/response schemas
│   │   └── __init__.py
│   ├── auth/
│   │   ├── jwt.py            # EXISTING: JWT verification
│   │   ├── password.py       # EXISTING: Password hashing
│   │   └── __init__.py
│   ├── database.py           # EXISTING: Database connection
│   └── main.py               # EXISTING: FastAPI app (will add chat routes)
└── tests/
    ├── test_mcp_tools.py     # NEW: MCP tool contract tests
    ├── test_chat_endpoint.py # NEW: Chat endpoint integration tests
    ├── test_api.py           # EXISTING: Task API tests
    └── test_app.py           # EXISTING: App tests

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/
│   │   │   └── page.tsx      # EXISTING: Dashboard (will add chat link)
│   │   ├── chat/
│   │   │   └── page.tsx      # NEW: Chat page
│   │   ├── login/
│   │   │   └── page.tsx      # EXISTING: Login
│   │   ├── signup/
│   │   │   └── page.tsx      # EXISTING: Signup
│   │   ├── layout.tsx        # EXISTING: Root layout
│   │   └── page.tsx          # EXISTING: Home page
│   ├── components/
│   │   ├── chat/             # NEW: Chat UI components
│   │   │   ├── ChatInterface.tsx  # OpenAI ChatKit integration
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── tasks/            # EXISTING: Task components
│   │   ├── auth/             # EXISTING: Auth components
│   │   ├── ui/               # EXISTING: UI primitives
│   │   └── layout/           # EXISTING: Layout components
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts     # EXISTING: API client (will add chat methods)
│   │   │   └── chat.ts       # NEW: Chat API methods
│   │   └── types/
│   │       └── chat.ts       # NEW: Chat TypeScript types
│   └── styles/               # EXISTING: Tailwind config
└── tests/
    └── components/
        └── chat/              # NEW: Chat component tests
```

**Structure Decision**: Web application monorepo (Option 2) - Feature adds new subdirectories to existing backend (`/backend/src/ai/`) and frontend (`/frontend/src/components/chat/`, `/frontend/src/app/chat/`) structure. Maintains clear separation between AI logic (MCP server), API layer (chat endpoint), and frontend (ChatKit UI).

## Complexity Tracking

**No constitutional violations detected.** All design decisions align with constitutional principles.

## Implementation Strategy

### Phase-Based Delivery

**Foundation Layer** (Blocking for all):
1. Database migration: Add `conversations` and `messages` tables
2. SQLModel models: Conversation and Message with proper relationships
3. Database operations: CRUD operations with user scoping

**Core Layer** (User Story enablement):
4. MCP tools: Implement 5 tools (add_task, list_tasks, update_task, complete_task, delete_task)
5. AI agent: OpenAI Agents SDK integration with MCP tool registration
6. Chat endpoint: POST `/api/{user_id}/chat` with full lifecycle

**Integration Layer** (User-facing features):
7. Frontend components: ChatInterface, ChatMessage, ChatInput
8. Chat page: `/app/chat/page.tsx` with ChatKit integration
9. API client: Add chat methods to existing client

### Incremental User Story Delivery

**MVP (P1 - Natural Language Task Creation)**:
- Foundation + Core layers complete
- Minimal frontend (basic chat interface)
- User can create tasks via natural language

**Iteration 1 (P2 - Task Queries + Conversation Continuity)**:
- Add conversation history loading to frontend
- Enhance chat UI for conversation display
- User can view tasks and resume conversations

**Iteration 2 (P3-P5 - Full CRUD via Chat)**:
- No new backend work required (tools already support all operations)
- Enhance AI agent system prompt for better task matching
- User can complete, update, delete tasks via chat

### Parallel Implementation Opportunities

**Backend Parallelization**:
- Database models can be built while MCP tools are being implemented (independent)
- Chat endpoint can be built after MCP tools are complete (dependent)
- Tests can be written in parallel with implementation

**Frontend Parallelization**:
- Chat components can be built before backend is complete (mock API responses)
- API client methods can be defined based on contracts (not implementation)

**Full Stack Parallelization**:
- Backend team: Database → MCP tools → Chat endpoint
- Frontend team: Components → Chat page → API integration (using contracts)
- Join point: Integration testing after both complete

### Testing Strategy

**Contract-Level Testing** (Independent of UI):
- MCP tools: Call each tool directly, verify database changes
- Chat endpoint: POST requests with various payloads
- Authorization: Cross-user access attempts, JWT validation

**Integration Testing** (End-to-End):
- User flow: Login → Send message → Verify task created → Check database
- Conversation persistence: Send message → Refresh → Verify history loaded
- Error handling: AI API down → Verify graceful degradation

**Performance Testing**:
- Load test: 100 concurrent chat requests
- Message history: Conversations with 100+ messages
- Database query performance: Verify composite index usage

### Rollout Plan

**Stage 1: Backend Deployment**
- Deploy database migration to staging
- Deploy MCP tools and chat endpoint
- Verify with API contract tests

**Stage 2: Frontend Deployment**
- Deploy chat UI to staging
- Enable for internal testing users
- Gather feedback on natural language interpretation

**Stage 3: Production Rollout**
- Enable for 10% of users (canary deployment)
- Monitor error rates, AI API costs, response times
- Gradually increase to 100% if metrics acceptable

### Risk Mitigation

**Risk 1: AI API Costs**
- Mitigation: Use OpenRouter with cost-effective models (Claude Haiku, Llama 3.1)
- Monitoring: Track token usage per request, alert if exceeds budget
- Fallback: Rate limit chat endpoint if costs spike

**Risk 2: Natural Language Interpretation Accuracy**
- Mitigation: Well-designed system prompt with clear examples
- Monitoring: Log tool calls to detect misinterpretations
- Fallback: Allow users to fall back to traditional UI

**Risk 3: Database Performance (Large Conversations)**
- Mitigation: Composite index on messages table
- Monitoring: Track query execution time for message loading
- Fallback: Implement conversation truncation if p95 latency >100ms

**Risk 4: AI API Availability**
- Mitigation: Graceful error handling with user-friendly messages
- Monitoring: Alert on repeated API failures
- Fallback: OpenRouter supports multiple providers (automatic fallback)

## Design Artifacts Summary

| Artifact | Status | Purpose |
|----------|--------|---------|
| [research.md](./research.md) | ✅ Complete | Technology decisions and best practices |
| [data-model.md](./data-model.md) | ✅ Complete | Database schema for conversations and messages |
| [contracts/chat-endpoint.md](./contracts/chat-endpoint.md) | ✅ Complete | Chat API endpoint specification |
| [contracts/mcp-tools.md](./contracts/mcp-tools.md) | ✅ Complete | MCP tool interface contracts |
| [quickstart.md](./quickstart.md) | ✅ Complete | Local development and testing guide |

**Next Command**: `/sp.tasks 004-ai-chatbot` - Generate task breakdown based on this implementation plan.
