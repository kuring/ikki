# 从零开发 Coding Agent ikki

这篇文档是我后续学习和开发 Agent 的总路线。

目标不是一开始就复制完整的 Claude Code，而是从一个很小的命令行 Agent 开始，逐步加入工具调用、代码仓库理解、文件编辑、命令执行、测试修复、计划管理、记忆、评测和安全边界。

## 文档定位

这篇文档是 `ikki` 主项目的总纲，回答三个问题：

- `ikki` 最终要做成什么样？
- 从阶段 0 到后续阶段应该按什么顺序推进？
- 每个阶段对应什么分支、tag 和学习重点？

具体到某个阶段的配置样例、目录细节、完成标准和复盘问题，放到 `docs/stages/` 下的阶段文档中维护。这样主线文档负责总览，每个阶段文档负责展开细节。

学习方式分成两条线：

- 理论线：先理解一个能力背后的概念、架构和常见问题。
- 开发线：在 `/Users/kuring/github/kuring/ikki` 中实现一个对应功能，并用 git 分支或 tag 保存阶段成果。

每个阶段都要做到三件事：

- 在笔记里写清楚：这个能力解决什么问题，核心概念是什么。
- 在 `ikki` 仓库里实现：功能能运行，有最小 demo。
- 留下可回溯版本：开发分支用于实现，tag 用于标记阶段成果。

## 项目定位

我要做的是一个面向代码仓库的 Coding Agent。它最终应该能完成类似这样的任务：

- 理解用户的自然语言开发需求。
- 搜索并阅读代码仓库。
- 制定修改计划。
- 修改文件。
- 运行测试或检查命令。
- 根据失败结果继续修复。
- 展示 diff 和解释改动。
- 保护用户已有改动。
- 在危险操作前请求确认。
- 留下完整执行轨迹，方便复盘和评测。

它和普通 Chatbot 的区别是：普通 Chatbot 主要给出回答，而 Coding Agent 会和真实环境交互。它需要读文件、执行命令、修改代码、观察结果，并根据观察继续行动。

## 仓库和版本管理

笔记仓库：

- `/Users/kuring/my_git/ai-notebook`
- 用来记录理论知识、设计思路、实验复盘和阶段总结。

代码仓库：

- `/Users/kuring/github/kuring/ikki`
- 用来实现这个 Coding Agent。

推荐规则：

- 每增加一个功能，用新分支开发。
- 每完成一个可运行阶段，打一个 tag。
- 分支表示开发过程，tag 表示学习里程碑。

示例：

```bash
git checkout -b feat/02-tool-calling

# 开发、测试、提交完成后
git tag v0.2-tools
```

分支命名建议：

- `feat/00-bootstrap`
- `feat/01-chat-loop`
- `feat/02-tool-calling`
- `feat/03-repo-context`

tag 命名建议：

- `v0.0-bootstrap`
- `v0.1-chat-loop`
- `v0.2-tools`
- `v0.3-repo-context`

## 总体路线图

