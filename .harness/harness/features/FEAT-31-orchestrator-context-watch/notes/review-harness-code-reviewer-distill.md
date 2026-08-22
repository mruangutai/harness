# Distillation — harness-code-reviewer — FEAT-31

## Dispositions of the three relayed candidates

1. **ACCEPTED, craft, Outcomes O-10.** "Disagreement had two correct sides" generalizes to a
   severity-reconciliation rule for merged findings, not a disagreement-adjudication rule per se —
   see below for why the disagreement framing itself was rejected.
2. **ACCEPTED, craft, Outcomes O-10** (merged into the same entry as #1 — same underlying
   mechanism: two reporters, one root cause). Text: "WHEN your finding and a peer's finding land
   on the same code site via different mechanisms DO check for one shared root cause before filing
   separately — merge into one finding and set severity to whichever side is more precisely
   verified, never an average of two guesses." This is the panel's own reconciliation move
   (security's demonstrated fixture + my untested-exception finding, severity reconciled DOWN, not
   averaged) turned into a rule.
3. **ACCEPTED, but at REPOSITORY tier, not craft** — `.harness/harness/expertise/harness-code-reviewer.md`
   Gotchas G-04. The general form ("does a self-test that reads real state actually run in any
   gate") is craft-shaped, but craft Patterns and Gotchas are both already at their 15-entry cap
   and the merge tool has no way to shrink a full section (see finding below), so I recorded the
   concrete, still-generalizable, actionable form instead: check `run-unit-tests.sh`'s two named
   script arrays by exact name. Verified directly: `verify-context-watch-live.py` is absent from
   both `UNIT_SCRIPTS` and `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:17-18`, grepped).

**Reviewer-disagreement candidate, standalone, REJECTED.** The literal "two correct sides, name
which claim each answers" framing is not novel enough to buy a slot on its own: O-07 already
teaches the general principle (state two true things about the same fact separately rather than
collapsing to one). Folding candidate 1 into candidate 2 above captures the part that *is* new
(severity arithmetic on merge) without adding a second, overlapping entry.

**My own four candidates from this run's note** (settled-obligation check, depth-direction
correction, the med finding, the docstring-anchor fix): the depth-direction and docstring-anchor
lessons are already covered verbatim by P-01 and G-08 respectively — not re-added. The med finding
is the same mechanism as relayed candidate 2 — covered by O-10. The settled-obligation-literal-clause
check (verify a decision/research note's *exact* required clauses against shipped text, not just its
spirit) is genuinely distinct from P-03/P-14 but I did not force a slot for it given the tool
constraint below; noted here so it isn't lost if a slot opens.

## Tool defect found and verified empirically (not worked around)

`expertise-merge.py` is a pure add-only union: it never removes an id, and a same-id-different-text
proposal is a hard CONFLICT (exit 7), not an overwrite. There is no code path that implements
`drop` or a real `replace`, despite `harness-distill/SKILL.md`'s documented ops schema listing
`add | replace | merge | drop`. Confirmed live against the real craft file: proposing one new
Patterns id at the existing 15/15 cap returned `CAP EXCEEDED section=Patterns cap=15
union_size=16`, exit 8, and the file's md5 was unchanged before/after (checked). Both craft
Patterns and craft Gotchas are at their caps with no way to curate them down through the sanctioned
tool. Raised as `open_questions` below — this is a harness defect, not mine to route around.

## Counts

| File | Section | Before | After |
|---|---|---|---|
| craft | Patterns | 15/15 | 15/15 (unchanged — capped, no drop path) |
| craft | Gotchas | 15/15 | 15/15 (unchanged — capped, no drop path) |
| craft | Outcomes | 9/10 | 10/10 (+O-10) |
| craft | Open | 0/5 | 0/5 |
| repo | Gotchas | 3/15 | 4/15 (+G-04) |
| repo | all other sections | 0 | 0 |

`check-expertise.sh` clean on both files after apply (exit 0). Craft file 45/150 lines, repo file
9/40 lines — both well under budget.
