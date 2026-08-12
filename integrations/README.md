# Agent 接入说明

普通用户和 Agent 都应优先使用项目根目录的一键安装器：

```bash
bash install.sh --agent auto
```

它会使用独立虚拟环境中的绝对 `anylover-mcp` 路径，避免桌面 App 因 PATH 不同而找不到服务。确定目标时可使用 `--agent codex`、`--agent claude` 或 `--agent workbuddy`。

## 手动接入

- Codex / ChatGPT 桌面端：`codex mcp add anylover -- /absolute/path/to/anylover-mcp`
- Claude Code：`claude mcp add --scope user anylover -- /absolute/path/to/anylover-mcp`
- WorkBuddy 5.3.x：把 `workbuddy/mcp.json.example` 的 server 合并到 `~/.workbuddy/.mcp.json`，并复制 Skill 到 `~/.workbuddy/skills/anylover-companion/`。
- 其他 Agent：把对应配置样例中的 command 换成绝对 `anylover-mcp` 路径。

现有同名 MCP 配置需要人工确认后才能替换。一键安装器只在显式传入 `--force-agent-config` 时执行替换，并在修改 WorkBuddy JSON 前创建备份。

## ChatGPT Web

不要尝试让 ChatGPT Web 连接电脑上的 STDIO 进程。它需要 M2 的远程 Streamable HTTP MCP gateway 和插件部署；当前仓库只提供本地运行时、插件骨架与远程 HTTP API 契约。
