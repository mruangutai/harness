# Handoff — FEAT-58-corpus-outside-worktree, plan → signature — written at 04765199, seq-7

## Next

The plan is presented for signature and the plan phase is DONE. The operator signs with
`plan-merge.py sign-approval`, recording the open findings in `approval.rulings` and ruling on
H-01 — accept it, or convert it to a build-phase task on N-13 carrying a MISSING-producing
mutation. On signature the next phase is build, whose entry step is `gh-sync.py open <feature-dir>`
before any task is dispatched. No further planning work is owed and no fix round remains: the
operator ruled cycle 8 the last one and the panel returned NOT STRUCTURAL with no new high.

## Trust

- 12 tasks (N-01..N-10, N-12, N-13; N-11 retired, id a deliberate gap), 17 decisions, BRIEF 10 REQ / 15 live criteria (SC-15 a deliberate gap), both approvals `pending` — orchestrator's own read — verified-at 04765199
- The panel's structural answer is NOT STRUCTURAL, with a producing mechanism enumerated for all ten REQs — runs/planpanellast-validator/digest.md, recorded at plan.yaml:676-696 — verified-at 04765199
- No new high or critical from the final panel; `scope`'s FAIL is on the standing H-01 alone under a severity_max rule — runs/planpanellast-validator/digest.md — verified-at 04765199
- The goal-check returned PASS with nothing structural, and the panel confirmed all six of its findings correctly graded — notes/research-FEAT-58-goalcheck-plan-c8.md — verified-at 04765199
- `check-state.sh:22-49` resolves root from `_selfdir`, never from cwd; `grep -c HARNESS_REVIEW_SHA` = 0; `core.hooksPath` is local config and not cloned; 89 dirs against 79 records — orchestrator's own measurements — verified-at 04765199
- Always-green set is H-01 and M-01; build catches M-02 and L-03 — panel, tested hardest on M-01's claim by two independent routes — UNVERIFIED at this tier
- Ledger 45 rows, no row lost, both evidence-form demotions still visible — goal-check and panel, by different methods — UNVERIFIED at this tier

## Dead ends

- Another fix round: the operator ruled cycle 8 the last, on the measured ground that each amendment hands the panel new text to falsify, so every round manufactures the next — notes/answers-operator-c8.md Q8 — verified-at 04765199
- The hardlink half, a persisted uniqueness index, remedy (b) for the audit sets, correcting the FEAT-02/FEAT-03 records, `fetch-depth: 0` on CI, and asserting any gate's decision by exit code: each rejected on the record with its reason — answers-operator-c3/c5/c6, D-14, D-17 — verified-at 04765199
- Migration/convergence, the corpus-root anchor, the fifteen-reader ledger, reflink, byte-count criteria, the incremental-sweep cache: all six killed by the DoD and confirmed not to have crept back across three rounds of growth — goalcheck axis 10 — verified-at 04765199

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanellast-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/research-FEAT-58-goalcheck-plan-c8.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: the operator signs the BRIEF and the plan, recording the open findings and ruling on H-01
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
