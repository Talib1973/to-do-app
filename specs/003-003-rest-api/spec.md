# Feature Specification: REST API Endpoints

**Feature Branch**: `003-003-rest-api`  
**Created**: 2026-02-06  
**Status**: Draft  
**Input**: User description: "create the rest api spec"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Task Creation (Priority: P1)

Users can create new tasks with title, description, and completion status to organize their work.

**Why this priority**: Task creation is the foundation of the application - without it, users cannot add any content. This is the most basic CRUD operation and must work first.

**Independent Test**: Can be fully tested by sending a POST request to /api/tasks with valid JWT token and verifying the task is created with user ownership.

**Acceptance Scenarios**:

1. **Given** I am authenticated with valid JWT, **When** I POST /api/tasks with {"title": "Buy groceries", "description": "Milk and eggs", "completed": false}, **Then** I receive 201 Created with the task object including generated id, user_id, and timestamps
2. **Given** I am authenticated with valid JWT, **When** I POST /api/tasks with {"title": "Meeting"} (minimal fields), **Then** I receive 201 Created with task having null description and completed=false as defaults
3. **Given** I am authenticated with valid JWT, **When** I POST /api/tasks with {"title": ""} (empty title), **Then** I receive 400 Bad Request with validation error
4. **Given** I am authenticated with valid JWT, **When** I POST /api/tasks with invalid JSON, **Then** I receive 400 Bad Request with parse error
5. **Given** I am NOT authenticated (no JWT), **When** I POST /api/tasks with any data, **Then** I receive 401 Unauthorized
6. **Given** I am authenticated with valid JWT, **When** I POST /api/tasks with {"title": "Task", "user_id": "other-user-id"} (attempting to set user_id), **Then** the request succeeds but user_id is set from JWT sub claim, not request body

---

### User Story 2 - Task Retrieval (Priority: P1)

Users can view all their tasks to see what they need to do.

**Why this priority**: Viewing tasks is equally critical to creating them - users must be able to see their work. This completes the basic read operation.

**Independent Test**: Can be fully tested by creating tasks for a user, then retrieving them via GET /api/tasks and verifying only that user's tasks are returned.

**Acceptance Scenarios**:

1. **Given** I am authenticated and have 5 tasks, **When** I GET /api/tasks, **Then** I receive 200 OK with array of exactly 5 tasks, all having my user_id
2. **Given** I am authenticated and have no tasks, **When** I GET /api/tasks, **Then** I receive 200 OK with empty array []
3. **Given** I am authenticated, **When** I GET /api/tasks/{task_id} for my own task, **Then** I receive 200 OK with that specific task object
4. **Given** I am authenticated, **When** I GET /api/tasks/{task_id} for another user's task, **Then** I receive 403 Forbidden
5. **Given** I am authenticated, **When** I GET /api/tasks/{task_id} for non-existent task_id, **Then** I receive 404 Not Found
6. **Given** I am NOT authenticated (no JWT), **When** I GET /api/tasks, **Then** I receive 401 Unauthorized
7. **Given** User A has 10 tasks and User B has 5 tasks, **When** User B GETs /api/tasks, **Then** User B receives only their 5 tasks, never seeing User A's tasks

---

### User Story 3 - Task Updates (Priority: P1)

Users can modify task details (title, description, completion status) to keep their information current.

**Why this priority**: Updating tasks (especially marking as completed) is core functionality. Users need to track progress and correct mistakes.

**Independent Test**: Can be fully tested by creating a task, updating it via PUT /api/tasks/{id}, and verifying the changes persist while user ownership is maintained.

**Acceptance Scenarios**:

