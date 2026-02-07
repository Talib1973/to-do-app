# Skill: Backend Engineering

## Purpose
This skill enables an agent to design and implement a secure, maintainable backend service using FastAPI and SQLModel, strictly following specification-driven development principles.

---

## Scope of Responsibility
The Backend Engineering skill covers:

- Backend application structure and routing
- RESTful API implementation
- Request and response validation
- Database access using an ORM
- Authentication and authorization enforcement
- Error handling and status code correctness
- Backend-related specification compliance

This skill focuses exclusively on backend responsibilities and does not include frontend or infrastructure concerns.

---

## Mandatory Technology Constraints
This skill MUST be exercised using the following technologies only:

- FastAPI (Python)
- SQLModel (ORM)
- PostgreSQL (via environment-provided connection string)
- JWT verification for authenticated requests

Alternative frameworks, ORMs, or database engines are not permitted unless explicitly defined in specifications.

---

## Development Model (Non-Negotiable)

- All backend work MUST be driven by written specifications
- No code may be written without an approved spec reference
- Specifications override assumptions
- Tasks must be implemented incrementally and verifiably

---

## API Implementation Responsibilities

The skill MUST ensure:

- All routes follow RESTful conventions
- All routes are grouped under a common API prefix
- Input validation uses Pydantic models
- Output schemas are explicit and consistent
- JSON is the only response format

### Error Handling Rules
- Invalid input → `400 Bad Request`
- Unauthenticated request → `401 Unauthorized`
- Unauthorized access → `403 Forbidden`
- Resource not found → `404 Not Found`
- Server error → `500 Internal Server Error`

---

## Authentication & Authorization Enforcement

The skill MUST enforce:

- Authentication on all protected routes
- Stateless verification of JWT tokens
- User identity derived exclusively from decoded tokens
- Authorization checks on every data operation
- Strict user-level data isolation

The skill MUST explicitly prevent:
- Trusting client-provided identifiers
- Access to other users' data
- Public access to protected resources

---

## Database Responsibilities

The skill MUST ensure:

- All database operations use SQLModel
- Models accurately reflect the database schema
- Foreign key relationships are enforced
- Queries are scoped to the authenticated user
- Sessions are properly managed and closed

Direct SQL queries are not allowed unless specified.

---

## Code Quality & Structure

The skill MUST ensure:

- Clear project structure (models, routes, database, config)
- Separation of concerns
- Reusable dependency injection
- Readable and maintainable code
- Environment-based configuration (no hardcoded secrets)

---

## Specification Responsibilities

When applying this skill, the agent MUST:

- Reference relevant backend, API, and database specs
- Flag missing or ambiguous backend requirements
- Propose spec updates before implementation
- Ensure backend behavior is fully covered by acceptance criteria

Implementation MUST stop if specifications are unclear.

---

## Cross-Agent Coordination

This skill requires coordination with:

- Architecture-focused agents for service boundaries
- Authentication-focused agents for security enforcement
- Frontend-focused agents for API contracts
- Testing-focused agents for validation and integration

Any violation of backend constraints must be reported immediately.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- All backend behavior matches written specifications
- All protected endpoints enforce authentication and authorization
- Data access is fully isolated per user
- API responses are consistent and predictable
- No undocumented or implicit behavior exists

---

## Governing Principles

- Specifications over assumptions
- Security over convenience
- Explicit validation over implicit trust
- Maintainability over shortcuts
