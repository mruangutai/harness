# Final canonical goal-check — BUG-1699-lifecycle-cards

## Conclusion

**PASS.** The approved `BRIEF.md` is delivered at pinned SHA `d29899ad3be07bc4999f202cacee7db58c4e8865`: all three declared perspectives and SC-01 through SC-16 are met. No stale c0/c1 finding or open question remains.

The pin contains the c2 SC-11 repair and is a descendant of `0274000f47a4c3ab3011b4ddaef295ac50c2f275`. From the c1 evidence head `d7310f865e03534c233085e5f0a768eb9eca4687` to the pin, the only executable test change is moving `tests/unit/test-gh-board.py`'s shared failure decision after every projection assertion; the other changes are the two evidence/ruling notes and the manifest reconciliation. Production lifecycle code, orchestration, focused integration tests, and decision authority are unchanged, so the exact-head c1 evidence remains applicable except where c2 repairs SC-11.

The former external matrix blocker is closed at the pin. `d29899ad` adds the missing frontend dashboard-client grant to `.harness/team-config.yaml`; the pinned manifest compares byte-identical with the control-plane manifest. The operator/orchestrator-supplied final execution of `.agents/skills/harness/bin/run-unit-tests.py --kind integration` at this exact pin reports **72 files, 0 failures, 92.93 seconds**. This is consumed evidence, not a rerun by this goal-check.

## Perspective grades

- **operator — met** — SC-01, SC-02, SC-03, SC-06, SC-07, SC-08, and SC-09 are all met: initial approval, active phases, approval reset/resume, ship, and bounded reconciliation project the complete eligible recorded card set at the required lifecycle stations.
- **orchestrator — met** — SC-04, SC-05, and SC-10 are all met: must-fix Building and next-boundary Review retain their explicit callers and ordering, preserve the existing reader topology, and keep GitHub synchronization local-first, per-card best effort, and non-gating.
- **code maintainer — met** — SC-11 through SC-16 are all met: the single projection policy and exact vocabulary are exercised by a fail-closed focused runner, preserved lifecycle contracts remain covered, callers are singular and traceable, and current decision authority plus its generated index agree.

## Success-criterion status

