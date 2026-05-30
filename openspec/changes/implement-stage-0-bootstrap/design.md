## Context

当前 Ikki 已有最小 CLI、`Agent` 外壳、环境变量配置和 echo 模型占位实现。阶段 0 的目标是把这些占位结构升级为后续 Agent 能力可复用的底座：配置系统要能承载复杂策略，模型层要隔离供应商协议，CLI 要能稳定组合配置、日志和模型 profile。

该变更仍然处于 bootstrap 阶段，不引入 Tool Calling、仓库读取、文件编辑、shell 执行、多轮历史、planning、memory 或 eval 系统。

## Goals / Non-Goals

**Goals:**

- 使用 YAML 作为主配置格式，并通过 Pydantic schema 约束运行时配置。
- 支持命令行参数、环境变量、配置文件和默认值的明确优先级。
- 将模型调用抽象为 `ModelRequest` / `ModelResponse` 统一接口，支持 echo、OpenAI-compatible 和 Anthropic Messages API。
- 保持无 API Key 的本地测试路径，确保 `local_test` profile 可运行。
- 提供中文 CLI 文案、中文错误提示、README 和里程碑更新。
- 用单元测试覆盖 CLI、配置加载、模型选择和 echo 模型。

**Non-Goals:**

- 不实现多轮会话历史和 system prompt 管理。
- 不实现工具调用、仓库上下文、文件编辑或 shell 执行。
- 不实现 token 统计、重试策略、流式输出或供应商高级参数。
- 不把 API Key 写入仓库、示例文件或测试 fixture。

## Decisions

1. YAML 作为外部配置格式，Pydantic 作为配置 schema。

   YAML 更适合后续表达工具权限、安全策略、工作区规则和评测任务。运行时代码不直接依赖 YAML 字典结构，而是先解析为 Pydantic 模型，集中处理默认值、类型转换、额外字段拦截、必填字段、数值范围和 provider 合法性。

   备选方案是 dataclass 加手写校验，或继续使用 TOML。dataclass 依赖少，但复杂嵌套、错误定位和字段约束会快速膨胀；TOML 语法严格，但在复杂嵌套策略上表达能力不足。Pydantic 的依赖成本是可接受的，因为配置入口是复杂系统的外部输入边界。

2. 配置优先级固定为命令行参数 > 环境变量 > 配置文件 > 默认值。

   CLI 参数用于单次运行覆盖；环境变量用于密钥和本机私有默认值；配置文件用于项目级可复用 profile；默认值保证最小运行路径。该优先级必须集中在 `config.py`，避免 CLI 和模型层重复拼接规则。

3. 模型接口从 `complete(task: str) -> str` 升级为 `ModelRequest` / `ModelResponse`。

   `ModelRequest` 至少包含 messages、temperature 和 timeout 等模型调用输入；`ModelResponse` 至少包含 text，并为后续 raw provider response、token usage、tool calls 或 streaming metadata 预留扩展空间。阶段 0 的 CLI 仍然可以把单次用户任务转换为一个 user message，但 Agent 和 provider 不再绑定到裸字符串任务接口。

   备选方案是沿用 `task: str`。该方案实现最简单，但会在阶段 1 引入 system prompt、多轮 messages 或工具调用时立即返工。

4. 模型层拆成 `models/` 包，每个供应商协议单独实现。

   `models/base.py` 定义统一请求和响应接口；`echo.py` 保证离线测试；`openai_compatible.py` 调用 Chat Completions 风格接口；`anthropic.py` 调用 Anthropic Messages API。`Agent` 只依赖统一模型接口，不关心 HTTP 协议细节。

5. HTTP 调用先使用同步实现。

   阶段 0 的 CLI 是单次任务执行，使用同步 HTTP 可以降低并发和生命周期复杂度。流式输出、异步调用和重试策略留到后续阶段，在接口稳定后再扩展。

6. 错误提示由模型层转换为面向用户的中文异常。

   供应商 HTTP、认证、超时和响应格式错误不应直接穿透到 CLI。模型层抛出项目内部异常，CLI 捕获后输出简短中文提示，并保留日志用于调试。

## Risks / Trade-offs

- [Risk] YAML 语法灵活，可能产生隐式类型或结构错误。→ 使用安全加载模式，并通过 Pydantic schema 校验类型、范围、额外字段和必填字段。
- [Risk] 同时接入 OpenAI-compatible 和 Anthropic 会扩大阶段 0 工作量。→ 只实现非流式最小文本完成路径，供应商高级参数延后。
- [Risk] HTTP 依赖会影响测试稳定性。→ 单元测试默认使用 echo 和 fake HTTP，不依赖真实网络或真实 API Key。
- [Risk] `ModelRequest` / `ModelResponse` 比 `task: str` 更重。→ 阶段 0 只填充最小字段，但接口形状提前兼容 messages、tools、usage 和 streaming metadata。

## Migration Plan

- 保留 `ikki "hello"` 的默认 echo 行为，避免现有最小测试和本地运行路径中断。
- 新增 `ikki.example.yaml`，用户需要真实模型时复制为 `~/.ikki/config.yaml` 并设置对应环境变量。
- 更新 README 说明 YAML 配置、模型 profile、OpenAI-compatible 和 Anthropic API 的用法。
- 回滚时可以继续使用 echo 模型路径；真实模型后端是新增能力，不迁移已有用户数据。

## Open Questions

- 阶段 0 是否需要固定具体 HTTP 客户端库名称，还是实现时按依赖体积和测试便利性选择。
- Anthropic 默认版本 header 是否在示例配置中暴露，还是由后端实现提供默认值。
