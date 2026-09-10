# Handoff — FEAT-58-corpus-outside-worktree, plan → third signature gate — written at 2b3ce8ef, seq-5

## Next

Present for the operator's third batched review. Not signable as it stands: the final panel
`planpanelfinal-validator` returned FAIL at `severity_max: high` with three NEW highs (PL-01,
PL-02, PL-03) and one med (PL-04) ranked to land with them, recorded in `plan.yaml`'s `panel` key
unresolved. DEC-207 forbids a pre-signature fix dispatch and no agent may risk-accept a high.
PL-02's remedy amends SC-09 in BRIEF.md, which is approval-gated — the operator makes that edit.
Two of the three highs share one root cause and PL-04 is it: nothing in the plan ever runs the
shipped `check-state.sh` against the real repository.

## Trust

- 11 tasks (N-01..N-10, N-12; N-11 retired into N-10), 15 decisions, BRIEF 10 REQ / SC-01..SC-14, both approvals `pending` — read from plan.yaml and BRIEF.md by the orchestrator — verified-at 2b3ce8ef
- The post-fix goal-check PASSED on all ten axes and D-2 enforcement SURVIVED the Q6 strike on both registered routes — notes/research-FEAT-58-goalcheck-plan-c5.md, runs/goalcheckfinal-product/digest.md — verified-at 2b3ce8ef
- 89 feature directories against 79 `feature.json` records, so PL-01's key mismatch is real — orchestrator's own `ls | wc -l`, both counts — verified-at 2b3ce8ef
- `branch-create-gate.sh` `deny()` at `:63-66` prints its payload then `exit 0`, and the allow path at `:91-92` is also `exit 0`, so PL-03 is real — orchestrator's own read of the source — verified-at 2b3ce8ef
- Both panel readers RAN and both returned PASS on their own charters; the FAIL is the new findings alone — runs/planpanelfinal-validator/digest.md — verified-at 2b3ce8ef
- Ledger 41 rows after ONE deliberate removal under Q6, recounted by the scope reader by direct row enumeration — runs/planpanelfinal-validator/digest.md — UNVERIFIED at this tier
- SC-15 exists in BRIEF.md only as its own strike record at `:106-116`; the live criteria are SC-01..SC-14 — orchestrator's own grep — verified-at 2b3ce8ef

## Dead ends

- The hardlink half — SC-15, N-11 PART 4, PART 5 (a)(b) and the `check-domain.sh` `_hardlink_plan` widening: struck by operator ruling, the general weakness filed as #1638, and re-proposing it is out of bounds — notes/answers-operator-c5.md Q6 — verified-at 2b3ce8ef
- A persisted uniqueness index: computed on demand at 0.0023 s median over 79 records; re-proposing a tracked artifact is what the ruling forbids — notes/answers-operator-c5.md, answers-operator-c3.md Q2 — verified-at 2b3ce8ef
- Correcting the FEAT-02 / FEAT-03 records: Arm B, era-exempt; both terminal, so correcting invents a value that never existed — notes/answers-operator-c3.md Q3 — verified-at 2b3ce8ef
- Setting `fetch-depth: 0` on the CI `integration` job: rejected on the record — it bends the runner to suit the measurement, and SC-12 asserts the runner is unchanged — notes/answers-operator-c5.md Q2 — verified-at 2b3ce8ef
- Recording any residual about `qa-*` probe trees in D-10 or N-02: the DoD sentence was withdrawn at source and the scope guard is correct behaviour — .harness/notes/dod-worktree-corpus-2026-09-10.md:136-143 — verified-at 2b3ce8ef

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanelfinal-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c5.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: the operator disposes of PL-01..PL-04 and amends SC-09 or rules otherwise, then signs
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
