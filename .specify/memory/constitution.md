<!--
Sync Impact Report - Constitution Update
=========================================
Version Change: TEMPLATE → 1.0.0
Change Type: MAJOR (Initial ratification)

Modified Principles:
- NEW: Specification-Driven Development
- NEW: Security-First Architecture
- NEW: Layered Implementation Order
- NEW: Authentication & Authorization Enforcement
- NEW: Technology Stack Immutability
- NEW: Monorepo Awareness

Added Sections:
- Core Principles (6 principles)
- Technology Constraints
- Security & Authentication Rules
- API Behavior Standards
- Implementation Workflow
- Governance

Template Updates Required:
✅ plan-template.md - Constitution Check section aligned
✅ spec-template.md - User scenarios and acceptance criteria format compatible
✅ tasks-template.md - Phase ordering matches execution structure
✅ No command file updates needed (generic guidance maintained)

Follow-up TODOs:
- None (all placeholders filled)

Rationale for MAJOR version:
- First official constitution ratification
- Establishes foundational governance framework
- All 6 core principles defined with enforcement rules
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

Backend Stack:
- Python FastAPI
- SQLModel ORM
- PostgreSQL (Neon Serverless)

Authentication Stack:
- Better Auth issues JWT tokens
- JWT verification uses shared secret
- Environment variable: `BETTER_AUTH_SECRET`

Prohibited:
- Alternative frameworks, databases, ORMs, or authentication systems
- Technology substitutions without formal constitutional amendment

Rationale: Technology consistency ensures maintainability, reduces cognitive load, prevents architectural fragmentation, and leverages team expertise. Changes require explicit justification and stakeholder approval.

### VI. Monorepo Awareness

**Development MUST respect layered guidance and maintain clear separation of concerns across the monorepo.**

Layered CLAUDE.md Hierarchy:
1. Root `/CLAUDE.md` — Global rules (this constitution)
2. `/frontend/CLAUDE.md` — Frontend-specific conventions
3. `/backend/CLAUDE.md` — Backend-specific conventions

Rules:
- Each layer inherits rules from layers above
- More specific guidance overrides general guidance
- Cross-cutting changes across frontend and backend are allowed ONLY when required by a single approved specification
- Frontend API access MUST go through a centralized API client (no direct fetch calls in components)

Implementation Order Within Monorepo:
- Database schema before API routes
- API routes before frontend integration
- Backend behavior before frontend consumption

Prohibited:
- Hardcoding secrets
- Bypassing JWT validation
- Sharing database connections across layers
- Implementing logic outside the specification system

Rationale: Monorepo structure requires clear boundaries to prevent coupling and maintain independent testability of layers. Centralized API client ensures consistent authentication and error handling.

## Technology Constraints

**Authoritative Spec Sources:**
- `@specs/overview.md`
- `@specs/features/task-crud.md`
- `@specs/features/authentication.md`
- `@specs/api/rest-endpoints.md`
- `@specs/database/schema.md`
- `@specs/ui/components.md`
- `@specs/ui/pages.md`

**API Behavior Standards:**

All REST endpoints MUST conform exactly to `@specs/api/rest-endpoints.md`:
- All routes under `/api/`
- JSON-only communication
- Pydantic request and response models
- SQLModel for database access
- Ownership enforced on every query
- No endpoint may expose or modify another user's data

**Database Standards:**
- PostgreSQL relational database
- SQLModel ORM for all queries
- User ownership foreign keys enforced
- Referential integrity maintained at schema level

**Frontend Standards:**
- Server components by default
- Client components only when interactivity or auth state required
- Centralized API client for all backend communication
- No inline fetch calls inside UI components
- TypeScript types complete (no `any` types)

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

**Out of Scope:**
- Chatbot or AI features
- Real-time collaboration features
- Mobile native applications
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

**Version**: 1.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
