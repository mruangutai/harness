# Draft plan — FEAT-2340

The constrained two-task draft passes plan-merge check: exit 0, two tasks, four anchors, zero failures. Status is plan; approval remains pending. Three independent readers follow; this is not a panel or implementation verdict.

## Scope and evidence

- Operator authority: owner-checkout .harness/notes/grilling-gate-naming-one-pattern-2026-11-22.md, Destination and Settled; issue #2340 https://github.com/mruangutai/harness/issues/2340. Inventory sections 1–4 and 7 supply the scoped findings at e239d88156c508c948d49cd31238ea13b3b39865. Section 5 is excluded.
- T-01 owns only the two simplify angle leaves and model-the-domain.md; naming bullets have one home. T-02 owns only check-domain.py and depends_on [T-01]. Named non-greedy handoff groups, case-asymmetric compilation of one plan text, aligned literal respellings and the frozen fixture exclusion are explicit in dispatch intent.
- Every literal path was queried using control-plane check-domain.py --resolve: all three .agents/skills guidance paths returned NOBODY, exit 0; gate source returned harness-backend-dev and harness-dev-ops, exit 0. Documentation consult-when identifies harness-documentor expertise for T-01 but cannot grant ownership. Both tasks therefore execute main-session-direct, T-02 under DEC-174 with harness-backend-dev spelling from FEAT-2274. Main owns orchestration under the entirely-direct rule.
- T-01 uses docs; T-02 uses scaffolding for a behavior-preserving structural refactor, not new runtime logic. Both configured matrix floors are empty and TDD-exempt. T-02 explicitly adds all existing check-domain integrations above that floor; choosing logic would require unit evidence no check-domain unit suite supplies. No tests are rewritten. Baseline and post-refactor receipts belong to execution, not this draft; no integration suite was run here.
- Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent. Product AGENTS.md explicitly maps spec and decision authority to .harness/harness/docs/SPEC.md (consulted section 4.2) and DECISIONS.md; no architecture document is invented. Task intents carry those read inputs and the missing-guidance disclosure.
- Keep dispositions cover DEC-174, DEC-179, DEC-195, DEC-234 and DEC-235. No hard-to-reverse new choice earns a D-NN; settled implementation constraints are not inflated into decisions. No decision text changes, so no task owns DECISIONS.md.

## Verification receipt and boundaries

Final command: python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2340-gate-one-pattern-per-concept/.harness/harness/features/FEAT-2340-gate-one-pattern-per-concept/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2340-gate-one-pattern-per-concept

Observed final exit 0: T-01 three anchors resolved; T-02 one anchor resolved; zero failures. An earlier proposal failed YAML parsing because a colon-ending quoted-content anchor was unquoted; nothing landed. An intermediate disposition check failed because a quotation crossed a physical source line; the corrected contiguous verbatim clause passed. All writes used plan-merge; stdout was captured. No APPROVAL-RESET receipt occurred, so no gh-sync ran. No approval or panel mapping was authored.

Writer-triggered check-state also reports unsigned BRIEF and absent Build-entry receipt, expected at this draft station; its first invocation additionally reported an unrelated /private/tmp/t03-main worktree, absent from later writer output. These are not a successful build claim and were not repaired outside scope. No builds, tests, lint or formatting ran.

## Principles applied

- Redesign From First Principles: express maintainability as an outcome while consolidating the two actual same-file concepts, not adding a wrapper or new authority.
- Outcome-Oriented Execution: prevention lands first with an explicit dependency; final regression evidence remains on the terminal gate task, without compatibility aliases.

## Open questions

None for the settled scope. At ship, excluded cross-file groups and identical non-path matchers become backlog issues for later sequential patches; external short renames and mechanical lint remain future work, never open SCs here. Four SCs cover two perspectives; one uses integration evidence, three use pinned-content/history inspection, none requires personal UAT.
