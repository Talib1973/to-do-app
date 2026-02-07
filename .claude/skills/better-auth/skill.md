# Skill: Authentication Engineering

## Purpose
This skill enables an agent to design, implement, and enforce secure authentication and authorization for a full-stack web application using Better Auth and JWT tokens, following spec-driven development principles.

---

## Scope of Responsibility
The Authentication Engineering skill covers:

- End-to-end authentication flow design
- Better Auth configuration on the frontend
- JWT issuance, structure, and expiry policy
- Stateless JWT verification in the backend
- Authorization enforcement and user isolation
- Authentication-related specification authoring

This skill is focused exclusively on authentication and authorization concerns.

---

## Mandatory Technology Constraints
This skill MUST be exercised using the following technologies only:

- Better Auth (frontend)
- JWT (JSON Web Tokens)
- FastAPI (backend verification)
- Shared secret via environment variable: `BETTER_AUTH_SECRET`

Alternative authentication mechanisms such as server-side sessions, custom token formats, or direct frontend-backend trust are not permitted.

---

## Authentication Model (Non-Negotiable)

### Flow Overview
- Authentication logic runs on the frontend via Better Auth
- Better Auth issues signed JWT tokens upon successful login or signup
- JWT is sent with every backend API request using:
  - **HTTP Authorization header**: `Authorization: Bearer <jwt-token>`
  - This is the ONLY accepted method; cookies or query parameters are NOT supported

### JWT Structure
The JWT payload MUST contain the following claims:
- `sub` (subject): User ID (primary identifier)
- `email`: User's email address
- `iat` (issued at): Token creation timestamp
- `exp` (expiration): Token expiry timestamp
- Optional: `name`, `role`, or other user metadata

### Backend Verification Process
1. Extract JWT from `Authorization` header
2. Verify signature using `BETTER_AUTH_SECRET`
3. Validate expiration (`exp` claim)
4. Extract `sub` (user_id) from verified token
5. Use extracted `user_id` for all database queries and authorization checks

### Security Boundaries and Trust Model
- **Frontend (Untrusted)**: Never trust any user identifier sent from the client
- **Backend (Trusted)**: All protected endpoints MUST extract `user_id` from verified JWT
- **Critical Rule**: The backend MUST NEVER accept `user_id` as a request parameter
  - ❌ **FORBIDDEN**: `POST /api/tasks {"user_id": 123, "title": "..."}`
  - ✅ **REQUIRED**: Extract user_id from JWT, ignore any client-provided user_id

### Token Lifecycle
- **Expiration**: JWTs expire after a configurable period (e.g., 24 hours, 7 days)
- **Refresh Strategy**: Handled by Better Auth (if supported) or re-authentication required
- **Revocation**: Stateless JWTs cannot be revoked; rely on short expiry times

### User Isolation and Authorization
- Every protected endpoint MUST filter data by authenticated `user_id`
- Example: When fetching tasks, query `WHERE user_id = <from_jwt>`
- Cross-user data access is BLOCKED by design
- Admin/role-based access requires explicit role claims in JWT

### Environment Configuration
- `BETTER_AUTH_SECRET`: Shared secret for signing and verifying JWTs
  - MUST be stored in `.env` (never hardcoded)
  - MUST be identical on frontend (Better Auth) and backend (FastAPI)
  - MUST be cryptographically secure (minimum 32 bytes, random)

---