| 阶段  | 详情文档 | 开发功能                     | 理论重点                         | 分支                     | tag                   |
| --- | --- | ------------------------ | ---------------------------- | ---------------------- | --------------------- |
| 0   | [项目底座](stages/stage-0-bootstrap.md) | CLI、配置文件、多模型调用、日志、README | 模型调用封装、配置优先级、供应商隔离          | `feat/00-bootstrap`    | `v0.0-bootstrap`      |
| 1   | [最小对话 Agent](stages/stage-1-chat-loop.md) | system prompt、消息结构、单轮/多轮对话 | Agent loop、上下文、会话历史          | `feat/01-chat-loop`    | `v0.1-chat-loop`      |
| 2   | [最小 Tool Calling](stages/stage-2-tool-calling.md) | 时间、计算器、读取文件              | 工具 schema、参数校验、工具结果回填        | `feat/02-tool-calling` | `v0.2-tools`          |
| 3   | [代码仓库感知](stages/stage-3-repo-context.md) | 目录查看、关键词搜索、文件读取          | Coding Agent 如何理解工作区         | `feat/03-repo-context` | `v0.3-repo-context`   |
| 4   | [只读代码分析](stages/stage-4-code-qa.md) | 回答代码位置、调用链、错误原因          | 基于证据回答、避免猜测                  | `feat/04-code-qa`      | `v0.4-code-qa`        |
| 5   | [安全命令执行](stages/stage-5-safe-shell.md) | shell 工具、白名单、dry-run     | 权限模型、危险命令识别                  | `feat/05-safe-shell`   | `v0.5-safe-shell`     |
| 6   | [文件编辑能力](stages/stage-6-file-edit.md) | patch 修改、diff 展示、改动保护    | 最小编辑、保护用户改动                  | `feat/06-file-edit`    | `v0.6-edit`           |
| 7   | [测试修复循环](stages/stage-7-test-loop.md) | 运行测试、读取失败、继续修复           | Observe-Think-Act 循环         | `feat/07-test-loop`    | `v0.7-test-loop`      |
| 8   | [任务计划系统](stages/stage-8-planning.md) | todo、步骤状态、失败重试           | Planning、状态机、长任务控制           | `feat/08-planning`     | `v0.8-planning`       |
| 9   | [Git 工作流](stages/stage-9-git-flow.md) | diff、提交说明、分支和 tag 辅助     | Agent 与版本管理协作                | `feat/09-git-flow`     | `v0.9-git-flow`       |
| 10  | [轨迹记录](stages/stage-10-trajectory.md) | 保存 prompt、工具调用、diff、测试结果 | Trajectory、可观测性              | `feat/10-trajectory`   | `v1.0-learning-agent` |
| 11  | [记忆系统](stages/stage-11-memory.md) | 用户偏好、项目约定、历史摘要           | Memory、遗忘、过期和检索              | `feat/11-memory`       | `v1.1-memory`         |
| 12  | [评测系统](stages/stage-12-eval.md) | 小任务集、成功率、失败归因            | Agent Eval、安全评测              | `feat/12-eval`         | `v1.2-eval`           |

## 阶段文档结构

每个阶段都拆成独立文档，放在 `docs/stages/` 下。阶段文档尽量保持相同结构，方便横向比较和持续补充：

- 阶段目标
- 要学习的问题
- 理论要点
- 开发范围
- 暂时不做什么
- 设计决策
- 建议目录或模块变化
- 实现任务
- 完成标准
- 复盘问题
- 相关笔记

## 阶段 0：项目底座

目标：让 `ikki` 从第一阶段开始就是一个可以真实运行、可以切换模型、可以继续扩展的 Agent 项目底座，而不是只会打印回显文本的演示程序。

阶段 0 可以适当前移一部分阶段 1 的内容：真实大模型调用应该放在这里完成。原因是后续所有能力，包括对话、工具调用、代码理解和文件编辑，都依赖稳定的模型调用层。如果模型层等到阶段 1 才做，阶段 0 的脚手架价值会太低。

这一阶段的主线范围：

- 建立 Python 包结构和 CLI 入口。
- 建立可扩展配置系统。
- 建立模型调用抽象。
- 支持本地 `echo` 模型、OpenAI-compatible 真实模型和 Anthropic API 真实模型。
- 支持多个模型 profile。
- 保留中文文档、中文 CLI 帮助、基础日志和最小测试。

这一阶段明确不做 Tool Calling、代码仓库读取、文件编辑、shell 执行、复杂 Planning、记忆系统和评测系统。

详细范围、推荐配置、目录结构和完成标准见：[阶段 0：项目底座](stages/stage-0-bootstrap.md)。

## 阶段 1：最小对话 Agent

目标：在阶段 0 已经能调用真实模型的基础上，做一个真正有 Agent 雏形的最小对话循环。

理论学习：

- Agent loop 是什么。
- system prompt、user message、assistant message 的区别。
- 上下文窗口为什么会影响 Agent 表现。
- 单轮调用和多轮对话有什么区别。

开发任务：

- 设计默认 system prompt。
- 把用户输入包装成标准消息结构。
- 支持单轮问答。
- 保存简单会话历史。
- 在日志或调试模式中展示发送给模型的消息结构。

完成标准：

- 可以执行一次完整问答。
- 可以看到发送给模型的消息结构。
- 可以继续一段简单多轮对话。
- 打 tag：`v0.1-chat-loop`。

对应笔记：

- Agent 与 Workflow（ai-notebook: `07-Agent/Agent 与 Workflow.md`）
- ReAct（ai-notebook: `07-Agent/ReAct.md`）