1. **Given** I am authenticated and have a task, **When** I PUT /api/tasks/{task_id} with {"title": "Updated title", "completed": true}, **Then** I receive 200 OK with updated task object
2. **Given** I am authenticated and have a task, **When** I PATCH /api/tasks/{task_id} with {"completed": true} (partial update), **Then** I receive 200 OK with task showing completed=true and other fields unchanged
3. **Given** I am authenticated, **When** I PUT /api/tasks/{task_id} for another user's task, **Then** I receive 403 Forbidden
4. **Given** I am authenticated, **When** I PUT /api/tasks/{task_id} with {"title": ""} (invalid data), **Then** I receive 400 Bad Request with validation error
5. **Given** I am authenticated, **When** I PUT /api/tasks/{task_id} with {"user_id": "other-user-id"} (attempting to change ownership), **Then** the update fails with 400 Bad Request (user_id is immutable)
6. **Given** I am NOT authenticated (no JWT), **When** I PUT /api/tasks/{task_id}, **Then** I receive 401 Unauthorized

---

### User Story 4 - Task Deletion (Priority: P1)

Users can permanently remove tasks they no longer need to keep their list clean.

**Why this priority**: Deletion completes the CRUD operations. Users must be able to remove completed or unwanted tasks.

**Independent Test**: Can be fully tested by creating a task, deleting it via DELETE /api/tasks/{id}, and verifying it no longer exists.

**Acceptance Scenarios**:

1. **Given** I am authenticated and have a task, **When** I DELETE /api/tasks/{task_id}, **Then** I receive 204 No Content and the task is permanently removed
2. **Given** I am authenticated, **When** I DELETE /api/tasks/{task_id} for another user's task, **Then** I receive 403 Forbidden
3. **Given** I am authenticated, **When** I DELETE /api/tasks/{task_id} for non-existent task_id, **Then** I receive 404 Not Found
4. **Given** I am authenticated, **When** I DELETE /api/tasks/{task_id} for a task I already deleted, **Then** I receive 404 Not Found
5. **Given** I am NOT authenticated (no JWT), **When** I DELETE /api/tasks/{task_id}, **Then** I receive 401 Unauthorized

---

### User Story 5 - Task Filtering (Priority: P2)

Users can filter tasks by completion status to focus on pending work or review completed items.

**Why this priority**: Filtering enhances usability but is not essential for MVP. Users can still manage tasks without filtering.

**Independent Test**: Can be fully tested by creating completed and pending tasks, then querying with ?completed=true and verifying only completed tasks are returned.

**Acceptance Scenarios**:

1. **Given** I am authenticated and have 3 completed and 7 pending tasks, **When** I GET /api/tasks?completed=true, **Then** I receive 200 OK with array of exactly 3 completed tasks
2. **Given** I am authenticated and have 3 completed and 7 pending tasks, **When** I GET /api/tasks?completed=false, **Then** I receive 200 OK with array of exactly 7 pending tasks
3. **Given** I am authenticated and have tasks, **When** I GET /api/tasks?completed=invalid, **Then** I receive 400 Bad Request with validation error
4. **Given** I am authenticated, **When** I GET /api/tasks?completed=true, **Then** I receive only MY completed tasks, not other users' tasks

---

### Edge Cases

- **What happens when a client sends a malformed task_id?** System returns 400 Bad Request for invalid UUID format, 404 Not Found for valid UUID that doesn't exist
- **How does the system handle concurrent updates to the same task?** Last-write-wins (no optimistic locking in MVP) - later update overwrites earlier one
- **What happens when request body exceeds size limits?** System returns 413 Payload Too Large (task title max 500 chars, description max 5000 chars)
- **How does the system handle requests with expired JWT tokens?** Returns 401 Unauthorized with error message "Token expired"
- **What happens when a user tries to create tasks with extremely long titles/descriptions?** Validation rejects with 400 Bad Request before database insertion
- **How does the system handle requests with missing Content-Type header?** Returns 415 Unsupported Media Type if Content-Type is not application/json for POST/PUT/PATCH

## Requirements *(mandatory)*

### Functional Requirements

#### API Endpoint Structure

