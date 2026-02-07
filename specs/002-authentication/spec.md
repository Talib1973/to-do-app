# Feature Specification: User Authentication

**Feature Branch**: `002-authentication`
**Created**: 2026-02-06
**Status**: Draft
**Input**: User description: "Create user authentication specification with Better Auth and JWT token implementation, including signup, login, logout flows and security requirements"

## Feature Summary

User authentication enables secure access control for the Todo application through email/password credentials. Users can create accounts (signup), access their accounts (login), and terminate their sessions (logout). Authentication uses Better Auth on the frontend to issue JWT tokens, which are verified by the FastAPI backend for every protected request.

All authentication mechanisms enforce user-level data isolation, ensuring that each user can only access their own tasks and data. The system uses stateless JWT tokens for scalability and performance.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Account Creation (Signup) (Priority: P1)

As a new user, I want to create an account with my email and password so that I can start managing my tasks securely.

**Why this priority**: Account creation is the entry point for all new users. Without this functionality, users cannot access the application. This is the foundation for user identification and data ownership.

**Independent Test**: A user can visit the signup page, enter a unique email and secure password, submit the form, and receive confirmation that their account was created. The user is automatically logged in and redirected to their empty dashboard with a valid JWT token.

**Acceptance Scenarios**:

1. **Given** a user visits the signup page, **When** they enter a valid email (user@example.com) and password (min 8 chars) and submit, **Then** a new user account is created in the database and the user receives a JWT token
2. **Given** a user attempts to signup, **When** they enter an email that already exists, **Then** the system returns 400 Bad Request with message "Email already registered" without revealing account existence
3. **Given** a user attempts to signup, **When** they enter an invalid email format (missing @, invalid domain), **Then** the system returns 400 Bad Request with message "Invalid email format"
4. **Given** a user attempts to signup, **When** they enter a password shorter than 8 characters, **Then** the system returns 400 Bad Request with message "Password must be at least 8 characters"
5. **Given** a user successfully signs up, **When** the account is created, **Then** the password is hashed using bcrypt or argon2 (never stored in plaintext)
6. **Given** a user successfully signs up, **When** they are redirected to the dashboard, **Then** they have a valid JWT token stored in the client that can be used for authenticated requests

---

### User Story 2 - Account Access (Login) (Priority: P1)

As a returning user, I want to log in with my email and password so that I can access my existing tasks and data.

**Why this priority**: Login is required for all returning users to access their data. Without login functionality, users cannot return to their accounts after signing up.

**Independent Test**: A user with an existing account can visit the login page, enter correct credentials, submit the form, and be redirected to their dashboard with all their existing tasks visible. The user receives a valid JWT token for subsequent requests.

**Acceptance Scenarios**:

1. **Given** a user with existing account (email: user@example.com, password: correctpass), **When** they enter correct credentials and submit, **Then** they receive a valid JWT token and are redirected to their dashboard
2. **Given** a user attempts to login, **When** they enter a correct email but incorrect password, **Then** the system returns 401 Unauthorized with message "Invalid email or password" (generic message to prevent email enumeration)
3. **Given** a user attempts to login, **When** they enter an email that doesn't exist, **Then** the system returns 401 Unauthorized with message "Invalid email or password" (same generic message)
4. **Given** a user successfully logs in, **When** the JWT token is issued, **Then** the token contains claims: sub (user_id), email, iat (issued at), exp (expiration time 24 hours from now)
5. **Given** a user logs in successfully, **When** they make subsequent API requests, **Then** the JWT token is automatically attached to requests via the Authorization Bearer header
6. **Given** a user is already logged in (has valid JWT), **When** they visit the login page directly, **Then** they are redirected to their dashboard (no need to login again)

---

### User Story 3 - Session Termination (Logout) (Priority: P1)

As a logged-in user, I want to log out so that my session ends and my account is secure on shared devices.

**Why this priority**: Logout is essential for security, especially on shared or public devices. Users must be able to explicitly terminate their sessions.

**Independent Test**: A logged-in user can click the logout button, have their JWT token cleared from the client, and be redirected to the login page. Subsequent attempts to access protected routes fail with 401 Unauthorized.

**Acceptance Scenarios**:

