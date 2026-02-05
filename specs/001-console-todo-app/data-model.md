# Data Model: Console Todo App (Phase I)

**Date**: 2026-02-05
**Branch**: `001-console-todo-app`

---

## Entity: Todo

The single entity in Phase I. Represents one task the user
wants to track.

### Fields

| Field | Type | Assigned By | Constraints |
|-------|------|-------------|-------------|
| `id` | `int` | System (sequential, auto-increment) | Unique across the lifetime of the process. Never reused after deletion. |
| `title` | `str` | User input | MUST contain at least one non-whitespace character. Leading/trailing whitespace is stripped before storage. |
| `completed` | `bool` | System (default `False`; set to `True` on complete) | One-directional transition: `False` → `True`. Cannot be reverted in Phase I. |

### State Transitions

```
 [created]
     │
     ▼
  pending (completed = False)
     │
     │  mark as complete
     ▼
 completed (completed = True)   ──►  [terminal state in Phase I]
```

A todo in either state may be deleted at any time. Deletion
removes the entity entirely; the ID is not reused.

### Validation Rules

| Rule | When Applied | Error Behaviour |
|------|--------------|-----------------|
| Title non-empty after strip | On add; on update | Error message displayed; entity not created / not mutated. |
| ID exists in store | On update, complete, delete | Error message displayed; no state change. |
| ID is a valid positive integer | On update, complete, delete | Error message displayed; no state change. |

---

## Collection: TodoStore

Holds the set of all `Todo` entities for the current session.

| Property | Value |
|----------|-------|
| Backing structure | `dict[int, Todo]` |
| ID generator | Monotonically increasing `int` counter, starts at 1 |
| Lifetime | Process lifetime only; empty on startup |
| Owner | Single instance; created once in `main.py` |

### Invariants

1. Every key in the dict equals the `id` field of its value.
2. The ID counter is always strictly greater than any
   existing key in the dict.
3. No two entries share the same key (enforced by dict
   semantics).
