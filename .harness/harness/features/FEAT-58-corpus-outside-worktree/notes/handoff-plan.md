# Handoff — FEAT-58-corpus-outside-worktree, plan → second signature gate — written at 5dda443b, seq-4

## Next

Present the plan for the operator's second batched review. It is not signable as it stands: the
re-run panel `planpanel4-validator` returned FAIL at `severity_max: high` with three NEW high
findings (VL-01, VL-02, VL-03), recorded in `plan.yaml`'s `panel` key at disposition open. DEC-207
forbids a pre-signature fix dispatch and no agent in this chain may risk-accept a high. All three
are correctable spec defects with named remedies, not risk questions. Four earlier findings
(F-10..F-13, forward-mapped to VL-05..VL-08) are still honestly owed and need a fold-or-defer
decision, and VL-07 needs a DoD amendment only the operator can make.

## Trust

- 12 tasks (N-01..N-12), 13 decisions, BRIEF 10 REQ / SC-01..SC-15, `status: plan`, both approvals `pending` — read from plan.yaml and BRIEF.md by the orchestrator — verified-at 5dda443b
- All nine of the operator's batched findings (F-01..F-09) verified ANSWERED in the written artifacts by both panel readers independently, F-06 against merge-gate.py source — runs/planpanel4-validator/digest.md disposition table — verified-at 5dda443b
- The three weight-bearing proofs survived two rounds of amendment and remain red-capable; none compares against a moving ref — runs/planpanel4-validator/digest.md dispatch answer 3 — verified-at 5dda443b
- Assertion ledger 36 in, 42 out, no row dropped, two evidence-form demotions visible in the evidence column — runs/consolidate-eng/digest.md second block, re-audited by the panel — verified-at 5dda443b
- Cone mode strips sibling `.harness` subtrees; a FILE path in a cone-mode set is a hard fatal at exit 128 — orchestrator's own probes, git 2.50.1 — verified-at 5dda443b
- `.github/workflows/tests.yml:50` is `actions/checkout@v4` with no `fetch-depth`, and `integration` is the sole required branch-protection context — validator lead, who reconciled VL-02 med->high on it — UNVERIFIED
- No goal-check has graded the POST-fix draft; `research-FEAT-58-goalcheck-plan-c3.md` is the pre-fix grade carrying GC-01 at high — panel finding VL-09, correcting my own dispatch claim — verified-at 5dda443b

## Dead ends

- A persisted uniqueness index: ruled out by the operator; computed on demand at 0.0023 s median over 79 records, and re-proposing a tracked artifact is what the ruling forbids — notes/answers-operator-c3.md Q2 — verified-at 5dda443b
- Correcting the FEAT-02 / FEAT-03 records: Arm B, era-exempt; both terminal, so correcting invents a value that never existed — notes/answers-operator-c3.md Q3 — verified-at 5dda443b
- Asserting a non-zero exit for merge-gate.py: it has zero `sys.exit` calls; `deny()` prints a PreToolUse JSON payload — operator's own measurement, notes/answers-operator-c3.md Q4 — verified-at 5dda443b
- Deferring any cross-feature scan site: all nine choke points are in, none deferred — notes/answers-operator-c3.md Q1 — verified-at 5dda443b
- The migration/convergence task, the corpus-root anchor, the fifteen-reader ledger, reflink, every byte-count criterion, the incremental-sweep cache: all six re-derived dead and confirmed not to have crept back during the growth — runs/arch2-eng/digest.md, goalcheck axis 9 — verified-at 5dda443b

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanel4-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c3.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: the operator disposes of VL-01, VL-02 and VL-03, rules on F-10..F-13 and VL-07, then signs
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
