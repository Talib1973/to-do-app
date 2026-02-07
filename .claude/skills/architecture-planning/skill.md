# Skill: Architecture Planning

## Purpose
This skill enables an agent to translate feature specifications into coherent, maintainable system architecture, making and documenting significant technical decisions that ensure the system meets functional and non-functional requirements.

---

## Scope of Responsibility
The Architecture Planning skill covers:

- System architecture and component design
- Technology stack selection and justification
- Component boundaries and interaction patterns
- Data flow and state management architecture
- API design and contract definition
- Security architecture and trust boundaries
- Performance and scalability architecture
- Architectural Decision Records (ADRs)
- Trade-off analysis and risk assessment
- Integration patterns and dependencies

This skill focuses on defining HOW the system will be built to meet the requirements defined in specifications.

---

## Mandatory Documentation Constraints
This skill MUST follow:

- Architecture plan templates (plan.md)
- Architectural Decision Record (ADR) format
- Clear separation between architecture (HOW) and requirements (WHAT)
- Version control and change tracking
- Architecture review and approval workflow

Architecture plans must be created AFTER specifications are approved and BEFORE implementation begins.

---

## Architecture Planning Model (Non-Negotiable)

- All architecture MUST be driven by approved specifications
- Architectural decisions MUST be justified with trade-off analysis
- Significant decisions MUST be documented in ADRs
- Architecture MUST define component boundaries, data flow, and interfaces
- Implementation details belong in code, not architecture docs

---

## Architecture Plan Structure Requirements

Every architecture plan MUST include:

### 1. Architecture Overview
- High-level system architecture diagram
- Component responsibilities and boundaries
- Technology stack with justification
- Deployment model and infrastructure

### 2. Component Architecture
- Frontend architecture (routing, state management, components)
- Backend architecture (API layer, business logic, data access)
- Database architecture (schema, relationships, constraints)
- Authentication architecture (JWT flow, security boundaries)

### 3. Data Flow and State Management
- Request/response flow across layers
- State management strategy (frontend and backend)
- Caching strategy (if applicable)
- Event flow and side effects

### 4. API Design and Contracts
- REST API design principles
- Endpoint structure and naming conventions
- Request/response schemas
- Error handling strategy
- Versioning strategy

### 5. Security Architecture
- Authentication flow and JWT handling
- Authorization model and access control
- Trust boundaries (client vs. server)
- Data protection (encryption, sanitization)
- Security best practices and standards

### 6. Data Architecture
- Database schema design rationale
- Entity relationships and cardinality
- Indexing strategy
- Data ownership and isolation model
- Migration and versioning strategy

### 7. Performance and Scalability
- Performance targets and budgets
- Scalability considerations
- Caching and optimization strategies
- Resource constraints and limits

### 8. Integration Patterns
- Frontend-backend integration
- Database access patterns
- External service integration (if applicable)
- Error handling and retry logic

### 9. Testing Strategy
- Unit testing approach
- Integration testing strategy
- End-to-end testing plan
- Test data management

### 10. Deployment and Operations
- Deployment architecture
- Environment configuration
- Monitoring and observability
- Error tracking and logging

### 11. Risks and Mitigations
- Technical risks identified
- Mitigation strategies
- Fallback plans
- Known limitations

### 12. Open Questions and Assumptions
- Unresolved architectural questions
- Assumptions requiring validation
- Dependencies on external decisions

---

## Architectural Decision Making

When making architectural decisions, the skill MUST:

### 1. Apply the Three-Part ADR Test
A decision is architecturally significant if ALL of these are true:
- **Impact**: Long-term consequences (framework, data model, API, security, platform)
- **Alternatives**: Multiple viable options were considered
- **Scope**: Cross-cutting and influences overall system design

### 2. Document Significant Decisions
Create an ADR when:
- Choosing between architectural patterns (MVC, layered, microservices)
- Selecting frameworks or major libraries
- Defining authentication/authorization strategy
- Designing data models and schemas
- Establishing API contracts and interfaces
- Making security-critical decisions
- Defining deployment and infrastructure approach

### 3. ADR Structure
Each ADR MUST include:
```markdown
# ADR [Number]: [Decision Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue we're facing? What factors are driving this decision?

## Decision
What architecture decision are we making?

## Alternatives Considered
- Option 1: [description, pros, cons]
- Option 2: [description, pros, cons]
- Option 3: [description, pros, cons]

## Consequences
### Positive
- Benefit 1
- Benefit 2

### Negative
- Drawback 1
- Drawback 2

### Risks
- Risk 1 and mitigation
- Risk 2 and mitigation

## Trade-offs
- Trade-off 1: [what we gain vs. what we sacrifice]
- Trade-off 2: [what we gain vs. what we sacrifice]
```

### 4. Group Related Decisions
Combine related decisions into a single ADR when appropriate:
- Example: "Authentication and Authorization Strategy" (covers JWT, Better Auth, backend verification)
- Example: "Technology Stack Selection" (covers Next.js, FastAPI, PostgreSQL, SQLModel)

---

## Technology Stack Architecture

When defining the technology stack, the skill MUST:

