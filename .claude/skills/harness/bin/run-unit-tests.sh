#!/usr/bin/env bash
set -uo pipefail
_SELF_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_ROOT="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; print(harness_boundary.resolve_root(sys.argv[1]))' "$_SELF_BIN" 2>/dev/null)"
if [ -z "$_ROOT" ] || [ ! -d "$_ROOT" ]; then
  echo "run-unit-tests.sh: no harness root could be resolved from $_SELF_BIN — refusing to run" >&2
  exit 2
fi
cd "$_ROOT" || exit 2
BIN_DIR=".claude/skills/harness/bin"





KIND="all"
CHECK_LAYOUT_ONLY=0
if [ "${1:-}" = "--kind" ]; then
  KIND="${2:-all}"
elif [ "${1:-}" = "--check-layout" ]; then
  CHECK_LAYOUT_ONLY=1
elif [ -n "${1:-}" ]; then
  echo "usage: run-unit-tests.sh [--kind unit|integration|all] [--check-layout]" >&2
  exit 2
fi
case "$KIND" in
  unit) SCRIPTS=(tests/unit/test-*.py) ;;
  integration) SCRIPTS=(tests/integration/test-*.py) ;;
  all) SCRIPTS=(tests/unit/test-*.py tests/integration/test-*.py) ;;
  *) echo "run-unit-tests.sh: unknown kind '$KIND' — use unit, integration or all" >&2; exit 2 ;;
esac

layout_out="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import suite_layout; [print(v) for v in suite_layout.violations(sys.argv[2])]' "$BIN_DIR" "$_ROOT" 2>&1)"
layout_status=$?
if [ "$layout_status" -ne 0 ]; then
  echo "MISCONFIGURED: layout check crashed: $layout_out" >&2
  exit 2
fi
if [ -n "$layout_out" ]; then
  while IFS= read -r line; do echo "MISCONFIGURED: $line" >&2; done <<< "$layout_out"
  exit 2
fi
if [ "$CHECK_LAYOUT_ONLY" -eq 1 ]; then
  exit 0
fi

exec python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]}"
