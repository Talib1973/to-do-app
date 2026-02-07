# Skill: Integration Testing

## Purpose
This skill enables an agent to validate that frontend, backend, authentication, and database components work together correctly as a cohesive system, ensuring end-to-end functionality, security enforcement, and specification compliance.

---

## Scope of Responsibility
The Integration Testing skill covers:

- End-to-end user flow validation
- Cross-layer integration verification
- Authentication and authorization testing
- API contract compliance
- Database state validation
- Error handling and edge case testing
- Security boundary enforcement

This skill focuses on system-wide integration and does not replace unit testing or component-level testing.

---

## Mandatory Technology Constraints
This skill MUST be exercised using the following technologies:

- pytest (Python testing framework)
- FastAPI TestClient (for backend API testing)
- PostgreSQL test database
- JWT tokens for authentication testing
- HTTP client for API requests

Testing must occur against actual integrated components, not mocks or stubs, unless explicitly specified.

---

## Testing Model (Non-Negotiable)

- All integration tests MUST be driven by written specifications
- Tests validate actual user flows and acceptance criteria
- Tests execute against real database and API instances
- Authentication flows use real JWT tokens
- No test may pass with hardcoded or mocked authentication

---

## End-to-End Flow Responsibilities

The skill MUST validate:

- Complete user registration and login flows
- Authenticated API request sequences
- Data persistence and retrieval across layers
- State consistency between frontend expectations and backend responses
- Proper handling of authentication state changes

### Example Flow Testing
- User signup → JWT issued → Authenticated request → Data created → Data retrieved → Data belongs to correct user

---

## Authentication & Authorization Testing

The skill MUST verify:

- JWT tokens are required for protected endpoints
- Invalid or expired tokens are rejected with `401 Unauthorized`
- Missing authentication headers return `401 Unauthorized`
- Users can only access their own data (`403 Forbidden` for cross-user access attempts)
- Logout invalidates client-side authentication state

### Security Boundary Tests
- ✅ Valid JWT → Access granted
- ❌ No JWT → `401 Unauthorized`
- ❌ Invalid JWT → `401 Unauthorized`
- ❌ Expired JWT → `401 Unauthorized`
- ❌ Valid JWT, wrong user → `403 Forbidden`

---

## API Contract Validation

The skill MUST verify:

- Request and response schemas match specifications
- HTTP status codes align with documented behavior
- Error responses include meaningful messages
- Content-Type headers are correct (`application/json`)
- API versioning and routing conventions are followed

### Status Code Testing
- Valid request → `200 OK` or `201 Created`
- Invalid input → `400 Bad Request`
- Unauthenticated → `401 Unauthorized`
- Unauthorized access → `403 Forbidden`
- Not found → `404 Not Found`
- Server error → `500 Internal Server Error`

---

## Database State Validation

The skill MUST verify:

- Data created via API is correctly persisted
- Foreign key relationships are maintained
- User ownership fields are correctly populated
- Data retrieved matches data created
- Database constraints are enforced (uniqueness, nullability)
- Cascading deletes work as specified

### Data Isolation Tests
- User A creates data → User B cannot access User A's data
- User B creates data → User A cannot access User B's data
- Each user sees only their own data

---

## Error Handling & Edge Cases

The skill MUST validate:

- Graceful handling of malformed requests
- Proper validation error messages
- Handling of missing required fields
- Handling of invalid data types
- Database constraint violations return appropriate errors
- Network and timeout scenarios (if applicable)

---

## Test Data Management

The skill MUST ensure:

- Test database is isolated from production
- Tests are idempotent and can run repeatedly
- Test data is cleaned up after test execution
- No test depends on another test's state
- Fixtures provide consistent starting state

---

## Specification Responsibilities

When applying this skill, the agent MUST:

- Reference acceptance criteria from specifications
- Validate that implementation meets all specified behaviors
- Flag any discrepancies between specs and actual behavior
- Document test coverage gaps
- Propose spec updates when edge cases are discovered

Tests MUST NOT validate undocumented or implicit behavior.

---

## Cross-Agent Coordination

This skill requires coordination with:

- Backend-focused agents for API implementation status
- Frontend-focused agents for client-side integration
- Authentication-focused agents for JWT flow correctness
- Database-focused agents for schema validation
- Specification-focused agents for acceptance criteria

Integration tests should run AFTER implementation is complete to validate the integrated system.

---

## Test Execution Workflow

1. **Setup**: Initialize test database, create test users, generate JWT tokens
2. **Execute**: Run user flow or scenario test
3. **Verify**: Assert expected outcomes (status codes, response data, database state)
4. **Teardown**: Clean up test data and reset state

---

## Test Coverage Requirements

The skill MUST ensure tests cover:

- Happy path scenarios (valid inputs, successful operations)
- Authentication flows (signup, login, logout)
- Authorization failures (cross-user access attempts)
- Input validation failures (missing fields, invalid types)
- Database constraint violations
- Error handling and recovery

Minimum coverage: All API endpoints, all user flows, all authentication scenarios.

---

## Success Criteria

This skill is considered successfully applied ONLY IF:

- All user flows execute successfully from start to finish
- Authentication and authorization are enforced correctly
- API responses match specifications (schema, status codes, data)
- Database state is consistent and correctly isolated per user
- Error scenarios return appropriate status codes and messages
- No security vulnerabilities exist (JWT bypass, cross-user access)
- Test suite is maintainable, reliable, and fast
- All acceptance criteria from specifications are validated

---

## Test Reporting

Tests MUST produce:

- Clear pass/fail indicators
- Detailed failure messages with context
- Information about which specification requirement failed
- Reproduction steps for failures
- Coverage reports showing tested vs. untested scenarios

---

## Governing Principles

- Validate specifications, not assumptions
- Test real integrations, not mocks
- Security enforcement is non-negotiable
- User isolation must be verified in every scenario
- Fast feedback over exhaustive coverage
- Maintainable tests over clever tests
- Explicit assertions over implicit expectations