- **FR-001**: All task management endpoints MUST be under the `/api/tasks` path
- **FR-002**: All endpoints MUST accept and return JSON (Content-Type: application/json)
- **FR-003**: All endpoints (except health checks) MUST require JWT authentication via Authorization: Bearer <token> header
- **FR-004**: All endpoints MUST return appropriate HTTP status codes (2xx success, 4xx client error, 5xx server error)
- **FR-005**: All endpoints MUST automatically filter data by authenticated user's user_id (extracted from JWT sub claim)

#### Task Creation Endpoint

- **FR-006**: System MUST expose POST /api/tasks endpoint for creating new tasks
- **FR-007**: POST /api/tasks MUST accept request body with: title (required, string, max 500 chars), description (optional, string, max 5000 chars), completed (optional, boolean, default false)
- **FR-008**: POST /api/tasks MUST return 201 Created with created task object on success
- **FR-009**: POST /api/tasks MUST automatically set user_id from JWT sub claim (not from request body)
- **FR-010**: POST /api/tasks MUST generate unique task id (UUID) and timestamps (created_at, updated_at)

#### Task Retrieval Endpoints

- **FR-011**: System MUST expose GET /api/tasks endpoint for listing all tasks belonging to authenticated user
- **FR-012**: GET /api/tasks MUST return 200 OK with array of task objects (empty array if no tasks)
- **FR-013**: GET /api/tasks MUST support optional query parameter `?completed=<boolean>` for filtering
- **FR-014**: System MUST expose GET /api/tasks/{task_id} endpoint for retrieving single task
- **FR-015**: GET /api/tasks/{task_id} MUST return 200 OK with task object if task exists and belongs to authenticated user
- **FR-016**: GET /api/tasks/{task_id} MUST return 403 Forbidden if task exists but belongs to different user
- **FR-017**: GET /api/tasks/{task_id} MUST return 404 Not Found if task_id does not exist

#### Task Update Endpoints

- **FR-018**: System MUST expose PUT /api/tasks/{task_id} endpoint for full task replacement
- **FR-019**: PUT /api/tasks/{task_id} MUST accept request body with: title (required), description (optional), completed (optional)
- **FR-020**: PUT /api/tasks/{task_id} MUST return 200 OK with updated task object on success
- **FR-021**: System MUST expose PATCH /api/tasks/{task_id} endpoint for partial task updates
- **FR-022**: PATCH /api/tasks/{task_id} MUST accept request body with any subset of: title, description, completed
- **FR-023**: PUT/PATCH /api/tasks/{task_id} MUST return 403 Forbidden if task belongs to different user
- **FR-024**: PUT/PATCH /api/tasks/{task_id} MUST update updated_at timestamp automatically
- **FR-025**: PUT/PATCH /api/tasks/{task_id} MUST reject attempts to modify user_id field (immutable)

#### Task Deletion Endpoint

- **FR-026**: System MUST expose DELETE /api/tasks/{task_id} endpoint for permanent task removal
- **FR-027**: DELETE /api/tasks/{task_id} MUST return 204 No Content on successful deletion
- **FR-028**: DELETE /api/tasks/{task_id} MUST return 403 Forbidden if task belongs to different user
- **FR-029**: DELETE /api/tasks/{task_id} MUST return 404 Not Found if task_id does not exist

#### Authentication & Authorization

- **FR-030**: All /api/tasks endpoints MUST verify JWT token signature using BETTER_AUTH_SECRET
- **FR-031**: All /api/tasks endpoints MUST return 401 Unauthorized if JWT is missing, invalid, or expired
- **FR-032**: All /api/tasks endpoints MUST extract user_id from JWT sub claim for user isolation
- **FR-033**: System MUST never allow users to access, modify, or delete tasks belonging to other users

#### Error Handling

