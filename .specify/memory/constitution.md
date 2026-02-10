<!--
Sync Impact Report - Constitution Update
=========================================
Version Change: 1.0.0 → 1.1.0
Change Type: MINOR (New AI chatbot principles added)

Modified Principles:
- UPDATED: Scope & Boundaries (added AI chatbot features to In Scope)

Added Principles:
- NEW: VII. AI Integration Architecture
- NEW: VIII. Stateless Conversation Management
- NEW: IX. MCP Tool-Based Operations

Added Sections:
- AI & Chatbot Standards (under Technology Constraints)
- MCP Server Architecture (new section)
- OpenAI/OpenRouter Configuration (new section)

Template Updates Required:
✅ plan-template.md - No changes needed (AI features follow same planning structure)
✅ spec-template.md - No changes needed (AI features use same spec format)
✅ tasks-template.md - No changes needed (AI features follow same task structure)
⚠️ CLAUDE.md files - May need AI-specific guidance (backend MCP server setup)

Follow-up TODOs:
- Consider adding `/backend/ai/CLAUDE.md` for AI agent and MCP server conventions
- Update API documentation to include /api/{user_id}/chat endpoint

Rationale for MINOR version:
- New functionality added (AI chatbot) without breaking existing features
- New principles expand governance without changing existing rules
- Backward compatible with all existing specs and implementations
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Specification-Driven Development

**All implementation work MUST be driven by written, approved specifications.**

Rules:
- No code may be written without a referenced specification document
- Specifications are the single source of truth for requirements
- If a requirement is unclear or missing: STOP, propose a spec update, do NOT implement
- Specifications override assumptions in all cases

Rationale: Prevents scope creep, ensures alignment between stakeholders and implementers, creates auditable requirements trail, reduces rework from misunderstood requirements.

### II. Security-First Architecture

**Security is non-negotiable and MUST be enforced at every layer.**

Rules:
- All API endpoints MUST require valid JWT authentication
- User identity MUST be derived exclusively from verified JWT tokens
- Client-provided identifiers MUST NOT be trusted
- User-level data isolation MUST be enforced on every database operation
- Unauthenticated requests MUST return 401 Unauthorized
- Unauthorized access attempts MUST return 403 Forbidden

Rationale: Multi-user system requires strict security boundaries to prevent data leaks and unauthorized access. Trust model clearly separates untrusted client zone from trusted backend zone.

### III. Layered Implementation Order

**Implementation MUST proceed in strict dependency order: Foundation → Core → Integration.**

Required Execution Order:
1. **Foundation & Infrastructure**
   - Specifications finalized
   - Architecture defined
   - Database connectivity established
   - Authentication and JWT verification in place
   - Application skeletons created

2. **Core Business Functionality**
   - Task CRUD backend endpoints
   - User-scoped database queries
   - Frontend task management UI
   - API client integration

3. **Integration, Validation & Polish**
   - End-to-end flow verification
   - Security enforcement validation
   - Error handling and UX refinement
   - Spec compliance confirmation

Prohibited Actions:
- Implementing later work before earlier work is complete
- Mixing responsibilities across execution steps
- Skipping validation between steps

Rationale: Database schema must exist before API routes can query it; API routes must exist before frontend can consume them; authentication must be in place before any protected operations. Sequential execution reduces integration failures and rework.

### IV. Authentication & Authorization Enforcement

**Every protected operation MUST verify authentication and enforce user-scoped authorization.**

Authentication Rules:
- JWT tokens MUST be transmitted via `Authorization: Bearer <token>` header only
- JWT verification MUST use the shared secret from `BETTER_AUTH_SECRET` environment variable
- Expired or invalid tokens MUST be rejected with 401 Unauthorized
- Missing authentication headers MUST return 401 Unauthorized

Authorization Rules:
- User ID MUST be extracted from verified JWT token's `sub` claim
- All database queries MUST filter by authenticated user ID
- Cross-user data access MUST be prevented
- If a user identifier appears in a route parameter, it MUST match the authenticated user from JWT, otherwise return 403 Forbidden

