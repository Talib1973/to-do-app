# MCP Tools Contract

**Feature**: 004-ai-chatbot
**Date**: 2026-02-07
**Status**: Design
**References**: [spec.md](../spec.md), [data-model.md](../data-model.md), [research.md](../research.md)

## Overview

MCP (Model Context Protocol) tools provide the interface between the AI agent and the task management application. The AI agent uses these tools exclusively to perform task operations—it has no direct database access. All tools enforce user-scoped authorization and return structured JSON responses.

---

## Tool Response Format (Standard)

All MCP tools return JSON responses following this structure:

```json
{
  "status": "success" | "error",
  "data": { ... },
  "error": null | "error message"
}
```

**Success Response**:
```json
{
  "status": "success",
  "data": { ... },
  "error": null
}
```

**Error Response**:
```json
{
  "status": "error",
  "data": null,
  "error": "Descriptive error message for AI agent"
}
```

---

## Tool 1: add_task

**Purpose**: Create a new task for the authenticated user.

### Input Schema

```json
{
  "user_id": "uuid",
  "title": "string",
  "description": "string (optional)"
}
```

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_id | UUID | Yes | Must be valid user ID | Task owner (enforces user scoping) |
| title | string | Yes | 1-200 characters | Task title |
| description | string | No | 0-1000 characters | Task description (optional) |

### Success Response

```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "description": "string",
    "completed": false,
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  },
  "error": null
}
```

### Error Responses

**Missing Required Field**:
```json
{
  "status": "error",
  "data": null,
  "error": "Title is required and cannot be empty"
}
```

**User Not Found**:
```json
{
  "status": "error",
  "data": null,
  "error": "User not found"
}
```

### Example Usage

**AI Agent Call**:
```python
result = await add_task(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    title="Buy groceries tomorrow",
    description="Milk, eggs, bread"
)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries tomorrow",
    "description": "Milk, eggs, bread",
    "completed": false,
    "created_at": "2026-02-07T14:30:00Z",
    "updated_at": "2026-02-07T14:30:00Z"
  },
  "error": null
}
```

**AI Agent Interpretation**:
- User said: "I need to buy groceries tomorrow"
- Agent calls: `add_task(user_id, "Buy groceries tomorrow", "")`
- Agent confirms: "I've added 'Buy groceries tomorrow' to your task list."

---

## Tool 2: list_tasks

**Purpose**: Retrieve tasks for the authenticated user, optionally filtered by completion status.

### Input Schema

```json
{
  "user_id": "uuid",
  "status": "all" | "pending" | "completed"
}
```

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_id | UUID | Yes | Must be valid user ID | Task owner (enforces user scoping) |
| status | string | No | One of: "all", "pending", "completed" | Filter by completion status (default: "all") |

### Success Response

```json
{
  "status": "success",
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "string",
      "description": "string",
      "completed": boolean,
      "created_at": "ISO 8601 timestamp",
      "updated_at": "ISO 8601 timestamp"
    }
  ],
  "error": null
}
```

**Empty Result** (no tasks):
```json
{
  "status": "success",
  "data": [],
  "error": null
}
```

### Error Responses

**Invalid Status Filter**:
```json
{
  "status": "error",
  "data": null,
  "error": "Status must be 'all', 'pending', or 'completed'"
}
```

### Example Usage

**AI Agent Call** (List pending tasks):
```python
result = await list_tasks(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    status="pending"
)
```

**Response**:
```json
{
  "status": "success",
  "data": [
    {
      "id": "123",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "",
      "completed": false,
      "created_at": "2026-02-07T10:00:00Z",
      "updated_at": "2026-02-07T10:00:00Z"
    },
    {
      "id": "456",
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Call mom",
      "description": "",
      "completed": false,
      "created_at": "2026-02-07T11:00:00Z",
      "updated_at": "2026-02-07T11:00:00Z"
    }
  ],
  "error": null
}
```

**AI Agent Interpretation**:
- User said: "What are my pending tasks?"
- Agent calls: `list_tasks(user_id, "pending")`
- Agent formats response: "You have 2 pending tasks: 1) Buy groceries, 2) Call mom"

---

## Tool 3: update_task

**Purpose**: Modify an existing task's title or description.

### Input Schema

```json
{
  "user_id": "uuid",
  "task_id": "uuid",
  "title": "string (optional)",
  "description": "string (optional)"
}
```

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_id | UUID | Yes | Must be valid user ID | Task owner (enforces user scoping) |
| task_id | UUID | Yes | Must exist and belong to user | Task to update |
| title | string | No | 1-200 characters | New title (if provided) |
| description | string | No | 0-1000 characters | New description (if provided) |

**Note**: At least one of `title` or `description` must be provided.

### Success Response

```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "description": "string",
    "completed": boolean,
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  },
  "error": null
}
```

### Error Responses

**Task Not Found**:
```json
{
  "status": "error",
  "data": null,
  "error": "Task not found or does not belong to user"
}
```

