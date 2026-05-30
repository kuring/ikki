from __future__ import annotations

from typing import Any

import requests

from ikki.config import ModelProfile

from .base import (
    ModelAuthenticationError,
    ModelHTTPError,
    ModelRequest,
    ModelResponse,
    ModelResponseError,
    ModelTimeoutError,
)


class AnthropicModelProvider:
    """调用 Anthropic Messages API 的同步模型后端。"""

    def __init__(self, profile: ModelProfile, api_key: str, session: Any | None = None) -> None:
        self._profile = profile
        self._api_key = api_key
        self._session = session or requests

    def complete(self, request: ModelRequest) -> ModelResponse:
        assert self._profile.base_url is not None
        assert self._profile.model is not None

        payload = {
            "model": self._profile.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "temperature": request.temperature,
            "max_tokens": 1024,
        }
        response_data = self._post_json(
            url=f"{self._profile.base_url.rstrip('/')}/v1/messages",
            headers={
                "x-api-key": self._api_key,
                "anthropic-version": self._profile.anthropic_version,
                "Content-Type": "application/json",
            },
            payload=payload,
            timeout=request.timeout_seconds,
        )
        text = self._extract_text(response_data)
        return ModelResponse(text=text, raw=response_data)

    def _post_json(
        self,
        url: str,
        headers: dict[str, str],
        payload: dict[str, Any],
        timeout: float,
    ) -> dict[str, Any]:
        try:
            response = self._session.post(url, headers=headers, json=payload, timeout=timeout)
        except requests.Timeout as exc:
            raise ModelTimeoutError("Anthropic 模型调用超时。") from exc
        except requests.RequestException as exc:
            raise ModelHTTPError(f"Anthropic 模型调用失败：{exc}") from exc

        status_code = getattr(response, "status_code", 0)
        if status_code in {401, 403}:
            raise ModelAuthenticationError(f"Anthropic 模型认证失败，HTTP 状态码：{status_code}。")
        if status_code >= 400:
            response_text = getattr(response, "text", "")
            raise ModelHTTPError(f"Anthropic 模型返回 HTTP {status_code}：{response_text}")

        try:
            data = response.json()
        except ValueError as exc:
            raise ModelResponseError("Anthropic 模型返回的 JSON 无法解析。") from exc
        if not isinstance(data, dict):
            raise ModelResponseError("Anthropic 模型返回格式无效。")
        return data

    def _extract_text(self, data: dict[str, Any]) -> str:
        content = data.get("content")
        if not isinstance(content, list):
            raise ModelResponseError("Anthropic 模型响应中缺少 content 列表。")

        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
        raise ModelResponseError("Anthropic 模型响应中缺少可用文本。")
