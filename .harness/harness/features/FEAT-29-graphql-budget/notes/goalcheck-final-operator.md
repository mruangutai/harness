# FEAT-29 — final grade on SC-08 and SC-09

Operator rulings, 2026-08-20, recorded by the main session after the orchestrator was stopped at
run 20 of 20 with its cycle budget exhausted. The final independent grade it was about to dispatch
never ran. These two grades stand in its place and their provenance is stated rather than implied:
**neither is an independent agent grade.**

## SC-09 — MET

Graded met on the operator's ruling, on a mechanical check that anyone can repeat in one command.

    pin=27b85f2
    git show 27b85f2:CLAUDE.md | grep -c "wait loop"   -> 1
    git show 27b85f2:CLAUDE.md | grep -c "Monitor"     -> 1

The rule is present in the COMMITTED tree, forbids shell wait loops outright, and names Monitor
and `run_in_background` as the replacements. Both dropped conjuncts — the 10-second conduct clause
and the 2-points-per-poll citation — are struck in place in `BRIEF.md` with their reasons.

Independence was weighed and declined. The criterion reduces to a grep against a committed file,
so a second reader repeats the command rather than exercising judgement. That is not true of
SC-08, and the two were treated differently on purpose.

## SC-08 — UNMET, and shipped that way deliberately

The operator declined to reword it. The record shows it failed. What follows is what was and was
not achieved, so a later reader is not left to guess which.

**Limb one — the scoped deliverable — is DONE and verified.**
`.harness/notes/grilling-graphql-cost-2026-08-10.md` carries the strike, the corrected 490-506
range, and all three governing conditions: board 3, 473 items, commit `6bbd706`. 608 is recorded
as the contaminated upper bound it is.

**Limbs two and three are UNGRADABLE by the method the criterion itself specifies.** They quantify
over every in-force document, asking whether it names a cost figure without its condition.
Deciding that requires judging, for every number in the corpus, whether it is a cost figure and
whether nearby text is its condition. No mechanical check does either.

This was measured, not assumed. A scan over the four live feature directories and `.harness/notes`
returned eight candidate documents. Three were inspected and **all three were false positives** — a
line number, a spawn count, and a timestamp. The scan is therefore evidence of nothing, in either
direction. It cannot show the corpus is dirty and it cannot show it is clean.

**Why it stays unmet rather than being narrowed.** The scoped work was done. The corpus sweep was
never in any task's `files:` and has no tooling. Rewording the criterion so that the part that was
achieved is all it ever asked for would be deciding the verdict first. The honest record is a
criterion that failed, next to a plain statement of what was delivered.

**What would close it:** a tool that enumerates cost claims from the claim rather than the call's
spelling. That distinction is not incidental — the orchestrator's own corpus sweep missed a
falsified figure in spawn-injected Expertise because it grepped `item-list` and `project_items`
and the offending line named neither.

## Provenance, stated plainly

Ten criteria. Eight graded met by pm's goal-check. SC-08 and SC-09 were graded UNMET by that
goal-check, amended afterwards on operator rulings, re-graded UNMET again, amended again, and
carry these two operator grades. No agent has graded either under its final wording.
