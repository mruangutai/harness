# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: BATCHED FIX APPLIED, cycle 0, 2026-09-10. The operator's four answers (`notes/answers-operator-c3.md`) landed whole and the panel independently verified all nine of them ANSWERED in the written artifacts. On disk: BRIEF.md at 10 REQ / SC-01..SC-15, plan.yaml at 12 tasks (N-01..N-12) and 13 decisions, `status: plan`, both approvals `pending`. Handoff: notes/handoff-plan.md
- squad: none — awaiting the operator's second batched signature review
- status: awaiting_user
- gate: the re-run panel (`planpanel4-validator`) returned FAIL, `severity_max: high`, 9 findings — 3 high (VL-01, VL-02, VL-03), 5 low, 1 info — recorded in plan.yaml's `panel` key at disposition open, with the previous panel's 13-row disposition preserved under `panel.prior_cycle`. All three highs are new defects that did not exist when the last panel ran. DEC-207 forbids a pre-signature fix dispatch and no agent may risk-accept a high, so they enter the operator's batched review.
- budget: cycles_used 5 of 10. runs 35 of a 20-run informational budget — INV-22 notes a long feature and never stops one.

## Open Questions

- THE THREE HIGHS, all correctable spec defects with named remedies, none risk-accepted: VL-01 — N-11 orders the hardlink scan to REFUSE on an unresolvable corpus root and N-10 has `corpus_root()` RAISE, but `_hardlink_plan` wraps only `os.stat` (`check-domain.sh:1907-1922`), the glob sits outside it and `_plan_route`'s sole caller is bare at `:1949`, so the raise exits 1 — which that file's own header at `:14` declares NON-blocking, and the write proceeds. VL-02 — `.github/workflows/tests.yml:50` is `actions/checkout@v4` with no `fetch-depth`, a depth-1 shallow clone, so N-09's pinned-range clauses red the `integration` job, which is the sole required branch-protection context with `enforce_admins` true; that reds every PR in the repository and falsifies SC-12's own claim that a CI runner is unchanged. VL-03 — N-06 mandates a marker on a site N-12's narrowed subject cannot detect, making N-12's verify unpassable for a correct N-06 implementation.
- STILL HONESTLY OWED and never in the operator's Q1-Q4 batch: F-10..F-13, forward-mapped to VL-05..VL-08. Fold into the next fix pass, or defer each by name at signature.
- ONLY THE OPERATOR CAN DECIDE: VL-07 — the DoD note states "A QA probe worktree now gets stripped automatically without QA knowing", which N-02's `_ID_RE` scope guard deliberately does not deliver because probe trees are named `qa-*`. Amend the DoD sentence, or knowingly keep it with the residual recorded in D-10 and N-02.
- MY OWN RECORD ERROR, corrected by the panel as VL-09 and not softened: my panel dispatch asserted the goal-check had been re-run and was clean. It had not — `notes/research-FEAT-58-goalcheck-plan-c3.md` is the PRE-fix grade carrying GC-01 at high, and `fixgoalcheck-product` applied both remedies afterwards. The panel verified both landed at source, but no goal-check has graded the post-fix draft, so the stale-grade WARN the operator wanted removed is still not removed.
- SCOPE I ADDED on my own ruling rather than on the operator's answers, flagged for striking: SC-15 and N-11's hardlink half. Striking it costs SC-15 and N-11 PART 4 / PART 5 (a)(b) and nothing else.
- Filed as their own tickets, untouched here: the unwritable `lanes:` key, the permitted `Write` outside every governed root, the `yield null data` defect, and `check-state.sh:762-766` grading the operator's budget reset as a violation.
