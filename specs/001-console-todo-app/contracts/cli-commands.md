# CLI Command Contract: Console Todo App (Phase I)

**Date**: 2026-02-05
**Branch**: `001-console-todo-app`
**Scope**: Defines the complete set of user-facing commands,
their input protocol, success output, and error output.
This contract is the Phase I equivalent of an API spec;
Phase II MUST honour every semantic defined here when
mapping these operations to REST endpoints.

---

## General Protocol

1. The application prints a **menu** listing all valid
   command keywords on startup and after every completed
   action (success or error).
2. The user types a single **command keyword** and presses
   Enter.
3. If the command requires additional input, the application
   prints a **prompt** and waits for one line of input.
4. The application prints a **response** (success or error)
   and returns to step 1.
5. Unrecognised keywords trigger the **help** response.

---

## Commands

### `add`

**Purpose**: Create a new todo item.

**Prompt after keyword**: `Enter title: `

**Input**: A single line of text (the title).

**Success output**:
```
Todo added: [id] - [title]
```
Where `[id]` is the system-assigned integer identifier and
`[title]` is the title as stored (stripped of leading/trailing
whitespace).

**Error — empty title**:
```
Error: Title cannot be empty.
```
No item is created. The menu is displayed again.

---

### `list`

**Purpose**: Display all todo items.

**Prompt after keyword**: None.

**Success output (items exist)**:
```
--- Todo List ---
[id] - [title] [status]
[id] - [title] [status]
...
```
Where `[status]` is either `[pending]` or `[completed]`.
Items are displayed in order of ascending `id`.

**Success output (no items)**:
```
--- Todo List ---
No todos yet. Use 'add' to create one.
```

---

### `update`

**Purpose**: Replace the title of an existing todo item.

**Prompt after keyword**: `Enter todo ID to update: `
**Second prompt**: `Enter new title: `

**Input**: First line is the ID (integer). Second line is the
new title.

**Success output**:
```
Todo updated: [id] - [new title]
```

**Error — ID not found**:
```
Error: Todo with ID [id] not found.
```

**Error — empty new title**:
```
Error: Title cannot be empty.
```
The original title remains unchanged.

**Error — non-integer ID**:
```
Error: Please enter a valid numeric ID.
```

---

### `complete`

**Purpose**: Mark a todo item as completed.

**Prompt after keyword**: `Enter todo ID to complete: `

**Input**: The ID (integer) of the todo to mark complete.

**Success output (was pending)**:
```
Todo completed: [id] - [title]
```

**Success output (already completed)**:
```
Todo [id] is already completed.
```
No error; idempotent behaviour.

**Error — ID not found**:
```
Error: Todo with ID [id] not found.
```

**Error — non-integer ID**:
```
Error: Please enter a valid numeric ID.
```

---

### `delete`

**Purpose**: Remove a todo item permanently.

**Prompt after keyword**: `Enter todo ID to delete: `

**Input**: The ID (integer) of the todo to delete.

**Success output**:
```
Todo deleted: [id] - [title]
```

**Error — ID not found**:
```
Error: Todo with ID [id] not found.
```

**Error — non-integer ID**:
```
Error: Please enter a valid numeric ID.
```

---

### `help`

**Purpose**: Display the menu of available commands.

**Prompt after keyword**: None.

**Output**: The standard menu block (same as startup menu).

---

### `quit`

**Purpose**: Exit the application gracefully.

**Prompt after keyword**: None.

**Output**:
```
Goodbye!
```
The process terminates with exit code 0.

---

## Menu Block (displayed on startup, after every action,
and on `help`)

```
========== Todo App ==========
Commands:
  add      - Add a new todo
  list     - List all todos
  update   - Update a todo's title
  complete - Mark a todo as complete
  delete   - Delete a todo
  help     - Show this menu
  quit     - Exit the app
==============================
Enter command:
```

---

## Error Taxonomy

| Error | Trigger | Recovery |
|-------|---------|----------|
| Empty title | `add` or `update` with blank input | Prompt returns to menu; no state change |
| ID not found | `update`/`complete`/`delete` with valid int but no matching todo | Prompt returns to menu; no state change |
| Invalid ID format | `update`/`complete`/`delete` with non-integer input | Prompt returns to menu; no state change |
| Unknown command | Any keyword not in the command set | Help menu displayed; no state change |
