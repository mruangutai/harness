# Observations — harness-orchestrator — BUG-2003-hook-internal-uris

- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE first line from the task prompt field, not the shared context field; a feature line placed only in context is refused as absent.
- 2026-10-03: patch intake landed in one product run (11 min, 0 cycles); pm anchored postDomain by symbol unprompted and produced an 83-line BRIEF.
- 2026-10-03: observations-merge.py apply does not create the observations/ directory; first append on a fresh feature fails at the lock-file open.
- 2026-10-03: gh-sync status review refuses while any task station is still `review`; the task must be `done` (its commit recorded) before the feature projects Review. Writing the station into plan.yaml after the pin trips INV-33, so order is: task done + feature station, seam commit, THEN pin to that commit (code-path diff from the code commit empty).
- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE line from the task text, not the shared context block; a dispatch with it only in context is refused.
- 2026-10-03: validate c0 over 85038f8c returned FAIL on a test-only SC-03 gap (no main-session edit control, no governed forbidden-file write/pre control); premise verified by reading the committed test file. Readers running inside the validate run still hit the unpatched hook (main checkout governs subagents, G-15), which is Q1.
