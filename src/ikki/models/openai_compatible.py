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


class OpenAICompatibleModelProvider:
    """调用 Chat Completions 风格接口的同步模型后端。"""

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
            "stream": False,
        }
        response_data = self._post_json(
            url=f"{self._profile.base_url.rstrip('/')}/chat/completions",
            headers={
                "Authorization": f"Bearer {self._api_key}",
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
            raise ModelTimeoutError("OpenAI-compatible 模型调用超时。") from exc
        except requests.RequestException as exc:
            raise ModelHTTPError(f"OpenAI-compatible 模型调用失败：{exc}") from exc

        status_code = getattr(response, "status_code", 0)
        if status_code in {401, 403}:
            raise ModelAuthenticationError(
                f"OpenAI-compatible 模型认证失败，HTTP 状态码：{status_code}。"
            )
        if status_code >= 400:
            response_text = getattr(response, "text", "")
            raise ModelHTTPError(
                f"OpenAI-compatible 模型返回 HTTP {status_code}：{response_text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ModelResponseError("OpenAI-compatible 模型返回的 JSON 无法解析。") from exc
        if not isinstance(data, dict):
            raise ModelResponseError("OpenAI-compatible 模型返回格式无效。")
        return data

    def _extract_text(self, data: dict[str, Any]) -> str:
        try:
            text = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ModelResponseError("OpenAI-compatible 模型响应中缺少 assistant 文本。") from exc

        if not isinstance(text, str) or not text.strip():
            raise ModelResponseError("OpenAI-compatible 模型响应中的 assistant 文本为空。")
        return text
