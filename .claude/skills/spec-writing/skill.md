# Skill: Specification Writing

## Purpose
This skill enables an agent to create clear, comprehensive, and testable feature specifications that serve as the authoritative source of truth for implementation, ensuring all stakeholders have a shared understanding before development begins.

---

## Scope of Responsibility
The Specification Writing skill covers:

- Feature requirement gathering and clarification
- User story and acceptance criteria definition
- Technical constraint documentation
- API contract specification
- Data model requirements
- Non-functional requirements (performance, security, scalability)
- Scope boundaries (in-scope vs. out-of-scope)
- Success metrics and validation criteria

This skill focuses on defining WHAT needs to be built, not HOW to build it. Implementation details belong in architecture and planning documents.

---

## Mandatory Documentation Constraints
This skill MUST follow:

- Spec-Kit conventions and templates (if available)
- Markdown format for all specifications
- Clear section structure (Overview, Requirements, Acceptance Criteria, Constraints)
- Version control and change tracking
- Specification review and approval workflow

Specifications must be written BEFORE implementation begins.

---

## Specification Writing Model (Non-Negotiable)

- All specifications MUST be complete and unambiguous before implementation
- Requirements MUST be testable and verifiable
- Acceptance criteria MUST be clear and measurable
- Constraints MUST be explicit, not implied
- Out-of-scope items MUST be documented to prevent scope creep

---

## Requirement Gathering Responsibilities

The skill MUST ensure:

- User needs and business goals are clearly understood
- Edge cases and error scenarios are identified
- Dependencies on other features or systems are documented
- Performance and scale requirements are quantified
- Security and privacy requirements are explicit
- Accessibility requirements are considered

### Question Framework
When gathering requirements, ask:
- **Who**: Who are the users? What roles exist?
- **What**: What problem does this solve? What are the use cases?
- **Why**: Why is this needed? What's the business value?
- **When**: When should this happen? What triggers this behavior?
- **Where**: Where does this fit in the system? What boundaries exist?
- **How Much**: What are the scale, performance, and cost constraints?

---

## Specification Structure Requirements

Every specification MUST include:

### 1. Overview
- Feature name and description
- Business context and motivation
- Target users and personas
- High-level goals and objectives

### 2. Functional Requirements
- User stories in the format: "As a [role], I want [capability], so that [benefit]"
- Detailed behavior descriptions
- Input and output specifications
- State transitions and workflow

### 3. Acceptance Criteria
- Testable, measurable success conditions
- Format: "Given [context], When [action], Then [outcome]"
- Both positive (happy path) and negative (error) scenarios
- Performance thresholds (response time, throughput, etc.)

### 4. API Contracts (if applicable)
- Endpoint definitions (method, path, parameters)
- Request schema (required/optional fields, types, validation)
- Response schema (success and error formats)
- Status codes and error handling
- Authentication and authorization requirements

### 5. Data Model Requirements (if applicable)
- Entities and their attributes
- Relationships and cardinality
- Constraints (uniqueness, nullability, defaults)
- Ownership and access control rules

### 6. Constraints and Limitations
- Technical constraints (technology stack, platform, libraries)
- Business constraints (budget, timeline, resources)
- Regulatory and compliance requirements
- Security and privacy constraints
- Performance and scalability limits

### 7. Out of Scope
- Explicitly list what is NOT included
- Future enhancements or deferred features
- Alternative approaches not being pursued

### 8. Open Questions and Assumptions
- Unresolved questions that need stakeholder input
- Assumptions made that need validation
- Risks and dependencies

---

## Clarity and Precision Standards

The skill MUST ensure:

- Use precise language (avoid "should", "might", "could" - use "MUST", "MUST NOT", "MAY")
- Define all domain-specific terms and acronyms
- Use consistent terminology throughout
- Avoid ambiguous requirements (e.g., "fast", "user-friendly", "secure")
- Quantify requirements where possible (e.g., "response time < 200ms", not "fast")

### Language Precision
- ✅ "The API MUST return a 401 status code when the JWT is missing or invalid"
- ❌ "The API should handle authentication errors properly"
- ✅ "The system MUST support 1000 concurrent users with p95 latency < 500ms"
- ❌ "The system should be fast and scalable"

---

## Acceptance Criteria Best Practices

The skill MUST write criteria that are:

- **Specific**: Clearly defined, no ambiguity
- **Measurable**: Can be tested and verified
- **Achievable**: Realistic given constraints
- **Relevant**: Tied to user value and business goals
- **Testable**: Can be validated through testing

### Acceptance Criteria Format
```
Given [initial context/state]
When [action or event occurs]
Then [expected outcome]
```

