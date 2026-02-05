import unittest

from src.store import TodoStore


class TestTodoStore(unittest.TestCase):
    def setUp(self) -> None:
        self.store = TodoStore()

    # ── add ─────────────────────────────────────────

    def test_add_returns_todo_with_sequential_ids(self) -> None:
        t1 = self.store.add("First")
        t2 = self.store.add("Second")
        self.assertEqual(t1.id, 1)
        self.assertEqual(t2.id, 2)

    def test_add_sets_title(self) -> None:
        todo = self.store.add("Hello")
        self.assertEqual(todo.title, "Hello")

    def test_add_default_not_completed(self) -> None:
        todo = self.store.add("Task")
        self.assertFalse(todo.completed)

    # ── get ─────────────────────────────────────────

    def test_get_existing(self) -> None:
        added = self.store.add("X")
        self.assertEqual(self.store.get(added.id), added)

    def test_get_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.get(999))

    # ── get_all ─────────────────────────────────────

    def test_get_all_empty(self) -> None:
        self.assertEqual(self.store.get_all(), [])

    def test_get_all_sorted_by_id(self) -> None:
        t1 = self.store.add("A")
        t2 = self.store.add("B")
        self.assertEqual(self.store.get_all(), [t1, t2])

    # ── update_title ────────────────────────────────

    def test_update_title_success(self) -> None:
        todo = self.store.add("Old")
        result = self.store.update_title(todo.id, "New")
        self.assertIsNotNone(result)
        self.assertEqual(result.title, "New")  # type: ignore[union-attr]

    def test_update_title_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.update_title(999, "X"))

    # ── complete ────────────────────────────────────

    def test_complete_sets_flag(self) -> None:
        todo = self.store.add("Do it")
        result = self.store.complete(todo.id)
        self.assertIsNotNone(result)
        self.assertTrue(result.completed)  # type: ignore[union-attr]

    def test_complete_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.complete(999))

    def test_complete_idempotent(self) -> None:
        todo = self.store.add("Again")
        self.store.complete(todo.id)
        result = self.store.complete(todo.id)
        self.assertTrue(result.completed)  # type: ignore[union-attr]

    # ── delete ──────────────────────────────────────

    def test_delete_removes_item(self) -> None:
        todo = self.store.add("Remove me")
        deleted = self.store.delete(todo.id)
        self.assertEqual(deleted, todo)
        self.assertIsNone(self.store.get(todo.id))

    def test_delete_missing_returns_none(self) -> None:
        self.assertIsNone(self.store.delete(999))

    def test_id_not_reused_after_delete(self) -> None:
        t1 = self.store.add("First")
        self.store.delete(t1.id)
        t2 = self.store.add("Second")
        self.assertEqual(t2.id, 2)  # id 1 is not reused


if __name__ == "__main__":
    unittest.main()
