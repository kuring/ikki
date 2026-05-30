# Ikki

Ikki 是一个面向学习的 Coding Agent 项目。

这个项目的目标不是一步到位复刻完整的 Claude Code，而是从一个很小的命令行程序开始，逐步加入模型调用、工具调用、代码仓库读取、文件编辑、命令执行、计划管理、记忆、评测和安全边界。

## 当前阶段

阶段：`v0.0-bootstrap`

这一阶段先完成项目底座：

- 在 `src/ikki` 下建立 Python 包结构。
- 增加命令行入口：`ikki`。
- 增加最小 `Agent` 类。
- 支持 `~/.ikki/config.yaml` 配置文件、环境变量和命令行覆盖。
- 增加基础日志初始化。
- 增加统一模型接口和 `echo`、OpenAI-compatible、Anthropic 三类模型后端。
- 增加 CLI、配置和模型测试。

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

默认情况下，Ikki 使用内置 `local_test` echo 模型，不需要网络和 API Key。也可以显式选择：

```bash
ikki --model local_test "hello"
```

## 配置模型

Ikki 的默认工作目录是 `~/.ikki/`，默认配置文件是 `~/.ikki/config.yaml`。复制示例配置：

```bash
mkdir -p ~/.ikki
cp ikki.example.yaml ~/.ikki/config.yaml
```

模型选择优先级固定为：

```text
--model > IKKI_MODEL > ~/.ikki/config.yaml 中的 app.default_model > 内置默认值
```

常用参数：

```bash
ikki --config ~/.ikki/config.yaml --model local_test --log-level DEBUG "hello"
```

配置路径可以通过 `--config` 临时指定，也可以通过 `IKKI_CONFIG` 设置本机默认配置文件。工作目录可以通过 `IKKI_HOME` 覆盖；未设置时使用 `~/.ikki/`，配置文件默认位于该目录下的 `config.yaml`。

如果不想每次都写 `--model claude_default`，把 `~/.ikki/config.yaml` 中的默认模型改成：

```yaml
app:
  default_model: claude_default
```

`models` 是以 profile 名称为 key 的映射，`app.default_model`、`IKKI_MODEL` 和 `--model` 都引用这个名称。示例配置默认保留 `local_test`，这样复制后不配置 API Key 也能先跑通。

`ikki.example.yaml` 包含三个 profile 示例：

- `local_test`：本地 echo 模型，用于离线开发和测试。
- `openai_default`：OpenAI-compatible Chat Completions 接口。
- `claude_default`：Anthropic Messages API 接口。

真实模型的 API Key 只通过环境变量读取，不要写入 `config.yaml`：

```bash
export OPENAI_API_KEY="..."
ikki --model openai_default "解释这段代码"

export ANTHROPIC_API_KEY="..."
ikki --model claude_default "解释这段代码"
```

OpenAI-compatible profile 使用 `base_url` 拼接 `/chat/completions`；Anthropic profile 使用 `base_url` 拼接 `/v1/messages`，并默认发送 `anthropic-version: 2023-06-01`。

## 安全注意事项

- 不要把真实 API Key 写入仓库、示例配置或测试 fixture。
- `config.yaml` 应作为本机私有配置管理，公开文档只保留环境变量名。
- 当前阶段只做非流式单次模型调用，不包含工具调用、文件编辑或 shell 执行能力。

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
