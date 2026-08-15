# STATE

## Current

- feature: FEAT-08-remove-cost-tracking
- run: ship phase, step 1 of 1 — A-5 written; returning for the user's re-signature
- squad: product
- status: awaiting_user

**Phase `ship` opened; `validate` closed at `notes/handoff-validate.md`.** Fifteen runs,
`cycles_used: 5` of 10. The fifth is the A-5 send-back, which product-lead reported against itself.

**The user ruled AMEND AND RE-SIGN on SC-05 and SC-06.** pm drafted **A-5** in `BRIEF.md` through
product-lead; the approved text of both criteria is left in place with a pointer, exactly as A-2 and
A-4 did, and the `## Approval` block is untouched — 297 insertions to `BRIEF.md`, none inside it.
**Both criteria now assert the property they were meant to test:** SC-05 in three clauses
(decoded-value equality, byte-level with the em-dash re-serialization named as a tolerance, and the
restored rule-surface diff clause over four literal files); SC-06 in three clauses scoped to the
seven feature directories that existed at `ae2443d`, returning the signed **89** and **67 of 67**
plus an empty-diff discriminator the counts lack.

**I re-ran all six clauses verbatim at my own tier.** SC-05: PASS/exit 0; live config EMPTY and the
template differing solely by the `—` escape; residual EMPTY/exit 1. SC-06: 89; 67 and 67; EMPTY.

**A-5 falsified three claims handed down as fact rather than pasting them forward — two were mine.**
Byte-identity does not hold for the template; my empty-diff-over-`runs/` suggestion is vacuous
(`git ls-tree` at `ae2443d` returns **0** tracked paths under any `runs/`), which I confirmed
independently; and product-lead's own cycle-0 sign-off missed that the draft had silently dropped
`check-state.sh` and `SKILL.md` from SC-05. That send-back is the fifth cycle.

**Discrimination, stated plainly: neither rewritten criterion would have failed at `ae2443d`** — both
are over-removal guards and SC-12 is the signed in-BRIEF precedent for the class. **Both CAN fail
against the delivered tree**, measured on ten scratch-only mutants. Nothing that cannot fail shipped.

**MF-1 is FIXED** (main-session-direct; no agent domain covers `.claude/commands/harness.md`) and is
committed here with A-5. Gates at the A-5 tip: unit 0, docs 0, state 0.

**SC-05 and SC-06 remain `not_met` and the goal-check remains FAIL.** I do not re-grade a criterion,
and the replacement text is not signed yet.

## Open Questions

IDs are not reused. Q2, Q4, Q5, Q7, Q8, Q18 are answered or ruled. **MF-1 is resolved.**

- **A-5 awaits the user's re-signature.** Until it lands, SC-05 and SC-06 stay `not_met`. On
  re-signature the goal-check re-grades them — pm, not me.
  Blocked on: the user.

- **Q27 (new)**: SC-06's hard-coded **67** can false-FAIL on a sanctioned `log_retention_days` prune
  of a historical run dir. pm asks the user to confirm the narrowing at signature.
  Blocked on: the user, at signature.

- **Q28 (new)**: SC-05 (c) resolves the signed text's undisambiguated `SKILL.md` to **three** literal
  files out of this repo's 20; a future `SKILL.md` documenting the cycle budget sits outside it.
  Blocked on: the user, at signature.

- **Q23 (new, cosmetic)**: A-4's "AWAITING RE-SIGNATURE" preamble is stale — `## Approval` already
  records A-4 as signed. Left unfixed; it is signed text and not worth a spawn.
  Blocked on: nobody.

- Q1 (carried): the briefing loses its only size signal. Issue **#79** filed, still unscheduled.
  Blocked on: the user, at the briefing.

- Q3 (carried, harness defect): a send-back gives the returning member a FRESH context, so
  `open_questions` it raised in its own previous DIGEST are unrecoverable to it. Raised twice more.
  Blocked on: nobody — in the briefing's backlog.

- Q6: SC-03 is repo-wide and passes today only because FEAT-09 sits in its own worktree — the hazard
  is dormant, not gone. Re-rooting `check-state.sh` via `CLAUDE_PROJECT_DIR` is **forbidden by user
  ruling** and was not proposed.
  Blocked on: nobody.

- Q9 (from eng-lead, raised twice): nothing detects live/template config divergence — the unit suite
  exited 0 on a half-stripped pair. **A-5 supplies partial cover** for the one key it guards.
  Blocked on: nobody — in the backlog.

- Q19 (harness defect): INV-4's task regex cannot tell a task DEFINITION from a REFERENCE.
  Blocked on: nobody — in the backlog.

- Q20 (raised independently by three agents): the **deployed global** rules still instruct every lead
  to run the deleted meter and write a `cost:` key. `/harness-deploy` after merge, **before** the
  queued preload-trimming batch.
  Blocked on: nobody — in the backlog, near-term.

- **My one substitution, still named rather than buried:** the three leads were not re-spawned to
  file domain reports for the briefing. All three ran inside the validate phase and their own digests
  are its source. Reversible for three spawns.
  Blocked on: the user, if they want it done properly.

- The full backlog is in the briefing. Anything not listed there dies silently.
