#!/usr/bin/env bash

set -Eeuo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
install_root="${ANYLOVER_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/anylover-runtime}"
bin_dir="${ANYLOVER_BIN_DIR:-$HOME/.local/bin}"
codex_config_home="${CODEX_HOME:-$HOME/.codex}"
claude_config_home="$HOME/.claude"
workbuddy_home="${ANYLOVER_WORKBUDDY_HOME:-$HOME/.workbuddy}"
python_bin="${ANYLOVER_PYTHON:-python3}"
companion_name="${ANYLOVER_COMPANION_NAME:-Any}"
agent_mode="auto"
force_agent_config=0
dry_run=0

usage() {
  cat <<'EOF'
AnyLover one-click installer

Usage:
  ./install.sh [options]

Options:
  --agent auto|all|codex|claude|workbuddy|none
                              Agent target. Default: auto-detect installed agents.
  --name NAME                 Initial companion name. Default: Any.
  --install-root PATH         Private runtime location.
  --force-agent-config        Replace an existing AnyLover MCP entry.
  --dry-run                   Show the installation plan without writing files.
  -h, --help                  Show this help.

Environment overrides:
  ANYLOVER_INSTALL_ROOT, ANYLOVER_BIN_DIR, ANYLOVER_PYTHON,
  ANYLOVER_WORKBUDDY_HOME, ANYLOVER_HOME, ANYLOVER_DB.
  Codex honors its standard CODEX_HOME setting.
EOF
}

info() {
  printf '[AnyLover] %s\n' "$*"
}

warn() {
  printf '[AnyLover] Warning: %s\n' "$*" >&2
}

die() {
  printf '[AnyLover] Error: %s\n' "$*" >&2
  exit 1
}

while (($#)); do
  case "$1" in
    --agent)
      (($# >= 2)) || die "--agent requires a value"
      agent_mode="$2"
      shift 2
      ;;
    --name)
      (($# >= 2)) || die "--name requires a value"
      companion_name="$2"
      shift 2
      ;;
    --install-root)
      (($# >= 2)) || die "--install-root requires a value"
      install_root="$2"
      shift 2
      ;;
    --force-agent-config)
      force_agent_config=1
      shift
      ;;
    --dry-run)
      dry_run=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "unknown option: $1"
      ;;
  esac
done

case "$agent_mode" in
  auto|all|codex|claude|workbuddy|none) ;;
  *) die "unsupported --agent value: $agent_mode" ;;
esac

[[ -f "$script_dir/pyproject.toml" ]] || die "run this installer from the AnyLover source package"

wants_agent() {
  local target="$1"
  case "$agent_mode:$target" in
    all:*) return 0 ;;
    codex:codex|claude:claude|workbuddy:workbuddy) return 0 ;;
    auto:codex) command -v codex >/dev/null 2>&1 ;;
    auto:claude) command -v claude >/dev/null 2>&1 ;;
    auto:workbuddy) [[ -d "$workbuddy_home" ]] ;;
    *) return 1 ;;
  esac
}