1. **Given** a user is logged in with a valid JWT token, **When** they click the logout button, **Then** the JWT token is cleared from client storage (localStorage, cookie, or memory)
2. **Given** a user has just logged out, **When** they attempt to access a protected route (e.g., /dashboard), **Then** they are redirected to the login page with 401 Unauthorized
3. **Given** a user has just logged out, **When** they try to make an API request, **Then** the request fails with 401 Unauthorized because no JWT token is present
4. **Given** a user logs out, **When** they are redirected to the login page, **Then** they see a confirmation message "You have been logged out successfully"

---

### User Story 4 - Automatic Session Expiration (Priority: P2)

As the system, I want JWT tokens to expire after 24 hours so that inactive sessions don't pose a security risk.

**Why this priority**: Token expiration is a security best practice that limits the window of vulnerability if a token is compromised. This reduces long-term security risks.

**Independent Test**: A user logs in and receives a JWT token. After 24 hours, the token expires. When the user attempts to make an API request with the expired token, they receive 401 Unauthorized and are redirected to login.

**Acceptance Scenarios**:

1. **Given** a user logs in at time T, **When** a JWT token is issued, **Then** the token's exp claim is set to T + 24 hours
2. **Given** a user has a JWT token issued 24 hours and 1 minute ago, **When** they make an API request, **Then** the backend returns 401 Unauthorized with message "Token expired"
3. **Given** a user receives a 401 due to token expiration, **When** the frontend detects this response, **Then** the user is redirected to the login page with message "Your session has expired, please log in again"
4. **Given** a user has a JWT token that is still valid (not expired), **When** they make an API request, **Then** the request succeeds with 200 OK and the token is accepted

---

### User Story 5 - Protected Route Access Control (Priority: P1)

As the system, I want to enforce authentication on all protected routes so that unauthenticated users cannot access user data.

**Why this priority**: Access control is a core security requirement. All user data must be protected behind authentication to prevent unauthorized access.

**Independent Test**: An unauthenticated user (no JWT token) attempts to access protected routes (/dashboard, /api/tasks). All requests are rejected with 401 Unauthorized and the user is redirected to the login page.

**Acceptance Scenarios**:

1. **Given** an unauthenticated user (no JWT token), **When** they attempt to access /dashboard, **Then** they are redirected to /login with 401 Unauthorized
2. **Given** an unauthenticated user, **When** they attempt to access GET /api/tasks, **Then** the API returns 401 Unauthorized with message "Authentication required"
3. **Given** a user with an invalid JWT token (malformed, wrong signature), **When** they attempt to access a protected route, **Then** the system returns 401 Unauthorized
4. **Given** a user with a valid JWT token, **When** they attempt to access a protected route, **Then** the request succeeds and user_id is extracted from the JWT sub claim
5. **Given** public routes (/login, /signup, /), **When** an unauthenticated user accesses them, **Then** the requests succeed without requiring a JWT token

---

### Edge Cases

- **What happens when a user submits the signup form multiple times rapidly?**
  The system uses email uniqueness constraint in the database. The first request creates the account; subsequent requests return 400 Bad Request "Email already registered". Idempotency is maintained.

- **What happens if the JWT secret (BETTER_AUTH_SECRET) is changed?**
  All existing JWT tokens become invalid immediately because the signature verification fails. All users must log in again to receive new tokens signed with the new secret.

- **What happens when a user tries to login with SQL injection attempts in the email field?**
  The system uses parameterized queries (SQLModel ORM), which automatically escapes user input. The login attempt fails with 401 Unauthorized as the malicious input won't match any email.

- **What happens if Better Auth is unavailable or fails to initialize?**
  The frontend displays an error message "Authentication service unavailable" and prevents users from accessing protected pages. The backend continues to verify JWTs normally for already-logged-in users.

- **What happens when a user's JWT token is stolen?**
  The attacker can access the user's account until the token expires (24 hours). There is no server-side token revocation in the stateless JWT model. Mitigation: short expiration times, HTTPS-only transmission, secure storage.

- **What happens when a user tries to use the same JWT token from multiple devices?**
  The JWT token works from any device because the backend is stateless. This is expected behavior. Users can log in from multiple devices simultaneously.

