# 里程碑

## v0.0-bootstrap

目标：让 Ikki 成为一个可以运行、可以继续扩展的 Python CLI 项目。

已完成：

- 增加 `src/ikki` 包结构。
- 增加 `ikki` 命令行入口。
- 增加最小 `Agent` 类。
- 增加占位模型客户端。
- 增加基于环境变量的配置读取。
- 增加基础日志初始化。
- 增加 README 和最小测试。
- 增加项目级开发约束，要求必要注释、中文注释和中文文档。

完成检查：

- `ikki --help` 在 editable install 后可以显示帮助信息。
- `ikki "hello"` 可以接收任务，并输出占位响应。
- `PYTHONPATH=src python3 -m unittest discover -s tests` 可以通过。

下一个里程碑：

- `v0.1-chat-loop`：调用真实模型，并保存一段简单会话历史。

