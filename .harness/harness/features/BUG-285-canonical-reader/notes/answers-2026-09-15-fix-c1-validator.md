# Operator answers — BUG-285 ship review

- ship_decision: accept
- backlog_selection:
  - B-1 — Make `observations-merge.py` create the per-feature observations parent directory before its first append.
  - B-2 — Repair the governed backend route to `xd://report_issue`.
  - B-3 — Let fix-team handoff validation recognize governed `head_sha`/`tip_sha` until the orchestrator repins `review_sha`.
  - B-4 — Make governed product-run checkpoint writes reliably mint and preserve `run_uid` plus `.run-identity.json`.
  - B-5 — Decide separately whether present top-level `github` or `factory` non-mapping values should be rejected.
- integration_constraint: Do not create, merge, or close a pull request in this run.
