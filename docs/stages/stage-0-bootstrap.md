# 阶段 0：项目底座

## 阶段目标

阶段 0 不应该只是“能跑 `ikki --help`”的空脚手架。`ikki` 的目标是成为一个真正可用的 Coding Agent，所以第一阶段就要把长期会依赖的底座打稳：CLI、配置、日志、模型调用抽象、真实大模型调用和最小测试。

可以把这一阶段理解成：先做出一台能接电、能换模型、能运行的机器，但还不急着给它装工具箱。

## 要学习的问题

- 用户从哪里启动程序？
- 配置文件、环境变量和命令行参数如何合并？
- API Key、base URL、模型名、超时、温度等模型参数放在哪里？
- 如何在不改 Agent 主流程的情况下切换不同模型？
- 模型调用失败时，如何给出可理解的错误信息？
- 日志、测试、README 和里程碑记录放在哪里？

## 理论要点

- CLI 是用户和 Agent 交互的第一个入口，参数设计会影响后续所有能力的使用方式。
- 模型调用层要和 Agent 主流程分开，否则后续切换模型、做重试、记录 token 用量都会很难。
- 配置系统要从一开始支持扩展，因为模型、工具、安全策略和工作区路径以后都会进入配置。
- API Key 不应该写进仓库，只应该通过环境变量或本机私有配置注入。
- 错误提示要面向使用者，而不是只暴露底层 HTTP 或 JSON 异常。

## 开发范围

- Python 包结构和 CLI 入口。
- 中文注释、中文 README、中文 CLI 帮助信息。
- 可扩展配置文件，例如 `ikki.yaml`。
- 配置优先级：命令行参数 > 环境变量 > 配置文件 > 默认值。
- 模型调用抽象，例如 `ModelClient` 或 `ModelProvider`。
- 至少三类模型后端：
  - `echo`：本地回显模型，用于无网络、无 API Key 的测试。
  - `openai-compatible`：兼容 OpenAI Chat Completions 风格接口的真实模型调用。
  - `anthropic`：兼容 Anthropic Messages API 的真实模型调用。
- 支持多模型 profile，例如 `default`、`fast`、`strong`、`local_test`。
- 基础日志和错误处理。
- 最小测试：CLI、配置加载、模型选择和 echo 模型。
- README 和 `docs/milestones.md`。

## 暂时不做什么

- Tool Calling。
- 读取本地代码仓库。
- 文件编辑。
- shell 命令执行。
- 多轮对话历史。
- 复杂 Agent planning。
- 记忆系统。
- 评测系统。

这些能力都很重要，但应该放到后续阶段。否则阶段 0 会从“底座”变成“半成品大系统”，边界会变得很模糊。

## 设计决策

### 配置文件采用 YAML

Ikki 的配置文件采用 YAML 作为主格式。这个选择不是为了最小依赖，而是为了从一开始面向复杂 Agent 系统设计：后续的模型 profile、工具权限、安全策略、工作区规则、记忆策略和评测任务都会进入配置系统，YAML 在表达嵌套结构、列表和策略型配置时更自然。

示例：

```yaml
app:
  log_level: INFO
  default_model: default

models:
  default:
    provider: openai-compatible
    model: gpt-4.1-mini
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.2
    timeout_seconds: 60

  fast:
    provider: openai-compatible
    model: gpt-4.1-nano
    base_url: https://api.openai.com/v1
    api_key_env: OPENAI_API_KEY
    temperature: 0.2
    timeout_seconds: 30

  claude:
    provider: anthropic
    model: claude-sonnet-4-5
    base_url: https://api.anthropic.com
    api_key_env: ANTHROPIC_API_KEY
    temperature: 0.2
    timeout_seconds: 60

  local_test:
    provider: echo
```

几个约定：

