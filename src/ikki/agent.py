from __future__ import annotations

from dataclasses import dataclass

from .config import RuntimeConfig
from .models import ModelMessage, ModelProvider, ModelRequest


@dataclass
class Agent:
    """阶段 0 的最小 Agent，只负责把任务转成统一模型请求。"""

    config: RuntimeConfig
    model: ModelProvider

    def run(self, task: str) -> str:
        normalized_task = task.strip()
        if not normalized_task:
            return "Ikki 收到了一个空任务。"

        request = ModelRequest(
            messages=[ModelMessage(role="user", content=normalized_task)],
            temperature=self.config.selected_model.temperature,
            timeout_seconds=self.config.selected_model.timeout_seconds,
        )
        return self.model.complete(request).text