Rationale: Stateless JWT authentication enables scalability while maintaining security. User-scoped filtering prevents data leaks between users. Never trusting client-provided identifiers closes a major security vulnerability.

### V. Technology Stack Immutability

**The approved technology stack is fixed and MUST NOT be altered without constitutional amendment.**

Frontend Stack:
- Next.js (App Router)
- TypeScript
- Tailwind CSS
- Better Auth for authentication
- OpenAI ChatKit for conversational UI (AI features only)

Backend Stack:
- Python FastAPI
- SQLModel ORM
- PostgreSQL (Neon Serverless)
- OpenAI Agents SDK (AI features)
- Official MCP SDK (Model Context Protocol server)

AI Integration Stack:
- OpenAI API or OpenRouter API (API-compatible alternative)
- OpenAI Agents SDK for agent runtime
- MCP Server for tool-based operations
- Database-backed conversation state (no in-memory state)

Authentication Stack:
- Better Auth issues JWT tokens
- JWT verification uses shared secret
- Environment variable: `BETTER_AUTH_SECRET`

Prohibited:
- Alternative frameworks, databases, ORMs, or authentication systems
- Technology substitutions without formal constitutional amendment
- In-memory state for conversations (MUST use database)

Rationale: Technology consistency ensures maintainability, reduces cognitive load, prevents architectural fragmentation, and leverages team expertise. Changes require explicit justification and stakeholder approval.

### VI. Monorepo Awareness

**Development MUST respect layered guidance and maintain clear separation of concerns across the monorepo.**

Layered CLAUDE.md Hierarchy:
1. Root `/CLAUDE.md` — Global rules (this constitution)
2. `/frontend/CLAUDE.md` — Frontend-specific conventions
3. `/backend/CLAUDE.md` — Backend-specific conventions
4. `/backend/ai/CLAUDE.md` — AI agent and MCP server conventions (if needed)

Rules:
- Each layer inherits rules from layers above
- More specific guidance overrides general guidance
- Cross-cutting changes across frontend and backend are allowed ONLY when required by a single approved specification
- Frontend API access MUST go through a centralized API client (no direct fetch calls in components)

Implementation Order Within Monorepo:
- Database schema before API routes
- API routes before frontend integration
- Backend behavior before frontend consumption
- MCP tools before AI agent integration

Prohibited:
- Hardcoding secrets (API keys, JWT secrets)
- Bypassing JWT validation
- Sharing database connections across layers
- Implementing logic outside the specification system
- Storing conversation state in memory

Rationale: Monorepo structure requires clear boundaries to prevent coupling and maintain independent testability of layers. Centralized API client ensures consistent authentication and error handling.

### VII. AI Integration Architecture

**AI features MUST follow the Model Context Protocol (MCP) architecture with stateless server design.**

MCP Architecture Requirements:
- AI agent MUST use MCP tools to interact with application data
- MCP server MUST expose all task operations as standardized tools
- MCP tools MUST be stateless (no in-memory state)
- All state MUST be persisted to database (conversations, messages, task operations)
- AI agent MUST NOT directly access database or application logic
- Tool invocations MUST be atomic and idempotent where possible

API Integration Requirements:
- MUST support both OpenAI API and OpenRouter API (API-compatible)
- API key MUST be stored in environment variable (`OPENAI_API_KEY` or `OPENROUTER_API_KEY`)
- API selection MUST be configurable via environment variable
- Fallback behavior: OpenRouter preferred for cost efficiency, OpenAI as primary standard

Agent Runtime Requirements:
- Use OpenAI Agents SDK for agent logic and tool orchestration
- Agent MUST be stateless (conversation history loaded from database per request)
- Agent configuration (system prompt, tools) MUST be declarative
- Agent MUST confirm actions with natural language responses