- YAML 只是外部文件格式，内部要先定义稳定的配置 schema，再把 YAML 解析结果转换成内部配置对象，避免后续业务逻辑直接依赖 YAML 结构细节。
- API Key 不直接写进配置文件，只写环境变量名，例如 `api_key_env = "OPENAI_API_KEY"`。
- `provider` 决定使用哪种模型后端。
- `model` 是供应商侧的模型名。
- `base_url` 允许切换到其他 OpenAI-compatible 服务。
- Anthropic 后端默认使用 Anthropic Messages API，`base_url` 用于切换官方或兼容服务地址。
- `default_model` 决定默认 profile。
- CLI 可以用 `--model fast` 临时切换 profile。
- YAML 解析使用安全加载模式，不执行任意对象构造；布尔值、数字和字符串要经过 schema 校验后再进入运行时。

### 模型后端先支持三类

- `echo` 用来保证本地测试不依赖网络和 API Key。
- `openai-compatible` 用来接入真实大模型，也为后续兼容其他 OpenAI 风格服务留出空间。
- `anthropic` 用来接入 Claude 等 Anthropic Messages API 模型，避免模型层只绑定 OpenAI 风格协议。

## 建议目录或模块变化

```text
ikki/
  AGENTS.md
  README.md
  pyproject.toml
  ikki.example.yaml
  src/
    ikki/
      __init__.py
      cli.py
      agent.py
      config.py
      logs.py
      models/
        __init__.py
        base.py
        echo.py
        openai_compatible.py
        anthropic.py
  tests/
    test_cli.py
    test_config.py
    test_models.py
  docs/
    milestones.md
```

文件职责：

- `cli.py`：命令行入口，负责解析任务、配置路径、模型 profile 和日志级别。
- `agent.py`：最小 Agent 主流程，先只负责接收任务并调用模型。
- `config.py`：读取 YAML 配置、环境变量和 CLI 覆盖项，并转换成内部配置对象。
- `models/base.py`：定义统一模型接口。
- `models/echo.py`：本地测试模型。
- `models/openai_compatible.py`：真实大模型调用实现。
- `models/anthropic.py`：Anthropic Messages API 模型调用实现。
- `logs.py`：统一初始化日志。
- `ikki.example.yaml`：给用户复制的配置模板。

## 实现任务

- [ ] 增加或调整 CLI 参数：`--config`、`--model`、`--log-level`。
- [ ] 增加 `ikki.example.yaml` 示例配置。
- [ ] 引入 YAML 解析依赖，并使用安全加载模式读取配置文件。
- [ ] 实现配置加载和优先级覆盖。
- [ ] 定义内部配置 schema，对模型 profile、数值范围和必填字段做校验。
- [ ] 拆分 `models/` 模块。
- [ ] 实现 `echo` 模型。
- [ ] 实现 OpenAI-compatible 模型调用。
- [ ] 实现 Anthropic API 模型调用。
- [ ] 在 Agent 主流程中通过配置选择模型。
- [ ] 补充中文 README 和里程碑。
- [ ] 补充 CLI、配置、模型相关测试。

## 完成标准

- [ ] `ikki --help` 可以正常显示中文帮助信息。
- [ ] `ikki --model local_test "hello"` 可以在无 API Key 的情况下运行。
- [ ] `ikki --config ikki.yaml --model default "hello"` 可以调用真实大模型。
- [ ] 支持至少一个 OpenAI-compatible 后端。
- [ ] 支持至少一个 Anthropic API 后端。
- [ ] 配置文件支持多个模型 profile。
- [ ] API Key 只从环境变量读取，不写进仓库。
- [ ] 模型调用失败时有清晰错误提示。
- [ ] README 写清楚安装、配置、运行和安全注意事项。
- [ ] 测试覆盖 CLI、配置加载、模型选择和 echo 模型。
- [ ] 提交代码并打 tag：`v0.0-bootstrap`。

## 复盘问题

- 为什么阶段 0 就要接入真实模型？
- 为什么模型调用层要和 Agent 主流程分开？
- 为什么配置要支持多个 model profile？
- 为什么 API Key 不应该写进配置文件？
- 阶段 0 和阶段 1 的边界在哪里？

## 相关笔记

- [从零开发 Coding Agent ikki](../roadmap.md)
- Coding Agent（ai-notebook: `07-Agent/Coding Agent.md`）
