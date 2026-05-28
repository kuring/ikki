from __future__ import annotations

import logging


def setup_logging(level: str = "WARNING") -> None:
    """初始化日志格式；无效日志级别会回退到 WARNING。"""

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.WARNING),
        format="%(levelname)s %(name)s: %(message)s",
    )
