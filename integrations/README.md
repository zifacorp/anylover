# Agent 接入说明

## 通用 Skill 安装（与 Vast.ai CLI 相同）

```bash
npx skills add zifacorp/anylover
npx skills add zifacorp/anylover --skill anylover-companion -g -a cursor -a windsurf -y
```

默认安装到当前项目；`-g` 是用户级安装。Skills CLI 支持 Codex、Claude Code、Cursor、Windsurf、OpenCode、Gemini CLI、GitHub Copilot、OpenClaw、CodeBuddy 等 Agent，详见[官方支持表](https://github.com/vercel-labs/skills#supported-agents)。WorkBuddy 继续使用下面的专用安装器，不把它误当作 CodeBuddy。

Skill 随包携带运行时安装脚本和 CLI 操作参考。首次让 Agent 安装运行时时，它运行 Skill 内的 `scripts/setup.sh`，需要 Python 3.11+ 和 Git，不需要仓库检出。安装器保留已有伴侣和记忆，不改写 MCP 配置。没有 MCP 时，Agent 通过本地 CLI 访问同一个数据库。

## 运行时和 Agent 一起安装

从项目根目录运行：

```bash
bash install.sh --agent auto
```

Codex、Claude Code、WorkBuddy 使用独立虚拟环境中的绝对 `anylover-mcp` 路径。还支持 `--agent cursor`、`windsurf`、`opencode`、`gemini-cli`、`github-copilot`、`openclaw`、`codebuddy`，这些入口需要 Node.js/npx，由 Skills CLI 安装 Skill，再使用本地 CLI，不自动改写这些 Agent 的 MCP 设置。

## 手动接入

- Codex / ChatGPT 桌面端：`codex mcp add anylover -- /absolute/path/to/anylover-mcp`
- Claude Code：`claude mcp add --scope user anylover -- /absolute/path/to/anylover-mcp`
- WorkBuddy 5.3.x：把 `workbuddy/mcp.json.example` 的 server 合并到 `~/.workbuddy/.mcp.json`，并复制 Skill 到 `~/.workbuddy/skills/anylover-companion/`。
- 其他 Agent：把对应配置样例中的 command 换成绝对 `anylover-mcp` 路径。

现有同名 MCP 配置需要人工确认后才能替换。一键安装器只在显式传入 `--force-agent-config` 时执行替换，并在修改 WorkBuddy JSON 前创建备份。

## ChatGPT Web

不要尝试让 ChatGPT Web 连接电脑上的 STDIO 进程。它需要 M2 的远程 Streamable HTTP MCP gateway 和插件部署；当前仓库只提供本地运行时、插件骨架与远程 HTTP API 契约。
