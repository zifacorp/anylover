# AnyLover installation contract for Agents

This file is for Codex, Claude Code, WorkBuddy, and other coding agents asked to install AnyLover for a user.

## Default action

From the AnyLover repository root, run:

```bash
bash install.sh --agent auto
```

The installer creates a private Python environment, initializes local data only when no database exists, installs the AnyLover Skill, and registers the STDIO MCP server with detected Agent tools.

Do not manually rewrite an Agent configuration before trying the installer. Do not use `sudo`, do not install into system Python, and do not copy secrets into commands or configuration files.

## Target one Agent

```bash
bash install.sh --agent codex
bash install.sh --agent claude
bash install.sh --agent workbuddy
```

Use `--agent all` to request all supported local integrations or `--agent none` for the runtime only. Use `--dry-run` when the user asks to inspect changes first.

If an Agent already has an MCP server named `anylover`, preserve it and report the conflict. Only use `--force-agent-config` after the user explicitly asks to replace that entry. The WorkBuddy merger backs up its JSON configuration before a write.

## Verify

After installation:

```bash
"${ANYLOVER_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/anylover-runtime}/venv/bin/anylover" companion
"${ANYLOVER_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/anylover-runtime}/venv/bin/python" -m pip check
```

For the selected Agent, also check its MCP status:

```bash
codex mcp get anylover
claude mcp get anylover
```

WorkBuddy 5.3.x reads the merged entry from `~/.workbuddy/.mcp.json`; restart WorkBuddy after installation. Never print unrelated MCP configuration values because those files may contain credentials.

## Product boundary

- Codex CLI, IDE, and ChatGPT desktop can use the local STDIO MCP configuration.
- Claude Code and the inspected WorkBuddy 5.3.x layout can use the same local runtime.
- ChatGPT Web cannot access a local STDIO process. Do not claim it is installed there; it requires the future remote MCP gateway.
- AnyLover does not automatically save full transcripts. Durable memory remains selective and consent-aware.
