# Receipt — harness-dev-ops — FEAT-23 V-01 independent re-verification of T-01 and T-05

Read-only run. No source file edited, no file created except this receipt. No git add/commit/checkout/stash, no gh command.

## Result: all five checks agree with the reported PASS. No disagreement found.

## 1. Working tree, unfiltered (`git status --porcelain`)

```
 M .claude/skills/harness/bin/run-unit-tests.sh
 M .harness/harness/features/FEAT-23-ship-flow-fixes/feature.json
 M .harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-orchestrator.md
?? .claude/skills/harness/bin/board-station.py
?? .claude/skills/harness/bin/test-board-station.py
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-code-reviewer-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-qa-premerge.md
?? .harness/harness/features/FEAT-20-migration-detector/notes/review-harness-security-reviewer-premerge.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-code-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-qa-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/notes/review-harness-security-reviewer-2026-08-15-rereview.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-qa.md
?? .harness/harness/features/FEAT-21-features-layout-migration/observations/harness-validator-lead.md
?? .harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-backend-dev-T-05-c1.md
```

Note: 3 files here are *modified* (`M`), not just untracked — `.claude/skills/harness/bin/run-unit-tests.sh`,
`.harness/harness/features/FEAT-23-ship-flow-fixes/feature.json`, and
`.harness/harness/features/FEAT-23-ship-flow-fixes/observations/harness-orchestrator.md`. These are
consistent with T-05's work (registering `test-board-station.py` in the drift detector) plus normal
feature bookkeeping, not with anything I ran — I made no writes. Flagging for the record since the dispatch
only pre-warned about untracked `.harness/**` notes, not modified files.

## 2. T-01's verify — extracted and piped to bash

Command (verbatim, from `plan.yaml`):
```
out=$(python3 .claude/skills/harness/bin/test-gh-sync.py 2>&1); rc=$?
say() { printf '%s\n' "$out"; }
say | grep -qF "ok    ship records feature.json status Done" || { echo "T-01: the ship status case did not pass or did not run"; exit 1; }
say | grep -qF "ok    abandon records feature.json status Abandoned" || { echo "T-01: the abandon status case did not pass or did not run"; exit 1; }
say | grep -qF "ok    ship closes the milestone regardless of parent origin" || { echo "T-01: the pre-existing milestone case vanished"; exit 1; }
say | grep -qF "ok    ship leaves an adopted parent open" || { echo "T-01: the pre-existing adopted-parent case vanished"; exit 1; }
say | grep -E "^FAIL" && { echo "T-01: a case failed"; exit 1; }
test "$rc" = 0 || { echo "T-01: the suite exited $rc"; exit 1; }
echo "T-01 GREEN"
```

Output:
```
T-01 GREEN
```
Exit code: `0`. Agrees with the reported PASS.

## 3. T-05's verify — extracted and piped to bash

Command (verbatim, from `plan.yaml`):
```
B=.claude/skills/harness/bin/board-station.py
T=.claude/skills/harness/bin/test-board-station.py
R=.claude/skills/harness/bin/run-unit-tests.sh
test -f "$B" || { echo "T-05: $B does not exist"; exit 1; }
grep -qF "test-board-station.py" "$R" || { echo "T-05: the new test file is not registered in run-unit-tests.sh; the drift detector fails the WHOLE run and would redden every other task"; exit 1; }
out=$(python3 "$T" 2>&1); rc=$?
say() { printf '%s\n' "$out"; }
say | grep -qF "PASS  board-station moves the named issue to the named station" || { echo "T-05: the station-write case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station with no board configured writes nothing and exits 0" || { echo "T-05: the unconfigured-board case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station reports a BoardError on stderr naming issue and station and exits 0" || { echo "T-05: the board-failure case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station rejects a missing argument with exit 2" || { echo "T-05: the usage case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station outside a harness root writes nothing and exits 0" || { echo "T-05: the no-harness-root case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station with github.sync false writes nothing and exits 0" || { echo "T-05: the sync-off case did not pass or did not run"; exit 1; }
say | grep -qF "PASS  board-station exits 0 when set_station raises a non-BoardError exception" || { echo "T-05: the non-BoardError case did not pass or did not run"; exit 1; }
say | grep -E "^FAIL" && { echo "T-05: a case failed"; exit 1; }
test "$rc" = 0 || { echo "T-05: the suite exited $rc"; exit 1; }
u=$(bash "$R" --kind unit 2>&1) || { echo "T-05: the unit bucket is not green with the new file registered"; exit 1; }
echo "T-05 GREEN"
```

