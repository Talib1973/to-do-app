---
id: 0001
title: Create REST API Endpoints Specification
stage: spec
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: 003-rest-api
branch: 003-003-rest-api
user: talib1973
command: /sp.specify
labels: ["specification", "rest-api", "crud", "endpoints", "jwt"]
links:
  spec: specs/003-003-rest-api/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-003-rest-api/spec.md
  - specs/003-003-rest-api/checklists/requirements.md
tests:
  - Quality validation checklist (all checks passed)
---

## Prompt

User command: `create the rest api spec`

Context: User requested creation of the REST API specification after completing the authentication specification (002-authentication), which established JWT token verification patterns. This spec defines the task management CRUD endpoints.

Full specification authoring workflow executed:
1. Generate short name: "rest-api"
2. Check for existing branches (none found)
3. Run create-new-feature.sh with number 003
4. Fill spec template with comprehensive REST API endpoint content
5. Create quality validation checklist
6. Validate specification against all quality criteria

## Response snapshot

Created comprehensive REST API Endpoints specification (003-rest-api) defining:

**Project Summary**: Complete CRUD API for task management with JWT-based authentication, user isolation, and RESTful design patterns.

**API Architecture**: RESTful design with six endpoints:
- POST /api/tasks - Create new task (201 Created)
- GET /api/tasks - List user's tasks with optional filtering (200 OK)
- GET /api/tasks/{task_id} - Retrieve single task (200 OK)
- PUT /api/tasks/{task_id} - Full task replacement (200 OK)
- PATCH /api/tasks/{task_id} - Partial task update (200 OK)
- DELETE /api/tasks/{task_id} - Delete task (204 No Content)

**User Stories (5)**:
1. P1: Task Creation - 6 acceptance scenarios (POST with validation, JWT enforcement, user_id from JWT)
2. P1: Task Retrieval - 7 acceptance scenarios (list all, filter by completion, get single task, cross-user access prevention)
3. P1: Task Updates - 6 acceptance scenarios (PUT full replacement, PATCH partial update, user_id immutability)
4. P1: Task Deletion - 5 acceptance scenarios (delete, cross-user prevention, idempotency)
5. P2: Task Filtering - 4 acceptance scenarios (filter by completed status)

**Functional Requirements (44)**: Covering:
- API endpoint structure (FR-001 to FR-005): JSON-only, /api/tasks path, JWT authentication, HTTP status codes, automatic user filtering
- Task creation (FR-006 to FR-010): POST endpoint, request validation, 201 response, user_id from JWT, UUID/timestamp generation
- Task retrieval (FR-011 to FR-017): GET list, GET single, ?completed filter, 200/403/404 responses
- Task updates (FR-018 to FR-025): PUT/PATCH endpoints, validation, 200/403/404 responses, updated_at auto-update, user_id immutability
- Task deletion (FR-026 to FR-029): DELETE endpoint, 204/403/404 responses
- Authentication & authorization (FR-030 to FR-033): JWT verification, 401 errors, user_id from sub claim, cross-user access prevention
- Error handling (FR-034 to FR-039): Standardized error format, 400/401/403/404/500 responses
- Data validation (FR-040 to FR-044): Title/description length limits, type validation, UUID format, Content-Type header

**Success Criteria (10)**: Measurable outcomes including task creation <2s, retrieval <1s, 100% JWT enforcement, 100% user-scoped queries, 100 concurrent operations, 100% HTTP compliance, validation <500ms, zero SQL injection, 100% error format consistency, 100% API documentation accuracy

**API Specifications**: Complete endpoint definitions with:
- Request/response examples for all 6 endpoints
- HTTP headers (Authorization: Bearer, Content-Type)
- Query parameters (?completed filter)
- Path parameters ({task_id} UUID)
- Validation rules (title max 500 chars, description max 5000 chars)
- Success responses (201/200/204)
- Error responses (400/401/403/404/413/415/500)

**Task Data Model**:
```json
{
  "id": "UUID",
  "user_id": "UUID (foreign key to users)",
  "title": "string (max 500 chars, required)",
  "description": "string (max 5000 chars, optional)",
  "completed": "boolean (default false)",
  "created_at": "timestamp (auto-generated)",
  "updated_at": "timestamp (auto-updated)"
}
```

**Standardized Error Format**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

**Security Requirements**:
- JWT Bearer token on all endpoints
- User ID extraction from JWT sub claim (never from request body)
- 401 Unauthorized for missing/invalid/expired tokens
- 403 Forbidden for cross-user access attempts
- SQL injection prevention through parameterized queries
- Input validation on all user-provided data

**Implementation Notes**: Separated FastAPI (backend) and Next.js (frontend) code examples as implementation guidance, not requirements

**Quality Validation**: Passed all checklist items
- Content quality ✅
- Requirement completeness ✅ (zero [NEEDS CLARIFICATION] markers)
- Feature readiness ✅

**Out of Scope** (documented assumptions for MVP):
- Pagination (assumes max 10,000 tasks per user)
- Sorting (returns in creation order)
- Search (no full-text search)
- Bulk operations (no batch endpoints)
- Task tags/categories/priority/due dates
- Task sharing/collaboration
- Soft deletes (DELETE is permanent)
- Task history/audit log
- Rate limiting
- API versioning
- Webhooks
- Real-time updates

**Edge Cases Documented**:
- Malformed task_id (400 Bad Request vs 404 Not Found)
- Concurrent updates (last-write-wins)
- Payload size limits (413 Payload Too Large)
- Expired JWT tokens (401 with "Token expired")
- Missing Content-Type header (415 Unsupported Media Type)

## Outcome

- ✅ Impact: REST API specification complete and validated. Complete CRUD API defined with 6 endpoints, security enforcement, standardized error handling, and comprehensive validation rules. Ready for architecture planning phase.
- 🧪 Tests: Quality validation checklist executed - 14/14 checks passed
- 📁 Files: specs/003-003-rest-api/spec.md (727 lines), specs/003-003-rest-api/checklists/requirements.md (validation results)
- 🔁 Next prompts: Create database schema specification (004-database-schema) to define tasks table structure, then run /sp.plan for architecture planning
- 🧠 Reflection: Successfully created REST API specification building on authentication foundation. Properly separated implementation details (FastAPI routes, SQLModel, Next.js API client) into "Technology Constraints" section. 25 acceptance scenarios provide comprehensive test coverage for all CRUD operations and error cases. Standardized error response format enables consistent frontend error handling.

## Evaluation notes (flywheel)

- Failure modes observed: None - all validation criteria passed on first iteration
- Graders run and results (PASS/FAIL): Manual quality checklist PASS (14/14 items)
- Prompt variant (if applicable): N/A (standard /sp.specify workflow)
- Next experiment (smallest change to try): Test REST API specification by creating database schema specification next, ensuring tasks table structure aligns with API data model (UUID identifiers, user_id foreign key, field length constraints)
