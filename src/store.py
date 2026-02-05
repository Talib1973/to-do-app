from src.todo import Todo


class TodoStore:
    def __init__(self) -> None:
        self._todos: dict[int, Todo] = {}
        self._next_id: int = 1

    def add(self, title: str) -> Todo:
        todo = Todo(id=self._next_id, title=title)
        self._todos[self._next_id] = todo
        self._next_id += 1
        return todo

    def get(self, id: int) -> Todo | None:
        return self._todos.get(id)

    def get_all(self) -> list[Todo]:
        return sorted(self._todos.values(), key=lambda t: t.id)

    def update_title(self, id: int, title: str) -> Todo | None:
        todo = self._todos.get(id)
        if todo is None:
            return None
        todo.title = title
        return todo

    def complete(self, id: int) -> Todo | None:
        todo = self._todos.get(id)
        if todo is None:
            return None
        todo.completed = True
        return todo

    def delete(self, id: int) -> Todo | None:
        return self._todos.pop(id, None)
