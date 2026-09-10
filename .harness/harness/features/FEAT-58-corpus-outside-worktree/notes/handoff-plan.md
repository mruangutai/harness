# Handoff — FEAT-58-corpus-outside-worktree, plan → fourth signature gate — written at 55d46767, seq-6

## Next

Present for the operator's fourth batched review. Not signable: the panel `planpanelc6-validator`
returned FAIL at `severity_max: high` with six new findings — PP-01..PP-04 high, PP-05 and PP-06
med — ALL on N-13, recorded unresolved in `plan.yaml`'s `panel` key. DEC-207 forbids a
pre-signature fix dispatch and no agent may risk-accept a high. PP-05's honest remedy edits SC-16,
approval-gated, so it is the operator's edit. **The budget is the live constraint: 8 of 10 cycles.
One fix-and-re-panel round fits; a second exhausts a HARD bound and the correct outcome then is
BLOCKED, not a quiet continuation.**

## Trust

- 12 tasks (N-01..N-10, N-12, N-13; N-11 retired, id a deliberate gap), 17 decisions, BRIEF 10 REQ / 15 criteria (SC-15 a deliberate gap), both approvals `pending` — orchestrator's own read of plan.yaml and BRIEF.md — verified-at 55d46767
- PL-01..PL-04 all verifiably RESOLVED at source by the panel, and the rest of the plan graded clean — runs/planpanelc6-validator/digest.md disposition table — verified-at 55d46767
- The post-fix goal-check PASSED all ten axes; its two med and two low findings were fixed BEFORE the panel read the draft — runs/goalcheckc6-product/digest.md, runs/fixgc6-product/digest.md — verified-at 55d46767
- `check-state.sh:22-49` resolves root from `_selfdir`, "never from the environment and never from the caller's cwd", so PP-01 is real — orchestrator's own read — verified-at 55d46767
- `grep -c HARNESS_REVIEW_SHA check-state.sh` = 0, so PP-05 is real — orchestrator's own measurement — verified-at 55d46767
- `core.hooksPath` is `--local` config and no tracked gitconfig exists, so it does NOT travel with a clone and PP-02 is real — orchestrator's own measurement — verified-at 55d46767
- `git ls-files -- '.harness/*/features'` returns 0 and `'.harness/*/features/*'` returns 3383, which is why GC6-02 was a real defect — orchestrator's own measurement — verified-at 55d46767
- Ledger 45 rows, nothing removed since the single named Q6 strike — panel cross-validated by chaining the three apply notes, a different method than the goal-check's — UNVERIFIED at this tier

## Dead ends

- The hardlink half — SC-15 and N-11's parts: struck by operator ruling, general weakness filed as #1638, re-proposing it is out of bounds — notes/answers-operator-c5.md Q6 — verified-at 55d46767
- A persisted uniqueness index: computed on demand at 0.0023 s median over 79 records — notes/answers-operator-c3.md Q2 — verified-at 55d46767
- Remedy (b) for the audit sets — restricting both to `feature.json`-carrying dirs: rejected, it buys a green audit by ignoring ten tracked directories, which is the defect this feature removes — notes/answers-operator-c6.md Q1 — verified-at 55d46767
- Correcting the FEAT-02 / FEAT-03 records: Arm B, era-exempt, both terminal — notes/answers-operator-c3.md Q3 — verified-at 55d46767
- Setting `fetch-depth: 0` on the CI `integration` job: rejected, it bends the runner to suit the measurement — notes/answers-operator-c5.md Q2 — verified-at 55d46767
- Asserting any gate's decision by exit code: both `merge-gate.py` and `branch-create-gate.sh` refuse by PAYLOAD at exit 0, recorded as the convention in D-17 — orchestrator's own source read — verified-at 55d46767

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanelc6-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c6.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: the operator disposes of PP-01..PP-06, edits SC-16 or rules otherwise on PP-05, then signs
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
