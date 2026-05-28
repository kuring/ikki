from __future__ import annotations

import argparse
from collections.abc import Sequence

from . import __version__
from .agent import Agent
from .config import Config
from .logs import setup_logging
from .model import EchoModelClient


class ChineseArgumentParser(argparse.ArgumentParser):
    """把 argparse 默认生成的帮助前缀改成中文。"""

    def format_usage(self) -> str:
        return super().format_usage().replace("usage:", "用法:", 1)

    def format_help(self) -> str:
        return super().format_help().replace("usage:", "用法:", 1)


def build_parser() -> argparse.ArgumentParser:
    """创建命令行解析器，集中维护 CLI 的用户可见文案。"""

    parser = ChineseArgumentParser(
        prog="ikki",
        add_help=False,
        description="一个面向学习的 Coding Agent。",
    )
    parser.add_argument("task", nargs="?", metavar="任务", help="交给 Agent 处理的任务。")
    parser.add_argument("-h", "--help", action="help", help="显示帮助信息并退出。")
    parser.add_argument(
        "--log-level",
        default=None,
        help="日志级别，例如 DEBUG、INFO、WARNING 或 ERROR。",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ikki {__version__}",
        help="显示版本号并退出。",
    )
    parser._positionals.title = "位置参数"
    parser._optionals.title = "选项"
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLI 主入口，负责组装配置、日志、模型和 Agent。"""

    parser = build_parser()
    args = parser.parse_args(argv)

    config = Config.from_env(log_level=args.log_level)
    setup_logging(config.log_level)

    if not args.task:
        parser.print_help()
        return 0

    # 真实模型调用会在下一阶段接入；当前先使用回显模型打通主流程。
    agent = Agent(config=config, model=EchoModelClient())
    print(agent.run(args.task))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
