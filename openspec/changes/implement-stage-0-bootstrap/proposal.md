## Why

阶段 0 需要把 Ikki 从只会回显任务的 CLI 脚手架，推进到可配置、可切换模型、可调用真实模型的 Agent 底座。后续对话循环、工具调用、仓库上下文、文件编辑和安全策略都会依赖这一层，模型与配置边界必须在早期稳定下来。

## What Changes

- 增加 YAML 主配置文件 `~/.ikki/config.yaml` 和示例配置 `ikki.example.yaml`。
- 增加配置加载、命令行覆盖、环境变量覆盖和内部配置 schema 校验。
- 将当前单文件占位模型拆分为可扩展的 `models/` 模块。
- 保留 `echo` 本地模型，并新增 OpenAI-compatible 与 Anthropic Messages API 模型后端。
- 增加 `--config`、`--model`、`--log-level` 等 CLI 参数，使 CLI 可以选择配置文件和模型 profile。
- 让 `Agent` 主流程通过配置选择模型客户端，并把模型调用错误转换成中文可理解提示。
- 补充配置、模型选择、CLI 和 echo 模型测试。
- 同步更新 README 与 `docs/milestones.md`，记录阶段 0 的完成情况和使用方式。

## Capabilities

### New Capabilities

- `cli-bootstrap`: CLI 启动、参数解析、日志初始化和任务分发能力。
- `configuration-system`: YAML 配置、环境变量、命令行覆盖和内部 schema 校验能力。
- `model-provider-layer`: 统一模型接口、本地 echo、OpenAI-compatible 和 Anthropic API 后端能力。

### Modified Capabilities

无。

## Impact

- 影响 `src/ikki/cli.py`、`src/ikki/config.py`、`src/ikki/agent.py`、现有模型代码和测试。
- 新增 `src/ikki/models/` 包、`ikki.example.yaml`、配置与模型相关测试。
- `pyproject.toml` 需要新增 YAML 解析和 HTTP 调用依赖。
- CLI 行为会从固定 echo 模型升级为按配置选择模型；默认仍需支持无 API Key 的本地 echo 运行路径。
