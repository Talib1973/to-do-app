from src.store import TodoStore
from src.todo import Todo


class TodoService:
    def __init__(self, store: TodoStore) -> None:
        self._store = store

    # ── US1 ────────────────────────────────────────────

    def add(self, title: str) -> Todo:
        stripped = title.strip()
        if not stripped:
            raise ValueError("Title cannot be empty.")
        return self._store.add(stripped)

    def list_all(self) -> list[Todo]:
        return self._store.get_all()

    # ── US2 ────────────────────────────────────────────

    def update(self, id: int, title: str) -> Todo:
        stripped = title.strip()
        if not stripped:
            raise ValueError("Title cannot be empty.")
        todo = self._store.update_title(id, stripped)
        if todo is None:
            raise KeyError(id)
        return todo

    def complete(self, id: int) -> Todo:
        todo = self._store.complete(id)
        if todo is None:
            raise KeyError(id)
        return todo

    # ── US3 ────────────────────────────────────────────

    def delete(self, id: int) -> Todo:
        todo = self._store.delete(id)
        if todo is None:
            raise KeyError(id)
        return todo
