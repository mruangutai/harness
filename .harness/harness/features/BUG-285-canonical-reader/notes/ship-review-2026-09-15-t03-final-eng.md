# Ship review — BUG-285-canonical-reader — manifest discovery block

The feature is not ready to ship. Both earlier accessor amendments are signed, implemented, and verified. T-03 advanced most semantic migrations but remains uncommitted and blocked because the signed remedy `manifest_domains(path, agent)` cannot preserve `harness_boundary.run_dir_grant_globs` generic discovery across every role. No report round was spawned. This briefing was assembled from all twelve run digests in `feature.json`; main-session-direct T-01 is evidenced by commit `12c0171b` and its Done station.

## Definition of done

| Perspective | Signed outcome | Verdict | SCs and evidence |
|---|---|---|---|
| operator | Every reader agrees while enforcement behavior is preserved. | unmet | T-03 is blocked and unverified; T-04 through T-08 have not run. SC-04/SC-05 remain open. Evidence: `runs/2026-09-15-t03-final-eng/digest.md`; `plan.yaml`. |
| code maintainer | One dependency-light reader module and AST guard cover all Python entrypoints with usable remedies. | unmet | T-01/T-02 are complete, but the team-config remedy cannot express all-role grant discovery. Evidence: `notes/receipt-harness-backend-dev-T-03-final-c1.md`. |
| reader (reviewer / qa) | Semantic and mechanical diffs remain separate with fail-first evidence. | unmet | T-03 has uncommitted semantic work and its exact verify fails at board-lifecycle fixtures; T-04 and validation have not run. Evidence: `runs/2026-09-15-t03-final-eng/digest.md`. |

## Blocking decision

Recommendation: generalize the existing `manifest_domains(manifest_path, agent)` so `agent=None` returns every named-role non-read domain glob in the first tuple while the existing shared globs remain the second tuple. Agent-specific callers retain their current result. `run_dir_grant_globs` can combine the two lists and filter `/runs/`. Do not add a second accessor, raw team-config parse, exemption, or hard-coded role enumeration.

The 13 current `test-board-lifecycle.py` failures are not a separate plan question: they are partial feature fixtures exposed by strict `load_feature_json` and should be repaired inside T-03 while preserving the behavior each fixture actually tests.

## Run summaries

- `runs/2026-09-13-plan-product/digest.md` — initial plan, superseded.
- `runs/2026-09-13-plan-apply-c1-product/digest.md` — deferred apply block, resolved.
- `runs/2026-09-14-plan-refresh-product/digest.md` — current-state plan panel and goal-check, PASS.
- `runs/2026-09-14-t09-eng/digest.md` — obsolete differential deletion, PASS.
- `runs/2026-09-14-t02-t04-eng/digest.md` — initial accessor layer and issue 1682 hardening, PASS after one send-back.
- `runs/2026-09-14-t03-eng/digest.md` — first remote harness text gap, BLOCKED.
- `runs/2026-09-14-t03-amend-product/digest.md` — first approved amendment, PASS.
- `runs/2026-09-15-t02-text-eng/digest.md` — remote harness text source, PASS.
- `runs/2026-09-15-t03-eng/digest.md` — GitHub array and feature-text gaps, BLOCKED.
- `runs/2026-09-15-t03-amend2-product/digest.md` — second approved amendment, PASS.
- `runs/2026-09-15-t02-shapes-eng/digest.md` — generalized GitHub values and feature text, PASS.
- `runs/2026-09-15-t03-final-eng/digest.md` — manifest discovery gap after one send-back, BLOCKED.

## Open questions

1. Approve the recommended `agent=None` all-role mode for the existing `manifest_domains`, or specify another single-accessor contract that preserves generic run-grant discovery.

## Resolved escalations

- Remote `harness.json` text, GitHub array values, and in-memory `feature.json` text now have approved single-accessor contracts and passing focused/full T-02 evidence.
- Source provenance, issue 1682 placement, and the removed shell boundary remain resolved.

## Spend and record

- `feature-record.py spend`: 12 runs, 244 recorded wall-clock minutes, build phase, tokens unmeasured, no validate rework window started.
- The run count is below the informational 20-run budget. `feature.json` still records `cycles_used: 0`; lead digests report six historical send-backs, and the missing authorized increment verb remains disclosed.

## Proposed backlog

| ID | Nature | Residual |
|---|---|---|
| B-1 | chore | Make `observations-merge.py` create or guarantee its parent directory. |
| B-2 | bug | Add an authorized feature-record verb for lead-reported send-backs. |
| B-3 | bug | Repair the denied `xd://report_issue` route reported during T-09. |
