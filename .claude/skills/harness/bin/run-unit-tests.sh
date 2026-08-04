#!/usr/bin/env bash
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

BIN_DIR=".claude/skills/harness/bin"
SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-render-brief.py" "test-cost-report.py" "test-harness-yaml.py" "test-harness-yaml-corpus.py" "test-upgrade-config.py" "test-team-catalog.py")

# Drift detector: any test-*.py under BIN_DIR not in the explicit list is misconfigured.
for f in "$BIN_DIR"/test-*.py; do
  base="$(basename "$f")"
  listed=0
  for s in "${SCRIPTS[@]}"; do
    if [ "$s" = "$base" ]; then
      listed=1
      break
    fi
  done
  if [ "$listed" -eq 0 ]; then
    echo "MISCONFIGURED: $f is not in run-unit-tests.sh's explicit script list" >&2
    exit 2
  fi
done

failures=0
for s in "${SCRIPTS[@]}"; do
  python3 "$BIN_DIR/$s"
  status=$?
  if [ "$status" -eq 0 ]; then
    echo "PASS $s"
  else
    echo "FAIL $s"
    failures=$((failures + 1))
  fi
done

if [ "$failures" -gt 0 ]; then
  exit 1
fi
exit 0