**No Fields to Update**:
```json
{
  "status": "error",
  "data": null,
  "error": "At least one field (title or description) must be provided"
}
```

### Example Usage

**AI Agent Call**:
```python
result = await update_task(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    task_id="123",
    title="Buy groceries and fruits",
    description="Milk, eggs, bread, apples"
)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "123",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries and fruits",
    "description": "Milk, eggs, bread, apples",
    "completed": false,
    "created_at": "2026-02-07T10:00:00Z",
    "updated_at": "2026-02-07T14:35:00Z"
  },
  "error": null
}
```

**AI Agent Interpretation**:
- User said: "Change the grocery task to include fruits"
- Agent calls: `list_tasks` to find "grocery" task
- Agent calls: `update_task(user_id, task_id, title="Buy groceries and fruits")`
- Agent confirms: "I've updated your task to 'Buy groceries and fruits'."

---

## Tool 4: complete_task

**Purpose**: Mark a task as completed.

### Input Schema

```json
{
  "user_id": "uuid",
  "task_id": "uuid"
}
```

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_id | UUID | Yes | Must be valid user ID | Task owner (enforces user scoping) |
| task_id | UUID | Yes | Must exist and belong to user | Task to mark complete |

### Success Response

```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "title": "string",
    "description": "string",
    "completed": true,
    "created_at": "ISO 8601 timestamp",
    "updated_at": "ISO 8601 timestamp"
  },
  "error": null
}
```

### Error Responses

**Task Not Found**:
```json
{
  "status": "error",
  "data": null,
  "error": "Task not found or does not belong to user"
}
```

**Task Already Completed**:
```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "completed": true,
    ...
  },
  "error": null
}
```
**Note**: Completing an already-completed task is idempotent and returns success.

### Example Usage

**AI Agent Call**:
```python
result = await complete_task(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    task_id="123"
)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "123",
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "",
    "completed": true,
    "created_at": "2026-02-07T10:00:00Z",
    "updated_at": "2026-02-07T15:00:00Z"
  },
  "error": null
}
```

**AI Agent Interpretation**:
- User said: "I finished buying groceries"
- Agent calls: `list_tasks` to find "groceries" task
- Agent calls: `complete_task(user_id, task_id)`
- Agent confirms: "Great! I've marked 'Buy groceries' as complete."

---

## Tool 5: delete_task

**Purpose**: Permanently remove a task from the user's task list.

### Input Schema

```json
{
  "user_id": "uuid",
  "task_id": "uuid"
}
```

| Parameter | Type | Required | Constraints | Description |
|-----------|------|----------|-------------|-------------|
| user_id | UUID | Yes | Must be valid user ID | Task owner (enforces user scoping) |
| task_id | UUID | Yes | Must exist and belong to user | Task to delete |

### Success Response

```json
{
  "status": "success",
  "data": {
    "id": "uuid",
    "deleted": true
  },
  "error": null
}
```

### Error Responses

**Task Not Found**:
```json
{
  "status": "error",
  "data": null,
  "error": "Task not found or does not belong to user"
}
```

### Example Usage

**AI Agent Call**:
```python
result = await delete_task(
    user_id="550e8400-e29b-41d4-a716-446655440000",
    task_id="123"
)
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "id": "123",
    "deleted": true
  },
  "error": null
}
```

**AI Agent Interpretation**:
- User said: "Delete the grocery task"
- Agent calls: `list_tasks` to find "grocery" task
- Agent calls: `delete_task(user_id, task_id)`
- Agent confirms: "I've deleted 'Buy groceries' from your task list."

---

## Authorization Enforcement

**Critical Security Rule**: Every MCP tool MUST filter database operations by `user_id`.

### Correct Implementation (Enforces User Scoping)

```python
@mcp.tool()
async def list_tasks(user_id: UUID, status: str = "all") -> dict:
    """List tasks for the authenticated user."""
    query = select(Task).where(Task.user_id == user_id)  # ✅ User scoping

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    tasks = await session.exec(query).all()
    return {"status": "success", "data": tasks, "error": null}
```

### INCORRECT Implementation (Security Violation)

```python
@mcp.tool()
async def list_tasks_INSECURE(status: str = "all") -> dict:
    """List ALL tasks in database (no user scoping)."""
    query = select(Task)  # ⚠️ Missing user_id filter!

    if status == "pending":
        query = query.where(Task.completed == False)

    tasks = await session.exec(query).all()  # Returns ALL users' tasks!
    return {"status": "success", "data": tasks, "error": null}
```

**Violation Impact**: AI agent could access and leak other users' tasks.

---

## Error Handling Strategy

### Database Errors

```python
try:
    task = await session.get(Task, task_id)
    if not task or task.user_id != user_id:
        return {
            "status": "error",
            "data": None,
            "error": "Task not found or does not belong to user"
        }
except Exception as e:
    logger.error(f"Database error in get_task: {e}")
    return {
        "status": "error",
        "data": None,
        "error": "An error occurred while retrieving the task"
    }
```