Prohibited:
- Storing conversation state in memory or local variables
- Direct database access from AI agent code
- Hardcoding API keys or model selection
- Bypassing MCP tool layer for task operations

Rationale: MCP architecture provides standardized interface between AI agents and application logic. Stateless design enables horizontal scaling and fault tolerance. Database-backed state ensures conversation persistence and server resilience.

### VIII. Stateless Conversation Management

**All conversation state MUST be stored in database; servers MUST remain stateless.**

Database Schema Requirements:
- `conversations` table: user_id, id, created_at, updated_at
- `messages` table: user_id, id, conversation_id, role (user/assistant), content, created_at
- Foreign key constraints MUST enforce user ownership and referential integrity

Request Lifecycle:
1. Receive user message via `/api/{user_id}/chat` endpoint
2. Load conversation history from database (if conversation_id provided)
3. Append user message to message history
4. Store user message in database BEFORE agent processing
5. Run AI agent with full message history + MCP tools
6. Store assistant response in database AFTER agent completes
7. Return response to client with conversation_id
8. Server discards all state (ready for next request)

Stateless Server Rules:
- NO conversation state in memory beyond single request scope
- NO caching of message history between requests
- NO WebSocket or long-lived connections for chat
- Each request MUST be independent and reproducible
- Server restart MUST NOT affect conversation continuity

User Scoping:
- All conversations MUST be scoped to authenticated user via JWT
- User ID in route parameter MUST match JWT user ID
- Cross-user conversation access MUST return 403 Forbidden

Rationale: Stateless architecture enables horizontal scaling, simplifies deployment, ensures conversation persistence across server restarts, and maintains security boundaries. Database is single source of truth for all state.

### IX. MCP Tool-Based Operations

**AI agents MUST interact with application exclusively through MCP tools; direct access is prohibited.**

MCP Tool Requirements:
- Each task operation (create, list, update, complete, delete) MUST have corresponding MCP tool
- Tools MUST accept user_id as required parameter for authorization
- Tools MUST return structured JSON responses with status, data, and error fields
- Tools MUST enforce user-scoped authorization (match user_id from JWT)
- Tool errors MUST be gracefully handled and returned to agent

Standard MCP Tools:
1. `add_task` - Create new task (parameters: user_id, title, description)
2. `list_tasks` - Retrieve tasks (parameters: user_id, status filter)
3. `update_task` - Modify task (parameters: user_id, task_id, title, description)
4. `complete_task` - Mark task done (parameters: user_id, task_id)
5. `delete_task` - Remove task (parameters: user_id, task_id)

Tool Response Format:
```json
{
  "status": "success" | "error",
  "data": { ... },
  "error": "error message if status=error"
}
```

Agent Behavior:
- Agent MUST interpret natural language into appropriate tool calls
- Agent MUST provide friendly confirmations after successful tool invocations
- Agent MUST handle tool errors gracefully with helpful user messages
- Agent MAY chain multiple tool calls in single turn (e.g., list then delete)

Prohibited:
- Agent accessing database directly
- Agent calling REST endpoints instead of MCP tools
- Bypassing user_id authorization in tool calls
- Exposing raw tool errors to users

Rationale: MCP tools provide standardized, testable interface between AI and application. Tool-based architecture enables independent testing of AI logic and application logic. Clear separation of concerns improves maintainability.

## Technology Constraints

**Authoritative Spec Sources:**
- `@specs/overview.md`
- `@specs/features/task-crud.md`
- `@specs/features/authentication.md`
- `@specs/features/ai-chatbot.md` (new)
- `@specs/api/rest-endpoints.md`
- `@specs/api/chat-endpoint.md` (new)
- `@specs/database/schema.md`
- `@specs/ui/components.md`
- `@specs/ui/pages.md`
- `@specs/ai/mcp-tools.md` (new)
- `@specs/ai/agent-behavior.md` (new)

**API Behavior Standards:**

All REST endpoints MUST conform exactly to `@specs/api/rest-endpoints.md`:
- All routes under `/api/`
- JSON-only communication
- Pydantic request and response models
- SQLModel for database access
- Ownership enforced on every query
- No endpoint may expose or modify another user's data

