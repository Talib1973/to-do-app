"""Tests for src/main.py — verifies the wiring entry point."""

import io
import sys
import unittest
from unittest.mock import patch

from src.main import main


class TestMain(unittest.TestCase):
    """Smoke tests that main() boots, wires correctly, and exits."""

    def _run_main_with_input(self, commands: str) -> str:
        """Helper: feed *commands* to main() via stdin, capture stdout."""
        stdin_patch = patch("sys.stdin", io.StringIO(commands))
        stdout_capture = io.StringIO()
        stdout_patch = patch("sys.stdout", stdout_capture)
        with stdin_patch, stdout_patch:
            main()
        return stdout_capture.getvalue()

    # ── startup & quit ──────────────────────────────

    def test_quit_prints_goodbye(self) -> None:
        output = self._run_main_with_input("quit\n")
        self.assertIn("Goodbye!", output)

    def test_menu_printed_on_startup(self) -> None:
        output = self._run_main_with_input("quit\n")
        self.assertIn("Todo App", output)
        self.assertIn("add", output)
        self.assertIn("list", output)

    # ── add + list round-trip ───────────────────────

    def test_add_and_list(self) -> None:
        output = self._run_main_with_input(
            "add\nBuy milk\nlist\nquit\n"
        )
        self.assertIn("Todo added: 1 - Buy milk", output)
        self.assertIn("1 - Buy milk [pending]", output)

    def test_add_empty_title_error(self) -> None:
        output = self._run_main_with_input("add\n\nquit\n")
        self.assertIn("Error: Title cannot be empty.", output)

    def test_list_empty(self) -> None:
        output = self._run_main_with_input("list\nquit\n")
        self.assertIn("No todos yet.", output)

    # ── update ──────────────────────────────────────

    def test_update_success(self) -> None:
        output = self._run_main_with_input(
            "add\nFirst\nupdate\n1\nSecond\nlist\nquit\n"
        )
        self.assertIn("Todo updated: 1 - Second", output)
        self.assertIn("1 - Second [pending]", output)

    def test_update_missing_id(self) -> None:
        output = self._run_main_with_input(
            "update\n99\nNew Title\nquit\n"
        )
        self.assertIn("Error: Todo with ID 99 not found.", output)

    def test_update_invalid_id(self) -> None:
        output = self._run_main_with_input(
            "update\nabc\nquit\n"
        )
        self.assertIn(
            "Error: Please enter a valid numeric ID.", output
        )

    def test_update_empty_title(self) -> None:
        output = self._run_main_with_input(
            "add\nKeep\nupdate\n1\n\nlist\nquit\n"
        )
        self.assertIn("Error: Title cannot be empty.", output)
        # original title preserved
        self.assertIn("1 - Keep [pending]", output)

    # ── complete ────────────────────────────────────

    def test_complete_pending(self) -> None:
        output = self._run_main_with_input(
            "add\nTask\ncomplete\n1\nlist\nquit\n"
        )
        self.assertIn("Todo completed: 1 - Task", output)
        self.assertIn("1 - Task [completed]", output)

    def test_complete_already_completed(self) -> None:
        output = self._run_main_with_input(
            "add\nTask\ncomplete\n1\ncomplete\n1\nquit\n"
        )
        self.assertIn("Todo 1 is already completed.", output)

    def test_complete_missing_id(self) -> None:
        output = self._run_main_with_input(
            "complete\n99\nquit\n"
        )
        self.assertIn("Error: Todo with ID 99 not found.", output)

    def test_complete_invalid_id(self) -> None:
        output = self._run_main_with_input(
            "complete\nxyz\nquit\n"
        )
        self.assertIn(
            "Error: Please enter a valid numeric ID.", output
        )

    # ── delete ──────────────────────────────────────

    def test_delete_success(self) -> None:
        output = self._run_main_with_input(
            "add\nGone\ndelete\n1\nlist\nquit\n"
        )
        self.assertIn("Todo deleted: 1 - Gone", output)
        self.assertIn("No todos yet.", output)

    def test_delete_missing_id(self) -> None:
        output = self._run_main_with_input(
            "delete\n99\nquit\n"
        )
        self.assertIn("Error: Todo with ID 99 not found.", output)

    def test_delete_invalid_id(self) -> None:
        output = self._run_main_with_input(
            "delete\nabc\nquit\n"
        )
        self.assertIn(
            "Error: Please enter a valid numeric ID.", output
        )

    # ── unknown command ─────────────────────────────

    def test_unknown_command_shows_menu(self) -> None:
        output = self._run_main_with_input("banana\nquit\n")
        # menu re-printed (count > 1 appearance of the header)
        self.assertGreater(output.count("Todo App"), 1)

    # ── help ────────────────────────────────────────

    def test_help_shows_menu(self) -> None:
        output = self._run_main_with_input("help\nquit\n")
        self.assertGreater(output.count("Todo App"), 1)

    # ── statefulness ────────────────────────────────

    def test_fresh_invocation_is_empty(self) -> None:
        """Each call to main() starts with an empty store."""
        self._run_main_with_input("add\nPersist?\nquit\n")
        # second invocation — store is fresh
        output = self._run_main_with_input("list\nquit\n")
        self.assertIn("No todos yet.", output)


if __name__ == "__main__":
    unittest.main()
