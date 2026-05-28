from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """运行配置，优先从环境变量读取。"""

    model_name: str = "bootstrap-echo"
    log_level: str = "WARNING"

    @classmethod
    def from_env(cls, log_level: str | None = None) -> "Config":
        """从环境变量和命令行参数合并配置。"""

        return cls(
            model_name=os.getenv("IKKI_MODEL", cls.model_name),
            log_level=(log_level or os.getenv("IKKI_LOG_LEVEL", cls.log_level)).upper(),
        )
