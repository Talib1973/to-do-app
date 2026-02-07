# Implementation Tasks: REST API Endpoints

**Feature**: 003-rest-api
**Branch**: `003-003-rest-api`
**Total Tasks**: 18
**Parallelizable**: 6 tasks

## Task Summary by User Story

- **Setup**: 3 tasks (schemas, error handlers, router setup)
- **Foundational**: 1 task (task schemas)
- **US1 - Task Creation**: 3 tasks
- **US2 - Task Retrieval**: 4 tasks
- **US3 - Task Updates**: 3 tasks
- **US4 - Task Deletion**: 2 tasks
- **US5 - Task Filtering**: 2 tasks

## Dependencies & Execution Order

**Sequential Blocks**:
1. Setup (T001-T003) → Foundational (T004) → User Stories
2. US1, US2 must complete before US3, US4, US5
3. US5 depends on US2 (filtering extends retrieval)

**MVP Scope**: US1 + US2 (create and retrieve tasks)

---

## Phase 1: Setup

**Goal**: Configure FastAPI router and error handling infrastructure

- [ ] T001 Create backend/src/api/tasks.py with APIRouter configured at /api/tasks
- [ ] T002 Create backend/src/api/errors.py with standardized error response format handler
- [ ] T003 Register tasks router in backend/src/main.py with /api prefix

---

## Phase 2: Foundational (Blocking Prerequisites)

**Goal**: Create Pydantic schemas for task operations

**Blocks**: All task endpoints require these schemas

- [ ] T004 [P] Create task request/response schemas in backend/src/schemas/task.py (TaskCreate, TaskUpdate, TaskPatch, TaskResponse)

---

## Phase 3: User Story 1 - Task Creation (P1)

**Story Goal**: Enable users to create new tasks via API

**Independent Test**: POST /api/tasks with valid JWT and task data, verify 201 Created with task object including user_id from JWT

**Acceptance**:
- Task created with user_id from JWT sub claim
- Returns 201 Created with full task object
- Validates title non-empty, max 500 chars
- Rejects missing JWT with 401
- Ignores user_id in request body

**Tasks**:

- [ ] T005 [US1] Implement POST /api/tasks endpoint in backend/src/api/tasks.py with Depends(get_current_user_id)
- [ ] T006 [US1] Add request validation for title (required, max 500 chars) and description (optional, max 5000 chars) in POST endpoint
- [ ] T007 [US1] Set user_id from JWT sub claim (ignore request body user_id) and generate UUID, timestamps in POST endpoint

---

## Phase 4: User Story 2 - Task Retrieval (P1)

**Story Goal**: Enable users to view their tasks

**Independent Test**: Create tasks for a user, GET /api/tasks, verify only that user's tasks returned

**Acceptance**:
- GET /api/tasks returns user's tasks only
- GET /api/tasks/{id} returns task if owned by user
- Returns 403 if accessing another user's task
- Returns 404 if task doesn't exist
- Rejects missing JWT with 401

**Tasks**:

- [ ] T008 [US2] Implement GET /api/tasks endpoint in backend/src/api/tasks.py filtered by user_id from JWT
- [ ] T009 [US2] Implement GET /api/tasks/{task_id} endpoint with ownership verification (403 if different user)
- [ ] T010 [US2] Add 404 Not Found error handling for non-existent task_id in GET single task endpoint
- [ ] T011 [US2] Add 400 Bad Request error handling for invalid UUID format in task_id parameter

---

## Phase 5: User Story 3 - Task Updates (P1)

**Story Goal**: Enable users to modify task details

**Independent Test**: Create task, PUT /api/tasks/{id} with updated data, verify changes persist and ownership maintained

**Acceptance**:
- PUT updates all fields (full replacement)
- PATCH updates provided fields only (partial)
- Returns 403 if accessing another user's task
- Validates title non-empty, max 500 chars
- Rejects user_id modification with 400
- Updates updated_at timestamp automatically

**Tasks**:

