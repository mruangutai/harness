#!/usr/bin/env bash
# PreToolUse Bash gate: a merge may not bypass a owed Build-entry receipt (DEC-138).
set -uo pipefail
_selfbin="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
root="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; print(harness_boundary.resolve_root(sys.argv[1]))' "$_selfbin" 2>/dev/null)"
if [ -z "$root" ] || [ ! -d "$root" ]; then
  echo "merge-gate.sh: no harness root could be resolved from $_selfbin — refusing to run" >&2
  exit 2
fi
exec python3 "$(dirname "$0")/merge-gate.py" "$root"
