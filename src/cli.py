import sys

from src.service import TodoService
from src.todo import Todo

MENU = """
========== Todo App ==========
Commands:
  add      - Add a new todo
  list     - List all todos
  update   - Update a todo's title
  complete - Mark a todo as complete
  delete   - Delete a todo
  help     - Show this menu
  quit     - Exit the app
=============================="""


def _status(todo: Todo) -> str:
    return "completed" if todo.completed else "pending"


def _print_menu() -> None:
    print(MENU)
    print("Enter command: ", end="", flush=True)


def _parse_id(raw: str) -> int | None:
    try:
        return int(raw)
    except ValueError:
        return None


# ── command handlers ────────────────────────────────────


def _cmd_add(service: TodoService) -> None:
    print("Enter title: ", end="", flush=True)
    title = input()
    try:
        todo = service.add(title)
        print(f"Todo added: {todo.id} - {todo.title}")
    except ValueError as exc:
        print(f"Error: {exc}")


def _cmd_list(service: TodoService) -> None:
    todos = service.list_all()
    print("--- Todo List ---")
    if not todos:
        print("No todos yet. Use 'add' to create one.")
    else:
        for todo in todos:
            print(f"{todo.id} - {todo.title} [{_status(todo)}]")


def _cmd_update(service: TodoService) -> None:
    print("Enter todo ID to update: ", end="", flush=True)
    raw_id = input()
    id_val = _parse_id(raw_id)
    if id_val is None:
        print("Error: Please enter a valid numeric ID.")
        return
    print("Enter new title: ", end="", flush=True)
    title = input()
    try:
        todo = service.update(id_val, title)
        print(f"Todo updated: {todo.id} - {todo.title}")
    except ValueError as exc:
        print(f"Error: {exc}")
    except KeyError:
        print(f"Error: Todo with ID {id_val} not found.")


def _cmd_complete(service: TodoService) -> None:
    print("Enter todo ID to complete: ", end="", flush=True)
    raw_id = input()
    id_val = _parse_id(raw_id)
    if id_val is None:
        print("Error: Please enter a valid numeric ID.")
        return
    try:
        todo_before = service.list_all()
        was_completed = any(
            t.id == id_val and t.completed for t in todo_before
        )
        todo = service.complete(id_val)
        if was_completed:
            print(f"Todo {todo.id} is already completed.")
        else:
            print(f"Todo completed: {todo.id} - {todo.title}")
    except KeyError:
        print(f"Error: Todo with ID {id_val} not found.")


def _cmd_delete(service: TodoService) -> None:
    print("Enter todo ID to delete: ", end="", flush=True)
    raw_id = input()
    id_val = _parse_id(raw_id)
    if id_val is None:
        print("Error: Please enter a valid numeric ID.")
        return
    try:
        todo = service.delete(id_val)
        print(f"Todo deleted: {todo.id} - {todo.title}")
    except KeyError:
        print(f"Error: Todo with ID {id_val} not found.")


# ── REPL ────────────────────────────────────────────────

COMMANDS: dict[str, object] = {
    "add": _cmd_add,
    "list": _cmd_list,
    "update": _cmd_update,
    "complete": _cmd_complete,
    "delete": _cmd_delete,
}


def run_repl(service: TodoService) -> None:
    _print_menu()
    for line in sys.stdin:
        command = line.strip().lower()

        if command == "quit":
            print("Goodbye!")
            break
        elif command == "help" or command == "":
            _print_menu()
            continue
        elif command in COMMANDS:
            COMMANDS[command](service)  # type: ignore[operator]
        else:
            _print_menu()
            continue

        _print_menu()
