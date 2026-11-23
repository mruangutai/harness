# BUG-2399 code review c2

**PASS — the three path rewordings preserve the operator checklist; no new findings. Accepted c1 grade-2 advisories remain unchanged.**

Reviewed `9eb07b4f3cd235c234a10edddbfe5542c1e85fba..54c702c7af73568249d51c07771c7727b6003b1f`, with this review scoped to `ec95d8fb6167cfe199c4a30d4b20860d852c48f0..54c702c7af73568249d51c07771c7727b6003b1f`. Unchanged assurance: `notes/review-harness-code-reviewer-c1.md` and `runs/r-20261122-4-validate-validator/digest.md`. Live review pin agrees; pinned feature.json records the earlier pin historically. No human-tagged commits; checkout dirt is confined to this feature's metadata/current run.

## Stage 1 — spec compliance: PASS

Measured delta: 13 files, 1,185 insertions/8 deletions. Outside this feature directory, exactly one path changes: `.claude/skills/harness/references/checkout-upgrade.md` (8 insertions/7 deletions). Remaining changes record c1 validation, run receipts, metadata and the c2 build explanation; the commit list contains only this feature's work. No Python, test, fixture, import, ignore-rule or policy-authority bytes change from c1.

**SC-02:** pinned `checkout-upgrade.md:38-83` retains the same commands, order and safety obligations: pause/isolate existing work, inspect old ignored evidence, invoke the existing merger, review diff/status, ordinary literal-path staging of explicitly reviewed records, inspect staged names, and make a separate commit before resuming. No force-add, automatic commit or broad staging is introduced. The reworded layout examples remain relative to the explicitly named target checkout's `.harness` directory, not either Harness anchor.

**SC-04 inspection:** pinned `.claude/skills/harness/references/checkout-upgrade.md:40-50` describes `runs/*/ui/**` under each feature and resolves both namespaced and legacy examples beneath the checkout's `.harness`. This preserves the previous locations and agrees with pinned DEC-257 (`.harness/harness/docs/DECISIONS.md:8536`), which still specifies the exact canonical ignore rule and cites DEC-238. DEC-112 deterministic merging/read-only check, DEC-238 retention and DEC-174 direct execution remain governing. SC-01/SC-03, SPEC, distillation ordering, research inventory, D-01 and plan amendments are unchanged; their c1 inspection remains applicable. No scope creep, omission or mismatch found.

## Stage 2 — quality: PASS with inherited advisory grades

The prose reflow introduces no executable or assertion change; checklist command meaning is unchanged. C1 independently measured the canonical merge-base grading range. Because every graded source path is byte-identical to c1, its `grade_2` result and accepted reasons carry forward without rerunning a gate:
- `case_remove_refuses_aborted_run_evidence`: cohesive landed setup, refusal and byte preservation (12/5/40.4 CC/cognitive/ABC).
- `case_bug2399_distill_records_commit_before_merge`: same candidate before and after commit/push (7/3/35.6).
- `case_bug2399_merge_replaces_broad_rules`: one migration/idempotence contract across three historical-rule combinations (7/4/30.2).

These accepted T-01 maintainability advisories are not new actionable findings. No tests, builds, lint, formatters or grading commands ran in c2; QA owns current-pin suite execution. Inspection does not claim the instruction-path gate was executed by this reader.

Open questions: none. Must-fix: none.
