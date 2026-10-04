# Observations — harness-orchestrator — BUG-2003-hook-internal-uris

- 2026-10-03: dispatch-guard reads the HARNESS-FEATURE first line from the task prompt field, not the shared context field; a feature line placed only in context is refused as absent.
- 2026-10-03: patch intake landed in one product run (11 min, 0 cycles); pm anchored postDomain by symbol unprompted and produced an 83-line BRIEF.
- 2026-10-03: observations-merge.py apply does not create the observations/ directory; first append on a fresh feature fails at the lock-file open.
