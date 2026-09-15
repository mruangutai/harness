# Ship review — BUG-285-canonical-reader — second T-03 contract block

The feature is not ready to ship. The first remote `harness.json` contract gap was approved, planned, signed, implemented, and verified. T-03 then found three more signed remedy/interface mismatches before source edits: two legitimate GitHub JSON array consumers are assigned to a mapping-only `parse_gh_json`, and one decoded in-memory `feature.json` consumer is assigned to path-only `load_feature_json`. No report round was spawned. This briefing was assembled from all nine run digests in `feature.json`; T-01 was main-session-direct and is evidenced by commit `12c0171b` and its Done task station.

## Definition of done

| Perspective | Signed outcome | Verdict | SCs and evidence |
|---|---|---|---|
| operator | Every reader agrees while hooks, gates, and validators preserve violations, diagnostics, and exits. | unmet | SC-04/SC-05 remain incomplete because T-03 stopped pre-edit and T-04 through T-08 have not run. Evidence: `runs/2026-09-15-t03-eng/digest.md`; `plan.yaml`. |
| code maintainer | One dependency-light reader module and one AST guard cover all Python entrypoints with named remedies. | unmet | T-01 and T-02 are built, including the first approved text-source amendment, but three T-03 rows still name incompatible interfaces. Evidence: `notes/receipt-harness-backend-dev-T-03-resume-c0.md`. |
| reader (reviewer / qa) | Semantic and mechanical diffs are separately reviewable with fail-first evidence. | unmet | T-02 has fail-first evidence; T-03/T-04 and final validation remain incomplete. Evidence: `runs/2026-09-15-t02-text-eng/digest.md`; `runs/2026-09-15-t03-eng/digest.md`. |

## Blocking decision

Recommendation:

1. Let the existing `parse_gh_json(text, context)` return any valid JSON value, including arrays, while retaining strict duplicate-key/non-finite parsing and `ArtifactAccessError`; each GitHub consumer keeps responsibility for its expected result shape.
2. Give the single public `load_feature_json` the same mutually-exclusive keyword-only in-memory text source mode already approved for `load_harness_json`, sharing the strict feature parser, mapping validation, caller context, and typed error.
3. Do not add second accessors, exemptions, generic caller-local JSON wrappers, or temporary files. Reopen T-02 narrowly, then re-run T-03.

## Run summaries

- `runs/2026-09-13-plan-product/digest.md` — initial plan, later superseded by current-state planning.
- `runs/2026-09-13-plan-apply-c1-product/digest.md` — deferred apply block, later resolved.
- `runs/2026-09-14-plan-refresh-product/digest.md` — current-state readers and goal-check passed.
- `runs/2026-09-14-t09-eng/digest.md` — obsolete shell differential deleted, PASS.
- `runs/2026-09-14-t02-t04-eng/digest.md` — canonical accessor seam and issue 1682 hardening, PASS after one send-back.
- `runs/2026-09-14-t03-eng/digest.md` — first remote `harness.json` contract block.
- `runs/2026-09-14-t03-amend-product/digest.md` — operator-approved first amendment represented exactly, PASS.
- `runs/2026-09-15-t02-text-eng/digest.md` — keyword-only remote `harness.json` text mode, PASS.
- `runs/2026-09-15-t03-eng/digest.md` — current three interface mismatches, BLOCKED before source edits.

## Open questions

1. Approve the two-part narrow amendment above, or specify another non-bypass interface for the two GitHub array consumers and the in-memory feature consumer.

## Resolved escalations

- The first `factory_config.product_config` blocker is closed by the signed keyword-only `load_harness_json(text=...)` mode and its passing focused/complete T-02 verification.
- Source provenance, issue 1682 placement, and the obsolete shell boundary remain resolved as recorded in the signed BRIEF and plan.

## Spend and record

- `feature-record.py spend`: 9 runs, 198 recorded wall-clock minutes, build phase, tokens unmeasured, no validate rework window started.
- The run count is below the informational 20-run budget. `feature.json` still records `cycles_used: 0`; lead digests report five historical send-backs, and the missing authorized increment verb remains disclosed in the previous briefing.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Make `observations-merge.py` create its parent directory or guarantee the parent precondition. |
| B-2 | bug | Add an authorized feature-record verb for lead-reported send-backs so `cycles_used` is not under-recorded. |
| B-3 | bug | Repair the denied `xd://report_issue` route reported during T-09. |