## Requirements *(mandatory)*

### Functional Requirements

#### Authentication Flow

- **FR-001**: System MUST provide a signup page at route /signup accessible to unauthenticated users
- **FR-002**: System MUST provide a login page at route /login accessible to unauthenticated users
- **FR-003**: System MUST provide a logout mechanism accessible to authenticated users
- **FR-004**: Signup process MUST accept email and password as required fields
- **FR-005**: Login process MUST accept email and password for authentication
- **FR-006**: System MUST validate email format (contains @, valid domain structure)
- **FR-007**: System MUST enforce password minimum length of 8 characters
- **FR-008**: System MUST hash passwords using bcrypt or argon2 before storing in database
- **FR-009**: System MUST never store passwords in plaintext
- **FR-010**: System MUST enforce email uniqueness (one account per email address)

#### JWT Token Management

- **FR-011**: System MUST use Better Auth library on the frontend to manage authentication state
- **FR-012**: Better Auth MUST issue JWT tokens upon successful login or signup
- **FR-013**: JWT tokens MUST contain the following claims:
  - `sub`: User ID (integer, primary key from users table)
  - `email`: User's email address (string)
  - `iat`: Issued at timestamp (Unix timestamp)
  - `exp`: Expiration timestamp (Unix timestamp, 24 hours from iat)
- **FR-014**: JWT tokens MUST be signed using HMAC SHA-256 (HS256) algorithm
- **FR-015**: JWT signing MUST use the shared secret from BETTER_AUTH_SECRET environment variable
- **FR-016**: BETTER_AUTH_SECRET MUST be identical on frontend (Better Auth) and backend (FastAPI)
- **FR-017**: BETTER_AUTH_SECRET MUST be at least 32 characters long and cryptographically random
- **FR-018**: JWT tokens MUST be transmitted via Authorization header in format: `Authorization: Bearer <token>`
- **FR-019**: System MUST NOT transmit JWT tokens via query parameters or cookies
- **FR-020**: JWT tokens MUST expire after 24 hours from issuance

#### Backend JWT Verification

- **FR-021**: Backend MUST verify JWT signature on every protected endpoint request
- **FR-022**: Backend MUST validate JWT expiration time (exp claim)
- **FR-023**: Backend MUST extract user_id from JWT sub claim after successful verification
- **FR-024**: Backend MUST use user_id from JWT for all database queries (never trust client-provided user_id)
- **FR-025**: Backend MUST return 401 Unauthorized for requests with missing JWT tokens
- **FR-026**: Backend MUST return 401 Unauthorized for requests with invalid JWT tokens (malformed, wrong signature)
- **FR-027**: Backend MUST return 401 Unauthorized for requests with expired JWT tokens
- **FR-028**: Backend MUST implement JWT verification as a FastAPI dependency (Depends) for reusability

#### API Endpoints

- **FR-029**: System MUST provide POST /api/auth/signup endpoint (public, no JWT required)
- **FR-030**: System MUST provide POST /api/auth/login endpoint (public, no JWT required)
- **FR-031**: System MUST provide POST /api/auth/logout endpoint (optional, client-side logout)
- **FR-032**: System MUST provide GET /api/auth/me endpoint (protected, returns current user profile)

#### Error Handling

- **FR-033**: Invalid credentials (login) MUST return 401 Unauthorized with generic message "Invalid email or password"
- **FR-034**: Email already exists (signup) MUST return 400 Bad Request with message "Email already registered"
- **FR-035**: Invalid email format MUST return 400 Bad Request with message "Invalid email format"
- **FR-036**: Password too short MUST return 400 Bad Request with message "Password must be at least 8 characters"
- **FR-037**: Missing required fields MUST return 400 Bad Request with field-specific error messages
- **FR-038**: System MUST NOT reveal whether an email exists in error messages for login (prevent email enumeration)

### Key Entities *(include if feature involves data)*

