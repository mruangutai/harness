# Observations — harness-documentor — FEAT-1821-ui-verification-lane

- 2026-09-19: A replayable-evidence amendment can intentionally supersede local-only wording in the signed BRIEF; canonical operational docs must state the amended committed-trace rule while the signed wording remains untouched and is reported as historical stale prose.
- 2026-09-19: Playwright `--list` still runs the UI reporter's end hook; without HARNESS_UI_FEATURE and HARNESS_UI_RUN_ID it writes `runs/local/ui/results.json`, so discovery commands need the same explicit run context as execution.