## 阶段 2：最小 Tool Calling

目标：让 Agent 从“会说”变成“会做”。

理论学习：

- Tool Calling 是什么。
- 工具 schema 为什么要结构化。
- 工具参数如何校验。
- 工具失败后怎么把错误返回给模型。

开发任务：

- 增加工具注册表。
- 增加 `get_time` 工具。
- 增加 `calculator` 工具。
- 增加 `read_file` 工具。
- 让模型可以选择工具并读取结果。

完成标准：

- Agent 能根据用户问题自动选择工具。
- 工具调用过程能在日志中看到。
- 工具参数错误时不会直接崩溃。
- 打 tag：`v0.2-tools`。

对应笔记：

- Tool Calling（ai-notebook: `07-Agent/Tool Calling.md`）

## 阶段 3：代码仓库感知

目标：让 Agent 能理解一个本地代码仓库。

理论学习：

- Coding Agent 为什么需要搜索而不是一次性读完整仓库。
- 文件树、关键词搜索、文件片段读取分别解决什么问题。
- `.gitignore`、隐藏文件和大文件为什么需要处理。

开发任务：

- 增加 `list_files` 工具。
- 增加 `search_text` 工具，优先使用 `rg`。
- 增加 `read_file_range` 工具。
- 增加工作区根目录限制，避免误读仓库外文件。

完成标准：

- Agent 能回答“某个函数或关键词在哪里”。
- Agent 回答时能引用具体文件路径。
- 打 tag：`v0.3-repo-context`。

对应笔记：

- Coding Agent（ai-notebook: `07-Agent/Coding Agent.md`）

## 阶段 4：只读代码分析

目标：让 Agent 在不修改代码的情况下完成代码理解任务。

理论学习：

- 什么是基于证据的代码回答。
- 为什么 Coding Agent 不能只靠模型记忆猜代码。
- 如何区分“我确认看到的事实”和“我的推断”。

开发任务：

- 增加代码问答模式。
- 要求回答中包含文件引用。
- 在证据不足时让 Agent 继续搜索。
- 记录一次完整分析轨迹。

完成标准：

- 能回答一个小仓库里的代码定位问题。
- 回答里能区分事实和推断。
- 打 tag：`v0.4-code-qa`。

对应笔记：

- Coding Agent（ai-notebook: `07-Agent/Coding Agent.md`）
- Agent 评测（ai-notebook: `07-Agent/Agent 评测.md`）

## 阶段 5：安全命令执行

目标：让 Agent 能运行命令，但不能乱运行危险命令。

理论学习：

- Shell 工具为什么是高风险工具。
- 什么是命令白名单、黑名单和确认点。
- dry-run 在 Agent 中有什么价值。

开发任务：

- 增加 `run_command` 工具。
- 支持只读命令，例如 `pwd`、`ls`、`rg`、`git status`。
- 对高风险命令进行拦截。
- 对需要确认的命令返回确认请求，而不是直接执行。

完成标准：

- Agent 可以运行安全检查命令。
- 危险命令不会被直接执行。
- 打 tag：`v0.5-safe-shell`。

对应笔记：

- Tool Calling（ai-notebook: `07-Agent/Tool Calling.md`）
- 评测与安全（ai-notebook: `10-评测与安全/README.md`）

## 阶段 6：文件编辑能力

目标：让 Agent 能修改代码，但修改过程必须可控。

理论学习：

- 为什么 patch 比直接覆盖文件更适合 Coding Agent。
- 如何保护用户未提交改动。
- 如何控制修改范围，避免顺手重构。

开发任务：

- 增加 `apply_patch` 风格的编辑能力。
- 修改前检查 git status。
- 修改后展示 diff。
- 限制 Agent 只能编辑工作区内文件。

完成标准：

- Agent 能完成一个很小的代码修改任务。
- 修改后能展示清晰 diff。
- 不会覆盖无关文件。
- 打 tag：`v0.6-edit`。

对应笔记：

- Coding Agent（ai-notebook: `07-Agent/Coding Agent.md`）

## 阶段 7：测试与修复循环

目标：让 Agent 形成“修改 -> 测试 -> 观察失败 -> 再修改”的闭环。