### 1. Justify Each Technology Choice
For each technology, document:
- **What**: The technology being selected
- **Why**: Reasons for selection (requirements it meets, strengths)
- **Alternatives**: Other options considered and why they were rejected
- **Trade-offs**: What we gain and what we sacrifice
- **Constraints**: Limitations and considerations

### 2. Ensure Stack Coherence
Verify that:
- Technologies integrate well together
- No conflicting dependencies or incompatibilities
- Team has expertise or can acquire it
- Licensing is compatible with project requirements
- Performance and scale requirements can be met

### 3. Technology Stack Template
```markdown
## Technology Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
  - Rationale: React-based, server-side rendering, excellent DX
  - Alternatives: Remix, SvelteKit, Nuxt (rejected for...)
  - Trade-offs: Learning curve for App Router vs. Pages Router

- **Styling**: Tailwind CSS
  - Rationale: Utility-first, highly customizable, small bundle
  - Alternatives: CSS Modules, Styled Components
  - Trade-offs: Verbose HTML vs. flexible styling

### Backend
- **Framework**: FastAPI (Python)
  - Rationale: High performance, async, automatic OpenAPI docs
  - Alternatives: Django REST, Flask (rejected for...)
  - Trade-offs: Python vs. Node.js, async complexity

### Database
- **DBMS**: PostgreSQL
  - Rationale: Relational, ACID, mature, excellent tooling
  - Alternatives: MySQL, MongoDB (rejected for...)
  - Trade-offs: SQL vs. NoSQL flexibility

- **ORM**: SQLModel
  - Rationale: Pydantic integration, type safety, FastAPI synergy
  - Alternatives: SQLAlchemy, Tortoise ORM
  - Trade-offs: Less mature vs. better DX
```

---

## Component Boundary Architecture

The skill MUST define clear boundaries:

### 1. Frontend Boundaries
- **Presentation Layer**: UI components (React components)
- **Application Layer**: Routing, state management, client logic
- **API Client Layer**: Centralized backend communication
- **Authentication Layer**: Better Auth integration, JWT handling

### 2. Backend Boundaries
- **API Layer**: FastAPI routes, request/response handling
- **Business Logic Layer**: Domain logic, validation, authorization
- **Data Access Layer**: SQLModel queries, database operations
- **Authentication Layer**: JWT verification, user extraction

### 3. Database Boundaries
- **Schema Layer**: Tables, relationships, constraints
- **Access Control Layer**: User ownership, data isolation
- **Migration Layer**: Schema versioning and updates

### 4. Boundary Rules
- Each layer depends only on layers below it
- No circular dependencies
- Clear interfaces between layers
- Data validation at boundaries

---

## Security Architecture Requirements

The skill MUST define:

### 1. Authentication Architecture
- **Frontend**: Better Auth handles login/signup, issues JWT
- **Token Format**: JWT with standard claims (sub, email, iat, exp)
- **Token Transmission**: Authorization Bearer header only
- **Backend**: Stateless JWT verification on every protected request
- **Secret Management**: BETTER_AUTH_SECRET in environment, never hardcoded

### 2. Authorization Architecture
- **User Identity**: Extracted from verified JWT (never from request body)
- **Access Control**: User-scoped data filtering on all queries
- **Isolation**: Users can only access their own data
- **Roles**: (If applicable) Role claims in JWT, enforced in backend

### 3. Trust Boundaries
```
┌─────────────────────────────────────────────────┐
│ UNTRUSTED ZONE (Client/Frontend)                │
│ - Never trust user-provided identifiers         │
│ - Never trust client-side validation            │
│ - Never trust client state                      │
└─────────────────────────────────────────────────┘
                      ↓ JWT Token
┌─────────────────────────────────────────────────┐
│ TRUSTED ZONE (Backend)                           │
│ - Verify JWT signature                          │
│ - Extract user_id from verified token           │
│ - Enforce authorization on all operations       │
└─────────────────────────────────────────────────┘
                      ↓ Validated Data
┌─────────────────────────────────────────────────┐
│ DATA ZONE (Database)                             │
│ - Enforce constraints at schema level           │
│ - Store user_id foreign keys                    │
│ - Ensure referential integrity                  │
└─────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

The skill MUST document end-to-end flows:

### Example: User Creates a Task
```
1. USER ACTION
   User submits task form in browser

2. FRONTEND (Client Component)
   - Validate input locally
   - Call API client: apiClient.tasks.create(taskData)

3. API CLIENT LAYER
   - Retrieve JWT from Better Auth session
   - Add Authorization: Bearer <jwt> header
   - POST /api/tasks with task data

4. BACKEND (API Layer)
   - Extract and verify JWT
   - Reject if invalid → 401 Unauthorized
   - Extract user_id from verified JWT

5. BACKEND (Business Logic)
   - Validate task data (title, description, etc.)
   - Reject if invalid → 400 Bad Request
   - Create task object with user_id from JWT

6. BACKEND (Data Access)
   - Insert task into database via SQLModel
   - Set task.user_id = authenticated_user_id
   - Return created task object

7. DATABASE
   - Enforce constraints (NOT NULL, foreign key)
   - Insert record with user_id
   - Return created record with ID