- **FR-034**: System MUST return standardized error response format: `{"error": {"code": "ERROR_CODE", "message": "Human-readable message", "details": {}}}`
- **FR-035**: System MUST return 400 Bad Request for validation errors (missing required fields, invalid types, constraint violations)
- **FR-036**: System MUST return 401 Unauthorized for authentication failures (missing/invalid/expired JWT)
- **FR-037**: System MUST return 403 Forbidden for authorization failures (valid JWT but accessing another user's resource)
- **FR-038**: System MUST return 404 Not Found for non-existent resources
- **FR-039**: System MUST return 500 Internal Server Error for unexpected server failures (with error logged but no sensitive details exposed)

#### Data Validation

- **FR-040**: System MUST validate task title is non-empty string with max length 500 characters
- **FR-041**: System MUST validate task description (if provided) is string with max length 5000 characters
- **FR-042**: System MUST validate completed field (if provided) is boolean type
- **FR-043**: System MUST validate task_id parameter is valid UUID format
- **FR-044**: System MUST validate Content-Type header is application/json for POST/PUT/PATCH requests

### Key Entities

- **Task**: Represents a single todo item with properties:
  - `id` (UUID, unique identifier)
  - `user_id` (UUID, foreign key to users table, identifies owner)
  - `title` (string, max 500 chars, required)
  - `description` (string, max 5000 chars, optional)
  - `completed` (boolean, default false)
  - `created_at` (timestamp, auto-generated)
  - `updated_at` (timestamp, auto-updated)

- **User**: Represents authenticated user (defined in authentication spec) referenced by Task.user_id

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a task via API in under 2 seconds (p95 latency)
- **SC-002**: Users can retrieve their task list in under 1 second (p95 latency)
- **SC-003**: 100% of API requests enforce JWT authentication (zero unauthenticated access)
- **SC-004**: 100% of database queries are user-scoped (zero cross-user data leaks)
- **SC-005**: API handles 100 concurrent task operations without errors
- **SC-006**: All API endpoints return correct HTTP status codes (100% compliance with REST standards)
- **SC-007**: API returns validation errors within 500ms for invalid requests
- **SC-008**: Zero SQL injection vulnerabilities in all endpoints (security scan pass)
- **SC-009**: All error responses follow standardized error format (100% consistency)
- **SC-010**: API documentation matches actual endpoint behavior (100% accuracy)

## API Specifications *(detailed contracts)*

### Endpoint: Create Task

**Method & Path**: `POST /api/tasks`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": false
}
```

**Validation Rules**:
- `title`: Required, non-empty string, max 500 characters
- `description`: Optional, string, max 5000 characters
- `completed`: Optional, boolean, default false
- `user_id`: Ignored if provided (always set from JWT)

**Success Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": false,
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid input (empty title, invalid type)
- 401 Unauthorized: Missing/invalid/expired JWT
- 413 Payload Too Large: Title/description exceeds length limits
- 415 Unsupported Media Type: Missing or incorrect Content-Type header
- 500 Internal Server Error: Unexpected server failure

---

### Endpoint: List Tasks

**Method & Path**: `GET /api/tasks`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
```

**Query Parameters**:
- `completed`: Optional, boolean (true/false), filters by completion status

**Success Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Buy groceries",
    "description": "Milk, eggs, and bread",
    "completed": false,
    "created_at": "2026-02-06T10:30:00Z",
    "updated_at": "2026-02-06T10:30:00Z"
  },
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "title": "Finish project",
    "description": null,
    "completed": true,
    "created_at": "2026-02-05T14:20:00Z",
    "updated_at": "2026-02-06T09:15:00Z"
  }
]
```

**Empty Response** (200 OK):
```json
[]
```

**Error Responses**:
- 400 Bad Request: Invalid query parameter value
- 401 Unauthorized: Missing/invalid/expired JWT
- 500 Internal Server Error: Unexpected server failure

---

### Endpoint: Get Single Task

**Method & Path**: `GET /api/tasks/{task_id}`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
```

