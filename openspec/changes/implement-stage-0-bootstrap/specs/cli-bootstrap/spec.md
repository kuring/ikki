## ADDED Requirements

### Requirement: CLI 暴露启动阶段控制参数

CLI SHALL 提供中文用户可见帮助文案，并接受任务文本、配置文件路径、模型 profile、日志级别和版本输出等启动阶段参数。

#### Scenario: 帮助输出使用中文

- **WHEN** 用户运行 `ikki --help`，或在未提供任务时运行 `ikki`
- **THEN** CLI 显示中文帮助文案并成功退出

#### Scenario: 接受启动阶段参数

- **WHEN** 用户运行 `ikki --config ~/.ikki/config.yaml --model local_test --log-level DEBUG "hello"`
- **THEN** CLI 能解析配置文件路径、模型 profile、日志级别和任务，并且不报告参数错误

### Requirement: CLI 组装运行时依赖

CLI SHALL 加载配置、初始化日志、选择请求的模型 profile、构造 Agent、执行任务，并打印模型响应。

#### Scenario: Echo 模型任务成功

- **WHEN** 用户在没有 API Key 的情况下运行 `ikki --model local_test "hello"`
- **THEN** CLI 打印 echo 模型响应，并以状态码 0 退出

#### Scenario: 空任务不调用模型

- **WHEN** 解析后的任务缺失或为空
- **THEN** CLI 显示帮助或清晰的中文提示，并且不调用远程模型后端

### Requirement: CLI 清晰报告模型错误

CLI SHALL 将配置失败和模型调用失败转换成简洁的中文用户可见错误信息。

#### Scenario: API Key 缺失

- **WHEN** 选中的真实模型 profile 引用了未设置的环境变量
- **THEN** CLI 报告缺失的环境变量名，并且默认不打印原始 traceback

#### Scenario: 远程模型调用失败

- **WHEN** 选中的远程模型后端因为超时、HTTP 错误或响应格式无效而失败
- **THEN** CLI 报告清晰的中文失败原因，并以非零状态码退出