- **User**: Represents an authenticated user account
  - Unique email address (used for login)
  - Hashed password (bcrypt or argon2)
  - User ID (primary key, used in JWT sub claim)
  - Created timestamp
  - Updated timestamp

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new user can create an account and be logged in within 30 seconds from landing on the signup page
- **SC-002**: 100% of signup attempts with duplicate emails are rejected with appropriate error messages
- **SC-003**: 100% of passwords are hashed before storage (zero plaintext passwords in database)
- **SC-004**: JWT tokens are successfully verified on 100% of valid authenticated requests
- **SC-005**: 100% of unauthenticated requests to protected endpoints return 401 Unauthorized
- **SC-006**: 100% of expired JWT tokens are rejected with 401 Unauthorized
- **SC-007**: Users can successfully log out and have their tokens cleared, preventing further API access
- **SC-008**: The authentication flow handles 100 concurrent signup/login requests without errors
- **SC-009**: Zero SQL injection vulnerabilities in authentication endpoints (verified through security testing)
- **SC-010**: JWT secret (BETTER_AUTH_SECRET) is never exposed in client-side code or API responses

## Technology Constraints *(mandatory)*

### Frontend Authentication

- **Better Auth**: JavaScript/TypeScript library for Next.js App Router
- **JWT Storage**: Better Auth manages token storage (localStorage, memory, or secure cookie)
- **Token Transmission**: Automatic attachment of Authorization Bearer header to API requests

### Backend Authentication

- **FastAPI Dependencies**: JWT verification implemented as reusable Depends() dependency
- **PyJWT Library**: Used for JWT decoding and signature verification
- **Passlib + Bcrypt**: Used for password hashing and verification
- **SQLModel**: ORM for user lookup and creation

### Environment Variables

- **BETTER_AUTH_SECRET**: Shared secret for JWT signing and verification (min 32 chars, random)
- **DATABASE_URL**: PostgreSQL connection string for user table access

### Security Standards

- **Password Hashing**: bcrypt or argon2 with appropriate cost factor
- **JWT Algorithm**: HS256 (HMAC SHA-256)
- **Token Expiration**: 24 hours from issuance
- **HTTPS**: Required in production for secure token transmission

## Dependencies & Assumptions

### External Dependencies

- **Better Auth**: Assumes Better Auth is compatible with Next.js 14+ App Router
- **PyJWT**: Python library for JWT operations
- **Passlib**: Python library for password hashing

### Assumptions

1. **No Refresh Tokens**: JWT tokens are long-lived (24 hours) without refresh token mechanism for MVP simplicity
2. **No Password Reset**: Password reset functionality is out of scope for this specification
3. **No Email Verification**: Users can signup and login immediately without email confirmation
4. **No Multi-Factor Authentication (MFA)**: Only email/password authentication for MVP
5. **No OAuth Providers**: Only email/password signup (no Google, GitHub, etc.)
6. **Stateless Backend**: No server-side session storage; JWT tokens are the only authentication mechanism
7. **Same-Origin Requests**: Frontend and backend deployed with proper CORS configuration
8. **HTTPS in Production**: All token transmission occurs over HTTPS to prevent man-in-the-middle attacks

### Out of Scope

The following are explicitly OUT OF SCOPE for this authentication specification:

- **Password Reset/Recovery**: No "forgot password" functionality
- **Email Verification**: No confirmation emails or account activation
- **OAuth2/Social Login**: No Google, GitHub, Facebook login
- **Multi-Factor Authentication (MFA)**: No TOTP, SMS codes, or authenticator apps
- **Refresh Tokens**: No token refresh mechanism (users must re-login after 24 hours)
- **Account Deletion**: User account deletion is not covered in this spec
- **Profile Updates**: Changing email or password is not covered
- **Session Management**: No server-side session tracking or concurrent session limits
- **Rate Limiting**: API rate limiting on auth endpoints is not specified here

## API Specifications

### POST /api/auth/signup

**Purpose**: Create a new user account

**Authentication**: None (public endpoint)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Request Validation**:
- `email`: Required, string, valid email format
- `password`: Required, string, minimum 8 characters

**Success Response (201 Created)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-06T12:00:00Z",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- `400 Bad Request`: Email already exists, invalid email format, password too short, missing fields
- `500 Internal Server Error`: Server-side error

**Example Error**:
```json
{
  "error": {
    "code": "EMAIL_EXISTS",
    "message": "Email already registered"
  }
}
```

---

### POST /api/auth/login

