# Feature Specification: Console Todo App (Phase I)

**Feature Branch**: `001-console-todo-app`
**Created**: 2026-02-05
**Status**: Draft
**Input**: In-memory, single-user, console-based Todo application.
All data exists only for the lifetime of the process.
Five core operations: add, list, update, complete, delete.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Add and List Todos (Priority: P1)

A user launches the application and is greeted with a menu.
They choose to add a new todo item by typing a title. The
system confirms the item was added and assigns it a visible
identifier. The user then chooses to list all todos and sees
every item they have added, each showing its identifier, title,
and whether it is pending or completed. When no todos exist,
the list view displays a clear "no items" message.

**Why this priority:** Add and List together form the minimum
viable loop. Without both, no other operation can be observed
or verified. Every subsequent story depends on at least one
item existing in the list.

**Independent Test:** Launch the app, add two items with
distinct titles, then list. Verify both items appear with
unique identifiers and status "pending". Restart the app and
verify the list is empty (stateless).

**Acceptance Scenarios:**

1. **Given** no todos exist, **When** the user chooses to list
   todos, **Then** the system displays a message indicating
   the list is empty.
2. **Given** the user chooses to add a todo, **When** they
   enter a non-empty title, **Then** the system stores the
   item, assigns it a unique identifier, and confirms
   creation with the identifier and title visible.
3. **Given** one or more todos exist, **When** the user
   chooses to list todos, **Then** every item is displayed
   with its identifier, title, and current status (pending
   or completed).
4. **Given** the user chooses to add a todo, **When** they
   enter an empty or whitespace-only title, **Then** the
   system rejects the input and displays an error message;
   no item is created.

---

### User Story 2 — Update and Complete Todos (Priority: P2)

A user who has previously added todos wants to correct a
typo in a title or mark an item as done. They choose to
update a todo, provide the identifier of the item they want
to change, and enter a new title. The system confirms the
change. Separately, the user can choose to mark a todo as
complete by providing its identifier. The system flips its
status to completed and confirms. Attempting either action
on an identifier that does not exist produces a clear error.

**Why this priority:** Update and Complete are the primary
mutation workflows. They give the todo list practical value
as a task-management tool. Both require a populated list
(Story 1) but are otherwise independent of each other.

**Independent Test:** Add an item (Story 1 prerequisite),
then update its title and verify the new title appears in
the list. Add a second item, mark it complete, and verify
its status changes to completed in the list.

**Acceptance Scenarios:**

1. **Given** a todo with identifier X exists, **When** the
   user chooses to update it and provides a new non-empty
   title, **Then** the system replaces the title and
   confirms the update.
2. **Given** no todo with identifier Y exists, **When** the
   user chooses to update identifier Y, **Then** the system
   displays an error indicating the identifier was not found;
   no state changes.
3. **Given** a todo with identifier X exists and is pending,
   **When** the user chooses to mark it as complete, **Then**
   the system sets its status to completed and confirms.
4. **Given** a todo with identifier X is already completed,
   **When** the user chooses to mark it as complete again,
   **Then** the system confirms the item is already complete;
   no error is raised.
5. **Given** the user chooses to update a todo, **When** they
   provide an empty or whitespace-only new title, **Then** the
   system rejects the input and displays an error; the
   original title is unchanged.

---

### User Story 3 — Delete a Todo (Priority: P3)

A user decides a todo item is no longer relevant and wants to
remove it entirely. They choose to delete a todo, provide the
identifier, and the system removes the item permanently from
the list and confirms. The item no longer appears in
subsequent list views. Attempting to delete a non-existent
identifier produces a clear error.

**Why this priority:** Deletion is a destructive, irreversible
action. It provides completeness but is the lowest-risk
operation to defer: the application is fully usable for
adding, viewing, updating, and completing todos without it.

**Independent Test:** Add two items, delete one by its
identifier, then list. Verify only the remaining item appears.
Attempt to delete the same identifier again and verify the
error message.

**Acceptance Scenarios:**

1. **Given** a todo with identifier X exists, **When** the
   user chooses to delete it, **Then** the system removes
   the item and confirms deletion.
2. **Given** no todo with identifier Y exists, **When** the
   user chooses to delete identifier Y, **Then** the system
   displays an error indicating the identifier was not found;
   no state changes.
3. **Given** a todo with identifier X was deleted, **When**
   the user lists all todos, **Then** identifier X does not
   appear in the list.

---

### Edge Cases

- What happens when the user enters a command that is not
  recognised? The system displays a help message listing
  valid commands; no state changes.
- What happens when the user provides a non-numeric or
  out-of-range identifier for update, complete, or delete?
  The system displays an error; no state changes.
- What happens when the list contains many items (e.g. 50+)?
  The system displays all items without truncation or
  pagination (single-user, in-memory constraint).
- What happens when the application starts with no prior
  state? The list is empty; this is the expected initial
  condition.
- What happens when two items share the same title? Both are
  stored as distinct items with different identifiers; the
  system does not enforce title uniqueness.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow a user to create a new
  todo item by providing a title. The title MUST contain at
  least one non-whitespace character.
- **FR-002**: The system MUST assign each todo item a unique,
  sequential numeric identifier at creation time.
- **FR-003**: The system MUST display all existing todo items
  in a list view, showing each item's identifier, title, and
  status.
- **FR-004**: The system MUST allow a user to update the title
  of an existing todo item identified by its identifier. The
  new title MUST contain at least one non-whitespace
  character.
- **FR-005**: The system MUST allow a user to mark an existing
  todo item as completed by its identifier. Marking an
  already-completed item as complete MUST succeed without
  error.
- **FR-006**: The system MUST allow a user to delete an
  existing todo item by its identifier, removing it
  permanently from the list.
- **FR-007**: The system MUST display a clear error message
  when the user references an identifier that does not exist
  for update, complete, or delete operations.
- **FR-008**: The system MUST display a help or menu screen
  when the application starts and when the user enters an
  unrecognised command.
- **FR-009**: The system MUST allow the user to exit the
  application gracefully.
- **FR-010**: All todo data MUST exist only in memory; no
  data MUST be written to disk or any external store.

### Key Entities

- **Todo Item**: Represents a single task. Attributes:
  unique numeric identifier (assigned by the system), title
  (non-empty string provided by the user), status (one of:
  pending, completed). A todo item starts in pending status.
  Status transitions: pending → completed (one direction
  only within Phase I).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can add a todo item and immediately see
  it in the list view with the correct title and a status
  of pending.
- **SC-002**: A user can perform all five core operations
  (add, list, update, complete, delete) in a single session
  without encountering any unhandled errors.
- **SC-003**: Every invalid user action (bad identifier,
  empty title, unknown command) produces a descriptive error
  message; the application does not crash.
- **SC-004**: Restarting the application results in an empty
  todo list, confirming no data persists between sessions.
- **SC-005**: The command flow is learnable without external
  documentation: the application's own menu and prompts are
  sufficient for a first-time user to complete all five
  operations.
- **SC-006**: The internal structure separates data
  representation and business rules from input/output
  handling, as verified by code review of the delivered
  artifacts.
