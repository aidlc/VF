# Claude Code 非交互模式命令手册

> 基于官方文档整理，适用于脚本、CI/CD、自动化场景

---

## 目录

1. [基础用法](#1-基础用法)
2. [续接会话](#2-续接会话)
3. [长提示词 Heredoc 写法](#3-长提示词-heredoc-写法)
4. [输出格式：JSON / 流式](#4-输出格式json--流式)
5. [工具权限控制](#5-工具权限控制)
6. [系统提示词定制](#6-系统提示词定制)
7. [Bare 模式（CI 推荐）](#7-bare-模式ci-推荐)
8. [费用与限制控制](#8-费用与限制控制)
9. [数据管道 Pipe 用法](#9-数据管道-pipe-用法)
10. [完整 Flag 速查表](#10-完整-flag-速查表)

---

## 1. 基础用法

```bash
# 最简单的非交互调用（-p / --print）
claude -p "What does the auth module do?"

# 指定模型
claude -p "解释这个函数" --model claude-opus-4-8

# 限制 agent 最大轮次
claude -p "Fix the bug in main.py" --max-turns 5
```

---

## 2. 续接会话

```bash
# 续接当前目录最近一次会话
claude -p "继续上次的任务" --continue
# 简写
claude -c -p "继续上次的任务"

# 先获取 session_id，再续接指定会话
session_id=$(claude -p "开始代码审查" --output-format json | jq -r '.session_id')
claude -p "聚焦数据库查询部分" --resume "$session_id"

# 按名字续接（先用 --name 命名）
claude -p "开始重构" -n "auth-refactor"
claude -p "继续重构，完成 PR" --resume "auth-refactor"

# 续接但生成新 session（fork）
claude -p "从这里分叉" --resume "auth-refactor" --fork-session

# 多轮对话完整示例
claude -p "Review this codebase for performance issues"
claude -p "Now focus on the database queries" --continue
claude -p "Generate a summary of all issues found" --continue
```

---

## 3. 长提示词 Heredoc 写法

### 基本 Heredoc

```bash
claude -p "$(cat <<'EOF'
# Task
分析 auth.py 中的安全漏洞

# Context
这是一个 Django 项目，使用 JWT 认证

# Constraints
- 只关注认证相关代码
- 输出中文
EOF
)"
```

### 带 --continue 的 Heredoc

```bash
claude -p "$(cat <<'EOF'
# Task
--continue

# Context
继续上一轮的安全分析，现在重点检查 SQL 注入风险

# Constraint
给出具体的修复建议
EOF
)" --continue
```

### 结合文件内容

```bash
claude -p "$(cat <<'EOF'
请审查以下代码，找出性能瓶颈：

$(cat src/main.py)

重点关注数据库查询和循环嵌套。
EOF
)" --output-format json
```

### 从文件读取提示词

```bash
# 把提示词写到文件
cat > /tmp/prompt.txt << 'EOF'
分析这个项目的整体架构，给出改进建议。
输出格式：Markdown，包含问题列表和优先级。
EOF

claude -p "$(cat /tmp/prompt.txt)"
```

---

## 4. 输出格式：JSON / 流式

### 纯文本输出（默认）

```bash
claude -p "Summarize this project"
```

### JSON 输出（含 session_id、cost 等元数据）

```bash
claude -p "Summarize this project" --output-format json

# 用 jq 提取纯文本结果
claude -p "Summarize this project" --output-format json | jq -r '.result'

# 提取 session_id
claude -p "Start a review" --output-format json | jq -r '.session_id'

# 查看费用
claude -p "Analyze auth.py" --output-format json | jq '.total_cost_usd'
```

### JSON Schema 结构化输出

```bash
# 提取函数名列表
claude -p "Extract the main function names from auth.py" \
  --output-format json \
  --json-schema '{"type":"object","properties":{"functions":{"type":"array","items":{"type":"string"}}},"required":["functions"]}' \
  | jq '.structured_output'

# 提取 TODO 列表
claude -p "Find all TODO comments in the codebase" \
  --output-format json \
  --json-schema '{
    "type": "object",
    "properties": {
      "todos": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "file": {"type": "string"},
            "line": {"type": "number"},
            "comment": {"type": "string"}
          }
        }
      }
    },
    "required": ["todos"]
  }'
```

### 流式输出（stream-json）

```bash
# 基础流式
claude -p "Explain recursion" \
  --output-format stream-json \
  --verbose \
  --include-partial-messages

# 用 jq 过滤只显示文字 token（连续流）
claude -p "Write a poem" \
  --output-format stream-json \
  --verbose \
  --include-partial-messages | \
  jq -rj 'select(.type == "stream_event" and .event.delta.type? == "text_delta") | .event.delta.text'

# 包含 hook 事件的流式输出
claude -p "Analyze the project" \
  --output-format stream-json \
  --verbose \
  --include-hook-events \
  "query"
```

### stream-json 事件结构

| 字段 | 说明 |
|------|------|
| `type` | 事件类型：`stream_event` / `system` |
| `event.delta.type` | `text_delta` 时含文字内容 |
| `event.delta.text` | 实际文字 token |
| `session_id` | 会话 ID |

API 重试事件（`system/api_retry`）字段：

| 字段 | 说明 |
|------|------|
| `attempt` | 当前重试次数（从 1 开始） |
| `max_retries` | 最大重试次数 |
| `retry_delay_ms` | 距下次重试的毫秒数 |
| `error` | 错误类别 |

---

## 5. 工具权限控制

```bash
# 允许特定工具（无需确认）
claude -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit"

# 允许特定 git 命令（前缀匹配，注意空格+*）
claude -p "Look at my staged changes and create an appropriate commit" \
  --allowedTools "Bash(git diff *),Bash(git log *),Bash(git status *),Bash(git commit *)"

# 禁用特定工具
claude -p "Review code" --disallowedTools "Bash"

# 只允许读文件，不允许写
claude -p "Analyze the project" --tools "Read,Bash"

# 禁用所有工具
claude -p "Answer a question" --tools ""

# Permission 模式
claude -p "Apply lint fixes" --permission-mode acceptEdits
claude -p "Read-only analysis" --permission-mode dontAsk
claude -p "Planning phase" --permission-mode plan
```

**Permission 模式说明：**

| 模式 | 说明 |
|------|------|
| `default` | 默认，需确认危险操作 |
| `acceptEdits` | 自动允许文件写入 + 常见文件系统命令 |
| `plan` | 只规划，不执行 |
| `auto` | 自动分类，智能决定是否需要确认 |
| `dontAsk` | 拒绝不在 allow 列表中的一切操作 |
| `bypassPermissions` | 跳过所有权限检查（危险） |

---

## 6. 系统提示词定制

```bash
# 完全替换系统提示词
claude -p "Review this code" \
  --system-prompt "You are a security engineer. Only look for vulnerabilities."

# 从文件替换
claude -p "Review this code" \
  --system-prompt-file ./prompts/security-review.txt

# 追加到默认提示词（推荐，保留默认工具指导）
claude -p "Write a function" \
  --append-system-prompt "Always use TypeScript. Never use any."

# 从文件追加
claude -p "Refactor this module" \
  --append-system-prompt-file ./style-rules.txt

# 结合 pipe：审查 PR diff
gh pr diff "$PR_NUMBER" | claude -p \
  --append-system-prompt "You are a security engineer. Review for vulnerabilities." \
  --output-format json
```

---

## 7. Bare 模式（CI 推荐）

跳过 hooks、skills、plugins、MCP servers、CLAUDE.md 等自动发现，启动更快，结果更稳定。

```bash
# 基础 bare 模式
claude --bare -p "Summarize this file" --allowedTools "Read"

# CI 场景：运行测试并修复
claude --bare -p "Run tests and fix failures" \
  --allowedTools "Bash,Read,Edit" \
  --output-format json

# 带认证（bare 模式不读 keychain，需显式传 API key）
ANTHROPIC_API_KEY=your_key claude --bare -p "Analyze auth.py"

# 带自定义设置
claude --bare -p "query" \
  --settings '{"model":"claude-sonnet-4-6","maxOutputTokens":4096}'
```

> **注意：** `--bare` 是 CI/脚本的推荐模式，未来版本将成为 `-p` 的默认行为。

---

## 8. 费用与限制控制

```bash
# 限制最大花费（美元）
claude -p "Analyze entire codebase" --max-budget-usd 2.00

# 限制最大轮次
claude -p "Fix all bugs" --max-turns 10

# 组合使用
claude -p "Refactor auth module" \
  --max-budget-usd 1.00 \
  --max-turns 5 \
  --output-format json

# 查看单次调用花费
claude -p "What is 2+2" --output-format json | jq '.total_cost_usd'

# 指定 fallback 模型（主模型过载时自动切换）
claude -p "Analyze this" --fallback-model claude-sonnet-4-6
```

---

## 9. 数据管道 Pipe 用法

```bash
# 基础：pipe 输入
cat build-error.txt | claude -p "Explain the root cause" > explanation.txt

# 分析日志
tail -100 /var/log/app.log | claude -p "找出错误模式，用中文总结"

# 代码审查 diff
git diff main | claude -p "Review this diff for bugs and style issues"

# package.json 脚本（typo 检查）
# 在 package.json 的 scripts 中：
# "lint:claude": "git diff main | claude -p \"you are a typo linter. for each typo in this diff, report filename:line on one line and the issue on the next.\""

# 多步管道
git diff HEAD~1 | \
  claude -p "Summarize changes" --output-format json | \
  jq -r '.result' | \
  claude -p "Translate to Chinese" --continue

# stdin 上限是 10MB，超过请用文件路径替代
claude -p "Analyze the large file at ./data/big-file.json"
```

---

## 10. 完整 Flag 速查表

### 核心 Flag

| Flag | 说明 | 示例 |
|------|------|------|
| `-p` / `--print` | 非交互模式 | `claude -p "query"` |
| `-c` / `--continue` | 续接最近会话 | `claude -c -p "query"` |
| `-r` / `--resume` | 按 ID 或名字续接 | `claude -r "session-name" "query"` |
| `-n` / `--name` | 命名会话 | `claude -n "my-task" -p "query"` |
| `--bare` | 极简模式（CI 推荐） | `claude --bare -p "query"` |

### 输出相关

| Flag | 说明 | 示例 |
|------|------|------|
| `--output-format` | `text`/`json`/`stream-json` | `--output-format json` |
| `--json-schema` | 结构化输出 schema | `--json-schema '{"type":"object",...}'` |
| `--verbose` | 显示详细日志 | `--verbose` |
| `--include-partial-messages` | 包含流式 token（需 stream-json） | `--include-partial-messages` |
| `--include-hook-events` | 包含 hook 事件（需 stream-json） | `--include-hook-events` |

### 会话管理

| Flag | 说明 | 示例 |
|------|------|------|
| `--session-id` | 指定 UUID | `--session-id "550e8400-..."` |
| `--fork-session` | 续接但生成新 session | `--fork-session` |
| `--no-session-persistence` | 不保存会话到磁盘 | `--no-session-persistence` |

### 权限控制

| Flag | 说明 | 示例 |
|------|------|------|
| `--allowedTools` | 免确认工具列表 | `--allowedTools "Bash,Read,Edit"` |
| `--disallowedTools` | 禁用工具列表 | `--disallowedTools "Bash"` |
| `--tools` | 限制可用工具集 | `--tools "Read,Bash"` |
| `--permission-mode` | 权限模式 | `--permission-mode acceptEdits` |
| `--dangerously-skip-permissions` | 跳过所有权限 | `--dangerously-skip-permissions` |

### 系统提示词

| Flag | 说明 |
|------|------|
| `--system-prompt` | 完全替换系统提示词 |
| `--system-prompt-file` | 从文件替换系统提示词 |
| `--append-system-prompt` | 追加到默认提示词（推荐） |
| `--append-system-prompt-file` | 从文件追加到默认提示词 |

### 模型与性能

| Flag | 说明 | 示例 |
|------|------|------|
| `--model` | 指定模型 | `--model claude-opus-4-8` |
| `--fallback-model` | 主模型不可用时的备用 | `--fallback-model claude-sonnet-4-6` |
| `--effort` | 推理努力程度 `low`/`medium`/`high`/`max` | `--effort high` |
| `--max-budget-usd` | 最大花费限制（美元） | `--max-budget-usd 5.00` |
| `--max-turns` | 最大 agent 轮次 | `--max-turns 10` |

### 加载外部配置

| Flag | 说明 | 示例 |
|------|------|------|
| `--settings` | 加载 settings JSON | `--settings ./settings.json` |
| `--mcp-config` | 加载 MCP 配置 | `--mcp-config ./mcp.json` |
| `--plugin-dir` | 加载插件目录 | `--plugin-dir ./my-plugin` |
| `--add-dir` | 添加额外工作目录 | `--add-dir ../lib` |

---

## 常用组合模板

### 一次性代码分析（不保存会话）

```bash
claude --bare -p "Analyze auth.py for security issues" \
  --allowedTools "Read" \
  --output-format json \
  --no-session-persistence \
  | jq -r '.result'
```

### CI 自动修复测试

```bash
claude --bare -p "Run the test suite and fix any failures" \
  --allowedTools "Bash,Read,Edit" \
  --permission-mode acceptEdits \
  --max-budget-usd 3.00 \
  --output-format json
```

### 多轮对话脚本

```bash
#!/bin/bash
# 第一轮
SESSION=$(claude -p "Start a full code review of this repo" \
  --output-format json | jq -r '.session_id')

# 第二轮：续接
claude -p "Focus on security issues" \
  --resume "$SESSION" \
  --output-format json | jq -r '.result'

# 第三轮：续接
claude -p "Now fix the top 3 issues you found" \
  --resume "$SESSION" \
  --allowedTools "Read,Edit" \
  --output-format json
```

### 结构化提取 + jq 处理

```bash
claude -p "List all API endpoints in this codebase" \
  --output-format json \
  --json-schema '{
    "type": "object",
    "properties": {
      "endpoints": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "method": {"type": "string"},
            "path": {"type": "string"},
            "description": {"type": "string"}
          }
        }
      }
    }
  }' | jq '.structured_output.endpoints[] | "\(.method) \(.path)"'
```

---

## 注意事项

- **stdin 上限**：pipe 输入最大 10MB（v2.1.128+），超过请改用文件路径
- **bare 模式认证**：不读 keychain，需设置 `ANTHROPIC_API_KEY` 环境变量
- **`--allowedTools` 前缀匹配**：`Bash(git diff *)` 中 `*` 前有空格，`Bash(git diff*)` 含义不同
- **续接会话**：`--continue` 续接当前目录最近会话；`--resume <id/name>` 续接指定会话
- **订阅计费**：2026年6月15日起，`claude -p` 使用独立的 Agent SDK 额度，与交互模式分开计费

---

*参考文档：https://code.claude.com/docs/en/headless | https://code.claude.com/docs/en/cli-reference*
