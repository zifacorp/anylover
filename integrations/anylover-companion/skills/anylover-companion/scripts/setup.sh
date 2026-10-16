#!/usr/bin/env bash
# Install only the shared runtime; never edit an agent's configuration.
set -Eeuo pipefail

install_root="${ANYLOVER_INSTALL_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/anylover-runtime}"
python_bin="${ANYLOVER_PYTHON:-python3}"
package_source="${ANYLOVER_SOURCE:-git+https://github.com/zifacorp/anylover.git}"
dry_run=0

while (($#)); do
  case "$1" in
    --source)
      [[ $# -ge 2 && -n "$2" ]] || { printf '%s\n' '--source requires a package path or Git URL' >&2; exit 2; }
      package_source="$2"
      shift 2
      ;;
    --dry-run) dry_run=1; shift ;;
    -h|--help)
      printf '%s\n' 'Usage: bash scripts/setup.sh [--source PATH_OR_GIT_URL] [--dry-run]' \
        'Requires Bash, Python 3.11+, and Git for the default GitHub source.' \
        'Overrides: ANYLOVER_INSTALL_ROOT, ANYLOVER_PYTHON, ANYLOVER_SOURCE, ANYLOVER_HOME, ANYLOVER_DB.'
      exit 0
      ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; exit 2 ;;
  esac
done

runtime_python="$install_root/venv/bin/python"
runtime_cli="$install_root/venv/bin/anylover"
if ((dry_run)); then
  printf '[AnyLover] Dry run; no files will be changed.\nRuntime: %s\nSource: %s\nCLI: %s\n' \
    "$install_root" "$package_source" "$runtime_cli"
  exit 0
fi

command -v "$python_bin" >/dev/null 2>&1 || { printf '%s\n' 'Python 3.11+ is required.' >&2; exit 1; }
"$python_bin" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' \
  || { printf '%s\n' 'Python 3.11+ is required.' >&2; exit 1; }
if [[ "$package_source" == git+* ]]; then
  command -v git >/dev/null 2>&1 || { printf '%s\n' 'Git is required for this package source.' >&2; exit 1; }
fi

mkdir -p "$install_root"
if [[ ! -x "$runtime_python" ]]; then
  "$python_bin" -m venv "$install_root/venv"
fi
"$runtime_python" -m pip install --upgrade "$package_source"
"$runtime_python" -m pip check
# Showing the profile initializes a missing one, but never overwrites an existing one.
"$runtime_cli" companion
printf '\n[AnyLover] Runtime ready. Use this absolute path (no PATH change needed):\n%s\n' "$runtime_cli"
