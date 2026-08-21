#!/usr/bin/env bash
set -uo pipefail
cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

BIN_DIR=".claude/skills/harness/bin"
# THE SPLIT IS BY WHAT IS TESTED, NOT BY THE CLOCK (issue #160). A runtime threshold
# drifts and teaches people to bump it; "does this drive a real script end to end?" does
# not. Measured when this landed: 3 files never spawn a subprocess (~0.33s total), 11 do
# (~15.6s). The spread does NOT track the fork line — test-check-state.py forks once and
# takes 1.21s, test-merge-settings.py forks twice and takes 0.12s — which is exactly why
# the principle is the discriminator and the timing is only evidence for it.
#
# Forking the real script is the RIGHT technique for testing a PreToolUse hook; a mocked
# check-domain.sh would prove nothing. Nothing here is being called a bad test. The problem
# #160 records is one populated kind doing two jobs while test_kinds.integration sat null,
# so INV-20 could never see the hole and the qa matrix could not tell the two apart.
UNIT_SCRIPTS=("test-harness-yaml-corpus.py" "test-render-brief.py" "test-team-catalog.py" "test-factory-cli.py" "test-factory-gh.py" "test-factory-config.py" "test-factory-workspace.py" "test-factory-decompose.py" "test-factory-claim.py" "test-factory-land.py" "test-no-distribution.py" "test-validate-feature-json.py" "test-gh-board.py" "test-branch-create-gate.py" "test-layout-migration.py" "test-board-station.py" "test-inject-expertise.py" "test-gh-cost-log.py" "test-context-watch.py")
INTEGRATION_SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-harness-yaml.py" "test-upgrade-config.py" "test-check-plan-routes.py" "test-merge-settings.py" "test-factory-integration.py" "test-feature-worktree.py" "test-expertise-merge.py")

# --kind DEFAULTS TO all, so every existing caller — harness.json, a human, a QA agent —
# keeps the behaviour it had before this split.
KIND="all"
if [ "${1:-}" = "--kind" ]; then
  KIND="${2:-all}"
elif [ -n "${1:-}" ]; then
  echo "usage: run-unit-tests.sh [--kind unit|integration|all]" >&2
  exit 2
fi
case "$KIND" in
  unit)        SCRIPTS=("${UNIT_SCRIPTS[@]}") ;;
  integration) SCRIPTS=("${INTEGRATION_SCRIPTS[@]}") ;;
  all)         SCRIPTS=("${UNIT_SCRIPTS[@]}" "${INTEGRATION_SCRIPTS[@]}") ;;
  *) echo "run-unit-tests.sh: unknown kind '$KIND' — use unit, integration or all" >&2; exit 2 ;;
esac

# The drift detector runs over the UNION, never the selected subset: a file missing from
# both arrays must be caught whichever kind is being run, or `--kind unit` becomes a way to
# skip the check that a new test file was registered at all.
ALL_SCRIPTS=("${UNIT_SCRIPTS[@]}" "${INTEGRATION_SCRIPTS[@]}")

# Drift detector: any test-*.py under BIN_DIR not in the explicit list is misconfigured.
for f in "$BIN_DIR"/test-*.py; do
  base="$(basename "$f")"
  listed=0
  for s in "${ALL_SCRIPTS[@]}"; do
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