**Chat API Standards:**

Chat endpoint MUST conform to `@specs/api/chat-endpoint.md`:
- Route: `POST /api/{user_id}/chat`
- Request: `{ "conversation_id": int | null, "message": string }`
- Response: `{ "conversation_id": int, "response": string, "tool_calls": array }`
- User ID in route MUST match JWT user ID
- Conversation history loaded from database per request
- All state persisted to database before returning response

**Database Standards:**
- PostgreSQL relational database
- SQLModel ORM for all queries
- User ownership foreign keys enforced
- Referential integrity maintained at schema level
- Conversations and messages tables for chat history

**Frontend Standards:**
- Server components by default
- Client components only when interactivity or auth state required
- Centralized API client for all backend communication
- No inline fetch calls inside UI components
- TypeScript types complete (no `any` types)
- OpenAI ChatKit for conversational UI (chat feature only)

**AI & Chatbot Standards:**
- OpenAI Agents SDK for agent runtime
- Official MCP SDK for MCP server
- Database-backed conversation state (no in-memory state)
- MCP tools for all task operations
- OpenAI API or OpenRouter API (configurable)
- Environment variables for API keys and model selection

## MCP Server Architecture

**MCP Server Design:**

The MCP server is a Python module within the FastAPI backend that:
- Exposes task operations as MCP-compliant tools
- Uses SQLModel ORM for database access
- Enforces user-scoped authorization on every tool call
- Returns structured JSON responses
- Remains stateless (no conversation or tool state in memory)

**MCP Tool Structure:**

```python
# Each tool accepts:
# - user_id (required): extracted from JWT for authorization
# - tool-specific parameters

# Each tool returns:
{
  "status": "success" | "error",
  "data": { ... },  # tool-specific response data
  "error": null | "error message"
}
```

**Tool Authorization Flow:**

1. Agent invokes MCP tool with user_id parameter
2. MCP server validates user_id matches authenticated user
3. MCP server queries database with user_id filter
4. MCP server returns scoped results to agent
5. Agent formats response for user

**MCP Server Location:**
- Module: `/backend/src/ai/mcp_server.py`
- Tools defined in: `/backend/src/ai/tools/`
- Integration with FastAPI: `/backend/src/api/chat.py`

## OpenAI/OpenRouter Configuration

**API Provider Selection:**

Environment variables control which API provider is used:

```bash
# Option 1: OpenAI (primary, standard)
OPENAI_API_KEY=sk-...
AI_PROVIDER=openai  # default if not specified

# Option 2: OpenRouter (cost-effective alternative)
OPENROUTER_API_KEY=sk-or-v1-...
AI_PROVIDER=openrouter

# Model selection (optional, defaults to gpt-3.5-turbo)
AI_MODEL=gpt-4  # or any OpenRouter-supported model
```

**API Compatibility:**

OpenRouter is API-compatible with OpenAI, requiring only:
- Different base URL: `https://openrouter.ai/api/v1`
- Different API key format
- Same request/response format

**Implementation Requirements:**

```python
# Backend must support both providers
if os.getenv("AI_PROVIDER") == "openrouter":
    base_url = "https://openrouter.ai/api/v1"
    api_key = os.getenv("OPENROUTER_API_KEY")
else:
    base_url = "https://api.openai.com/v1"
    api_key = os.getenv("OPENAI_API_KEY")

# OpenAI SDK can use custom base URL
client = OpenAI(api_key=api_key, base_url=base_url)
```

**Model Selection Guidelines:**

- **OpenAI GPT-3.5-turbo**: Fast, cost-effective, good for basic chat
- **OpenAI GPT-4**: Higher quality reasoning, slower, more expensive
- **OpenRouter Claude Sonnet**: High quality, competitive pricing
- **OpenRouter Claude Haiku**: Very fast, low cost, good for simple tasks

