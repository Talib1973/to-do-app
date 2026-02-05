import unittest

from src.todo import Todo


class TestTodo(unittest.TestCase):
    def test_default_completed_is_false(self) -> None:
        todo = Todo(id=1, title="Buy milk")
        self.assertFalse(todo.completed)

    def test_fields_assigned(self) -> None:
        todo = Todo(id=42, title="Walk dog", completed=True)
        self.assertEqual(todo.id, 42)
        self.assertEqual(todo.title, "Walk dog")
        self.assertTrue(todo.completed)

    def test_equality(self) -> None:
        a = Todo(id=1, title="A")
        b = Todo(id=1, title="A")
        self.assertEqual(a, b)

    def test_inequality_different_id(self) -> None:
        a = Todo(id=1, title="A")
        b = Todo(id=2, title="A")
        self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
