from __future__ import annotations

from .base import ModelRequest, ModelResponse


class EchoModelProvider:
    """本地回显模型，用于无网络、无 API Key 的确定性测试路径。"""

    def complete(self, request: ModelRequest) -> ModelResponse:
        user_text = ""
        for message in reversed(request.messages):
            if message.role == "user":
                user_text = message.content
                break
        return ModelResponse(text=f"Ikki 已接收任务：{user_text}")
