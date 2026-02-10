---
id: 0002
title: Research Implementation Technologies for AI Chatbot
stage: spec
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: 004-ai-chatbot
branch: 004-ai-chatbot
user: talib1973
command: research
labels: ["research", "ai-chatbot", "mcp", "openai-agents", "openrouter", "chatkit", "database-design"]
links:
  spec: /specs/004-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - /specs/004-ai-chatbot/research.md
tests:
  - None (research phase)
---

## Prompt

Research the following topics for AI Chatbot implementation with MCP architecture:

1. **OpenAI Agents SDK Best Practices**:
   - How to set up an agent with OpenAI Agents SDK
   - Tool registration and invocation patterns
   - Stateless agent design (loading conversation history per request)
   - System prompt design for task management chatbot

2. **MCP (Model Context Protocol) Server Implementation**:
   - Official MCP SDK usage patterns for Python
   - Tool definition structure and JSON schema
   - Best practices for tool naming and parameter design
   - Error handling and response formatting

3. **OpenRouter API Integration**:
   - API compatibility with OpenAI API
   - Authentication and API key management
   - Model selection and configuration
   - Rate limiting and error handling differences

4. **OpenAI ChatKit Frontend Integration**:
   - Installation and setup for Next.js
   - Message rendering and conversation display
   - API integration patterns (connecting to custom backend)
   - Styling and customization options

5. **Database Schema Design for Conversations**:
   - Conversation and message table structure
   - Indexing strategies for fast message retrieval
   - Handling large conversation histories
   - User scoping and foreign key constraints

For each topic, provide:
- **Decision**: What approach to use
- **Rationale**: Why this approach was chosen
- **Alternatives Considered**: Other options and why rejected
- **Implementation Pattern**: Concrete code/config example if applicable

Focus on practical implementation guidance that can be directly used in the planning phase.

## Response snapshot

Created comprehensive research document at `/specs/004-ai-chatbot/research.md` with detailed findings for all five requested topics:

**1. OpenAI Agents SDK Best Practices**:
- Decision: Session-based state management with stateless server design
- Implemented pattern showing agent creation with MCP tools, database-loaded conversation history
- Rationale: Enables horizontal scaling, survives server restarts, constitutional compliance
- Alternatives rejected: In-memory session cache, WebSocket connections, manual history management

**2. MCP Server Implementation**:
- Decision: FastMCP with @mcp.tool() decorator for type-safe tool definitions
- Five tools implemented: add_task, list_tasks, update_task, complete_task, delete_task
- Pydantic models for automatic JSON Schema generation and validation
- Standard response format: {status: "success"|"error", data: {}, error: null}
- User scoping enforced via user_id parameter on every tool

**3. OpenRouter API Integration**:
- Decision: OpenAI SDK with configurable base_url for provider switching
- Environment-based configuration (AI_PROVIDER, OPENAI_API_KEY, OPENROUTER_API_KEY)
- Exponential backoff retry logic for rate limiting and API errors
- Model recommendations: claude-3-haiku for fast/cheap, gpt-4 for complex reasoning

**4. OpenAI ChatKit Frontend Integration**:
- Decision: Self-hosted backend integration with custom fetch method
- TypeScript implementation with Next.js App Router
- Custom ChatInterface and ChatInput components with Tailwind styling
- Optimistic UI updates, URL-based conversation tracking
- Alternatives rejected: OpenAI-hosted backend (requires domain allowlist)

**5. Database Schema Design**:
- Decision: Composite index on (user_id, conversation_id, created_at) for messages
- Conversations table: user_id, id, created_at, updated_at
- Messages table: user_id, conversation_id, role, content, created_at
- Foreign key constraints with cascade deletes for referential integrity
- Pagination strategy for large conversation histories (100+ messages)

All sections include concrete code examples ready for implementation in Phase 1 (design) and Phase 2 (tasks).

## Outcome

- ✅ Impact: Completed foundational research for all five critical technology areas. Provides actionable implementation patterns with code examples for planning and implementation phases.
- 🧪 Tests: None (research phase - no tests required)
- 📁 Files: Created `/specs/004-ai-chatbot/research.md` (comprehensive 600+ line research document)
- 🔁 Next prompts: Phase 1 design artifacts (data-model.md, quickstart.md, contracts/), then Phase 2 tasks breakdown
- 🧠 Reflection: Research incorporated 2026-current documentation via web search, ensuring latest SDK patterns (OpenAI Agents SDK v2, MCP SDK v1.7+, ChatKit). All recommendations align with constitutional requirements: stateless architecture, MCP tool-based operations, database-backed state, JWT authentication.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitutional compliance check - PASS (all 9 principles satisfied per plan.md)
- Prompt variant (if applicable): N/A (standard research request)
- Next experiment (smallest change to try): Proceed to `/sp.plan` Phase 1 design to generate data models and contracts based on research findings
