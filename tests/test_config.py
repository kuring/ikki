from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ikki.config import ConfigError, load_config


class ConfigTest(unittest.TestCase):
    def test_default_config_uses_local_echo_profile(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)

        config = load_config(env={"IKKI_HOME": temp_dir.name})

        self.assertEqual(config.selected_model_name, "local_test")
        self.assertEqual(config.selected_model.provider, "echo")
        self.assertEqual(config.log_level, "WARNING")
        self.assertEqual(config.paths.work_dir, Path(temp_dir.name))
        self.assertEqual(config.paths.config_path, Path(temp_dir.name) / "config.yaml")

    def test_valid_yaml_config_loads(self) -> None:
        path = self._write_config(
            """
app:
  log_level: INFO
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )

        config = load_config(config_path=path, env={})

        self.assertEqual(config.log_level, "INFO")
        self.assertEqual(config.selected_model_name, "local_test")

    def test_ikki_home_defines_default_config_path(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        config_path = Path(temp_dir.name) / "config.yaml"
        config_path.write_text(
            """
app:
  log_level: INFO
  default_model: local_test
models:
  local_test:
    provider: echo
""".strip(),
            encoding="utf-8",
        )

        config = load_config(env={"IKKI_HOME": temp_dir.name})

        self.assertEqual(config.paths.work_dir, Path(temp_dir.name))
        self.assertEqual(config.paths.config_path, config_path)
        self.assertEqual(config.log_level, "INFO")

    def test_ikki_config_env_overrides_default_config_path(self) -> None:
        path = self._write_config(
            """
app:
  log_level: ERROR
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )

        config = load_config(env={"IKKI_CONFIG": str(path)})

        self.assertEqual(config.paths.config_path, path)
        self.assertEqual(config.log_level, "ERROR")

    def test_cli_config_path_overrides_ikki_config_env(self) -> None:
        env_path = self._write_config(
            """
app:
  log_level: ERROR
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )
        cli_path = self._write_config(
            """
app:
  log_level: INFO
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )

        config = load_config(config_path=cli_path, env={"IKKI_CONFIG": str(env_path)})

        self.assertEqual(config.paths.config_path, cli_path)
        self.assertEqual(config.log_level, "INFO")

    def test_missing_config_file_is_reported(self) -> None:
        with self.assertRaisesRegex(ConfigError, "配置文件不存在"):
            load_config(config_path="/tmp/ikki-does-not-exist.yaml", env={})

    def test_missing_ikki_config_env_file_is_reported(self) -> None:
        with self.assertRaisesRegex(ConfigError, "配置文件不存在"):
            load_config(env={"IKKI_CONFIG": "/tmp/ikki-does-not-exist.yaml"})

    def test_cli_model_overrides_default_model(self) -> None:
        path = self._write_config(
            """
app:
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

        config = load_config(config_path=path, cli_model_name="local_test", env={})

        self.assertEqual(config.selected_model_name, "local_test")
        self.assertEqual(config.selected_model.provider, "echo")

    def test_environment_log_level_overrides_file_value(self) -> None:
        path = self._write_config(
            """
app:
  log_level: WARNING
  default_model: local_test
models:
  local_test:
    provider: echo
"""
        )

        config = load_config(config_path=path, env={"IKKI_LOG_LEVEL": "DEBUG"})

        self.assertEqual(config.log_level, "DEBUG")

    def test_schema_rejects_unknown_provider(self) -> None:
        path = self._write_config(
            """
models:
  broken:
    provider: unknown
"""
        )

        with self.assertRaisesRegex(ConfigError, "provider"):
            load_config(config_path=path, env={})

    def test_schema_rejects_missing_default_model(self) -> None:
        path = self._write_config(
            """
app:
  default_model: missing
models:
  local_test:
    provider: echo
"""
        )

        with self.assertRaisesRegex(ConfigError, "默认模型 profile 不存在"):
            load_config(config_path=path, env={})

    def test_schema_rejects_extra_field_and_invalid_numeric_values(self) -> None:
        extra_field_path = self._write_config(
            """
models:
  local_test:
    provider: echo
    unexpected: true
"""
        )
        invalid_number_path = self._write_config(
            """
models:
  local_test:
    provider: echo
    temperature: 3
"""
        )

        with self.assertRaisesRegex(ConfigError, "unexpected"):
            load_config(config_path=extra_field_path, env={})
        with self.assertRaisesRegex(ConfigError, "temperature"):
            load_config(config_path=invalid_number_path, env={})

    def _write_config(self, content: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "ikki.yaml"
        path.write_text(content.strip(), encoding="utf-8")
        return path
