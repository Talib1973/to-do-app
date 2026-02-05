# Quickstart: Console Todo App (Phase I)

**Date**: 2026-02-05
**Branch**: `001-console-todo-app`
**Purpose**: Step-by-step guide to set up, run, and manually
verify the application. Also serves as the acceptance-test
walkthrough for all three user stories.

---

## Prerequisites

- Python 3.13 or later installed and on `PATH`
- `uv` installed and on `PATH`

---

## Setup

```bash
# From the repository root:
uv sync
```

This creates (or updates) the virtual environment and
installs the lock file. No third-party packages are added;
`uv sync` still sets up the environment correctly.

---

## Run

```bash
uv run python -m src.main
```

The application prints the menu and waits for input.

---

## Verification Walkthrough

Execute the steps below in order. Each step maps to one or
more acceptance scenarios from the spec.

### 1. Empty list (US1 — Scenario 1)

Immediately after startup, type:
```
list
```
**Expected**: The list header appears followed by the
"No todos yet" message.

### 2. Add two items (US1 — Scenario 2)

```
add
```
When prompted for a title, type: `Buy groceries`

Observe the confirmation: `Todo added: 1 - Buy groceries`

```
add
```
When prompted, type: `Walk the dog`

Observe: `Todo added: 2 - Walk the dog`

### 3. List after adding (US1 — Scenario 3)

```
list
```
**Expected**: Both items appear with IDs 1 and 2, status
`[pending]`, in ascending ID order.

### 4. Empty title rejection (US1 — Scenario 4)

```
add
```
Press Enter immediately (empty title).

**Expected**: `Error: Title cannot be empty.` No item created.

### 5. Update a title (US2 — Scenario 1)

```
update
```
When prompted for ID, type: `1`
When prompted for new title, type: `Buy groceries and milk`

**Expected**: `Todo updated: 1 - Buy groceries and milk`

Verify with `list`: item 1 shows the new title.

### 6. Update non-existent ID (US2 — Scenario 2)

```
update
```
When prompted for ID, type: `99`

**Expected**: `Error: Todo with ID 99 not found.`

### 7. Complete a todo (US2 — Scenario 3)

```
complete
```
When prompted for ID, type: `2`

**Expected**: `Todo completed: 2 - Walk the dog`

Verify with `list`: item 2 shows `[completed]`.

### 8. Complete an already-completed todo (US2 — Scenario 4)

```
complete
```
Type: `2`

**Expected**: `Todo 2 is already completed.` (no error)

### 9. Update with empty title (US2 — Scenario 5)

```
update
```
ID: `1`
New title: (press Enter, empty)

**Expected**: `Error: Title cannot be empty.`
Verify with `list`: item 1 title is unchanged.

### 10. Delete a todo (US3 — Scenario 1)

```
delete
```
When prompted for ID, type: `1`

**Expected**: `Todo deleted: 1 - Buy groceries and milk`

### 11. Verify deletion (US3 — Scenario 3)

```
list
```
**Expected**: Only item 2 (`Walk the dog`) appears. Item 1
is gone.

### 12. Delete non-existent ID (US3 — Scenario 2)

```
delete
```
Type: `1` (already deleted)

**Expected**: `Error: Todo with ID 1 not found.`

### 13. Unknown command (Edge case)

Type any unrecognised word, e.g.: `foo`

**Expected**: The menu is displayed again. No state change.

### 14. Invalid ID format (Edge case)

```
complete
```
Type: `abc`

**Expected**: `Error: Please enter a valid numeric ID.`

### 15. Graceful exit

```
quit
```
**Expected**: `Goodbye!` The process exits with code 0.

---

## Statefulness check

Close the application and restart with `uv run python -m
src.main`. Type `list`.

**Expected**: Empty list. All previously added/modified data
is gone.

---

## Success criteria mapping

| SC | Verified by steps |
|----|-------------------|
| SC-001 | 2, 3 |
| SC-002 | 2–15 (full session) |
| SC-003 | 4, 6, 9, 12, 13, 14 |
| SC-004 | Statefulness check |
| SC-005 | Menu displayed at every step |
| SC-006 | Code-review gate (not a runtime check) |
