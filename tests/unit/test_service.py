import unittest

from src.service import TodoService
from src.store import TodoStore


class TestTodoService(unittest.TestCase):
    def setUp(self) -> None:
        self.store = TodoStore()
        self.service = TodoService(self.store)

    # ── add ─────────────────────────────────────────

    def test_add_strips_whitespace(self) -> None:
        todo = self.service.add("  hello  ")
        self.assertEqual(todo.title, "hello")

    def test_add_empty_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            self.service.add("")

    def test_add_whitespace_only_raises_valueerror(self) -> None:
        with self.assertRaises(ValueError):
            self.service.add("   ")

    # ── list_all ────────────────────────────────────

    def test_list_all_empty(self) -> None:
        self.assertEqual(self.service.list_all(), [])

    def test_list_all_returns_added(self) -> None:
        t = self.service.add("Item")
        self.assertEqual(self.service.list_all(), [t])

    # ── update ──────────────────────────────────────

    def test_update_changes_title(self) -> None:
        t = self.service.add("Old")
        updated = self.service.update(t.id, "New")
        self.assertEqual(updated.title, "New")

    def test_update_strips_whitespace(self) -> None:
        t = self.service.add("X")
        updated = self.service.update(t.id, "  Y  ")
        self.assertEqual(updated.title, "Y")

    def test_update_empty_title_raises_valueerror(self) -> None:
        t = self.service.add("X")
        with self.assertRaises(ValueError):
            self.service.update(t.id, "")

    def test_update_missing_id_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            self.service.update(999, "Title")

    # ── complete ────────────────────────────────────

    def test_complete_sets_completed(self) -> None:
        t = self.service.add("Task")
        result = self.service.complete(t.id)
        self.assertTrue(result.completed)

    def test_complete_already_completed_no_error(self) -> None:
        t = self.service.add("Task")
        self.service.complete(t.id)
        result = self.service.complete(t.id)  # idempotent
        self.assertTrue(result.completed)

    def test_complete_missing_id_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            self.service.complete(999)

    # ── delete ──────────────────────────────────────

    def test_delete_removes_item(self) -> None:
        t = self.service.add("Gone")
        deleted = self.service.delete(t.id)
        self.assertEqual(deleted.id, t.id)
        self.assertEqual(self.service.list_all(), [])

    def test_delete_missing_id_raises_keyerror(self) -> None:
        with self.assertRaises(KeyError):
            self.service.delete(999)


if __name__ == "__main__":
    unittest.main()
