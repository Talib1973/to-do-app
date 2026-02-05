# Implementation Plan: Console Todo App (Phase I)

**Branch**: `001-console-todo-app` | **Date**: 2026-02-05
**Spec**: `specs/001-console-todo-app/spec.md`
**Input**: Feature specification from
`/specs/001-console-todo-app/spec.md`

## Summary

Build a single-user, in-memory, console-based Todo
application in Python 3.13+ with zero external dependencies.
The application exposes five CRUD operations through a
keyword-driven REPL. Domain logic and state are encapsulated
in a dedicated service and store; the CLI layer is a thin
dispatcher. All modules are designed for reuse in Phase II
(web API) without modification to their public interfaces.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: None (standard library only)
**Storage**: In-memory (`dict`-backed store, reset on exit)
**Testing**: `unittest` (standard library)
**Target Platform**: Any OS with Python 3.13+; console
(stdin/stdout)
**Project Type**: Single project
**Performance Goals**: Command response <100 ms (constitution
mandate; trivially met with in-memory operations)
**Constraints**: No file I/O, no network, no external
packages. Stateless across executions. Single-user.
**Scale/Scope**: Single user; tens of todo items at most.
Single development iteration.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after
Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Simplicity First | ✅ PASS | Single project, stdlib only. No abstractions beyond what 5 CRUD ops require. |
| II. Progressive Enhancement | ✅ PASS | Domain and Logic modules are framework-agnostic. Public interfaces designed for Phase II reuse. |
| III. Separation of Concerns | ✅ PASS | Four layers enforced: Domain (`todo.py`), Logic (`service.py`), Interface (`cli.py`), Infrastructure (`store.py`). No cross-boundary imports. |
| IV. Deterministic Behaviour | ✅ PASS | No randomness. ID assignment is sequential. No implicit side-effects. |
| V. Explicit State | ✅ PASS | Single `TodoStore` owns all mutable state. Mutations only via `TodoService` methods. |
| VI. Interface Evolution | ✅ PASS | CLI commands are new; nothing to break. Command set is additive by design. |
| VII. AI Additive | N/A | Phase I contains no AI components. |
| VIII. Zero Hard-Coded Env | ✅ PASS | Phase I has no environment-dependent configuration. |

**Post-design re-check**: All gates remain green after Phase 1
design. No violations. Complexity Tracking table not required.

## Project Structure

### Documentation (this feature)

```text
specs/001-console-todo-app/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── cli-commands.md  # CLI interface contract
└── tasks.md             # Phase 2 output (/sp.tasks)
```

### Source Code (repository root)

```text
src/
├── todo.py              # Domain: Todo dataclass + status enum
├── store.py             # Infrastructure: in-memory TodoStore
├── service.py           # Logic: TodoService (CRUD + validation)
├── cli.py               # Interface: REPL loop + output formatting
└── main.py              # Entry point: wiring + startup

tests/
└── unit/
    ├── test_todo.py     # Unit tests for Todo entity
    ├── test_store.py    # Unit tests for TodoStore
    ├── test_service.py  # Unit tests for TodoService
    └── test_cli.py      # Unit tests for CLI command parsing
```

**Structure Decision**: Option 1 (single project) selected.
This is a standalone console application with no web or
mobile components. The four source files map directly to the
four constitutional layers: Domain → `todo.py`, Logic →
`service.py`, Interface → `cli.py`, Infrastructure →
`store.py`. The entry point (`main.py`) is the only file
that imports from more than one layer; it performs
dependency injection (creates the store, passes it to the
service, passes the service to the CLI).

## Complexity Tracking

> No Constitution Check violations detected. This table is
> intentionally empty.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| — | — | — |
