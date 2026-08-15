# Observations — harness-orchestrator — FEAT-21-features-layout-migration

- 2026-08-14: I re-dispatched product-lead for the post-ruling revision without naming a run-dir
  purpose, and the lead reused `runs/2026-08-14-1-product/` from the plan run. The revision digest
  OVERWROTE the plan run's consolidated digest — the record of what the review panel bought, which
  was the most valuable artifact of the whole phase. Nothing was recoverable: the feature dir is
  untracked, so there was no git copy. The substance survived only because eng-lead and ui-reviewer
  write to their own paths (`runs/2026-08-14-1-eng/`, `notes/review-harness-ui-reviewer-*.md`).
  The playbook's run-dir rule (`<task-or-purpose>-<squad>`) exists for exactly this and I read it
  as a naming convention rather than as collision protection. A second dispatch to the same squad
  inside one flow needs its own purpose slug — `revision-product`, not a reused id.

- 2026-08-14: The lead deviated from an operator ruling in the right direction and disclosed it.
  Q8 was ruled "anchor tests.yml's measured numbers with a sha"; pm found the number was ALREADY
  false at base (`git ls-files` returns 19 at HEAD, 8 at eafc8ad where the comment was written) and
  corrected it as well as dating it, because dating a false figure asserts a falsehood at a sha.
  I re-ran both counts before accepting. The lesson is about what to check: when a ruling says
  "anchor this measurement", the measurement itself may already have drifted, and anchoring is
  the one operation that makes drift permanent and unfalsifiable.

- 2026-08-14: A reviewer's non-blocking finding was worth more than its flag suggested. ui-reviewer
  returned PASS while noting SC-14 claimed test-backing that no `verify:` enforced — nothing would
  ship wrong, only the record would be false. The operator ruled to add the checks, and writing
  them exposed a real trap: a whole-file grep for the migrated path in `test-check-plan-routes.py`
  is already satisfied by a DIFFERENT case's required rewrite, so the clause had to be region-
  anchored to `case_22a`'s own assertion expression to discriminate at all. An assertion that
  cannot fail is the defect; "the code is right anyway" is not a reason to skip it.

- 2026-08-14: Verifying a plan's boundary conditions MYSELF before dispatching pm paid twice. The
  detector looked like it would red post-move because `mruangutai/harness` is deliberately absent
  from `fleet.yaml`, but `layout_migration.py:144-161` derives harness's own segment from
  `harness.json` instead — so a fleet edit that would have contradicted DEC-174 am.1 never entered
  the plan. Reading the resolver beat reasoning about the config.
