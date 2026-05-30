from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from ikki.cli import main


class CliTest(unittest.TestCase):
    def test_help_is_printed_without_task(self) -> None:
        stdout = io.StringIO()

        with self._isolated_env(), redirect_stdout(stdout):
            exit_code = main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("用法: ikki", stdout.getvalue())

    def test_task_is_accepted_by_default_echo_model(self) -> None:
        stdout = io.StringIO()

        with self._isolated_env(), redirect_stdout(stdout):
            exit_code = main(["hello"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "Ikki 已接收任务：hello")

    def test_config_model_and_log_level_arguments_are_accepted(self) -> None:
        stdout = io.StringIO()
        config_path = self._write_config(
            """
app:
  log_level: WARNING
  default_model: remote
models:
  remote:
    provider: openai-compatible
    model: gpt-test
    base_url: https://example.test/v1
    api_key_env: OPENAI_API_KEY
  local_test:
    provider: echo
"""
        )

        with self._isolated_env(), redirect_stdout(stdout):
            exit_code = main(
                [
                    "--config",
                    str(config_path),
                    "--model",
                    "local_test",
                    "--log-level",
                    "DEBUG",
                    "hello",
                ]
            )

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "Ikki 已接收任务：hello")

    def test_config_default_model_is_used_without_model_argument(self) -> None:
        stdout = io.StringIO()
        config_path = self._write_config(
            """
app:
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )

        with self._isolated_env(), redirect_stdout(stdout):
            exit_code = main(["--config", str(config_path), "hello"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "Ikki 已接收任务：hello")

    def test_missing_remote_api_key_is_reported_in_chinese(self) -> None:
        stderr = io.StringIO()
        config_path = self._write_config(
            """
app:
  default_model: remote
models:
  remote:
    provider: openai-compatible
    model: gpt-test
    base_url: https://example.test/v1
    api_key_env: OPENAI_API_KEY
"""
        )

        with self._isolated_env(), redirect_stderr(stderr):
            exit_code = main(["--config", str(config_path), "hello"])

        self.assertEqual(exit_code, 1)
        self.assertIn("模型错误：", stderr.getvalue())
        self.assertIn("OPENAI_API_KEY", stderr.getvalue())

    def _write_config(self, content: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "ikki.yaml"
        path.write_text(content.strip(), encoding="utf-8")
        return path

    def _isolated_env(self) -> object:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        return patch.dict(os.environ, {"IKKI_HOME": temp_dir.name}, clear=True)


if __name__ == "__main__":
    unittest.main()
