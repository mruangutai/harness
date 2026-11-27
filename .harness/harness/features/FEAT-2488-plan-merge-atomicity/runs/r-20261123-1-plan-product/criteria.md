# Send-back criteria — written before any return (product-lead P-05)

draft / apply send back if any fails:
- BRIEF.md has `## Approval` pending; plan.yaml `approval.status: pending`; no `panel:` at draft.
- SC-01..SC-05 present, each perspective-tagged with `verify:`; no SC phrased as a line count; BRIEF states E is ~LOC-neutral, may be net-positive.
- Named non-goals: YAML round-trip; LOC target; sign-approval preliminary writes; snapshot isolation; check-plan-routes.py (E2, #2489); legacy PLAN.md parser.
- Every task `execution_mode: main-session-direct`.
- Journal primitive + recovery in harness_merge.py; plan-first order; idempotent re-run; lock order plan.yaml.lock -> feature.json.lock documented.
- guards._replace_bytes and _restore_plan deleted; feature_json_write.py fsync claim corrected; 5 dead reset lines removed.
- Compensation tests migrated not deleted; torn states built on disk; no injection hooks; red first.
- No files: entry for check-plan-routes.py or its test; stations._task_search/text._item_range_within untouched; PRESERVE_BASE_BYTES/UNION_MERGE kept.
- decisions_affected rows keep-only or `[]` unless shown otherwise.
- Anchors content / file:symbol, no line numbers; plan-merge check exit 0 with --root the worktree.

apply additionally: record-panel exit 0; every finding carries an explicit disposition.
goalcheck: one grade per perspective against the grilling artifact, not the BRIEF.