**Path Parameters**:
- `task_id`: UUID, required

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": false,
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T10:30:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid UUID format
- 401 Unauthorized: Missing/invalid/expired JWT
- 403 Forbidden: Task exists but belongs to different user
- 404 Not Found: Task does not exist
- 500 Internal Server Error: Unexpected server failure

---

### Endpoint: Update Task (Full Replacement)

**Method & Path**: `PUT /api/tasks/{task_id}`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters**:
- `task_id`: UUID, required

**Request Body**:
```json
{
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, and butter",
  "completed": true
}
```

**Validation Rules**:
- `title`: Required, non-empty string, max 500 characters
- `description`: Optional, string, max 5000 characters, null allowed
- `completed`: Optional, boolean
- `user_id`: Immutable (cannot be changed)

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, and butter",
  "completed": true,
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T11:45:00Z"
}
```

**Error Responses**:
- 400 Bad Request: Invalid input or attempt to modify user_id
- 401 Unauthorized: Missing/invalid/expired JWT
- 403 Forbidden: Task exists but belongs to different user
- 404 Not Found: Task does not exist
- 415 Unsupported Media Type: Missing or incorrect Content-Type header
- 500 Internal Server Error: Unexpected server failure

---

### Endpoint: Update Task (Partial Update)

**Method & Path**: `PATCH /api/tasks/{task_id}`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
Content-Type: application/json
```

**Path Parameters**:
- `task_id`: UUID, required

**Request Body** (any subset):
```json
{
  "completed": true
}
```

**Validation Rules**:
- At least one field must be provided
- All provided fields must pass validation rules from PUT endpoint
- `user_id`: Immutable (cannot be changed)

