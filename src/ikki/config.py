from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal, Mapping

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator


SUPPORTED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


class ConfigError(Exception):
    """配置加载或校验失败时抛出的面向用户异常。"""


class AppConfig(BaseModel):
    """应用级配置。"""

    model_config = ConfigDict(extra="forbid")

    log_level: str = "WARNING"
    default_model: str = "local_test"

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        normalized = value.upper()
        if normalized not in SUPPORTED_LOG_LEVELS:
            raise ValueError(f"不支持的日志级别：{value}")
        return normalized


class ModelProfile(BaseModel):
    """单个模型 profile 的配置。"""

    model_config = ConfigDict(extra="forbid")

    provider: Literal["echo", "openai-compatible", "anthropic"]
    model: str | None = None
    base_url: str | None = None
    api_key_env: str | None = None
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)
    timeout_seconds: float = Field(default=60.0, gt=0.0, le=600.0)
    anthropic_version: str = "2023-06-01"

    @model_validator(mode="after")
    def validate_provider_fields(self) -> "ModelProfile":
        if self.provider == "echo":
            return self

        missing_fields = [
            field_name
            for field_name in ("model", "base_url", "api_key_env")
            if not getattr(self, field_name)
        ]
        if missing_fields:
            joined = "、".join(missing_fields)
            raise ValueError(f"{self.provider} 模型 profile 缺少必填字段：{joined}")
        return self


class ProjectConfig(BaseModel):
    """YAML 文件解析后的项目配置。"""

    model_config = ConfigDict(extra="forbid")

    app: AppConfig = Field(default_factory=AppConfig)
    models: dict[str, ModelProfile] = Field(
        default_factory=lambda: {"local_test": ModelProfile(provider="echo")}
    )

    @model_validator(mode="after")
    def validate_default_model(self) -> "ProjectConfig":
        if self.app.default_model not in self.models:
            raise ValueError(f"默认模型 profile 不存在：{self.app.default_model}")
        return self


class RuntimePaths(BaseModel):
    """Ikki 运行期路径。"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    work_dir: Path
    config_path: Path


class RuntimeConfig(BaseModel):
    """运行时已经完成优先级合并的有效配置。"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    paths: RuntimePaths
    app: AppConfig
    models: dict[str, ModelProfile]
    selected_model_name: str
    selected_model: ModelProfile

    @property
    def log_level(self) -> str:
        return self.app.log_level


class ConfigLoader:
    """集中处理默认值、YAML、环境变量和命令行覆盖的优先级。"""

    DEFAULT_WORK_DIR = Path("~/.ikki")
    DEFAULT_CONFIG_NAME = "config.yaml"

    def __init__(self, env: Mapping[str, str] | None = None) -> None:
        self._env = env if env is not None else os.environ

    def load(
        self,
        config_path: str | os.PathLike[str] | None = None,
        cli_model_name: str | None = None,
        cli_log_level: str | None = None,
    ) -> RuntimeConfig:
        paths, config_required = self._resolve_paths(config_path)
        raw_config = self._load_raw_config(paths.config_path, required=config_required)
        project_config = self._validate_project_config(raw_config)

        app_overrides: dict[str, Any] = {}
        env_model_name = self._env.get("IKKI_MODEL")
        env_log_level = self._env.get("IKKI_LOG_LEVEL")

        selected_model_name = cli_model_name or env_model_name or project_config.app.default_model
        if cli_log_level or env_log_level:
            app_overrides["log_level"] = cli_log_level or env_log_level

        if app_overrides:
            try:
                app_config = project_config.app.model_copy(update=app_overrides)
                app_config = AppConfig.model_validate(app_config.model_dump())
            except ValidationError as exc:
                raise ConfigError(f"配置校验失败：{_format_validation_error(exc)}") from exc
        else:
            app_config = project_config.app

        if selected_model_name not in project_config.models:
            raise ConfigError(f"模型 profile 不存在：{selected_model_name}")

        return RuntimeConfig(
            paths=paths,
            app=app_config,
            models=project_config.models,
            selected_model_name=selected_model_name,
            selected_model=project_config.models[selected_model_name],
        )

    def _resolve_paths(
        self, config_path: str | os.PathLike[str] | None
    ) -> tuple[RuntimePaths, bool]:
        work_dir = self._expand_path(self._env.get("IKKI_HOME") or self.DEFAULT_WORK_DIR)

        if config_path is not None:
            path = self._expand_path(config_path)
            config_required = True
        elif env_config_path := self._env.get("IKKI_CONFIG"):
            path = self._expand_path(env_config_path)
            config_required = True
        else:
            path = work_dir / self.DEFAULT_CONFIG_NAME
            config_required = False

        return RuntimePaths(work_dir=work_dir, config_path=path), config_required

    def _load_raw_config(self, path: Path, required: bool) -> dict[str, Any]:
        if not path.exists():
            if required:
                raise ConfigError(f"配置文件不存在：{path}")
            return {}

        try:
            with path.open("r", encoding="utf-8") as file:
                loaded = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            raise ConfigError(f"配置文件 YAML 解析失败：{exc}") from exc
        except OSError as exc:
            raise ConfigError(f"无法读取配置文件：{path}，原因：{exc}") from exc

        if loaded is None:
            return {}
        if not isinstance(loaded, dict):
            raise ConfigError("配置文件根节点必须是 YAML 映射。")
        return loaded

    def _validate_project_config(self, raw_config: dict[str, Any]) -> ProjectConfig:
        try:
            return ProjectConfig.model_validate(raw_config)
        except ValidationError as exc:
            raise ConfigError(f"配置校验失败：{_format_validation_error(exc)}") from exc

    def _expand_path(self, path: str | os.PathLike[str]) -> Path:
        return Path(path).expanduser()


def load_config(
    config_path: str | os.PathLike[str] | None = None,
    cli_model_name: str | None = None,
    cli_log_level: str | None = None,
    env: Mapping[str, str] | None = None,
) -> RuntimeConfig:
    """加载运行时配置，供 CLI 和测试复用。"""

    return ConfigLoader(env=env).load(
        config_path=config_path,
        cli_model_name=cli_model_name,
        cli_log_level=cli_log_level,
    )


def _format_validation_error(exc: ValidationError) -> str:
    first_error = exc.errors()[0]
    location = ".".join(str(part) for part in first_error["loc"]) or "root"
    message = first_error["msg"]
    return f"{location}: {message}"


# 兼容早期代码中导入的 Config 名称；新代码应使用 RuntimeConfig。
Config = RuntimeConfig
