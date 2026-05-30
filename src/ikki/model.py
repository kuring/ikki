from __future__ import annotations

from .models import EchoModelProvider, ModelProvider, ModelRequest, ModelResponse


# 兼容阶段 0 早期模块路径，实际实现已经迁移到 ikki.models。
ModelClient = ModelProvider
EchoModelClient = EchoModelProvider

__all__ = ["EchoModelClient", "ModelClient", "ModelRequest", "ModelResponse"]
