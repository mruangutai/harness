# STATE

## Current

- feature: FEAT-06-team-layer-inv6
- phase: validate
- run: runs/amend2-product/ (complete, PASS)
- squad: product
- status: awaiting_user

**ONE THING IS LEFT AND IT IS THE USER'S: SC-13, the UAT.** 14 of 15 SCs are met. Every gate is
green — unit 0, docs 0, `check-state.sh` zero violations — each re-run at the orchestrator's own
tier, not taken on report. **BRIEF and PLAN also await the main session's RE-SIGNATURE** after the
amendments; only it writes `## Approval`.

**SC-05 is CLOSED** by the main session's one-line fix, and the trap held: the assertion went into
`test-harness-yaml-corpus.py` (now 13 checks), not `test-team-catalog.py`, which still names exactly
**10** as T-07's signed verify requires.

**`personas:` and `filter:` are both deleted from `build.yaml` on the user's rulings, and both were
right.** SC-07 had begun passing **vacuously** (an absent set is trivially a subset) and SC-08 had
become **unsatisfiable**; both are reworded to the substance the shipped checks prove. **EMF-2 is
completed, not reversed** — the finding was that the filter was not evaluable; the resolution is
that it is not needed. **T-04's signed `verify:` was RED on two different keys in succession**
(`KeyError: 'personas'`, then `KeyError: 'filter'`) and now runs green **while asserting their
absence**, so it is strictly stronger than the original. Executed here at exit 0, not asserted.

**THE SITE LIST WAS SHORT THREE TIMES ON THIS FEATURE** — 4 named comment sites vs 6 real; 2 named
persona sites vs 5, the missed one being T-04's verify; 4 named filter sites vs 6, with 2 anchors
already drifted. The orchestrator's own re-grep caught the remainder each time. **The layer a site
list forgets is the verification criterion.**

**COST IS OVER BY A MULTIPLE: $253 measured of the $100 allowance (2.5x), ceiling $403.** The
orchestrator's own session is **$139 of it — 55%**, the largest single line, and DEC-148's
square-of-session-length effect measured rather than argued. Nine of ten build tasks also ran at
depth-0 and are not separable, so the true total is higher. No figure is invented.

**Two things not run, neither a budget cut:** feature-close distillation — its **precondition is
unmet**, since it runs after the SCs pass and SC-13 has not; and the three-lead parallel briefing
report, because every digest is already held and eng-lead did no build or validate work.

**Two harness gaps found this run, both for the backlog:** no gate reads team-file field content
beyond `test-team-catalog.py`'s ten named checks, so the `filter:` deletion passed every gate; and
the `SubagentStop` hook does not reject a member `artifact:` pointing at a non-digest file —
**measured**, since `validate-digest.py` run on `PLAN.md` returns BLOCKED, so the validator catches
it and the hook is not invoking it there.

**Five commits on `main`, not pushed, not merged.** `review_sha` is pinned at `9f87c48`; HEAD has
moved past it, which is fine — INV-6 requires pinned, not equal-to-HEAD.

## Open Questions

- **SC-13 (BLOCKING, the user's alone):** read `teams/build.yaml` and `SKILL.md:40-47` and rule.
- **Re-signature (BLOCKING, main session):** BRIEF and PLAN amended; both need `## Approval` rewritten.
- Non-blocking: the 11-item proposed backlog in the briefing, filed in ONE pass at ship acceptance
  per the user's instruction. Anything struck there dies silently, so the list is complete.
