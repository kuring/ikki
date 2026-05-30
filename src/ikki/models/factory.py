from __future__ import annotations

import os
from typing import Mapping

from ikki.config import ModelProfile

from .anthropic import AnthropicModelProvider
from .base import ModelAuthenticationError, ModelProvider
from .echo import EchoModelProvider
from .openai_compatible import OpenAICompatibleModelProvider


class ModelFactory:
    """根据已校验的模型 profile 构造具体 provider。"""

    def __init__(self, env: Mapping[str, str] | None = None) -> None:
        self._env = env if env is not None else os.environ

    def create(self, profile_name: str, profile: ModelProfile) -> ModelProvider:
        if profile.provider == "echo":
            return EchoModelProvider()

        api_key = self._resolve_api_key(profile_name, profile)
        if profile.provider == "openai-compatible":
            return OpenAICompatibleModelProvider(profile=profile, api_key=api_key)
        if profile.provider == "anthropic":
            return AnthropicModelProvider(profile=profile, api_key=api_key)

        raise ModelAuthenticationError(f"不支持的模型 provider：{profile.provider}")

    def _resolve_api_key(self, profile_name: str, profile: ModelProfile) -> str:
        if not profile.api_key_env:
            raise ModelAuthenticationError(f"模型 profile `{profile_name}` 未配置 api_key_env。")

        api_key = self._env.get(profile.api_key_env)
        if not api_key:
            raise ModelAuthenticationError(
                f"模型 profile `{profile_name}` 缺少环境变量 `{profile.api_key_env}`。"
            )
        return api_key