## Security & Authentication Rules

**Trust Boundaries:**

```
┌─────────────────────────────────┐
│ UNTRUSTED ZONE (Client)         │
│ - Never trust user-provided IDs │
│ - Never trust client validation │
└─────────────────────────────────┘
           ↓ JWT Token
┌─────────────────────────────────┐
│ TRUSTED ZONE (Backend)           │
│ - Verify JWT signature          │
│ - Extract user_id from token    │
│ - Enforce authorization          │
└─────────────────────────────────┘
           ↓ Validated Data
┌─────────────────────────────────┐
│ AI ZONE (MCP Server + Agent)     │
│ - Tools enforce user scoping    │
│ - Stateless conversation mgmt   │
│ - Database-backed state          │
└─────────────────────────────────┘
           ↓ User-Scoped Queries
┌─────────────────────────────────┐
│ DATA ZONE (Database)             │
│ - Enforce constraints            │
│ - Store user_id foreign keys    │
└─────────────────────────────────┘
```

**JWT Structure Requirements:**
- `sub` (subject): User ID (primary identifier)
- `email`: User's email address
- `iat` (issued at): Token creation timestamp
- `exp` (expiration): Token expiry timestamp
- Optional: `name`, `role`, or other user metadata

**Security Validation Checklist (Every Protected Endpoint):**
- [ ] JWT verification in place via dependency injection
- [ ] User ID extracted from validated token, NOT request body
- [ ] Database queries filtered by authenticated user ID
- [ ] Proper 401/403/404 responses for security scenarios
- [ ] No sensitive data leaked in error messages

**Chat Endpoint Security:**
- [ ] User ID in route path matches JWT user ID
- [ ] Conversation ID (if provided) belongs to authenticated user
- [ ] MCP tools receive user_id from JWT, not request
- [ ] AI responses do not leak other users' data
- [ ] API keys never exposed to client

## Implementation Workflow

**Mandatory Development Model:**

Follow the Agentic Dev Stack workflow:

1. Read relevant specifications
2. Generate an implementation plan
3. Break the plan into discrete tasks
4. Implement tasks incrementally
5. Validate each task against acceptance criteria

**Prohibited Actions:**
- Writing code without a referenced specification
- Skipping planning or task decomposition
- Inferring requirements not explicitly stated in specs

**Task Completion Criteria:**

A task is complete ONLY IF:
- It satisfies the referenced specification
- It meets acceptance criteria
- It enforces authentication and authorization
- It integrates cleanly into the monorepo
- Tests pass (if tests are included in acceptance criteria)

If any condition fails, the task is incomplete.

## Scope & Boundaries

**In Scope:**
- Task CRUD functionality
- REST API endpoints
- Responsive web frontend
- Persistent PostgreSQL storage
- User authentication using Better Auth
- JWT-secured backend communication
- **AI-powered chatbot for task management** (NEW)
- **Natural language task operations via MCP tools** (NEW)
- **Stateless conversation management with database persistence** (NEW)

**Out of Scope:**
- Real-time collaboration features
- Mobile native applications
- Voice or image-based chat interactions
- Multi-user conversations or shared tasks via chat
- Any functionality not defined in approved specifications

## Governance

**Constitutional Authority:**

This constitution supersedes all other practices and conventions.

**Amendment Process:**
- Amendments require documented justification
- Version increment following semantic versioning (MAJOR.MINOR.PATCH)
- Stakeholder approval required for MAJOR changes
- Migration plan required for breaking changes
- Update to dependent templates and documentation

**Compliance:**
- All pull requests and code reviews MUST verify constitutional compliance
- Constitution violations MUST be documented in Complexity Tracking section of plan.md with justification
- Use `/CLAUDE.md`, `/frontend/CLAUDE.md`, and `/backend/CLAUDE.md` for runtime development guidance

**Final Authority:**
- Specifications override assumptions
- Security overrides convenience
- Correctness overrides speed

**Version**: 1.1.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-07
