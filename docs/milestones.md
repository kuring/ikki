# 里程碑

## v0.0-bootstrap

目标：让 Ikki 成为一个可以运行、可以继续扩展的 Coding Agent 项目底座。

阶段详情见：[stage-0-bootstrap.md](stages/stage-0-bootstrap.md)。

已完成：

- 增加 `src/ikki` 包结构。
- 增加 `ikki` 命令行入口。
- 增加最小 `Agent` 类。
- 增加 `~/.ikki/config.yaml` / `ikki.example.yaml` 配置文件支持。
- 增加 Ikki 工作目录解析，默认工作目录为 `~/.ikki/`，并支持 `IKKI_HOME`、`IKKI_CONFIG` 和 `--config` 覆盖。
- 增加 Pydantic 配置 schema，校验 provider、默认模型、必填字段、额外字段、timeout 和 temperature。
- 实现模型选择优先级：`--model` > `IKKI_MODEL` > YAML 文件中的 `app.default_model` > 内置默认值。
- 增加统一模型接口 `ModelRequest` / `ModelResponse`。
- 增加 `echo`、OpenAI-compatible 和 Anthropic Messages API 模型后端。
- 增加模型工厂和中文模型错误提示。
- 增加基础日志初始化。
- 增加 README、示例配置、CLI/配置/模型测试。
- 增加项目级开发约束，要求必要注释、中文注释和中文文档。

后续需要补齐：

- 多轮对话消息历史。
- system prompt 管理。
- 工具调用和安全执行边界。
- 真实任务上下文读取和文件编辑能力。

完成检查：

- `ikki --help` 在 editable install 后可以显示帮助信息。
- `ikki "hello"` 可以接收任务，并输出本地 echo 响应。
- `ikki --model local_test "hello"` 可以在无 API Key 情况下运行。
- 在 `~/.ikki/config.yaml` 中设置 `app.default_model: claude_default` 后，可以不传 `--model claude_default` 直接使用该 profile。
- `ikki --config ~/.ikki/config.yaml --model default "hello"` 可按配置选择真实模型 profile。
- API Key 只通过 profile 中的环境变量名读取，不写入仓库配置。
- 模型调用失败时，CLI 输出中文错误提示并返回非零状态码。
- `PYTHONPATH=src python3 -m unittest discover -s tests` 可以通过。

下一个里程碑：

- `v0.1-chat-loop`：在模型调用底座上建立 system prompt、消息结构和简单会话历史。