**Success Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Buy groceries",
  "description": "Milk, eggs, and bread",
  "completed": true,
  "created_at": "2026-02-06T10:30:00Z",
  "updated_at": "2026-02-06T11:45:00Z"
}
```

**Error Responses**: Same as PUT endpoint

---

### Endpoint: Delete Task

**Method & Path**: `DELETE /api/tasks/{task_id}`

**Authentication**: Required (JWT Bearer token)

**Request Headers**:
```
Authorization: Bearer <jwt-token>
```

**Path Parameters**:
- `task_id`: UUID, required

**Success Response** (204 No Content):
```
(empty body)
```

**Error Responses**:
- 400 Bad Request: Invalid UUID format
- 401 Unauthorized: Missing/invalid/expired JWT
- 403 Forbidden: Task exists but belongs to different user
- 404 Not Found: Task does not exist
- 500 Internal Server Error: Unexpected server failure

---

### Standardized Error Response Format

All error responses MUST follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Task title cannot be empty",
    "details": {
      "field": "title",
      "constraint": "non_empty"
    }
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Input validation failure
- `AUTHENTICATION_ERROR`: JWT missing/invalid/expired
- `AUTHORIZATION_ERROR`: Valid JWT but insufficient permissions
- `RESOURCE_NOT_FOUND`: Requested resource does not exist
- `INTERNAL_SERVER_ERROR`: Unexpected server failure

## Technology Constraints *(implementation guidance)*

### Backend Implementation Notes

**Framework**: FastAPI with Python 3.11+

**Required Dependencies**:
- `fastapi`: Web framework
- `sqlmodel`: ORM for database operations
- `pyjwt`: JWT token verification
- `pydantic`: Request/response validation
- `uvicorn`: ASGI server

**JWT Verification Middleware**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
import os

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Extract and validate user_id from JWT token."""
    try:
        token = credentials.credentials
        secret = os.getenv("BETTER_AUTH_SECRET")
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        return user_id
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

**Task Model** (SQLModel):
```python
from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    title: str = Field(max_length=500)
    description: str | None = Field(default=None, max_length=5000)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Example Route Implementation**:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    completed: bool | None = None,
    user_id: str = Depends(get_current_user_id),
    session: Session = Depends(get_session)
):
    """List all tasks for authenticated user, optionally filtered by completion status."""
    query = select(Task).where(Task.user_id == user_id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    tasks = session.exec(query).all()
    return tasks
```

### Frontend Implementation Notes

**Framework**: Next.js 14+ App Router with TypeScript

**API Client** (centralized in `lib/api/client.ts`):
```typescript
import { getSession } from '@/lib/auth/client';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth(endpoint: string, options: RequestInit = {}) {
  const session = await getSession();
  
  if (!session?.token) {
    throw new Error('Not authenticated');
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${session.token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error?.message || 'Request failed');
  }
  
  if (response.status === 204) {
    return null; // No content
  }
  
  return response.json();
}

export const tasksApi = {
  list: (completed?: boolean) => 
    fetchWithAuth(`/api/tasks${completed !== undefined ? `?completed=${completed}` : ''}`),
  
  get: (taskId: string) => 
    fetchWithAuth(`/api/tasks/${taskId}`),
  
  create: (data: { title: string; description?: string; completed?: boolean }) =>
    fetchWithAuth('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  
  update: (taskId: string, data: { title: string; description?: string; completed?: boolean }) =>
    fetchWithAuth(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  
  patch: (taskId: string, data: Partial<{ title: string; description: string; completed: boolean }>) =>
    fetchWithAuth(`/api/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  
  delete: (taskId: string) =>
    fetchWithAuth(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    }),
};
```

**Usage in Server Component**:
```typescript
import { tasksApi } from '@/lib/api/client';

export default async function TasksPage() {
  const tasks = await tasksApi.list();
  
  return (
    <div>
      {tasks.map(task => (
        <div key={task.id}>{task.title}</div>
      ))}
    </div>
  );
}
```

**Usage in Client Component**:
```typescript
'use client';

import { useState } from 'react';
import { tasksApi } from '@/lib/api/client';

export function TaskForm() {
  const [title, setTitle] = useState('');
  
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    await tasksApi.create({ title });
    setTitle('');
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input value={title} onChange={(e) => setTitle(e.target.value)} />
      <button type="submit">Create Task</button>
    </form>
  );
}
```

## Out of Scope *(explicitly excluded)*

- **Pagination**: MVP returns all tasks for a user (assumed reasonable for personal todo app)
- **Sorting**: Tasks returned in creation order (no custom sorting)
- **Search**: No full-text search or advanced filtering (only completed status filter)
- **Bulk operations**: No batch create/update/delete endpoints
- **Task tags/categories**: Single flat list of tasks
- **Task priority/due dates**: Only title, description, and completed status
- **Task sharing/collaboration**: Strict user isolation, no sharing between users
- **Soft deletes**: DELETE permanently removes tasks (no trash/archive)
- **Task history/audit log**: No tracking of task modifications
- **Rate limiting**: No per-user request throttling (rely on infrastructure)
- **API versioning**: Single version (/api/tasks, no /v1/ prefix)
- **Webhooks**: No event notifications for task changes
- **Real-time updates**: No WebSocket/SSE for live task sync

## Assumptions & Dependencies

**Dependencies**:
- Authentication specification (002-authentication) MUST be implemented first (JWT verification required)
- Database schema specification (004-database-schema) MUST define tasks table with user_id foreign key
- Users table MUST exist with UUID primary key (defined in database schema spec)

**Assumptions**:
- Maximum 10,000 tasks per user (no pagination needed in MVP)
- Task title and description limits (500/5000 chars) are sufficient for personal todo use
- Last-write-wins for concurrent updates (no optimistic locking)
- 24-hour JWT expiration is acceptable (no refresh tokens)
- Single-region deployment (no geo-distribution concerns)
- PostgreSQL database handles UUID generation and timestamp defaults
- API runs on HTTPS in production (TLS termination at load balancer)
- Error messages safe to expose to clients (no sensitive data leakage)
