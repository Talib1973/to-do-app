# Research: Console Todo App (Phase I)

**Date**: 2026-02-05
**Branch**: `001-console-todo-app`
**Purpose**: Resolve all technical unknowns before design.

---

## Decision 1: Project initialisation and environment

**Decision**: Use `uv` to initialise and manage the Python
project. Run the application via `uv run python -m src.main`
(or equivalent entry-point configuration in `pyproject.toml`).

**Rationale**: The user explicitly mandates UV for dependency
and environment management. UV creates a `pyproject.toml`,
a virtual environment, and a lock file even when there are
zero third-party dependencies. This gives Phase II a clean
upgrade path (simply add dependencies to the same
`pyproject.toml`).

**Alternatives considered**:
- Plain `python main.py` with no project tooling — rejected;
  does not honour the UV mandate and leaves no upgrade path
  for Phase II.
- `poetry` — rejected; user mandate is UV.

---

## Decision 2: Entity representation

**Decision**: Represent `Todo` as a Python `dataclass` with
fields `id: int`, `title: str`, `completed: bool`.

**Rationale**: `dataclass` is stdlib, zero-dependency,
provides `__repr__` for free, and is the idiomatic way to
define simple value-carrying objects in modern Python.
The fields map directly to the spec's Key Entity definition.
`completed` is a `bool` rather than a `Status` enum because
Phase I has only two states (pending / completed); if Phase
II needs richer states, a `Status` enum can replace the bool
without changing the entity's public interface (the field
name and position stay the same).

**Alternatives considered**:
- `NamedTuple` — rejected; immutable, which conflicts with
  the "mark as complete" mutation pattern. Would require
  replacing the entire object on every state change.
- `Status` enum with `PENDING`/`COMPLETED` — considered for
  expressiveness but adds a module and indirection for a
  binary flag. Deferred to Phase II where additional states
  (e.g., IN_PROGRESS, ARCHIVED) may justify the enum.

---

## Decision 3: In-memory storage pattern

**Decision**: `TodoStore` wraps a `dict[int, Todo]` keyed by
todo ID, plus an `int` counter for sequential ID generation.
Exposes `add`, `get`, `get_all`, `update`, `delete` methods.

**Rationale**: A `dict` gives O(1) lookup by ID, which is the
dominant access pattern (update, complete, delete all look up
by ID first). The counter is incremented on every `add` and
never reused, even after a deletion — this guarantees IDs are
unique and sequential regardless of deletion history, which
is the simplest correct behaviour.

**Alternatives considered**:
- `list[Todo]` with index-based lookup — rejected; deletion
  shifts indices, making IDs unstable.
- Auto-decrementing counter on delete to fill gaps — rejected;
  violates determinism and makes ID semantics surprising.

---

## Decision 4: Testing framework

**Decision**: Use Python `unittest` (standard library) for all
unit tests. Test discovery via `python -m unittest discover`.

**Rationale**: Constitution mandates stdlib-only for Phase I
and explicitly names `unittest` for Phase I tests. No
third-party test runner is permitted.

**Alternatives considered**:
- `pytest` — preferred in general Python practice but is a
  third-party package; violates the stdlib-only constraint.
  Deferred to Phase II+.

---

## Decision 5: CLI interaction model

**Decision**: Keyword-driven REPL. The application prints a
menu on startup and after every action. The user types a
single keyword (`add`, `list`, `update`, `complete`, `delete`,
`help`, `quit`). For `add`, `update`, `complete`, and `delete`,
the application prompts for additional input (title or ID)
on the next line.

**Rationale**: A REPL with prompts is the simplest console
interaction model that satisfies all acceptance scenarios.
It avoids argument-parsing complexity (no `argparse` needed),
keeps each interaction short, and the menu satisfies
SC-005 (learnable without external documentation).

**Alternatives considered**:
- Single-line commands with inline arguments (e.g.,
  `add Buy milk`) — rejected; requires splitting and
  parsing the line, which adds edge cases (titles with
  spaces, quoting) for no user-facing benefit in a
  single-user tool.
- `argparse`-based subcommands (`python main.py add ...`) —
  rejected; exits after each command, breaking the
  "single session with all five operations" success
  criterion (SC-002).

---

## Resolution status

All NEEDS CLARIFICATION items: **none identified**.
All decisions above are settled. Phase 1 design may proceed.
