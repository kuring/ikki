# Ikki

Ikki 是一个面向学习的 Coding Agent 项目。

这个项目的目标不是一步到位复刻完整的 Claude Code，而是从一个很小的命令行程序开始，逐步加入模型调用、工具调用、代码仓库读取、文件编辑、命令执行、计划管理、记忆、评测和安全边界。

## 当前阶段

阶段：`v0.0-bootstrap`

这一阶段先完成项目底座：

- 在 `src/ikki` 下建立 Python 包结构。
- 增加命令行入口：`ikki`。
- 增加最小 `Agent` 类。
- 从环境变量读取配置。
- 增加基础日志初始化。
- 增加占位模型客户端。
- 增加最小测试和里程碑记录。

阶段 0 的完整目标已经扩展为：CLI、可扩展配置、多模型调用、日志和测试底座；模型层需要同时兼容 OpenAI-compatible 接口和 Anthropic API。详细范围见 [docs/roadmap.md](docs/roadmap.md) 和 [docs/stages/stage-0-bootstrap.md](docs/stages/stage-0-bootstrap.md)。

## 开发约束

- 代码中保留必要注释，重点说明设计意图、边界条件和阶段性占位原因。
- 注释、docstring、README、开发文档和面向用户的 CLI 文案默认使用中文。
- Python 标识符继续使用常规英文命名，保证生态兼容性和可读性。

## 环境要求

- Python 3.11 或更高版本。

## 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

## 使用方式

查看帮助：

```bash
ikki --help
```

运行一个任务：

```bash
ikki "hello"
```

当前阶段的预期输出：

```text
Ikki 已接收任务：hello
```

这一阶段还不会调用真实模型。`model.py` 只是一个占位层，用来给后续真实模型调用留出清晰位置。

## 开发

运行测试：

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## 项目文档

- [项目路线](docs/roadmap.md)
- [阶段 0：项目底座](docs/stages/stage-0-bootstrap.md)
- [里程碑](docs/milestones.md)

通用 Agent 概念笔记保留在 `/Users/kuring/my_git/ai-notebook`，本仓库只维护和 `ikki` 代码强绑定的项目文档。

## 路线图摘要

- `v0.0-bootstrap`：项目底座。
- `v0.1-chat-loop`：最小对话 Agent。
- `v0.2-tools`：最小工具调用。
- `v0.3-repo-context`：代码仓库搜索和文件读取。
