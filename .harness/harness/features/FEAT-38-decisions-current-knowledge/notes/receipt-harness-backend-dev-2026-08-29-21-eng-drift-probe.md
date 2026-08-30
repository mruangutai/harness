# Receipt — harness-backend-dev — FEAT-38 — S2 drift-detector probe — 2026-08-29-21

## Setup (disposable /tmp copy, recipe from qa-2026-08-29-11-validator-c2.md §B)

```
WT=/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-38-decisions-current-knowledge
git -C "$WT" rev-parse HEAD          # 99bb52cc5f84b75f8b61636efbdfce79d057387b
mkdir -p /tmp/feat38-probe
git -C "$WT" archive HEAD | tar -x -C /tmp/feat38-probe
cd /tmp/feat38-probe && git init -q && git add -A && git -c user.email=t@t -c user.name=t commit -q -m tmp
```
Result: commit `56c9c07`, working copy healthy (git index materialized so `check-decision-anchors.py`'s
`git ls-files` subprocess calls succeed instead of failing with exit 128, per the cited recipe's §B
finding). Baseline copy also tarred to `/tmp/feat38-probe-baseline.tgz` for state-4's reset.

All commands below run with `cwd=/tmp/feat38-probe`, invoking
`bash .claude/skills/harness/bin/run-unit-tests.sh …`. No command touches the real worktree.

## Predictions (written before any state past 0 was run)

- **State 0** (no edits): exit 0, `check-kinds: ... agree.` on stdout. This just confirms the copy is
  healthy.
- **State 1** (T-24 only — array entry removed from `run-unit-tests.sh`, files left on disk,
  `harness.json` untouched): predict **exit 2** on both `--check-kinds` and `--kind integration`,
  because `test-check-decision-claims.py` is still on disk under `BIN_DIR` and the file-presence
  detector (lines 61-74) iterates `$BIN_DIR/test-*.py` and checks membership in `ALL_SCRIPTS`
  (union of both arrays) — independent of `harness.json` and independent of `--kind`/`--check-kinds`,
  and it runs *before* the `--check-kinds` early exit (line 142) and before the kind-drift check
  reaches line 96. Predict `MISCONFIGURED:` present, `KIND-DRIFT:` absent (detector never reached —
  the script exits at line 72 first), and `PASS test-check-decision-anchors.py` absent (test loop at
  line 147 never reached either).
- **State 2** (+ T-25 — path also removed from `harness.json`'s `detect` string, files still on disk):
  predict **exit 2, unchanged from state 1** — the file-presence detector reads only `BIN_DIR` and
  `ALL_SCRIPTS`, never `harness.json`, so removing the path from `harness.json` cannot satisfy it.
  Predict `MISCONFIGURED:` present, same as state 1.
- **State 3** (+ T-26 — both files deleted): predict **exit 0** for both `--check-kinds` and
  `--kind integration`. The glob at line 61 no longer matches the deleted file, so the presence
  detector is silent; the kind-drift check no longer has the name in either array or in `detect`, so
  it agrees. Predict `MISCONFIGURED:`/`KIND-DRIFT:` both absent, `check-kinds: ... agree.` present for
  (a), and `PASS test-check-decision-anchors.py` present for (b) (that script is untouched and still
  in `INTEGRATION_SCRIPTS`).
- **State 4** (remedy — array removal + both file deletions in ONE step, `harness.json` left
  untouched, naming the path in `detect` for a script that no longer exists): predict **exit 0** for
  both commands. Presence detector: file absent from disk, glob doesn't match — silent. Kind-drift
  check only asserts (a) every `INTEGRATION_SCRIPTS` name has a matching `detect` entry and (b) no
  `UNIT_SCRIPTS` name appears in `detect` — it never asserts the reverse (that every `detect` entry
  names a script still in one of the arrays), so a stale, no-longer-referenced `detect` entry is
  invisible to it. Predict both checks pass, `check-kinds: ... agree.` on stdout, `PASS
  test-check-decision-anchors.py` present in the integration run.

**Net predicted conclusion**: the plan's own T-24→T-25→T-26 order produces two full runner exit-2
states (state 1 and state 2) that its own ordering rationale does not mention, confirming the eng
lead's belief. The remedy (single atomic step combining the array edit and both file deletions,
independent of when `harness.json` is edited) stays green throughout.

## Measured results
### State 0 — baseline
```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
check-kinds: the script arrays and test_kinds.integration.detect agree.
EXIT=0
```
Matches prediction. Copy is healthy — no fix needed.