**Purpose**: Authenticate an existing user and issue JWT token

**Authentication**: None (public endpoint)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Success Response (200 OK)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error Responses**:
- `401 Unauthorized`: Invalid credentials (wrong email or password)
- `400 Bad Request`: Missing required fields
- `500 Internal Server Error`: Server-side error

**Example Error**:
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

---

### GET /api/auth/me

**Purpose**: Get the currently authenticated user's profile

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Success Response (200 OK)**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "created_at": "2026-02-06T12:00:00Z"
}
```

**Error Responses**:
- `401 Unauthorized`: Missing, invalid, or expired JWT token
- `500 Internal Server Error`: Server-side error

---

### POST /api/auth/logout (Optional)

**Purpose**: Logout endpoint (primarily client-side token clearing)

**Authentication**: Optional (can be called with or without token)

**Request**: Empty body

**Success Response (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

**Notes**:
- Logout is primarily handled client-side by clearing the JWT token
- This endpoint is optional and can be used for logging or analytics
- Server does not maintain session state, so logout only clears client token

## Frontend Implementation Notes

### Better Auth Configuration

```typescript
// frontend/src/lib/auth.ts
import { createAuth } from 'better-auth'

export const auth = createAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  jwt: {
    algorithm: 'HS256',
    expiresIn: '24h'
  },
  endpoints: {
    signup: '/api/auth/signup',
    login: '/api/auth/login',
    logout: '/api/auth/logout'
  }
})
```

### API Client JWT Injection

```typescript
// frontend/src/lib/api-client.ts
import { auth } from './auth'

async function apiRequest(endpoint: string, options: RequestInit = {}) {
  const token = await auth.getToken()
  
  const headers = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers
  })
  
  if (response.status === 401) {
    // Token expired or invalid, redirect to login
    auth.logout()
    window.location.href = '/login'
  }
  
  return response
}
```

## Backend Implementation Notes

### JWT Verification Dependency

```python
# backend/src/auth/jwt.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from sqlmodel import Session, select
from src.database import get_session
from src.models.user import User
import os

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    token = credentials.credentials
    secret = os.getenv("BETTER_AUTH_SECRET")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = session.exec(
            select(User).where(User.id == user_id)
        ).first()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
```

### Password Hashing

```python
# backend/src/auth/password.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

## Security Considerations

### Password Security

- **Hashing Algorithm**: bcrypt with default cost factor (12 rounds) or argon2
- **Salt**: Automatically generated per password by bcrypt/argon2
- **Plaintext Storage**: NEVER store passwords in plaintext
- **Password Transmission**: Always over HTTPS in production

### JWT Security

- **Secret Key**: BETTER_AUTH_SECRET must be strong (min 32 chars, cryptographically random)
- **Algorithm**: Only HS256 allowed (no "none" algorithm)
- **Expiration**: Mandatory 24-hour expiration
- **Transmission**: Only via Authorization Bearer header (not URL params or cookies)
- **Storage**: Client-side storage managed by Better Auth (secure practices)

### Attack Mitigation

- **SQL Injection**: Prevented by SQLModel parameterized queries
- **Brute Force**: Not addressed in this spec (rate limiting out of scope)
- **Email Enumeration**: Generic error messages for login failures
- **Token Theft**: Mitigated by HTTPS, short expiration, secure storage
- **CSRF**: Not applicable (stateless JWT, no cookies with credentials)
- **XSS**: Client-side framework (Next.js) handles escaping

## Next Steps

Once this specification is approved:

1. **Database Schema**: Ensure users table exists with required fields (covered in 004-database-schema)
2. **Backend Implementation**:
   - Implement POST /api/auth/signup endpoint
   - Implement POST /api/auth/login endpoint
   - Implement GET /api/auth/me endpoint
   - Create JWT verification dependency
   - Create password hashing utilities
3. **Frontend Implementation**:
   - Configure Better Auth
   - Create SignupForm component
   - Create LoginForm component
   - Create logout functionality
   - Integrate JWT with API client
4. **Testing**:
   - Unit tests for password hashing
   - Unit tests for JWT verification
   - Integration tests for auth endpoints
   - End-to-end tests for complete auth flows