**Example:**
```
Given a user is logged in with a valid JWT token
When the user requests GET /api/tasks
Then the API returns 200 OK with a JSON array of tasks owned by that user
And the response time is less than 200ms
And tasks belonging to other users are not included
```

---

## API Specification Standards

When documenting APIs, the skill MUST include:

### Endpoint Definition
```
POST /api/tasks
Description: Create a new task for the authenticated user
Authentication: Required (JWT Bearer token)
```

### Request Schema
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional, max 2000 chars)",
  "due_date": "ISO 8601 datetime (optional)",
  "priority": "enum: low|medium|high (optional, default: medium)"
}
```

### Success Response
```
Status: 201 Created
Content-Type: application/json

{
  "id": "integer",
  "title": "string",
  "description": "string|null",
  "due_date": "ISO 8601 datetime|null",
  "priority": "string",
  "completed": "boolean",
  "user_id": "integer",
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

### Error Responses
```
400 Bad Request - Invalid input (missing title, title too long, etc.)
401 Unauthorized - Missing or invalid JWT token
500 Internal Server Error - Server-side error
```

---

## Data Model Specification Standards

When documenting data models, the skill MUST define:

### Entity Definition
```
Entity: Task
Description: A user's to-do item

Fields:
- id: integer, primary key, auto-increment
- user_id: integer, foreign key -> User.id, NOT NULL
- title: string(200), NOT NULL
- description: text, nullable
- due_date: datetime, nullable
- priority: enum(low, medium, high), default: medium, NOT NULL
- completed: boolean, default: false, NOT NULL
- created_at: datetime, NOT NULL, auto-set on create
- updated_at: datetime, NOT NULL, auto-update on modify

Constraints:
- user_id foreign key with ON DELETE CASCADE
- Index on user_id for query performance
- Index on (user_id, completed) for filtering

Access Control:
- Users can only access their own tasks (enforced via user_id)
```

---

## Non-Functional Requirements

The skill MUST document:

### Performance Requirements
- Response time targets (p50, p95, p99)
- Throughput requirements (requests per second)
- Resource limits (memory, CPU, storage)

### Security Requirements
- Authentication and authorization mechanisms
- Data encryption (at rest and in transit)
- Input validation and sanitization rules
- Rate limiting and abuse prevention

### Scalability Requirements
- Expected user growth
- Data volume projections
- Concurrent user capacity

### Reliability Requirements
- Uptime SLA targets
- Error rate thresholds
- Disaster recovery and backup needs

---

## Stakeholder Collaboration

The skill MUST ensure:

- Regular review and feedback cycles
- Clear communication of trade-offs and decisions
- Documentation of requirement changes and rationale
- Sign-off from stakeholders before implementation begins

---

## Specification Quality Checklist

Before marking a spec as complete, verify:

- ✅ All user stories have clear acceptance criteria
- ✅ All API endpoints are fully documented (request, response, errors)
- ✅ All data models define fields, types, and constraints
- ✅ Performance, security, and scale requirements are quantified
- ✅ In-scope and out-of-scope items are clearly separated
- ✅ No ambiguous language (e.g., "should", "fast", "secure")
- ✅ All domain terms are defined
- ✅ Open questions are documented (or resolved)
- ✅ Dependencies on other systems/features are identified
- ✅ Error scenarios and edge cases are covered

---

## Cross-Agent Coordination

This skill requires coordination with:

- Architecture-focused agents for technical feasibility review
- Backend-focused agents for API contract validation
- Frontend-focused agents for UI/UX requirements
- Database-focused agents for data model validation
- Testing-focused agents for acceptance criteria review

Specifications should be reviewed by relevant agents before approval.

---

## Specification Lifecycle

1. **Draft**: Initial requirement gathering and documentation
2. **Review**: Stakeholder and technical review
3. **Refinement**: Address feedback and clarify ambiguities
4. **Approval**: Stakeholder sign-off
5. **Implementation**: Used as source of truth during development
6. **Maintenance**: Updated as requirements evolve

---

## Change Management

When specifications change:

- Document the reason for the change
- Assess impact on existing implementation
- Update all affected sections
- Notify relevant stakeholders and agents
- Version the specification or track changes

No undocumented changes are permitted.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- The specification is complete, clear, and unambiguous
- All requirements are testable and measurable
- Stakeholders agree the spec accurately reflects their needs
- Implementation teams can build from the spec without additional clarification
- The spec defines WHAT to build, not HOW to build it
- No implicit assumptions or undocumented behavior exists
- The spec can serve as the basis for test cases
- The spec is maintainable and can evolve with changing requirements

---

## Governing Principles

- Clarity over brevity
- Precision over flexibility
- Testability over aspiration
- Stakeholder alignment over assumption
- Documentation before implementation
- Completeness before approval
- Explicit over implicit
