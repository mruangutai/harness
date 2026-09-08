# Receipt — harness-ai-dev — SIMPLIFICATION angle — BUG-148-gate-record-correction

**BLUF: SIMPLIFICATION: no finding.** Both corrected passages are already at the length the
facts need; the one candidate restatement I checked turns out to be load-bearing sentence
structure, not duplication.

## What I read

- Skill `## SIMPLIFICATION` section (harness-simplify/SKILL.md:49-60).
- Plan `decisions:` D-01, D-04, D-05 and tasks T-01 (intent lines 120-164, verify 110-119) and
  T-02 (intent lines 187-236, verify 177-186) — `plan.yaml`.
- DEC-174 region, full span read: `.harness/harness/docs/DECISIONS.md:4245-4330` (heading at
  4302 through "Self-hosting caught none of these" paragraph ending ~4330; corrected sentence
  at **4308-4317**).
- FEAT-05 `STATE.md` `## Current` section: `:1-27` (corrected passage at **14-20**).
- Full three-file diff (41c16c7..f60d5d2), restricted to the product paths.

## Analysis

The DEC-174 sentence states the three-real-gates fact **twice**: once at 4308 ("`run-unit-tests.sh`,
`check-docs.sh` and `check-state.sh` were green") and again at 4316-4317 ("Those three real gates
were green while:"). This is the shape the skill asks me to hunt for — same fact, different
spelling, one passage.

I checked whether the second instance can be dropped. It can't, without breaking the passage:
the first mention exists to introduce the fourth-gate contrast ("...were green, **and the
fourth gate**... was no gate at all"); the second is the antecedent clause for the trailing
`while:` connective the contract requires (T-01 intent: "keep the sentence ending with `while:`
so the three-bullet defect list... reads as its continuation"). Between the two mentions sits
the entire mechanism explanation (argv fall-through, `ffbdbfa1`, the read-only form) — nine
lines of intervening text. Deleting the second mention leaves `while:` dangling with no
subject-verb clause of its own (e.g. "...`DECISIONS-INDEX.md`\`, while:" — ungrammatical). This
is the skill's own carve-out: "an anchor that took rounds to get right is not complexity to be
trimmed" — the restatement is the anchor for the required `while:` ending, not a drifting
duplicate of a rule.

No other candidate found in either passage:
- The "was no gate at all: `--check` was never a supported mode" clause (DECISIONS.md:4309-4310)
  is assertion-plus-explanation via colon, not the same fact twice — and the second half is a
  verify-grepped literal (`never a supported mode`), so it's required text regardless.
- STATE.md's "**Corrected 2026-09-06 under BUG-148:**" (line 15) reads like a narrated-change
  clause, but D-05 ruling (1) and T-02's intent (plan.yaml:197, invariant list requiring
  `2026-09-06`) both require exactly this inline dated marker as the STATE.md-appropriate form
  of "current truth" — settled, not a finding.
- No dead reference to a pre-revision shape in either passage: both correctly describe the
  argv-fallthrough mechanism as current fact, nothing points at a shape the rewrite removed.
- DECISIONS-INDEX.md changes are pure regenerated-anchor shifts (`@4424`→`@4432` etc.),
  mechanical, nothing to simplify.

I did not propose a shortening; there is no BEFORE/AFTER to give.

## Cross-record repetition (settled, not re-flagged)

The mechanism clause and the `--stdout | diff` form repeat, near-verbatim, across DECISIONS.md
and STATE.md. Per the dispatch's settled item 3 (D-05 ruling 3) and item 2, this is required and
out of scope — not reported as a finding.

**SIMPLIFICATION: no finding.**