**Key Points**:
- Log technical details for debugging
- Return user-friendly error messages to AI agent
- Never expose database schema, connection strings, or SQL queries

### Validation Errors

```python
if not title or len(title) > 200:
    return {
        "status": "error",
        "data": None,
        "error": "Title must be between 1 and 200 characters"
    }
```

---

## Tool Invocation Examples (AI Agent Behavior)

### Natural Language → Tool Call Mapping

| User Input | Agent Interprets As | Tool Called | Response |
|------------|---------------------|-------------|----------|
| "I need to buy groceries" | Create task | `add_task(user_id, "Buy groceries", "")` | "I've added 'Buy groceries' to your tasks." |
| "Show my tasks" | List all tasks | `list_tasks(user_id, "all")` | "You have 3 tasks: ..." |
| "What's pending?" | List incomplete | `list_tasks(user_id, "pending")` | "You have 2 pending tasks: ..." |
| "Mark task 3 done" | Complete by ID | `complete_task(user_id, task_id)` | "I've marked task 3 as complete." |
| "I'm done with groceries" | Complete by title match | `list_tasks` → find → `complete_task` | "Great! 'Buy groceries' is complete." |
| "Change task 1 to 'Call mom at 6pm'" | Update task | `update_task(user_id, task_id, "Call mom at 6pm")` | "I've updated task 1." |
| "Delete the old meeting task" | Delete by title match | `list_tasks` → find → `delete_task` | "I've deleted 'Old meeting' task." |

### Multi-Step Tool Chains

**Example**: User says "I finished buying groceries"

1. Agent interprets: User wants to mark "groceries" task complete
2. Agent calls: `list_tasks(user_id, "pending")` to find the task
3. Agent matches: Finds task with title containing "groceries" (ID: 123)
4. Agent calls: `complete_task(user_id, 123)`
5. Agent responds: "Great! I've marked 'Buy groceries' as complete."

**Tool Calls Array**:
```json
[
  {
    "tool": "list_tasks",
    "parameters": {"user_id": "...", "status": "pending"},
    "result": {"status": "success", "data": [{"id": "123", "title": "Buy groceries", ...}]}
  },
  {
    "tool": "complete_task",
    "parameters": {"user_id": "...", "task_id": "123"},
    "result": {"status": "success", "data": {"id": "123", "completed": true, ...}}
  }
]
```

---

## Agent System Prompt Guidelines

The AI agent should be configured with a system prompt that:

1. **Defines role**: "You are a helpful task management assistant."
2. **Explains tools**: "You have access to 5 tools to help users manage tasks..."
3. **Instructs on natural language**: "Interpret user requests naturally; they won't use technical commands."
4. **Handles ambiguity**: "If a user request is unclear, ask clarifying questions."
5. **Confirms actions**: "Always confirm task operations with friendly responses."
6. **Stays in domain**: "You can only help with task management, not other topics."

**Example System Prompt**:
```
You are a helpful task management assistant. Users will ask you to create, view, update, complete, or delete tasks using natural language.

You have 5 tools available:
- add_task: Create a new task
- list_tasks: View tasks (all, pending, or completed)
- update_task: Change a task's title or description
- complete_task: Mark a task as done
- delete_task: Remove a task

Always confirm actions with friendly, conversational responses. If a request is ambiguous (e.g., "change it"), ask which task they mean. Only help with task management—politely redirect other requests.
```

---

## Performance Considerations

### Database Query Optimization

- All tools use indexed queries (`WHERE user_id = ?`)
- `list_tasks` may benefit from composite index `(user_id, completed)` for filtered queries
- Tools should return data efficiently (avoid N+1 queries)

### Tool Response Size

- `list_tasks` may return 100+ tasks for active users
- Consider pagination in future enhancement if response size becomes issue
- Current implementation loads all tasks (acceptable for MVP)

---

## Testing Scenarios

### Contract Tests (Tool-Level)

1. **add_task**: Call with valid inputs → verify task created in DB
2. **list_tasks**: Call with status filter → verify correct tasks returned
3. **update_task**: Call with new title → verify task updated
4. **complete_task**: Call with task_id → verify completed=true
5. **delete_task**: Call with task_id → verify task removed from DB

### Authorization Tests

1. **Cross-user protection**: User A's task_id with User B's user_id → error
2. **User scoping**: list_tasks for User A → returns only User A's tasks
3. **Invalid user_id**: Non-existent user_id → error

### Error Handling Tests

1. **Missing required field**: add_task without title → error response
2. **Invalid UUID**: Malformed task_id → error response
3. **Database connection failure**: Simulated DB down → graceful error

### Integration Tests (AI Agent)

1. Natural language "Add task X" → verify add_task called
2. Natural language "Show tasks" → verify list_tasks called
3. Natural language "Done with X" → verify complete_task called
4. Multi-step: "I finished X" → verify list_tasks + complete_task chain
