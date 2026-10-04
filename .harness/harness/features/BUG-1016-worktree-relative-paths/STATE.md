# STATE

## Current

- feature: BUG-1016-worktree-relative-paths
- run: none (build entry; no build run opened yet)
- squad: none
- status: blocked
- mission: plan
- station: building
- verdict: none
- approval: BRIEF approved, plan.yaml approved (2026-10-04, molchairuangutai; rework 2 rounds / 90 min)
- github: build_entry opened; status building projected to #1016 #1570 #2016 #2017 #2018
- cycles_used: 0/10
- review_sha: none
- next: T-01 is main-session-direct (DEC-174) — main session builds .omp/extensions/harness-hooks.ts + tests/unit/omp-hooks.test.ts, runs `python3 tests/unit/test-omp-hooks.py`, commits `[harness:t-01]`, then re-dispatches orchestrator; orchestrator then sets T-01 done, dispatches T-02 (documentor) via product lead, simplify via eng lead, pins review_sha, validate

## Open Questions

- Q1 (harness defect, non-blocking): governed `write agent://<peer>` and `write xd://report_issue` were refused by check-domain as filesystem paths `agent:/`, `xd:/` in two squads this run — BUG-2003's scheme pass-through is not reaching the gate for the live hook. Harness owner to triage; T-01's SC-05 must not regress on it.
- Q2 (blocking, T-01 hand-off): T-01 awaits main-session-direct execution per DEC-174.
