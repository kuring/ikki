from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ModelMessage:
    """统一模型消息格式，后续阶段可继续扩展 system、tool 等角色。"""

    role: str
    content: str


@dataclass(frozen=True)
class ModelRequest:
    """供应商无关的模型请求。"""

    messages: list[ModelMessage]
    temperature: float = 0.0
    timeout_seconds: float = 60.0


@dataclass(frozen=True)
class ModelResponse:
    """供应商无关的模型响应。"""

    text: str
    raw: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelProvider(Protocol):
    """所有模型后端都实现的同步文本补全接口。"""

    def complete(self, request: ModelRequest) -> ModelResponse:
        """执行一次非流式模型调用。"""


class ModelError(Exception):
    """模型选择或调用失败时抛出的面向用户异常。"""


class ModelAuthenticationError(ModelError):
    """认证或密钥缺失。"""


class ModelTimeoutError(ModelError):
    """远程模型调用超时。"""


class ModelHTTPError(ModelError):
    """远程模型返回 HTTP 错误。"""


class ModelResponseError(ModelError):
    """远程模型响应格式不符合预期。"""
