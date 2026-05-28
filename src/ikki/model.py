from __future__ import annotations

from typing import Protocol


class ModelClient(Protocol):
    """模型客户端协议，用来隔离 Agent 逻辑和具体模型供应商。"""

    def complete(self, task: str) -> str:
        """根据用户任务返回模型响应。"""


class EchoModelClient:
    """真实模型接入前使用的占位客户端。"""

    def complete(self, task: str) -> str:
        return f"Ikki 已接收任务：{task}"