### State 1 — T-24 only (array entry removed, files still on disk, harness.json untouched)
(a) `--check-kinds`:
```
MISCONFIGURED: .claude/skills/harness/bin/test-check-decision-claims.py is not in run-unit-tests.sh's explicit script list
STATE1a_EXIT=2
```
(b) `--kind integration` (output captured to a shell variable, not piped):
```
MISCONFIGURED: .claude/skills/harness/bin/test-check-decision-claims.py is not in run-unit-tests.sh's explicit script list
STATE1b_EXIT=2
```
`^MISCONFIGURED:` count = 1, `^KIND-DRIFT:` count = 0, `^PASS test-check-decision-anchors\.py$` count = 0.
**Matches prediction exactly.** T-24's own verify block (exit 0, no MISCONFIGURED, no KIND-DRIFT,
`PASS test-check-decision-anchors.py` present) is FALSE at this state — the whole runner is exit 2,
every kind, before any test runs. This is the mechanism the plan's ordering rationale never named.

### State 2 — + T-25 (path also removed from harness.json's detect; files still on disk)
```
$ bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds
MISCONFIGURED: .claude/skills/harness/bin/test-check-decision-claims.py is not in run-unit-tests.sh's explicit script list
STATE2_EXIT=2
```
**Matches prediction exactly — unchanged from state 1.** Editing harness.json cannot satisfy the
file-presence detector, which never opens harness.json. T-25's verify ("exits 0") is FALSE here too.

### State 3 — plan's END state (+ T-26, both files deleted)
(a) `--check-kinds`:
```
check-kinds: the script arrays and test_kinds.integration.detect agree.
STATE3a_EXIT=0
```
(b) `--kind integration` (captured to a variable; full integration suite, ~155s, ends at line 1961
of output):
```
STATE3b_EXIT=0
^MISCONFIGURED: count = 0
^KIND-DRIFT: count = 0
^PASS test-check-decision-anchors\.py$ count = 1  (line 1961: "PASS test-check-decision-anchors.py")
^FAIL  count = 0
```
**Matches prediction exactly.** The plan's declared end state is green on both detectors, confirming
the removal itself is sound — the defect is only in the T-24→T-25→T-26 *interval*, not the outcome.

### State 4 — the lead's proposed remedy (array removal + BOTH file deletions in one step; reset to
baseline first via `rm -rf /tmp/feat38-probe && tar xzf baseline.tgz`, confirmed 0-line
`git status --porcelain` and both refs present before re-applying; harness.json left untouched,
still naming `.claude/skills/harness/bin/test-check-decision-claims.py` in `detect` — confirmed
`grep -c` = 1 on the stale path after the edit, and `ls … | grep decision-claims` exit 1 confirming
both files gone)
(a) `--check-kinds`:
```
check-kinds: the script arrays and test_kinds.integration.detect agree.
STATE4a_EXIT=0
```
(b) `--kind integration` (captured to a variable, full suite, ~155s):
```
STATE4b_EXIT=0
^MISCONFIGURED: count = 0
^KIND-DRIFT: count = 0
^PASS test-check-decision-anchors\.py$ count = 1
^FAIL  count = 0
```
**Matches prediction exactly.** The kind-drift check only asserts that every `INTEGRATION_SCRIPTS`
name has a matching `detect` entry and no `UNIT_SCRIPTS` name is in `detect` — it never asserts the
reverse (every `detect` entry names a script still in one of the arrays), so a `detect` entry left
dangling for a deleted, no-longer-listed script is invisible to it. Combining the array edit with
both file deletions in one atomic step — regardless of when harness.json is separately touched —
never exposes the interval where the file-presence detector trips.

## Prediction accuracy
All five states landed exactly as predicted before running; no prediction was wrong. The measurement
confirms the eng lead's belief: the plan's T-24→T-25→T-26 order (each committed independently, as a
real land-per-task sequence would do) produces two full-suite exit-2 states — after T-24 alone, and
after T-24+T-25 — that only clear once T-26 lands. The remedy that stays green throughout is folding
the `INTEGRATION_SCRIPTS` array edit and both `git rm`s into a single atomic step; the ordering of the
harness.json edit relative to that step does not matter to either detector.

## Real-worktree integrity
```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/BRIEF.md
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/observations/harness-pm.md
 M .harness/harness/features/FEAT-38-decisions-current-knowledge/plan.yaml
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-ai-dev-2026-08-29-21-eng-simplify-altitude.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-21-eng-drift-probe.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-backend-dev-2026-08-29-21-eng-simplify-reuse.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-data-engineer-2026-08-29-21-eng-simplify-efficiency.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/receipt-harness-dev-ops-2026-08-29-21-eng-simplify-simplification.md
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/notes/review-harness-ui-reviewer-replan.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/grilling-remove-executable-claims-2026-08-29.md
```
The `M` and `??` entries above other than this receipt are from concurrent sibling agents (pm,
ai-dev, dev-ops, data-engineer, ui-reviewer) working the same feature in parallel — I did not touch
BRIEF.md, plan.yaml, observations/harness-pm.md, logs, or any other agent's receipt/note. The only
path I wrote inside the worktree is this receipt, at the path this dispatch and the handoff contract
grant me. Every mutation for the probe itself happened under `/tmp/feat38-probe` (now removed) and
`/tmp/feat38-probe-baseline.tgz` (also removed) — zero paths under the worktree were used for any
edit, deletion, `git add`, or git-state change during the probe.