| SC | Status | Evidence tied to `d29899ad3be07bc4999f202cacee7db58c4e8865` |
|---|---|---|
| SC-01 | met | Historical red and fixed behavior are recorded in `notes/receipt-main-direct-validation-c1.md:14` and `notes/review-harness-qa-c1-r1.md:25`; the focused signature scenario validates dynamic `RESUME`, mirror-open-before-status, and complete Ready projection in `tests/integration/test-station-argument-spelling.py` and `tests/integration/test-gh-sync-record.py`. Those subjects are unchanged through the pin. |
| SC-02 | met | The same historical checkpoint red and c1 green cover Building before ordinary dispatch, with complete-card projection (`notes/review-harness-qa-c1-r1.md:25,35`). The final 72-file integration matrix is green at the pin. |
| SC-03 | met | The historical checkpoint red and focused green cover complete-card Review before validation dispatch (`notes/review-harness-qa-c1-r1.md:25,35`); the orchestration and projection subjects are unchanged through the pin. |
| SC-04 | met | The must-fix Building ordering scenario and its reversal control pass, with the historical absent/misordered checkpoint red recorded at `notes/receipt-main-direct-validation-c1.md:14` and fixed evidence summarized at `notes/review-harness-qa-c1-r1.md:25,35`. |
| SC-05 | met | The focused scenario keeps Review at the next validation boundary and outside the fix-team DAG, including wrong-placement controls (`notes/review-harness-qa-c1-r1.md:25,35`); no post-c1 orchestration file changed. |
| SC-06 | met | The pre-repair 24-assertion red and fixed focused cases prove pending approval, interrupted-phase metadata, local Plan, complete-card Plan, and receipt-gated outbound status (`notes/receipt-main-direct-validation-c1.md:13`; `notes/review-harness-qa-c1-r1.md:26`). |
| SC-07 | met | The same historical red plus focused green proves Ready, Building, and terminal-interrupted Review restoration on reapproval (`notes/receipt-main-direct-validation-c1.md:13`; `notes/review-harness-qa-c1-r1.md:26`). |
| SC-08 | met | Complete source/parent/non-abandoned-task Done behavior is green. Its parent-omission red is an honestly labelled **reconstructed mutation proof**, not a historical pre-implementation red (`notes/receipt-harness-backend-dev-fix-c1-r1.md:11,16,20`; `notes/review-harness-qa-c1-r1.md:27,35`). |
| SC-09 | met | The historical ten-failure red and fixed integration scenario prove one bounded snapshot, all-card apply, failure continuation, exclusions, and mutation-free immediate repetition (`notes/receipt-main-direct-validation-c1.md:15`; `notes/review-harness-qa-c1-r1.md:28`). |
| SC-10 | met | Historical local-first/reset reds, the powered no-network control, and fixed per-card continuation prove outbound-only best effort without a hidden plan-mutation write (`notes/receipt-main-direct-validation-c1.md:13-16`; `notes/review-harness-qa-c1-r1.md:29`). |
| SC-11 | met | The c2 negative control reconstructs the runner defect precisely: at old `d7310f8`, an intentionally false late projection assertion printed `FAIL` but exited **0**; at repaired `0274000f`, the equivalent assertion exited **1**; after removal, the focused runner exited **0** and ended `all pass` (`notes/qa-fix-c2.md:13-32`; `notes/receipt-harness-backend-dev-fix-c2.md:7-58`). This red is a **reconstructed negative control, not a historical pre-implementation red**. The repaired test is unchanged at `d29899ad`; the exact signed T-01 seven-runner command and configured 40-file unit matrix are green, and the reconciled configured 72-file integration matrix is green at the pin. |
| SC-12 | met | Abandoned-task exclusion and existing abandonment semantics are green. The abandoned-card-admission red is an honestly labelled reconstructed mutation proof (`notes/receipt-harness-backend-dev-fix-c1-r1.md:12,16,20`; `notes/review-harness-qa-c1-r1.md:31,35`). |
| SC-13 | met | Lifecycle and ship transitions retain workflow-owned issue closure. The injected direct-close red is an honestly labelled reconstructed mutation proof (`notes/receipt-harness-backend-dev-fix-c1-r1.md:13,16,20`; `notes/review-harness-qa-c1-r1.md:32,35`). |
| SC-14 | met | Open-child holds and in-run refresh remain green. The stale-refresh red is an honestly labelled reconstructed mutation proof (`notes/receipt-harness-backend-dev-fix-c1-r1.md:14,16,20`; `notes/review-harness-qa-c1-r1.md:33,35`). |
| SC-15 | met | Pinned inspection traces one `gh_board.project` policy through status, INV-26 drift, and reconciliation; reset/resume metadata stays local; checkpoint callers are singular and ordered (`notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c1.md:40`; `notes/review-harness-code-reviewer-c1-r1.md:7-9`). No inspected production or caller path changed after c1. |
| SC-16 | met | Pinned inspection confirms DEC-138, DEC-203, DEC-220, DEC-224, and DEC-229 state current lifecycle truth, DEC-146 remains preserved, and the generated index agrees (`notes/research-BUG-1699-lifecycle-cards-goalcheck-validate-c1.md:41`). Neither decision file changed after c1. |

## Evidence disposition

- Historical fail-first evidence remains historical for SC-01–SC-07, SC-09, and the historical portions of SC-10.
- SC-08 and SC-12–SC-14 rely on criterion-specific reconstructed live mutants, explicitly not historical pre-implementation reds.
- SC-11 relies on the c2 reconstructed old-exit-0/new-exit-1 negative control, explicitly not a historical pre-implementation red, plus restored focused, signed T-01, configured unit, and final reconciled integration greens.
- The c0 verdict and the c1 SC-11 finding are superseded by their evidenced repairs. The c2 matrix finding is closed by exact pinned-manifest reconciliation and the supplied 72-file/0-failure/92.93-second exact-pin result.

Open questions: `[]`