8. BACKEND RESPONSE
   - Return 201 Created
   - Include task object in JSON response

9. FRONTEND UPDATE
   - Update UI with new task
   - Refresh task list or add optimistically
```

---

## API Architecture Standards

The skill MUST define:

### 1. API Design Principles
- RESTful conventions (resources, verbs, status codes)
- Consistent naming (plural nouns, lowercase, hyphens)
- Versioning strategy (if applicable)
- Idempotency for mutations

### 2. Endpoint Structure
```
/api/v1/resources
/api/v1/resources/:id
/api/v1/resources/:id/sub-resources
```

### 3. Authentication Enforcement
- All endpoints except public ones require JWT
- Middleware extracts and verifies JWT
- User identity available to all route handlers

### 4. Error Handling Strategy
- Consistent error response format
- Appropriate HTTP status codes
- Meaningful error messages (without leaking internals)
- Error logging and monitoring

### 5. Response Standards
```json
// Success Response
{
  "data": { ... },
  "meta": { "count": 10, "page": 1 }
}

// Error Response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Title is required",
    "details": { "field": "title", "constraint": "required" }
  }
}
```

---

## Performance Architecture

The skill MUST address:

### 1. Performance Budgets
- API response time targets (p50, p95, p99)
- Frontend page load targets
- Database query performance limits
- Resource consumption limits

### 2. Optimization Strategies
- Database indexing for common queries
- API response pagination
- Frontend code splitting
- Asset optimization (images, bundles)

### 3. Caching Strategy (if applicable)
- What to cache (static data, computed results)
- Where to cache (browser, CDN, server, database)
- Cache invalidation strategy
- TTL and eviction policies

### 4. Scalability Considerations
- Stateless backend for horizontal scaling
- Database connection pooling
- Concurrent user capacity
- Data growth projections

---

## Testing Architecture

The skill MUST define:

### 1. Test Pyramid Strategy
```
         ┌─────────────┐
         │   E2E Tests  │  (Few, critical user flows)
         ├─────────────┤
         │ Integration  │  (API + DB, cross-layer)
         ├─────────────┤
         │  Unit Tests  │  (Many, fast, isolated)
         └─────────────┘
```

### 2. Testing Boundaries
- **Unit**: Individual functions, components, models
- **Integration**: API endpoints with database, auth flows
- **E2E**: Complete user flows from UI to database

### 3. Test Data Strategy
- Test database isolated from production
- Fixtures for consistent starting state
- Cleanup after each test
- No test interdependencies

---

## Architecture Quality Checklist

Before finalizing architecture, verify:

- ✅ All components have clear responsibilities
- ✅ Boundaries and interfaces are well-defined
- ✅ Data flow is documented for key scenarios
- ✅ Security architecture addresses all trust boundaries
- ✅ Technology choices are justified with trade-off analysis
- ✅ Significant decisions documented in ADRs
- ✅ Performance and scale requirements addressed
- ✅ Testing strategy is comprehensive
- ✅ Risks identified with mitigation strategies
- ✅ Architecture supports specification requirements
- ✅ No circular dependencies or coupling
- ✅ Deployment and operations considered

---

## Cross-Agent Coordination

This skill requires coordination with:

- **Spec-writer**: Ensure architecture meets all requirements
- **Database-engineer**: Validate data model and schema design
- **Backend-engineer**: Review API architecture and boundaries
- **Frontend-engineer**: Review component architecture and integration
- **Auth-engineer**: Validate authentication and security architecture
- **Integration-tester**: Ensure testability of architecture

Architecture should be reviewed by all relevant agents before implementation.

---

## Architecture Lifecycle

1. **Planning**: Review specifications, identify architectural needs
2. **Design**: Create architecture plan with component boundaries
3. **Decision Documentation**: Create ADRs for significant decisions
4. **Review**: Technical review by specialized agents
5. **Refinement**: Address feedback and concerns
6. **Approval**: Stakeholder and technical sign-off
7. **Implementation Guidance**: Support teams during development
8. **Evolution**: Update architecture as requirements change

---

## Change Management

When architecture changes:

- Document the reason for the change
- Assess impact on existing implementation
- Create or update ADRs as needed
- Update architecture diagrams and documentation
- Notify all affected agents and teams
- Ensure backward compatibility or migration path

No undocumented architectural changes are permitted.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- Architecture plan is complete, clear, and implementable
- All significant decisions documented with justification
- Component boundaries and interfaces are well-defined
- Architecture meets all functional and non-functional requirements
- Trade-offs are explicitly analyzed and documented
- Technology stack is coherent and justified
- Security architecture is robust and comprehensive
- Performance and scale requirements are addressed
- Testing strategy enables verification
- Risks are identified with mitigation plans
- Architecture is reviewable and maintainable
- No implicit assumptions or undocumented decisions

---

## Governing Principles

- Specifications drive architecture
- Justify all significant decisions
- Document trade-offs explicitly
- Security is non-negotiable
- Simplicity over complexity
- Coherence over fragmentation
- Testability over cleverness
- Evolvability over perfection
- Clear boundaries over tight coupling
- Explicit over implicit