理论学习：

- ReAct 中的 Observe-Think-Act 是什么。
- 为什么测试失败输出是 Agent 的关键观察。
- 为什么需要限制重试次数。

开发任务：

- 允许 Agent 运行测试命令。
- 解析测试失败输出。
- 根据失败信息再次搜索和修改。
- 增加最大循环次数。

完成标准：

- Agent 能在一个小任务中完成至少一次失败后修复。
- 日志里能看到每一轮行动和观察。
- 打 tag：`v0.7-test-loop`。

对应笔记：

- ReAct（ai-notebook: `07-Agent/ReAct.md`）
- Agent 评测（ai-notebook: `07-Agent/Agent 评测.md`）

## 阶段 8：任务计划系统

目标：让 Agent 不只是一步一步反应，而是能维护任务计划。

理论学习：

- Planning 和 ReAct 的区别。
- 计划什么时候有用，什么时候反而浪费。
- 状态机如何避免 Agent 陷入混乱。

开发任务：

- 增加 todo list。
- 支持任务状态：pending、in_progress、completed。
- 每完成一步更新状态。
- 失败时记录失败原因和下一步选择。

完成标准：

- Agent 能把复杂任务拆成多个步骤。
- 用户能看到当前进度。
- 打 tag：`v0.8-planning`。

对应笔记：

- Agent 与 Workflow（ai-notebook: `07-Agent/Agent 与 Workflow.md`）

## 阶段 9：Git 工作流

目标：让 Agent 和 git 协作，而不是绕开 git。

理论学习：

- 为什么 Coding Agent 必须尊重工作区状态。
- diff、commit、branch、tag 在学习型项目中的作用。
- 自动提交为什么需要用户确认。

开发任务：

- 增加 `git_status` 工具。
- 增加 `git_diff` 工具。
- 自动生成 commit message。
- 辅助创建分支和 tag。

完成标准：

- Agent 能解释当前 diff。
- Agent 能给出合适的提交说明。
- 不会自动提交用户没确认的内容。
- 打 tag：`v0.9-git-flow`。

对应笔记：

- 工程化与部署（ai-notebook: `09-工程化与部署/README.md`）
- Coding Agent（ai-notebook: `07-Agent/Coding Agent.md`）

## 阶段 10：轨迹记录

目标：让每次 Agent 执行都可以复盘。

理论学习：

- Trajectory 是什么。
- 为什么只看最终回答无法评测 Agent。
- 如何记录工具调用、观察、决策和结果。

开发任务：

- 保存每次任务的输入。
- 保存模型消息。
- 保存工具调用和返回值。
- 保存 diff、测试命令和结果。
- 生成一次任务总结。

完成标准：

- 每次任务结束后都有一份轨迹文件。
- 可以根据轨迹复盘 Agent 哪里做得好、哪里做错。
- 打 tag：`v1.0-learning-agent`。

对应笔记：

- Agent 评测（ai-notebook: `07-Agent/Agent 评测.md`）

## 阶段 11：记忆系统

目标：让 Agent 能记住稳定偏好和项目约定，而不是每次从零开始。

理论学习：

- Memory 和上下文有什么区别。
- 什么内容值得长期记忆。
- 记忆为什么需要过期、验证和引用来源。

开发任务：

- 增加本地 memory 文件。
- 记录用户偏好。
- 记录项目约定。
- 在任务开始时检索相关记忆。
- 回答时区分当前观察和历史记忆。

完成标准：

- Agent 能复用稳定项目约定。
- Agent 不会把过期记忆当成当前事实。
- 打 tag：`v1.1-memory`。

对应笔记：

- Agent Memory（ai-notebook: `07-Agent/Agent Memory.md`）

## 阶段 12：评测系统

目标：用一批固定任务评估 Agent 是否真的变强。

理论学习：

- Agent 评测和普通模型评测有什么区别。
- 如何设计小而稳定的任务集。
- 如何统计成功率、失败类型、成本和耗时。

开发任务：

- 准备一组小型代码任务。
- 每个任务包含输入、期望结果和检查方法。
- 运行 Agent 完成任务。
- 记录成功率和失败原因。

完成标准：

- 有一套可重复运行的 eval。
- 能比较两个 tag 的能力差异。
- 打 tag：`v1.2-eval`。

