# AnyLover without MCP

Use this reference when the current agent has a shell but no AnyLover MCP tools,
or when the user asks to install the shared local runtime after adding the Skill.

## Find or install the runtime

Prefer an existing `anylover` on PATH. Otherwise check the executable at
`${ANYLOVER_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/anylover-runtime}/venv/bin/anylover`.
Use that absolute path if present; changing PATH is unnecessary.

When the user requested setup and the runtime is missing, run the bundled script
using its actual installed Skill path:

```bash
bash /absolute/path/to/anylover-companion/scripts/setup.sh
```

It requires Bash, Python 3.11+, and Git. It installs AnyLover from the official
GitHub repository into a private virtual environment. It preserves existing
profiles and memories and does not edit any MCP or Agent configuration. For an
offline/local-source workflow, pass `--source /absolute/path/to/anylover`.
`--dry-run` previews without writes. Use the absolute CLI path printed at the end
and verify it with `companion`. If the user wants MCP registration as well, follow
the repository's `AGENT_INSTALL.md` and `install.sh` instead.

## Equivalent operations

The examples use `anylover`; substitute the discovered absolute path when needed.
Quote actual user strings using the shell's quoting rules. Do not interpolate
untrusted text into executable shell code. Never put chat text in session metadata.

| MCP operation | CLI equivalent |
|---|---|
| `anylover_start_session` | `anylover session --surface cursor --external-id SESSION_ID` |
| `anylover_get_context` | `anylover context --query 'CURRENT USER MESSAGE' --json` |
| `anylover_remember` | `anylover remember --kind preference --consent explicit --surface cursor -- 'CONCISE MEMORY'` |
| `anylover_list_memories` | `anylover list --json` |
| `anylover_forget` | `anylover forget MEMORY_ID --confirm DELETE` |

Use the actual surface (`cursor`, `windsurf`, `opencode`, `gemini-cli`,
`github-copilot`, `openclaw`, `codebuddy`, `codex`, `claude-code`, or `workbuddy`).
When a stable external session ID is available, create a session at most once and
pass its returned ID to memory writes with `--session-id`. Never invent provenance.
For a correction, add `--supersedes OLD_MEMORY_ID`. Sensitive memories still need
explicit consent and the server-side opt-in; never enable that opt-in silently.

Apply `companion`, `memories`, and `prompt` from the JSON context to the response.
Use the complete current message as the query, and retrieve again when a new
personal topic or continuity signal warrants it. Automatic retrieval does not
authorize writing memories. The explicit-delete requirement is identical to MCP.

The CLI accesses the same local database as MCP, normally
`~/.anylover/anylover.sqlite3`. Different machines or remote workspaces do not share
it automatically; cloud sync and mobile apps remain roadmap items. Shell access
and local Python are required for this fallback; it does not make ChatGPT Web
capable of running local commands.
