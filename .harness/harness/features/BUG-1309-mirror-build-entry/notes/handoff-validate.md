# Handoff — BUG-1309-mirror-build-entry, validate → ship decision — written at 9fe5cf31, seq-2

## Next

Return SC-04's ONE remaining evidence gap to the operator together with the SC-10 hand test, and
dispatch NOTHING until they rule. The budget is spent — `cycles_used` 16 of 16 — so no fix is
dispatchable and no cycle exists to spend on the gap. The operator's two options, in pm's words
(`notes/research-BUG-1309-goalcheck-c18.md`, Q1): accept the clause-(f) wording gap with a recorded
ruling on inspected-correct behaviour, or defer it as a follow-up bug and hold SC-04 unmet. The
UAT Step 3b amendment stays gated off until that ruling; SC-10 is runnable by hand right now,
unamended, and its pass rule at `uat-...md:337-340` already names Step 3b.

## Trust

- The only change this cycle is `9fe5cf31`, `tests/integration/test-merge-gate.py` +37/-1, additive assertions, no production source — `git show --stat 9fe5cf31` — verified-at 9fe5cf31
- `review_sha` was re-pinned to `9fe5cf31` BEFORE any validator ran; `plan.yaml` and `BRIEF.md` are byte-unchanged this cycle, so no post-record re-pin is owed — `feature.json:5` — verified-at 9fe5cf31
- Suite at the pin: 36 ok, 0 FAIL, `ALL PASSED`, rc=0 from a variable; `matrix_ok: true`; panel PASS, `severity_max: med`, `must_fix: []`, four reviewers ran — `notes/qa-c18.md`, `runs/c18-validator/digest.md` — verified-at 9fe5cf31
- Gap A and gap C are CLOSED by mutation: every one of gap C's four arms reddens its case when removed — `notes/qa-c18.md` section 3 — verified-at 9fe5cf31
- SC-04 clause (f) has no assertion: production emits `Correct the duplicated top-level "branch" field` at `merge-gate.py:174`; the carrying case at `test-merge-gate.py:159-163` asserts ids, `gh-sync.py` absence and run-to-run equality only; whole-file grep for `duplicat`/`Correct`/`more than one` returns fixture ids alone — verified-at 9fe5cf31
- The clause-(f) gap is NOT new breakage: c17's clause table had ten rows and no row for it — `notes/research-BUG-1309-goalcheck-c17.md:44-56` — verified-at 9fe5cf31
- Gap B's case does not redden against an `owners[0]`-keyed era hoist: `glob.glob` returns fixtures in creation order here and the non-era fixture is created first — reproduced by the orchestrator in a scratch tree — verified-at 9fe5cf31
- SC-11 MET at this pin; no production file changed in `94b5e465..9fe5cf31` and the commit's hunks miss the SC-11 loop — `notes/research-BUG-1309-goalcheck-c18.md` section 3 — verified-at 9fe5cf31
- The UAT file is byte-unchanged: Step 3b still has three commands and a three-line rule — `notes/uat-BUG-1309-mirror-build-entry.md:179-210` — verified-at 9fe5cf31

## Dead ends

- Do NOT re-litigate gap B as a production defect. `merge-gate.py:167-181` guards on `len(owners)` alone, never on `owners[0]`'s identity, so the ordering is correct in source; the weakness is in the fixture — verified-at 9fe5cf31
- Do NOT accept the code reviewer's c18 reading that gap B's case is ordering-binding. Its mutant shape leaves the length check below the hoist, so that mutant denies and the case passes — `notes/review-harness-code-reviewer-c18.md:62-78`, overruled by the lead on two measurements — verified-at 9fe5cf31
- Do NOT amend UAT Step 3b before the operator rules. The gate is the operator's own "if and only if SC-04 and SC-11 are met", and pm correctly declined to open the file — `runs/c18gc-product/digest.md` — verified-at 9fe5cf31
- `git merge` in any form still cannot be probed from inside a run: `bash-write-guard.sh` refuses the command name outright, including in a throwaway `/tmp` repo — refusal text observed at c17 — verified-at 94b5e465

## Working set

- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/research-BUG-1309-goalcheck-c18.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/qa-c18.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/notes/uat-BUG-1309-mirror-build-entry.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/runs/c18-validator/digest.md`
- `.harness/harness/features/BUG-1309-mirror-build-entry/feature.json`

## Done when

Scope: operator rules on SC-04 clause (f), and SC-10 is hand-tested
Authority: brief-sc:SC-04
Authority: brief-sc:SC-10
