# Handoff — FEAT-58-corpus-outside-worktree, plan → halted — written at 402e23ac, seq-2

## Next

Do NOTHING until the main session dispatches a new mission naming a new answers file — the operator
halted this run to rework the definition of done from scratch, and an injected message is explicitly
not that dispatch. When it comes, step zero is deciding whether BRIEF.md is amended or replaced: the
operator's direction is a fresh BRIEF and a fresh plan at cycle 0 carrying this run's findings as
evidence, because 8 of 10 cycles here were spent against a problem statement now believed wrong.

## Trust

- BRIEF.md and plan.yaml carry the operator's cycle-1 answers and the cycle-2 goal-check gaps and nothing later — `git show 402e23ac` vs working tree, 4 files changed — verified-at 402e23ac
- Panel cycle 2 PASSED, severity_max med, must_fix empty, both readers ran — runs/planpanel2-validator/digest.md — verified-at 402e23ac
- 16 tasks, 15 decisions, 12 REQ / 15 SC all traced, depends_on acyclic, check-plan-routes 0 violations — harness_yaml.load_plan + check-plan-routes.py, run by the orchestrator — verified-at 402e23ac
- Three live defects outliving this plan: merge-gate.py:169, branch-create-gate.sh:38/:88-90, check-domain.sh:2150 — notes/receipt-harness-backend-dev-{arch,denialtier}-eng.md — verified-at 402e23ac
- 19 of 30 standing checkouts already merged, so most of the footprint is housekeeping — operator, measured at abff2a84 — UNVERIFIED
- FEAT-02 and FEAT-03-subissue-mirror both claim feat/harness-native-foundation — operator, measured at abff2a84; eng re-derivation concurs from merge commits 37a8a66e / 04a57fcf — UNVERIFIED

## Dead ends

- The incremental/changed-slice sweep with a version-keyed marker: withdrawn by the operator as solving the wrong problem — Main IRC 2026-09-10 — verified-at 402e23ac
- Raising max_total_cycles to finish re-shaping this plan: ruled the wrong instrument — Main IRC 2026-09-10 — verified-at 402e23ac
- Reflink/clonefile as the mechanism, and any du/df byte criterion: both satisfied by the excluded mechanism — .harness/notes/grilling-worktree-corpus-2026-09-09.md "Out of scope" — verified-at 402e23ac
- Executing any of this through a team run: enforcement-layer changes are made directly — DECISIONS.md DEC-174, corrected in the grilling artifact at :89-92 — verified-at 402e23ac

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/notes/answers-operator-c1.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/rederive-eng/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanel2-validator/digest.md

## Done when

Scope: a new mission naming a new answers file arrives and the BRIEF is amended or replaced
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
