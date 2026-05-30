from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__
from .agent import Agent
from .config import ConfigError, load_config
from .logs import setup_logging
from .models import ModelError, ModelFactory


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
        "--config",
        default=None,
        help="配置文件路径，默认读取 ~/.ikki/config.yaml，可用 IKKI_CONFIG 覆盖。",
    )
    parser.add_argument("--model", default=None, help="本次运行使用的模型 profile。")
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

    try:
        config = load_config(
            config_path=args.config,
            cli_model_name=args.model,
            cli_log_level=args.log_level,
        )
    except ConfigError as exc:
        print(f"配置错误：{exc}", file=sys.stderr)
        return 2

    setup_logging(config.log_level)

    if not args.task:
        parser.print_help()
        return 0

    try:
        model = ModelFactory().create(config.selected_model_name, config.selected_model)
        agent = Agent(config=config, model=model)
        print(agent.run(args.task))
    except ModelError as exc:
        print(f"模型错误：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
