# AnyLover installation contract for Agents

This file is for Codex, Claude Code, WorkBuddy, and other coding agents asked to install AnyLover for a user.

## Portable Skills CLI installation

Users can install the Skill like the Vast.ai CLI Skill:

```bash
npx skills add zifacorp/anylover
npx skills add zifacorp/anylover --skill anylover-companion -g -a cursor -a windsurf -y
```

This installs instructions and bundled resources, not the Python runtime or MCP
configuration. If the user requested setup, run `bash scripts/setup.sh` relative
to the installed Skill directory and verify its absolute CLI path with
`companion`. It installs from the official GitHub repository and preserves the
existing profile. No source checkout is required. Read the Skill's
`references/cli.md` for MCP-to-CLI mappings. Node.js/npm is needed for the Skills
CLI; the runtime needs Python 3.11+ and Git for its default source.

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
bash install.sh --agent cursor
bash install.sh --agent windsurf
bash install.sh --agent opencode
bash install.sh --agent gemini-cli
bash install.sh --agent github-copilot
bash install.sh --agent openclaw
bash install.sh --agent codebuddy
```

Use `--agent all` to request all supported local integrations or `--agent none` for the runtime only. Use `--dry-run` when the user asks to inspect changes first.

Portable targets are installed with `npx skills`, using global scope and copied
supporting files. They use the CLI rather than receiving an automatic MCP config
rewrite. `auto` detects local agent executables/config directories. CodeBuddy is
not WorkBuddy. Tests must use isolated HOME/config roots, never the real user's
Agent configuration. Codex honors `CODEX_HOME`, Claude honors
`CLAUDE_CONFIG_DIR`, and WorkBuddy honors `ANYLOVER_WORKBUDDY_HOME`.

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
- Skills CLI compatibility verifies distribution and CLI access, not each agent's
  in-app behavior. A remote/cloud-only agent cannot read a local database without
  a separately configured transport; do not claim multi-device sync.

## Validate changes to this installation flow

```bash
python -m unittest discover -s tests -v
python scripts/verify_skills_install.py
```

The latter is a networked smoke test using temporary HOME, Agent config roots,
runtime, and memory storage. It installs with the real Skills CLI across nine
agent targets, runs the copied Skill's setup script, checks CLI recall, and
checks that a wrapper upgrade preserves the existing profile and memory.
