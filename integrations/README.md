# 进阶安装与 Agent 接入

普通用户从[快速开始](../README.md#快速开始推荐)进入即可。本页只用于指定 Agent、更新 Skill、安装 WorkBuddy 或配置本地 MCP，不是快速开始之后必须执行的第二轮安装。

## Skills CLI 可选参数与更新

已经走完快速开始的用户，不需要再安装运行环境。只在需要时使用下面的命令：

```bash
# 指定 Agent，跳过交互
npx skills add zifacorp/anylover --skill anylover-companion -g -a cursor -a windsurf -y
# 查看可安装的 Skill、已安装的 Skill，或检查更新
npx skills add zifacorp/anylover --list
npx skills list -g
npx skills update
```

`-g` 是用户级安装，省略后仅安装到当前项目。Skills CLI 支持 Codex、Claude Code、Cursor、Windsurf、OpenCode、Gemini CLI、GitHub Copilot、OpenClaw、CodeBuddy 等 Agent，详见[官方支持表](https://github.com/vercel-labs/skills#supported-agents)。WorkBuddy 不是 CodeBuddy，请使用下面的本地 MCP 安装。

Skill 随包携带运行时安装脚本和 CLI 操作参考。快速开始的初始化步骤会让 Agent 运行 Skill 内的 `scripts/setup.sh`，需要 Python 3.11+ 和 Git，不需要仓库检出。该脚本保留已有伴侣和记忆，不创建全局 CLI 入口，也不改写 MCP 配置。Agent 使用脚本输出的绝对 CLI 路径访问同一个数据库；已有 MCP 连接时优先使用 MCP。

## 本地 MCP 安装

这是快速开始的替代方式，适用于 WorkBuddy，或希望为 Codex / Claude Code 自动注册本地 MCP 的用户。它会一次完成运行环境、伴侣初始化、Skill 和 MCP 配置，不需要先装 Skills CLI 再初始化。

需要 macOS 或 Linux、Python 3.11+ 和 Git。先下载源码；如果已下载，直接进入已有项目目录，不要重复克隆：

```bash
git clone https://github.com/zifacorp/anylover.git
cd anylover
```

按你使用的 Agent 选择一条命令，不要全部执行：

```bash
bash install.sh --agent workbuddy
# 或 Codex
bash install.sh --agent codex
# 或 Claude Code
bash install.sh --agent claude
```

希望自动检测本机已有 Agent 时，可改用：

```bash
bash install.sh --agent auto
```

安装器创建独立 Python 环境、初始化不存在的本地伴侣档案和 SQLite 记忆库、安装 Skill，并创建 `~/.local/bin/anylover` 和 `anylover-mcp` 入口。Codex、Claude Code、WorkBuddy 使用独立虚拟环境中的绝对 `anylover-mcp` 路径。安装完成后重启对应 Agent，再问“你目前记得我什么”验证读取。

还支持 `--agent cursor`、`windsurf`、`opencode`、`gemini-cli`、`github-copilot`、`openclaw`、`codebuddy`，这些入口需要额外的 Node.js/npx，由 Skills CLI 安装 Skill，再使用本地 CLI，不自动改写这些 Agent 的 MCP 设置。

先预览计划，不修改任何文件：

```bash
bash install.sh --dry-run --agent all
```

两条安装路径默认共用同一份本地数据库，保留已有伴侣和记忆。已经通过 Skill 初始化且 CLI 可用的用户，不需要为了使用记忆再装一次；只有确实需要 MCP 自动配置时才使用本节。

已有同名 `anylover` MCP 配置默认保留。只有明确要替换时，才在所选安装命令后加 `--force-agent-config`；WorkBuddy JSON 修改前会创建备份。

需要 Agent 代为安装源码版本时，可以把这句话发给它：

> 请阅读项目根目录的 `AGENT_INSTALL.md`，按默认安全流程安装并验证 AnyLover。

## 手动接入

- Codex / ChatGPT 桌面端：`codex mcp add anylover -- /absolute/path/to/anylover-mcp`
- Claude Code：`claude mcp add --scope user anylover -- /absolute/path/to/anylover-mcp`
- WorkBuddy 5.3.x：把 `workbuddy/mcp.json.example` 的 server 合并到 `~/.workbuddy/.mcp.json`，并复制 Skill 到 `~/.workbuddy/skills/anylover-companion/`。
- 其他 Agent：把对应配置样例中的 command 换成绝对 `anylover-mcp` 路径。

现有同名 MCP 配置需要人工确认后才能替换。一键安装器只在显式传入 `--force-agent-config` 时执行替换，并在修改 WorkBuddy JSON 前创建备份。

## ChatGPT Web

不要尝试让 ChatGPT Web 连接电脑上的 STDIO 进程。它需要 M2 的远程 Streamable HTTP MCP gateway 和插件部署；当前仓库只提供本地运行时、插件骨架与远程 HTTP API 契约。
