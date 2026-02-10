---
id: 0002
title: Add AI Chatbot Principles to Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: talib1973
command: /sp.constitution
labels: ["constitution", "ai-chatbot", "mcp-server", "governance"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - None (governance document update)
---

## Prompt

User requested constitution update before proceeding with AI chatbot feature specification:

"first we should update our sp.constitution than move next"

Context: User wants to add AI chatbot feature to existing Todo app with these requirements:
- AI-powered chatbot for task management via natural language
- MCP (Model Context Protocol) server architecture
- OpenAI Agents SDK for AI logic
- Stateless chat endpoint with database-persisted conversations
- OpenRouter API as cost-effective alternative to OpenAI
- ChatKit frontend for conversational UI
- MCP tools for all task operations (add, list, update, complete, delete)
- Database schema: conversations and messages tables
- Maintain existing Todo CRUD functionality

## Response snapshot

Updated constitution from v1.0.0 → v1.1.0 (MINOR version bump) with three new core principles:

**VII. AI Integration Architecture**
- MCP architecture with stateless server design
- MCP tools as interface between AI and application
- Support for both OpenAI and OpenRouter APIs
- Database-backed state only (no in-memory state)
- Agent must not directly access database

**VIII. Stateless Conversation Management**
- All conversation state stored in database
- Server remains stateless across requests
- Request lifecycle defined (load history → process → store → respond)
- Conversations and messages tables required
- User scoping enforced via JWT

**IX. MCP Tool-Based Operations**
- Five standard tools: add_task, list_tasks, update_task, complete_task, delete_task
- Tools enforce user authorization
- Structured JSON responses
- Agent interprets natural language to tool calls

Added sections:
- MCP Server Architecture (design, tool structure, authorization flow)
- OpenAI/OpenRouter Configuration (provider selection, API compatibility, model guidelines)
- Updated AI Zone in trust boundaries diagram
- Updated scope to include AI chatbot features

Technology stack additions:
- OpenAI ChatKit (frontend)
- OpenAI Agents SDK (backend)
- Official MCP SDK (backend)
- OpenRouter API support

## Outcome

- ✅ Impact: Constitutional framework established for AI chatbot feature development
- 🧪 Tests: No tests (governance document)
- 📁 Files: constitution.md updated with 3 new principles, 2 new sections
- 🔁 Next prompts: /sp.specify 004-ai-chatbot → /sp.plan → /sp.tasks
- 🧠 Reflection: Clean separation of concerns maintained. MCP architecture prevents tight coupling between AI and application logic. Stateless design enables horizontal scaling. OpenRouter option reduces cost barrier.

## Evaluation notes (flywheel)

- Failure modes observed: None. Constitution update straightforward.
- Graders run and results (PASS/FAIL): Manual review - PASS (all new principles align with existing security and architecture standards)
- Prompt variant (if applicable): Standard /sp.constitution workflow
- Next experiment (smallest change to try): Proceed with /sp.specify to create AI chatbot specification following new constitutional principles
