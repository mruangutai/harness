# Observations - harness-pm

- 2026-08-23: plan-merge.py cannot be dry-run — it exits 9 on any --file outside a features
  directory, and bash-write-guard refuses a pm `cp` of plan.yaml to scratch, so the only rehearsal
  available is getting the proposal right first. Its proposal parse also dies on a plain scalar
  containing ": " (exit 5, "mapping values are not allowed here"); rewrite the prose with " - "
  instead of quoting.
- 2026-08-23: a lane argument from "it is the blocking qa gate's runner" was wrong for
  run-unit-tests.sh. DEC-174 am.4's rule fires on the DAY a script's gate status changes; adding a
  basename to UNIT_SCRIPTS changes nothing, and check-domain.sh --resolve already answered
  (harness-backend-dev, harness-dev-ops). Resolve the lane from --resolve plus the day-it-changes
  test, not from what the script is downstream of.
- 2026-08-24: adding `source_issues` to plan.yaml is NOT sufficient for `gh-sync.py closes` to emit. `closes` reads feature.json `github.source_issues` (gh-sync.py:1054, load_recorded), which only `cmd_open` refreshes (gh-sync.py:705,784). FEAT-35 plan.yaml got the key; the mirror was still `[]` and `closes` printed nothing until `open` re-ran. Same shape stranded FEAT-33/PR #785 (#806).
