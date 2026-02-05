# Tasks: Console Todo App (Phase I)

**Input**: Design documents from `specs/001-console-todo-app/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | data-model.md ✅ | contracts/cli-commands.md ✅ | research.md ✅ | quickstart.md ✅

**Tests**: Omitted from generated tasks per user input
("Testing frameworks or CI/CD pipelines (optional later
phases)"). A Polish-phase task is included to add unit tests
if desired.

---

## Phase 1: Setup

**Purpose**: UV project scaffold and directory structure.

- [x] T001 Initialise UV project at repository root: run
  `uv init` to create `pyproject.toml`, then create
  directories `src/` and `tests/unit/`
- [x] T002 Add `[project.scripts]` entry in `pyproject.toml`
  so the app is runnable via `uv run python -m src.main`
  (set `requires-python = ">=3.13"`)

---

## Phase 2: Foundational

**Purpose**: Domain entity and in-memory store — shared by
all user stories. MUST be complete before any story begins.

- [x] T003 [P] Create `src/__init__.py` (empty) so `src` is
  a package
- [x] T004 [P] Create `src/todo.py`: define the `Todo`
  dataclass with fields `id: int`, `title: str`,
  `completed: bool = False`. No imports beyond `dataclasses`.
- [x] T005 [P] Create `src/store.py`: define `TodoStore` class
  wrapping `dict[int, Todo]` and an `_next_id: int` counter
  starting at 1. Methods: `add(title: str) -> Todo`,
  `get(id: int) -> Todo | None`, `get_all() -> list[Todo]`
  (sorted by id ascending), `update_title(id: int, title: str)
  -> Todo | None`, `complete(id: int) -> Todo | None`,
  `delete(id: int) -> Todo | None`. Import `Todo` from
  `src.todo`. No validation logic here — store is a thin
  data layer.

**Checkpoint**: `Todo` and `TodoStore` exist and are
importable. Foundation ready.

---

## Phase 3: User Story 1 — Add and List (P1) 🎯 MVP

**Goal**: User can add a todo and see it in a list.
Covers FR-001, FR-002, FR-003, FR-008.

**Independent Test**: Run the app, type `add` → enter a
title → type `list`. Confirm item appears. Type `list`
before adding anything — confirm empty-list message.

- [x] T006 [US1] Create `src/service.py`: define
  `TodoService` class that takes a `TodoStore` in `__init__`.
  Implement `add(title: str) -> Todo` (strips whitespace,
  raises `ValueError` if empty, delegates to store) and
  `list_all() -> list[Todo]` (delegates to store).
- [x] T007 [US1] Create `src/cli.py`: define the REPL loop.
  Print the menu block (from `contracts/cli-commands.md`).
  Read a command keyword. Dispatch `add` and `list` to
  `TodoService`. For `add`: prompt `Enter title: `, call
  `service.add()`, print `Todo added: {id} - {title}` on
  success or `Error: Title cannot be empty.` on `ValueError`.
  For `list`: call `service.list_all()`, print each item as
  `{id} - {title} [{status}]` (status is `pending` or
  `completed`), or print the empty-list message if none. Any
  unrecognised command re-prints the menu. Include stub
  handlers for `update`, `complete`, `delete` (print a
  placeholder like `Not yet implemented`), plus `help`
  (re-prints menu) and `quit` (prints `Goodbye!`, exits
  cleanly).
- [x] T008 [US1] Create `src/main.py`: import `TodoStore`,
  `TodoService`, and the REPL function from `cli`. Instantiate
  store, pass to service, pass service to REPL, call REPL.
  This is the only file that crosses layer boundaries.

**Checkpoint**: `uv run python -m src.main` launches the app.
Add and list work end-to-end. MVP is functional.

---

## Phase 4: User Story 2 — Update and Complete (P2)

**Goal**: User can update a title and mark a todo complete.
Covers FR-004, FR-005, FR-007.

**Independent Test**: Add an item, update its title, verify
via list. Add a second item, complete it, verify status
change. Try update/complete on a non-existent ID — confirm
error message.

- [x] T009 [US2] Add `update(id: int, title: str) -> Todo`
  and `complete(id: int) -> Todo` methods to `TodoService`
  in `src/service.py`. `update`: parse id, strip title, raise
  `ValueError` if title empty, raise `KeyError` if id not in
  store. `complete`: raise `KeyError` if not found; if already
  completed return the todo unchanged (no error).
- [x] T010 [US2] Wire `update` and `complete` commands in the
  REPL in `src/cli.py`. Replace the stub handlers. `update`:
  prompt for ID (`Enter todo ID to update: `), validate it is
  an integer (print `Error: Please enter a valid numeric ID.`
  otherwise), prompt for new title (`Enter new title: `), call
  `service.update()`, print success or error per contract.
  `complete`: prompt for ID, validate integer, call
  `service.complete()`, print `Todo completed: {id} - {title}`
  if it was pending, or `Todo {id} is already completed.` if
  it was already done. Handle `KeyError` → `Error: Todo with
  ID {id} not found.`

**Checkpoint**: Update and complete work end-to-end with
correct error messages for bad/missing IDs and empty titles.

---

## Phase 5: User Story 3 — Delete (P3)

**Goal**: User can permanently remove a todo.
Covers FR-006, FR-007.

**Independent Test**: Add two items, delete one, list —
confirm only one remains. Try deleting the same ID again —
confirm error.

- [x] T011 [US3] Add `delete(id: int) -> Todo` method to
  `TodoService` in `src/service.py`. Raise `KeyError` if id
  not found; otherwise call `store.delete()` and return the
  removed todo.
- [x] T012 [US3] Wire `delete` command in the REPL in
  `src/cli.py`. Replace stub. Prompt for ID, validate integer,
  call `service.delete()`, print `Todo deleted: {id} - {title}`
  on success. Handle `KeyError` → not-found error per contract.

**Checkpoint**: All five CRUD operations functional.
Application matches the full CLI contract.

---

## Phase 6: Polish & Cross-Cutting

**Purpose**: Final validation and optional additions.

- [x] T013 Run the quickstart walkthrough (`quickstart.md`)
  step by step against the running application. Fix any
  output mismatches (exact strings, ordering, error messages)
  so every step passes.
- [x] T014 [P] (Optional) Add unit tests in `tests/unit/`
  using `unittest`: `test_todo.py` (entity construction),
  `test_store.py` (CRUD + invariants), `test_service.py`
  (validation paths), `test_cli.py` (command parsing). Run
  with `python -m unittest discover -s tests`. Only execute
  this task if tests are desired.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1.
  BLOCKS all user stories.
- **US1 (Phase 3)**: Depends on Phase 2. No other story
  dependency.
- **US2 (Phase 4)**: Depends on Phase 3 (needs `add` to
  populate items for update/complete).
- **US3 (Phase 5)**: Depends on Phase 3 (needs `add` to
  populate items for delete).
- **Polish (Phase 6)**: Depends on Phase 5 (all stories done).

### Within Each User Story

- Service method before CLI wiring (service is tested via
  CLI in the independent test).
- Story complete before moving to next priority.

### Parallel Opportunities

- T003, T004, T005 (Foundational) — all target different files.
- T014 (tests) is independent of T013 (quickstart walk).

---

## Implementation Strategy

### MVP (Phase 1 + 2 + 3 only)

1. Phase 1: Setup
2. Phase 2: Foundational
3. Phase 3: US1 (Add + List)
4. **STOP**: app is runnable and demonstrates value.

### Full Delivery

Phases 1 → 2 → 3 → 4 → 5 → 6 sequentially.
Total: 14 tasks (12 required, 1 quickstart validation,
1 optional tests).
