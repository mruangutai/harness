#!/usr/bin/env bash
set -uo pipefail
cd "${HARNESS_PROJECT_DIR:-${CLAUDE_PROJECT_DIR:-$(pwd)}}"

BIN_DIR=".agents/skills/harness/bin"
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
UNIT_SCRIPTS=("test-harness-yaml-corpus.py" "test-render-brief.py" "test-team-catalog.py" "test-factory-cli.py" "test-factory-gh.py" "test-factory-config.py" "test-factory-workspace.py" "test-factory-decompose.py" "test-factory-claim.py" "test-factory-land.py" "test-no-distribution.py" "test-validate-feature-json.py" "test-gh-board.py" "test-branch-create-gate.py" "test-layout-migration.py" "test-board-station.py" "test-inject-expertise.py" "test-gh-cost-log.py" "test-context-watch.py" "test-board-lifecycle.py" "test-orchestrator-playbook.py" "test-omp-hooks.py" "test-check-omp-port.py" "test-sync-agent-adapters.py")
INTEGRATION_SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-harness-yaml.py" "test-upgrade-config.py" "test-check-plan-routes.py" "test-merge-settings.py" "test-factory-integration.py" "test-feature-worktree.py" "test-expertise-merge.py" "test-context-watch-cli.py" "test-context-watch-hook.py" "test-run-unit-tests-kinds.py" "test-harness-merge.py" "test-plan-merge.py" "test-observations-merge.py" "test-inflight-registry.py" "test-dispatch-guard.py" "test-merge-gitignore.py" "test-worktree-terminal.py" "test-post-merge-sweep.py" "test-hooks-install.py")

# --kind DEFAULTS TO all, so every existing caller — harness.json, a human, a QA agent —
# keeps the behaviour it had before this split.
KIND="all"
CHECK_KINDS_ONLY=0
if [ "${1:-}" = "--kind" ]; then
  KIND="${2:-all}"
elif [ "${1:-}" = "--check-kinds" ]; then
  # Runs the drift detector and the kind cross-check, then exits, running NO tests. It
  # exists so the cross-check's own test cases cost milliseconds instead of driving the
  # ~15s suite. --kind keeps its exact previous behaviour and its default of all.
  CHECK_KINDS_ONLY=1
elif [ -n "${1:-}" ]; then
  echo "usage: run-unit-tests.sh [--kind unit|integration|all] [--check-kinds]" >&2
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

# --- KIND CROSS-CHECK (FEAT-31 T-12) ---------------------------------------------
# WHY THIS EXISTS. The drift detector above reads only the two bash arrays and NEVER opens
# harness.json, which is exactly how eight files came to sit in INTEGRATION_SCRIPTS while
# the qa matrix classified them as unit (D-18). Two lists that describe the same thing and
# cannot see each other will diverge, and the divergence is silent.
#
# IT IS A SET COMPARISON WITH NO GLOB CLASSIFIER IN IT, deliberately:
#   every INTEGRATION_SCRIPTS name must appear as the explicit literal path
#   .agents/skills/harness/bin/<name> among integration.detect's pipe-separated entries;
#   no UNIT_SCRIPTS name may appear there.
# Whether an explicit path beats a catch-all glob is an unanswered question for the
# operator, and a check resting on the answer would be built on an unwritten rule. So this
# asks only whether the two lists AGREE, never which kind a file "really" is.
#
# A MISSING OR UNPARSEABLE CONFIG IS A LOUD FAILURE, never a skip. tests.yml runs this as a
# required step, and a silent skip inside a required step is a green suite that verified
# nothing.
#
# It runs on EVERY invocation and for every --kind including all, for the same reason the
# drift detector runs over the union: a mismatch must not be skippable by choosing a kind.
HARNESS_JSON="${HARNESS_JSON:-.harness/harness.json}"
kind_drift_out="$(
  HARNESS_JSON="$HARNESS_JSON" \
  UNIT_LIST="$(printf '%s\n' "${UNIT_SCRIPTS[@]}")" \
  INTEGRATION_LIST="$(printf '%s\n' "${INTEGRATION_SCRIPTS[@]}")" \
  python3 - <<'KINDCHECK'
import json, os, sys

path = os.environ["HARNESS_JSON"]
try:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    detect = doc["test_kinds"]["integration"]["detect"]
    if not isinstance(detect, str):
        raise TypeError("integration.detect is %s, not a string" % type(detect).__name__)
except Exception as e:
    print("KIND-DRIFT: cannot read %s: %s" % (path, e), file=sys.stderr)
    sys.exit(2)

PREFIX = ".agents/skills/harness/bin/"
declared = {p.strip() for p in detect.split("|") if p.strip()}
unit = [n for n in os.environ.get("UNIT_LIST", "").splitlines() if n.strip()]
integ = [n for n in os.environ.get("INTEGRATION_LIST", "").splitlines() if n.strip()]

bad = 0
for name in integ:
    if PREFIX + name not in declared:
        print("KIND-DRIFT: %s is in INTEGRATION_SCRIPTS but absent from "
              "test_kinds.integration.detect" % name, file=sys.stderr)
        bad += 1
for name in unit:
    if PREFIX + name in declared:
        print("KIND-DRIFT: %s is in UNIT_SCRIPTS but present in "
              "test_kinds.integration.detect" % name, file=sys.stderr)
        bad += 1
sys.exit(2 if bad else 0)
KINDCHECK
)" 2>&1
kind_drift_status=$?
if [ -n "$kind_drift_out" ]; then
  printf '%s\n' "$kind_drift_out" >&2
fi
if [ "$kind_drift_status" -ne 0 ]; then
  exit 2
fi

if [ "$CHECK_KINDS_ONLY" -eq 1 ]; then
  echo "check-kinds: the script arrays and test_kinds.integration.detect agree."
  exit 0
fi

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
