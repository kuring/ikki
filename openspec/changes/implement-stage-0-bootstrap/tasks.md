## 1. 配置和依赖

- [x] 1.1 在 `pyproject.toml` 中新增 YAML 安全解析、Pydantic 和同步 HTTP 调用依赖。
- [x] 1.2 新增 `ikki.example.yaml`，包含 `local_test`、OpenAI-compatible 和 Anthropic profile 示例。
- [x] 1.3 重构 `src/ikki/config.py`，用 Pydantic 定义 app 配置、模型 profile 和有效运行配置 schema。
- [x] 1.4 实现 YAML 配置读取、安全加载、默认配置合并和缺失配置文件错误处理。
- [x] 1.5 实现模型选择优先级：`--model` > `IKKI_MODEL` > YAML 文件中的 `app.default_model` > 内置默认值。
- [x] 1.6 实现 Pydantic 配置 schema 校验，覆盖 provider、default model、必填字段、额外字段、timeout 和 temperature。
- [x] 1.7 实现默认工作目录 `~/.ikki/`、默认配置文件 `~/.ikki/config.yaml`，并支持 `IKKI_HOME`、`IKKI_CONFIG` 和 `--config` 覆盖。

## 2. 模型提供层

- [x] 2.1 新建 `src/ikki/models/` 包，并在 `models/base.py` 定义 `ModelMessage`、`ModelRequest`、`ModelResponse` 和统一模型 provider 接口。
- [x] 2.2 将当前 echo 实现迁移到 `models/echo.py`，保持无网络、无 API Key 的确定性响应。
- [x] 2.3 实现模型工厂，根据 Pydantic 校验后的有效 model profile 构造对应 provider。
- [x] 2.4 实现 `models/openai_compatible.py`，支持非流式 Chat Completions 请求和响应解析。
- [x] 2.5 实现 `models/anthropic.py`，支持非流式 Anthropic Messages API 请求和响应解析。
- [x] 2.6 定义项目内部模型异常，把认证、超时、HTTP 错误和响应格式错误转换成中文错误信息。

## 3. CLI 和 Agent 集成

- [x] 3.1 扩展 CLI 参数，新增 `--config` 和 `--model`，保留 `--log-level`、`--help`、`--version`。
- [x] 3.2 调整 CLI 主流程，按配置加载、日志初始化、模型选择、Agent 构造、任务执行的顺序组装运行时。
- [x] 3.3 调整 `Agent`，将任务文本转换为 `ModelRequest`，并只依赖统一模型接口，不导入供应商实现。
- [x] 3.4 在 CLI 捕获配置和模型异常，输出中文错误提示并返回非零退出码。
- [x] 3.5 保持 `ikki "hello"` 和 `ikki --model local_test "hello"` 的本地 echo 运行路径。

## 4. 测试

- [x] 4.1 补充 CLI 测试，覆盖无任务帮助、`--config`、`--model`、`--log-level` 和 echo 成功路径。
- [x] 4.2 新增配置测试，覆盖 YAML 加载、默认值、命令行覆盖、环境变量覆盖和 Pydantic schema 校验失败。
- [x] 4.3 新增运行时路径测试，覆盖默认路径、`IKKI_HOME`、`IKKI_CONFIG` 和 `--config` 优先级。
- [x] 4.4 新增模型接口和工厂测试，覆盖 `ModelRequest`、`ModelResponse`、echo、OpenAI-compatible、Anthropic 和未知 provider。
- [x] 4.5 新增远程模型后端单元测试，使用 fake HTTP 响应覆盖成功、HTTP 错误、超时和无效响应。
- [x] 4.6 运行 `PYTHONPATH=src python3 -m unittest discover -s tests` 并修复失败项。

## 5. 文档和里程碑

- [x] 5.1 更新 README，写清安装、`ikki.example.yaml`、模型 profile、OpenAI-compatible、Anthropic API 和安全注意事项。
- [x] 5.2 更新 `docs/milestones.md`，把已完成项和完成检查同步到阶段 0 实现结果。
- [x] 5.3 复查 `docs/stages/stage-0-bootstrap.md`，确保实现结果与阶段设计保持一致。
- [x] 5.4 清理开发中生成的缓存文件，避免提交 `__pycache__`、本地配置或真实密钥。
