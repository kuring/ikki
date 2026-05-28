from __future__ import annotations

from dataclasses import dataclass

from .config import Config
from .model import ModelClient


@dataclass
class Agent:
    """脚手架阶段的最小 Agent 外壳。"""

    config: Config
    model: ModelClient

    def run(self, task: str) -> str:
        normalized_task = task.strip()
        if not normalized_task:
            return "Ikki 收到了一个空任务。"

        return self.model.complete(normalized_task)
