#!/usr/bin/env bash
set -uo pipefail
# THE ROOT COMES FROM THIS SCRIPT'S OWN LOCATION, never from the environment and never from
# the caller's cwd (FEAT-42 T-03). What stood here was a cd through the two-name environment
# chain with a pwd fallback, and that fallback is why a suite invoked from anywhere ran against
# whatever checkout the caller happened to be standing in, exited 0, and reported green for the
# wrong tree. No gate in this repository can see that. Do not name the old variables here even
# in prose: the invariant that keeps them gone counts the name in every tracked source file.
# REFUSING IS THE POINT — there is deliberately no fallback.
_SELF_BIN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_ROOT="$(python3 -I -c 'import sys; sys.path.insert(0, sys.argv[1]); import harness_boundary; print(harness_boundary.resolve_root(sys.argv[1]))' "$_SELF_BIN" 2>/dev/null)"
if [ -z "$_ROOT" ] || [ ! -d "$_ROOT" ]; then
  echo "run-unit-tests.sh: no harness root could be resolved from $_SELF_BIN — refusing to run" >&2
  exit 2
fi
cd "$_ROOT" || exit 2

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
UNIT_SCRIPTS=("test-harness-yaml-corpus.py" "test-render-brief.py" "test-team-catalog.py" "test-factory-cli.py" "test-factory-gh.py" "test-factory-config.py" "test-factory-workspace.py" "test-factory-decompose.py" "test-factory-claim.py" "test-factory-land.py" "test-no-distribution.py" "test-validate-feature-json.py" "test-gh-board.py" "test-branch-create-gate.py" "test-layout-migration.py" "test-board-station.py" "test-inject-expertise.py" "test-gh-cost-log.py" "test-board-lifecycle.py" "test-orchestrator-playbook.py" "test-lead-stop-and-wake.py" "test-omp-hooks.py" "test-check-omp-port.py" "test-sync-agent-adapters.py" "test-harness-boundary.py" "test-wayfind.py" "test-feature-json-merge.py" "test-panel-findings.py" "test-plan-panel.py" "test-code-grade.py" "test-gate-policy.py" "test-check-fixture-secrets.py" "test-suite-independence.py")
INTEGRATION_SCRIPTS=("test-validate-digest.py" "test-gh-sync.py" "test-check-state.py" "test-check-expertise.py" "test-gen-decisions-index.py" "test-bash-write-guard.py" "test-check-domain.py" "test-harness-yaml.py" "test-upgrade-config.py" "test-check-plan-routes.py" "test-merge-settings.py" "test-factory-integration.py" "test-feature-worktree.py" "test-expertise-merge.py" "test-run-unit-tests-kinds.py" "test-harness-merge.py" "test-plan-merge.py" "test-observations-merge.py" "test-inflight-registry.py" "test-dispatch-guard.py" "test-merge-gitignore.py" "test-worktree-terminal.py" "test-post-merge-sweep.py" "test-hooks-install.py" "test-gh-close-gate.py" "test-plan-sign-gate.py" "test-code-grade-cli.py" "test-check-decision-anchors.py" "test-quarantine.py" "test-run-pool.py")

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

# PROBE DRIFT (issue #1187): a `probe-*.py` script under BIN_DIR is, by naming convention,
# deliberately excluded from the test-*.py sweep above and from both UNIT_SCRIPTS and
# INTEGRATION_SCRIPTS — it needs a real host and live credentials CI does not carry (DEC-201).
# That naming convention is exactly how it could go unregistered forever: nothing else in this
# file would ever notice. So every probe-*.py must appear in test_kinds.<some kind>.detect for
# a kind whose status is "locally_run", checked below alongside the kind cross-check.
shopt -s nullglob
PROBE_FILES=("$BIN_DIR"/probe-*.py)
shopt -u nullglob

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
  PROBE_LIST="$(printf '%s\n' "${PROBE_FILES[@]##*/}")" \
  python3 -I - <<'KINDCHECK'
import json, os, sys

path = os.environ["HARNESS_JSON"]
try:
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    kinds = doc["test_kinds"]
    detect = kinds["integration"]["detect"]
    if not isinstance(detect, str):
        raise TypeError("integration.detect is %s, not a string" % type(detect).__name__)
except Exception as e:
    print("KIND-DRIFT: cannot read %s: %s" % (path, e), file=sys.stderr)
    sys.exit(2)

PREFIX = ".claude/skills/harness/bin/"
declared = {p.strip() for p in detect.split("|") if p.strip()}
unit = [n for n in os.environ.get("UNIT_LIST", "").splitlines() if n.strip()]
integ = [n for n in os.environ.get("INTEGRATION_LIST", "").splitlines() if n.strip()]
probes = [n for n in os.environ.get("PROBE_LIST", "").splitlines() if n.strip()]

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

locally_run_declared = set()
for kind_name, kind in kinds.items():
    if not isinstance(kind, dict) or kind.get("status") != "locally_run":
        continue
    kind_detect = kind.get("detect")
    if not isinstance(kind_detect, str):
        print("KIND-DRIFT: test_kinds.%s has status locally_run but detect is %s, "
              "not a string" % (kind_name, type(kind_detect).__name__), file=sys.stderr)
        bad += 1
        continue
    locally_run_declared |= {p.strip() for p in kind_detect.split("|") if p.strip()}
for name in probes:
    if PREFIX + name not in locally_run_declared:
        print("KIND-DRIFT: %s exists under bin/ but is not registered in any "
              "test_kinds kind with status locally_run — it would be watched only "
              "by memory, never by name (issue #1187)" % name, file=sys.stderr)
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

# Bash owns kind selection; run_pool.py owns scheduling and attribution (D-05).
exec python3 "$BIN_DIR/run_pool.py" --mutation-check "$BIN_DIR" -- "${SCRIPTS[@]/#/$BIN_DIR/}"
