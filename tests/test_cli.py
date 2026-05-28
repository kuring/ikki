from __future__ import annotations

import io
import unittest
from contextlib import redirect_stdout

from ikki.cli import main


class CliTest(unittest.TestCase):
    def test_help_is_printed_without_task(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("用法: ikki", stdout.getvalue())

    def test_task_is_accepted(self) -> None:
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            exit_code = main(["hello"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "Ikki 已接收任务：hello")


if __name__ == "__main__":
    unittest.main()
