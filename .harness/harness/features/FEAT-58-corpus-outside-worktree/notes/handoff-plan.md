# Handoff — FEAT-58-corpus-outside-worktree, plan → signature gate — written at d6a67f5a, seq-3

## Next

Present the plan for the operator's signature. It is NOT signable as it stands: the adversarial
panel returned FAIL at `severity_max: high` with six open high findings (F-01..F-06, recorded in
`plan.yaml`'s `panel` key with disposition `open`). Under DEC-207 those cannot be fixed by a
pre-signature dispatch and no agent may risk-accept one — they enter the operator's ONE batched
review pass, which disposes of each by ordering a fix or by `sign-approval --overrule PF-ID:<reason>`.
Two of them (F-01, F-02) are genuine scope decisions the operator must make, not defects an agent
can correct. D-06 also awaits the operator's arm pick, and picking Arm A also signs one named
pathspec exclusion.

## Trust

- 9 tasks (N-01..N-09), 12 decisions, BRIEF 10 REQ / SC-01..SC-13, `status: plan`, both approvals `pending` — read from plan.yaml and BRIEF.md by the orchestrator — verified-at d6a67f5a
- All seven binding items each hold their own REQ and >=1 SC, none merged — BRIEF.md:88-99 coverage table, cross-read against the REQ text at :50-79 — verified-at d6a67f5a
- Panel recorded: `last_run: planpanel3-validator`, cycle 0, 13 findings, 6 at `severity: high`, every disposition `open` — grepped in plan.yaml — verified-at d6a67f5a
- Cone mode strips sibling `.harness` subtrees: cone `top` + `.harness/harness/features/FEAT-A` materialises ONLY `top/f`, `.harness/root.md`, `.harness/harness/features/FEAT-A/a.md` — orchestrator's own probe, git 2.50.1 — verified-at d6a67f5a
- A FILE path in a cone-mode `sparse-checkout set` is a hard fatal at exit 128 without `--skip-checks`; with it, `list` round-trips exactly — orchestrator's own probe, git 2.50.1 — verified-at d6a67f5a
- 36 of 36 assertion-ledger rows landed after 19->9 consolidation, re-audited by an inverted method — runs/planpanel3-validator/digest.md, corroborating runs/goalcheck3-product — verified-at d6a67f5a
- The three weight-bearing proofs are each red-capable, and the positive controls now see a NEW nested subtree, not only the one defect that was caught — runs/planpanel3-validator/digest.md — verified-at d6a67f5a
- The goal-check graded the PRE-amendment plan; no goal-check has read the amended draft. `check-state.sh:551-558` grades that a WARN at signature — runs/panelrecord3-product digest Q1 — UNVERIFIED

## Dead ends

- The migration/convergence task, the corpus-root anchor concept, the fifteen-reader ledger, the reflink/clonefile mechanism, every byte-count criterion, the incremental-sweep cache: all six re-derived and confirmed dead, none forced back — runs/arch2-eng/digest.md "Item 7 — the kill list" — verified-at d6a67f5a
- Adding the branch-uniqueness index to the sparse cone: measured a hard fatal at exit 128; it resolves at the OWNER ROOT — orchestrator probe, git 2.50.1 — verified-at d6a67f5a
- Repairing `check-domain.sh:2150` as D-2's enforcement: D-2 is already enforced on BOTH write routes through `harness_boundary.classify()`; `:2150` governs a REPORT and folds into the D-3 task — runs/arch2-eng/digest.md Ruling 1 — verified-at d6a67f5a
- Executing any of this through a team run: DEC-174 puts hooks, validators, gate scripts AND their tests with the main session; all nine tasks are `main-session-direct` — plan.yaml D-07 — verified-at d6a67f5a
- Editing plan.yaml's top-level `lanes:` block: unwritable by ANY route, and nothing reads it — plan-merge.py:121/:1249 plus a zero-match grep under bin/ and hooks/ — verified-at d6a67f5a

## Working set

- .harness/harness/features/FEAT-58-corpus-outside-worktree/plan.yaml
- .harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/planpanel3-validator/digest.md
- .harness/harness/features/FEAT-58-corpus-outside-worktree/runs/consolidate-eng/digest.md
- .harness/notes/dod-worktree-corpus-2026-09-10.md

## Done when

Scope: the operator disposes of all six open high panel findings and picks D-06's arm, then signs
Authority: approval:.harness/harness/features/FEAT-58-corpus-outside-worktree/BRIEF.md#Approval