- [ ] T012 [US3] Implement PUT /api/tasks/{task_id} endpoint in backend/src/api/tasks.py with ownership verification
- [ ] T013 [US3] Implement PATCH /api/tasks/{task_id} endpoint for partial updates with ownership verification
- [ ] T014 [US3] Add validation to reject user_id modification attempts (immutable field) in PUT/PATCH endpoints

---

## Phase 6: User Story 4 - Task Deletion (P1)

**Story Goal**: Enable users to permanently remove tasks

**Independent Test**: Create task, DELETE /api/tasks/{id}, verify 204 No Content and task no longer exists

**Acceptance**:
- Returns 204 No Content on success
- Returns 403 if accessing another user's task
- Returns 404 if task doesn't exist
- Task permanently removed from database

**Tasks**:

- [ ] T015 [US4] Implement DELETE /api/tasks/{task_id} endpoint in backend/src/api/tasks.py with ownership verification
- [ ] T016 [US4] Return 204 No Content on successful deletion and handle 404 for non-existent tasks

---

## Phase 7: User Story 5 - Task Filtering (P2)

**Story Goal**: Enable users to filter tasks by completion status

**Independent Test**: Create completed and pending tasks, GET /api/tasks?completed=true, verify only completed tasks returned

**Acceptance**:
- ?completed=true returns only completed tasks
- ?completed=false returns only pending tasks
- Invalid completed value returns 400
- Filtering respects user_id isolation

**Tasks**:

- [ ] T017 [P] [US5] Add optional completed query parameter to GET /api/tasks endpoint in backend/src/api/tasks.py
- [ ] T018 [US5] Add validation for completed parameter (must be boolean) with 400 Bad Request on invalid value

---

## Parallel Execution Opportunities

**Can Run in Parallel**:
- T004 (schemas) can run with T001-T003 (setup)
- T017 (filtering) independent from T012-T016 (update/delete)
- Backend tasks can run parallel with frontend API client integration (separate feature)

**Must Run Sequentially**:
- T001-T003 (setup) before T005-T018 (endpoints)
- T004 (schemas) before T005-T018 (endpoints)
- T005-T007 (create) before T012-T014 (update) - update depends on create
- T008-T011 (retrieval) before T015-T016 (delete) - delete returns task data

---

## Implementation Strategy

**MVP Delivery** (US1 + US2):
1. Complete Setup + Foundational (T001-T004)
2. Implement US1 Task Creation (T005-T007)
3. Implement US2 Task Retrieval (T008-T011)
4. Test: Create task → List tasks → Get single task

**Incremental Additions**:
- Add US3 (update) for task modification
- Add US4 (delete) for task removal
- Add US5 (filtering) for enhanced usability

**Validation**:
- US1: POST /api/tasks returns 201 with user_id from JWT
- US2: GET /api/tasks returns only authenticated user's tasks
- US3: PUT/PATCH updates task, 403 for other users
- US4: DELETE removes task, 204 on success
- US5: ?completed filter works, respects user isolation

---

## File Changes Summary

**Backend New Files** (3):
- backend/src/api/tasks.py (T001, T005, T008-T009, T012-T013, T015, T017)
- backend/src/api/errors.py (T002)
- backend/src/schemas/task.py (T004)

**Backend Modified Files** (1):
- backend/src/main.py (T003)

**Total Implementation Time Estimate**: 4-5 hours for MVP (US1, US2), 2-3 hours for US3, US4, US5

---

## Task Details

### Setup Phase

**T001**: Create the FastAPI router file for task endpoints
- Create `backend/src/api/tasks.py`
- Initialize APIRouter with prefix="/api/tasks" and tags=["tasks"]
- Add docstring explaining this module handles all task CRUD operations

**T002**: Create standardized error response handler
- Create `backend/src/api/errors.py`
- Implement error response format: `{"error": {"code": str, "message": str, "details": dict}}`
- Define error codes: VALIDATION_ERROR, AUTHENTICATION_ERROR, AUTHORIZATION_ERROR, RESOURCE_NOT_FOUND, INTERNAL_SERVER_ERROR