Output:
```
T-05 GREEN
```
Exit code: `0`. Agrees with the reported PASS.

## 4. Standing gate: `test-check-plan-routes.py`

```
cd /Users/molchairuangutai/GitHub/harness && python3 .claude/skills/harness/bin/test-check-plan-routes.py
```

Exit code: `0`. Final line: `ALL PASS`.

`case_20` lines, verbatim:
```
PASS case_20_bash_write_guard_sh_probes_the_manifest
PASS case_20_board_station_py_probes_the_manifest
PASS case_20_check_domain_sh_probes_the_manifest
PASS case_20_check_plan_routes_py_probes_the_manifest
PASS case_20_gh_sync_py_probes_the_manifest
PASS case_20_the_detector_is_not_blind
```

No FAIL lines anywhere in the output. `case_20_board_station_py_probes_the_manifest` is present and
**PASSes** — the standing gate the dispatch flagged as a risk (`board-station.py` tripping `case_20`'s
`.harness`-paired-with-a-filesystem-predicate check) is not currently red. This is a fact worth
surfacing prominently: the dispatch described this as a gate T-05's own verify cannot execute and did
not say whether it currently passes — it does, at HEAD, with the working tree exactly as `git status`
shows above.

## 5. Full suite, both buckets

```
cd /Users/molchairuangutai/GitHub/harness && bash .claude/skills/harness/bin/run-unit-tests.sh --kind all
```

Exit code: `0`.

No `^FAIL` line anywhere in the captured output (`grep -c '^FAIL'` = 0). 197 `PASS <file>`-style
per-test-file lines total. Representative final lines:
```
ok    (H) at least one gh call was recorded (anti-vacuum)
ok    (H) no recorded gh call names the other repository's board number
ok    (H) at least one recorded gh call names the served repository's own board number (proves the check above has power)

106/106 checks passed.
PASS test-factory-integration.py
```
(`test-factory-integration.py`, the integration bucket's last file, is the final line printed; the
runner has no single grand-total line spanning both buckets — each test file prints its own N/N line.)
Runtime: ~1m21s (`time` output: `48.56s user 17.13s system 81% cpu 1:21.05 total`), under the 5-minute
budget I used.

## Addendum — concurrent activity during this run

A final `git status --porcelain` taken after writing this receipt shows an additional untracked file
that was not present in section 1's snapshot: `.harness/harness/features/FEAT-23-ship-flow-fixes/notes/receipt-harness-backend-dev-T-05-c2.md`.
It appeared mid-run from concurrent activity elsewhere in the same working tree — no tracked file
changed, and no result above is affected by it, but the tree was not perfectly static for the duration
of an "independent" verification window and the eng lead should know that.

## Bypass question — does any test in `test-board-station.py` reach the real `gh` or real board?

**No.** Every one of the 7 test cases calls `run(tmp, args, ...)` (lines 137, 156, 168, 180–182, 193,
205, 217 of `.claude/skills/harness/bin/test-board-station.py`), and `run()` (defined lines 109–127)
sets both `env["FACTORY_GH"]` and `env["GH_SYNC_GH"]` (lines 116–117) to the same fake-`gh` script path
returned by `install_gh()` before invoking `board-station.py` as a subprocess. There is no direct
`subprocess.run` call anywhere else in the file, and no case constructs `env` independently of `run()`.
The module docstring (lines 8–14) states this explicitly as "THE FAKE-BINARY TRAP" and I confirmed the
code matches the claim by reading it end to end — no invocation bypasses the helper.