describe_targets() {
  local targets=()
  local output=""
  local target
  wants_agent codex && targets+=("Codex/ChatGPT desktop")
  wants_agent claude && targets+=("Claude Code")
  wants_agent workbuddy && targets+=("WorkBuddy")
  if ((${#targets[@]} == 0)); then
    printf 'runtime only'
  else
    for target in "${targets[@]}"; do
      [[ -z "$output" ]] || output+=", "
      output+="$target"
    done
    printf '%s' "$output"
  fi
}

venv_dir="$install_root/venv"
runtime_python="$venv_dir/bin/python"
anylover_cli="$venv_dir/bin/anylover"
anylover_mcp="$venv_dir/bin/anylover-mcp"
skill_source="$script_dir/integrations/anylover-companion/skills/anylover-companion"

if ((dry_run)); then
  info "Dry run; no files will be changed."
  info "Runtime: $install_root"
  info "Agents: $(describe_targets)"
  info "Companion: $companion_name"
  info "MCP command: $anylover_mcp"
  exit 0
fi

command -v "$python_bin" >/dev/null 2>&1 || die "Python 3.11 or newer is required"
"$python_bin" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
  || die "Python 3.11 or newer is required"

info "Installing the private runtime at $install_root"
mkdir -p "$install_root"
if [[ ! -x "$runtime_python" ]]; then
  "$python_bin" -m venv "$venv_dir"
fi
"$runtime_python" -m pip install --upgrade "$script_dir"
"$runtime_python" -m pip check

mkdir -p "$bin_dir"
install_link() {
  local target="$1"
  local link_path="$2"
  if [[ -L "$link_path" ]] && [[ "$(readlink "$link_path")" == "$target" ]]; then
    return
  fi
  if [[ -e "$link_path" || -L "$link_path" ]]; then
    warn "$link_path already exists; keeping it. Use $target directly."
    return
  fi
  ln -s "$target" "$link_path"
}
install_link "$anylover_cli" "$bin_dir/anylover"
install_link "$anylover_mcp" "$bin_dir/anylover-mcp"

configured_db="${ANYLOVER_DB:-${ANYLOVER_HOME:-$HOME/.anylover}/anylover.sqlite3}"
if [[ ! -f "$configured_db" ]]; then
  info "Creating the local companion profile '$companion_name'"
  "$anylover_cli" init --name "$companion_name" >/dev/null
else
  info "Existing local companion data found; leaving it unchanged."
fi

install_skill() {
  local target="$1"
  local target_parent
  local backup_path
  target_parent="$(dirname "$target")"
  mkdir -p "$target_parent"
  if [[ -d "$target" ]]; then
    if diff -qr "$skill_source" "$target" >/dev/null 2>&1; then
      info "Skill already current: $target"
      return
    fi
    backup_path="${target}.backup-$(date -u +%Y%m%dT%H%M%SZ)-$$"
    cp -R "$target" "$backup_path"
    info "Backed up the previous skill to $backup_path"
  fi
  mkdir -p "$target"
  cp -R "$skill_source/." "$target/"
  info "Installed skill: $target"
}

register_codex() {
  install_skill "$codex_config_home/skills/anylover-companion"
  if ! command -v codex >/dev/null 2>&1; then
    warn "Codex CLI was not found; the skill is installed but MCP registration was skipped."
    return
  fi
  if codex mcp get anylover >/dev/null 2>&1; then
    if ((force_agent_config)); then
      codex mcp remove anylover
    else
      warn "Codex already has an 'anylover' MCP entry; keeping it. Pass --force-agent-config to replace it."
      return
    fi
  fi
  codex mcp add anylover -- "$anylover_mcp"
  info "Registered AnyLover with Codex and ChatGPT desktop."
}

register_claude() {
  install_skill "$claude_config_home/skills/anylover-companion"
  if ! command -v claude >/dev/null 2>&1; then
    warn "Claude Code was not found; the skill is installed but MCP registration was skipped."
    return
  fi
  if claude mcp get anylover >/dev/null 2>&1; then
    if ((force_agent_config)); then
      claude mcp remove anylover
    else
      warn "Claude Code already has an 'anylover' MCP entry; keeping it. Pass --force-agent-config to replace it."
      return
    fi
  fi
  claude mcp add --scope user anylover -- "$anylover_mcp"
  info "Registered AnyLover with Claude Code."
}

register_workbuddy() {
  local -a merge_args
  local merge_output
  install_skill "$workbuddy_home/skills/anylover-companion"
  merge_args=(
    "$runtime_python"
    "$script_dir/scripts/merge_mcp_config.py"
    --file "$workbuddy_home/.mcp.json"
    --name anylover
    --command "$anylover_mcp"
  )
  if ((force_agent_config)); then
    merge_args+=(--replace)
  fi
  if merge_output="$("${merge_args[@]}")"; then
    info "WorkBuddy MCP configuration: $merge_output"
  else
    warn "WorkBuddy already has a different 'anylover' entry; keeping it. Pass --force-agent-config to replace it."
  fi
}

wants_agent codex && register_codex
wants_agent claude && register_claude
wants_agent workbuddy && register_workbuddy

info "Installation complete for: $(describe_targets)"
info "Your local data stays in ${ANYLOVER_HOME:-$HOME/.anylover}"
info "Restart the installed Agent apps. Personal and companion conversations will retrieve relevant AnyLover context automatically."
case ":$PATH:" in
  *":$bin_dir:"*) ;;
  *) warn "$bin_dir is not on PATH. Agent integrations still work; add it to PATH for direct 'anylover' CLI use." ;;
esac
