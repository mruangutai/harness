# Receipt — harness-dev-ops — F4 test-gate revival

## BLUF
Gate revived. Removed the three dangling registrations (`test-context-watch.py` from
`UNIT_SCRIPTS`; `test-context-watch-cli.py`, `test-context-watch-hook.py` from
`INTEGRATION_SCRIPTS`) in `.claude/skills/harness/bin/run-unit-tests.sh`. All remaining
registered names verified present on disk. Both `--kind unit` and the full run now discover
and execute the suite with zero failures — discovery is restored well above the pre-merge
1012-line baseline, not suppressed.

## Change
- `run-unit-tests.sh` line 30/31: deleted exactly the three names, kept every other entry
  and order, including `test-panel-findings.py` and `test-plan-panel.py` (T-09/T-10).
- Nothing else touched. `--check-kinds` cross-check (harness.json vs the arrays) was left
  untouched and still runs.

## Dangling-registration sweep
Command: iterated every name in `UNIT_SCRIPTS` (30 entries) and `INTEGRATION_SCRIPTS`
(27 entries) after the edit, checking `[ -f .claude/skills/harness/bin/$f ]` for each.

Result: `unit_count=30 integration_count=27 missing=0` — no other dangling name exists.
Only the three files named in the dispatch were missing; the sweep confirms no others.

## Acceptance measurements
1. `bash run-unit-tests.sh --kind unit`: `rc=0`, `FAIL_lines=0` (grep `^FAIL `),
   `total_lines=1414`.
2. `bash run-unit-tests.sh` (full, no args): `rc=0`, `FAIL_lines=0`, `total_lines=3357`.
   Pre-merge baseline was 1012 lines at rc=0. Current full run (3357 lines) is well above
   that order of magnitude — discovery is restored, not still suppressed. (Higher than
   baseline is expected: baseline predates T-09/T-10's `test-panel-findings.py` /
   `test-plan-panel.py` additions and this run also now includes the previously-dead
   `--kind unit` slice contributing to total collected output.)
3. `bash run-unit-tests.sh --check-kinds`: `rc=0`, output
   `check-kinds: the script arrays and test_kinds.integration.detect agree.`
4. Existence check for step 2 (dangling-registration sweep): see above — `missing=0`.

## Findings
No FAILing tests surfaced in either run (`FAIL_lines=0` both for `--kind unit` and the full
run). No `must_fix` entries to report — the revived gate is clean.

## Files touched
- `.claude/skills/harness/bin/run-unit-tests.sh`
- this receipt
