# Observations — harness-orchestrator — BUG-2003-hook-internal-uris

- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE first line from the task prompt field, not the shared context field; a feature line placed only in context is refused as absent.
- 2026-10-03: patch intake landed in one product run (11 min, 0 cycles); pm anchored postDomain by symbol unprompted and produced an 83-line BRIEF.
- 2026-10-03: observations-merge.py apply does not create the observations/ directory; first append on a fresh feature fails at the lock-file open.
- 2026-10-03: gh-sync status review refuses while any task station is still `review`; the task must be `done` (its commit recorded) before the feature projects Review. Writing the station into plan.yaml after the pin trips INV-33, so order is: task done + feature station, seam commit, THEN pin to that commit (code-path diff from the code commit empty).
- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE line from the task text, not the shared context block; a dispatch with it only in context is refused.
- 2026-10-03: validate c0 over 85038f8c returned FAIL on a test-only SC-03 gap (no main-session edit control, no governed forbidden-file write/pre control); premise verified by reading the committed test file. Readers running inside the validate run still hit the unpatched hook (main checkout governs subagents, G-15), which is Q1.
- 2026-10-03: a main-session-direct fix is not a run, so the cycle it costs has nowhere to land except re-closing the FAIL run with `run-end --cycles-used 1`; that re-close rewrites `ended_at` to now (tokens preserved). check-state's `cycles_used < FAIL runs` rule wants the attribution regardless.
- 2026-10-03: bash-write-guard resolves `$VAR` paths literally — `sed -i` on `$F/feature.json` is refused as outside domain while the same command with the absolute path spelled out passes.
- 2026-10-03: validate c1 over c2170e26 PASSED all five readers; the lead reported one internal goalcheck send-back (BLOCKED-pending-QA resolved on the same pin) as cycles_used 1, so a clean panel still cost a cycle.