对应笔记：

- Agent 评测（ai-notebook: `07-Agent/Agent 评测.md`）

## 补充练习项目

这些项目不是 `ikki` 主线的替代品，而是围绕 Agent 能力展开的专项练习。它们可以在主线阶段之间穿插做，用来加深对某个能力的理解。

### 练习项目 1：最小 Tool-Calling Agent

- 输入：用户自然语言任务
- 工具：时间查询、计算器、文件读取或简单 API
- 目标：理解工具 schema、参数生成、工具结果解释
- 产出：一篇项目实践笔记和一次执行轨迹

### 练习项目 2：个人知识库 RAG Agent

- 输入：一组本地文档或学习笔记
- 工具：检索、引用、摘要、问答
- 目标：理解 Agent 如何使用外部知识
- 产出：RAG 设计、检索评测和失败案例

### 练习项目 3：Coding Agent

- 输入：一个小型代码修改任务
- 工具：文件搜索、文件编辑、测试运行、git diff
- 目标：理解代码 Agent 的工作循环
- 产出：任务轨迹、测试结果和复盘

### 练习项目 4：Browser Agent

- 输入：一个网页信息收集或表单操作任务
- 工具：浏览器导航、点击、输入、截图
- 目标：理解 Agent 如何操作外部环境
- 产出：页面状态记录、失败恢复策略和安全确认点

### 练习项目 5：Multi-Agent Workflow

- 输入：一个需要分工的复杂任务
- 角色：Planner、Executor、Reviewer
- 目标：理解多 Agent 协作的收益和复杂度
- 产出：角色边界、消息协议、评测结果

## 每次迭代的固定流程

每次增加功能时，都按照这个节奏走：

1. 先补理论：我先学习这个功能背后的概念。
2. 明确边界：这个阶段只做什么，不做什么。
3. 创建分支：在 `ikki` 中创建对应 `feat/*` 分支。
4. 实现功能：只实现当前阶段需要的最小能力。
5. 本地验证：运行 demo、测试或手动任务。
6. 写复盘：记录设计、实现、问题和下一步。
7. 打 tag：标记这个可回看的学习版本。

每次复盘至少回答这些问题：

- 这个阶段学到的核心概念是什么？
- 实现时遇到的主要问题是什么？
- Agent 哪些行为符合预期？
- Agent 哪些行为不稳定或危险？
- 下个阶段应该补什么能力？

## 学习笔记记录方式

每个阶段的项目文档直接维护在 `docs/stages/` 下；通用概念笔记仍保留在 `ai-notebook`。

推荐结构：

```text
# 阶段标题

## 我想解决的问题

## 核心概念

## 最小实现

## 关键代码路径

## 运行示例

## 失败案例

## 复盘

## 下一步
```

如果某个理论点不清楚，就单独拆成概念笔记。例如：

- Tool Calling 的 schema 设计。
- ReAct 为什么需要 observation。
- Coding Agent 如何保护用户改动。
- Agent Memory 如何避免记错。
- Agent Eval 怎么判断任务成功。

## 当前优先级

近期先完成前三个阶段：

1. `v0.0-bootstrap`：搭好 `ikki` 项目骨架。
2. `v0.1-chat-loop`：做出最小对话 Agent。
3. `v0.2-tools`：做出最小 Tool Calling。

这三个阶段完成后，Agent 才算真正进入“可以做事”的状态。后续再进入代码仓库理解、文件编辑和测试修复循环。

## 暂时不做的事情

为了避免一开始过度复杂，前期暂时不做：

- 多 Agent 协作。
- 浏览器自动化。
- RAG 知识库。
- 复杂 TUI。
- 插件市场。
- 远程沙箱。
- 自动提交和自动推送。

这些能力不是不重要，而是要等最小 Coding Agent 跑通后再加入。

## 最终目标

最终我希望 `ikki` 不只是一个 demo，而是一个学习型 Coding Agent：

- 每个能力都有理论笔记。
- 每个能力都有对应实现。
- 每个阶段都有 tag。
- 每次失败都能复盘。
- 每次增强都能看出为什么需要这个功能。

这样我学习 Agent 的过程，不是只读资料，也不是只堆代码，而是用一个真实项目把理论、实现、评测和复盘串起来。
