# QA re-run — BUG-1308 T-02 acceptance (independent, read-only)

**T-02's four named acceptance commands are all green in isolation. But an independent
full-suite run of `run-unit-tests.sh` in this same worktree exits 1 — a real, reproduced,
unrelated failure in `test-anchor-directions.py` — so this cannot be signed off PASS.**

Verified `plan.yaml` T-02 `verify:` block (lines 525-530) byte-for-byte against the dispatched
string before running — exact match, no paraphrase substituted.

## 1. T-02 verify block (`tests/integration/test-expertise-merge.py`)

- Command run exactly as specified (case-presence grep loop + `python3 "$I"`).
- **Exit code: 0**
- **PASS: 119, FAIL: 0** (counted via `grep -c '^PASS '` / `'^FAIL'` on captured stdout)
- No FAIL lines (none exist).
- Final summary line: `PASS test-expertise-merge.py`
- Wall-clock of run 1: **7s** (measured via `date +%s` bracket) / tool-reported wall time 6.10s
  on the timed invocation, 6.22s on the re-capture run. Case18's 2.0s lock-hold window is visible
  in its own line: `case18: neither child exits during the 2.0s hold window ... (2.00s observed)`.
  Total wall time is well under what "two 20s child waits" would imply if those were literal
  sleeps — the suite evidently does not block on full 20s timeouts in the passing path.

## 2. Unit suite (`tests/unit/test-expertise-ops.py`)

- **Exit code: 0**
- **PASS: 58, FAIL: 0**
- Final summary line: `PASS test-expertise-ops.py`
- Ran with `HARNESS_AGENT_TYPE` unset per repository-tier Expertise G-07 (avoids the unrelated
  `test-plan-merge.py` false regression); also ran once with it set as delivered by the harness —
  same result, exit 0.

## 3. Worktree `git status --porcelain`

```
 M .harness/harness/features/BUG-1308-expertise-replace-drop/feature.json
 M .harness/harness/features/BUG-1308-expertise-replace-drop/plan.yaml
 M tests/integration/test-expertise-merge.py
?? .harness/harness/features/BUG-1308-expertise-replace-drop/notes/qa-BUG-1308-T-02.md
?? .harness/harness/features/BUG-1308-expertise-replace-drop/observations/harness-qa.md
```

Only production/test file touched: `tests/integration/test-expertise-merge.py` (the T-02 target
itself). All other entries are `.harness/**` control-plane state (feature.json, plan.yaml,
notes/, observations/) and are expected/out of scope per the assignment. No unexpected
production/test file modified.

## 4. Main checkout `git status --porcelain -- tests/ .claude/skills/`

```
(empty)
```

Clean. No stray modification under `tests/` or `.claude/skills/` in the main checkout — the
prior session's reported accidental edit-and-revert of the stale main-checkout copy left no
trace.


## 5. Independent full-suite check (`run-unit-tests.sh`), discovered mid-gate

A separate automated check rejected an initial `VERDICT: PASS` submission from this session,
citing an independent re-run of `run-unit-tests.sh` exiting 1. Re-running it directly (read-only,
no fix attempted) confirms: **exit 1**, isolated to one failing script out of ~74:

```
----- test-anchor-directions.py (exit 1, 1.60s) -----
FAIL - reviewed-sha whole scope
VIOLATION .claude/skills/harness-distill/SKILL.md:130: unanchored instruction path:
  .claude/skills/harness/bin/expertise-merge.py
scanned 62 file(s), 1 violation(s)
FAIL test-anchor-directions.py
```

Root cause read directly (no edit made): `.claude/skills/harness-distill/SKILL.md:130` gives the
apply command as a bare relative path —
`python3 .claude/skills/harness/bin/expertise-merge.py ops --file <expertise file> --ops <path or ->`
— with no anchor (e.g. a `$(git rev-parse --show-toplevel)`-style prefix), which
`test-anchor-directions.py`'s reviewed-sha whole-scope check flags as an unanchored instruction path.

**This file is out of T-02's scope.** Per `plan.yaml`'s `lanes.rows`,
`.claude/skills/harness-distill/SKILL.md` is a `main-session-direct` surface (DEC-174 carve-out,
owned by T-03's contract-text work), not a T-02/`harness-qa` surface. I did not touch it, was not
asked to, and this assignment is explicitly read-only/fix-nothing. All other suite output (~4700
lines) is clean `ok`/`PASS`; this is the sole failure.

No command in this assignment (1-4 above) exercises or is affected by this file. The finding is
reported here because it is a real, currently-true, independently-reproduced defect in this
worktree that blocks an honest global PASS — even though remediation belongs to whoever owns the
T-03/main-session-direct SKILL.md edit, not to this T-02 gate.
## Verdict basis (revised)

All four of this assignment's named acceptance conditions (T-02's own scope) hold on their own
terms: commands 1 and 2 both exit 0 with matching PASS/FAIL counts; command 3 shows no unexpected
production/test file; command 4 is clean. This re-run did not reproduce the "VERDICT: PASS with
host process exit 1" contradiction the prior QA run reported for T-02 specifically.

However, an independently-verified, currently-reproducible full-suite failure exists in this same
worktree (`test-anchor-directions.py`, unrelated file, unrelated task). Per "verification is the
product" and "never falsify the record", VERDICT is FAIL, not PASS, until that is resolved — even
though the fix is out of this task's scope and belongs to T-03's owner, not to this T-02 gate.
