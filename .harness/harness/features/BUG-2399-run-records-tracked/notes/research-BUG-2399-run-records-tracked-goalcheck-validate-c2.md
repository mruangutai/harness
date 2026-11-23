# BUG-2399 — goalcheck, validate c2

**PASS: SC-01..04 and both perspectives remain met at 54c702c7af73568249d51c07771c7727b6003b1f (P).** No amend/strike disposition requires grading. Run: r-20261122-5-validate-validator.

## Pin and evidence transfer

Read BRIEF and plan through `git show P:<path>`. Direct diff from accepted c1 ec95d8fb6167cfe199c4a30d4b20860d852c48f0 to P establishes exactly one change outside this feature directory: `.claude/skills/harness/references/checkout-upgrade.md`. Its delta is three path rewordings plus wrapping, with no command change. All source, tests, fixtures, ignore inputs and configuration are identical. Feature-directory changes add c1 validation records and Fix c2 narrative, not historical backfill. `notes/build-T-01-T-03.md:34-35` explains the instruction-path CI motivation; PM does not independently claim that CI gate execution.

Unchanged automated assurance transfers from accepted c1, not a claimed c2 re-execution: pinned `notes/review-harness-qa-c1.md:13-35` records integration 95/95, exit 0, tested_commit ec95d8fb…, the carrying cases and preserved pre-fix red. Full unchanged-clause inspection, baseline retention/invariant comparisons, original red integrity and accepted advisor dispositions are in `notes/research-BUG-2399-run-records-tracked-goalcheck-validate-c1.md:18-37`. No tests/build/lint/formatting ran in this goalcheck. Conventional product docs/spec.md, docs/decisions.md and docs/architecture.md remain absent at P; assigned self-hosted SPEC and DECISIONS supply guidance.

## Criteria and perspectives

| Criterion | Grade / method | Evidence at P, with c1 execution explicitly inherited |
|---|---|---|
| SC-01 | met / automated | QA c1 names `bug2399_repository_rules_track_run_records` and `bug2399_fresh_install_tracks_run_records`; unchanged `tests/integration/test-merge-gitignore.py:149-213` and ignore inputs prove ordinary staging of named records, UI/lock exclusions; original red is unchanged. |
| SC-02 | met / automated | QA c1 names obsolete-rule check, replacement, rationale, line-ending and operator-composition cases. P's unchanged `test-merge-gitignore.py:309-356` covers legacy/namespaced evidence, spaces/metacharacters, exact literal staging, no automatic commit, separate commit and byte preservation. Directly inspected P's revised checklist :38-85: target checkout's `.harness` explicitly scopes both relative layouts; “runs/*/ui/** under each feature” cites DEC-257 rather than changing the actual installed pattern. Commands still compose: pause/isolate → inspect → merger → review status/diff → explicit literal add → cached-list review → separate commit → resume. No force-add or broad staging was introduced. |
| SC-03 | met / automated | QA c1 names dirty distill refusal/ordinary commit/push/exact-head merge and removal exit-4/WOULD-DISCARD/byte-preservation assertions; source/tests unchanged. Carry c1's accepted hand-built `running` interrupted-state fixture limitation, not a claim to exercise an interruption producer. |
| SC-04 | met / inspection | P's DECISIONS.md:8538-8568 (DEC-257) retains the exact namespaced UI rule, lock exclusion, ordinary staging and DEC-238 retention. Revised upgrade :38-85 agrees with SPEC :249-255, :1626-1627, :2313-2317 and distillation :49-63 (commit/push before merge-distill). All but upgrade are byte-identical to accepted c1; unchanged inventory/recheck receipt is cited there at :23,31. No gate, retention or historical-backfill change appears in this delta. |

**operator: met** — SC-01/02, traced by T-01/T-02/T-03, retain normal staging and reviewed upgrade before resumption. **code maintainer: met** — SC-03/04, traced by T-01/T-03 and T-02/T-03 respectively, retain regression-backed dirty-tree consequences and one consistent tracking policy.

## Decision dispositions

Pinned plan `decisions_affected` contains DEC-112, DEC-174 and DEC-238, all **keep**, and zero amend/strike rows. Mode 2 therefore emits no invented DEC sc_status rows. D-01 remains landed by pinned DEC-257 :8538-8568; T-03 owns DECISIONS.md if remediation were required. No remediation is needed. Unchanged c1 preservation evidence applies to those sections, SPEC §8.6 and INV-7/INV-36.

## Open questions

None. This is product goal-check, not ship authorization or a claim that c2 QA has finished.