**T003**: Register tasks router in main application
- Edit `backend/src/main.py`
- Import tasks router
- Register with app.include_router(tasks.router)

### Foundational Phase

**T004**: Create Pydantic schemas for task operations
- Create `backend/src/schemas/task.py`
- TaskCreate: title (str, max 500), description (str | None, max 5000), completed (bool, default False)
- TaskUpdate: title (str, max 500), description (str | None, max 5000), completed (bool)
- TaskPatch: title (str | None, max 500), description (str | None, max 5000), completed (bool | None)
- TaskResponse: id (UUID), user_id (UUID), title, description, completed, created_at, updated_at

### User Story 1 - Task Creation

**T005**: Implement POST /api/tasks endpoint
- Add route handler to `backend/src/api/tasks.py`
- Use Depends(get_current_user_id) for authentication
- Accept TaskCreate schema in request body
- Return 201 Created with TaskResponse

**T006**: Add request validation for task creation
- Validate title is non-empty string, max 500 characters
- Validate description (if provided) is string, max 5000 characters
- Return 400 Bad Request with error details on validation failure

**T007**: Set user_id from JWT and generate metadata
- Extract user_id from get_current_user_id() dependency
- Generate UUID for task.id
- Set created_at and updated_at to current timestamp
- Ignore user_id from request body if provided

### User Story 2 - Task Retrieval

**T008**: Implement GET /api/tasks list endpoint
- Add route handler to `backend/src/api/tasks.py`
- Filter tasks WHERE user_id = authenticated user
- Return 200 OK with array of TaskResponse (empty array if no tasks)

**T009**: Implement GET /api/tasks/{task_id} single task endpoint
- Add route handler with task_id path parameter
- Query task by id
- Verify task.user_id matches authenticated user_id
- Return 403 Forbidden if task belongs to different user
- Return 200 OK with TaskResponse if owned by user

**T010**: Add 404 error handling for non-existent tasks
- Return 404 Not Found if task_id does not exist in database
- Use standardized error response format

**T011**: Add 400 error handling for invalid UUID format
- Validate task_id parameter is valid UUID format
- Return 400 Bad Request with error details if invalid

### User Story 3 - Task Updates

**T012**: Implement PUT /api/tasks/{task_id} full update endpoint
- Add route handler with task_id path parameter
- Accept TaskUpdate schema in request body
- Verify task.user_id matches authenticated user_id
- Return 403 Forbidden if different user
- Update all fields (title, description, completed)
- Update updated_at timestamp
- Return 200 OK with updated TaskResponse

**T013**: Implement PATCH /api/tasks/{task_id} partial update endpoint
- Add route handler with task_id path parameter
- Accept TaskPatch schema (all fields optional)
- Verify ownership
- Update only provided fields
- Update updated_at timestamp
- Return 200 OK with updated TaskResponse

**T014**: Reject user_id modification attempts
- Check if user_id is in request body for PUT/PATCH
- Return 400 Bad Request with error: "user_id is immutable"
- Never allow user_id to be changed after task creation

### User Story 4 - Task Deletion

**T015**: Implement DELETE /api/tasks/{task_id} endpoint
- Add route handler with task_id path parameter
- Verify task.user_id matches authenticated user_id
- Return 403 Forbidden if different user
- Delete task from database
- Return 204 No Content on success

**T016**: Handle 404 for non-existent task deletion
- Return 404 Not Found if task_id does not exist
- Return 404 Not Found if attempting to delete already-deleted task
- Use standardized error response format

### User Story 5 - Task Filtering

**T017**: Add completed query parameter to list endpoint
- Modify GET /api/tasks endpoint
- Add optional completed: bool | None query parameter
- Filter WHERE completed = <value> when parameter provided
- Maintain user_id filtering (AND condition)
- Return 200 OK with filtered TaskResponse array

**T018**: Validate completed parameter type
- Check completed parameter is boolean (true/false)
- Return 400 Bad Request if value is not boolean (e.g., "invalid", "1", "yes")
- Use standardized error response format
