# Observations — harness-qa — FEAT-2622-practicality-rule

- 2026-11-28: In test-practicality-rule.py every gating-severity case also sets severity_max high, so _severity_max_errors masks _severity_errors: removing the per-finding ceiling leaves the suite green (P-06 ordering). The pairing needs a severity_max-med row.
- 2026-11-28: A sitecustomize.py on PYTHONPATH that wraps harness_boundary.load_repo_module patches validate-digest in-process and reaches plan-merge CLI subprocesses (the test ENV keeps PYTHONPATH). Subprocess markers land in captured stderr, so prove the patch reached by a red, not by a marker count. test-panel-findings loads panel_findings by spec_from_file_location, so module patches never reach it.
- 2026-11-28: Copying runner logs into runs/<id>/qa/ is outside the QA grant (manifest-*.json only); I removed them and kept the logs in /tmp with sha256 in the note.
