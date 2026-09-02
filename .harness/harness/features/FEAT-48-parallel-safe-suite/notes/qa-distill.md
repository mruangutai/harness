# QA Expertise distillation — FEAT-48-parallel-safe-suite

BLUF: 5 entries applied — 3 craft displacements (P-06, G-06, G-09), 2 repository additions
(G-07, G-08). All three relayed candidates accepted after independent judgment; two self-derived
repository facts added from the ship briefing (B-9, and the `bugfix.when` placeholder observed
across qa-c7/c8/c9). Both files pass `check-expertise.sh` (`OK`).

## Source material read

`notes/qa-c7.md`, `notes/qa-c8.md`, `notes/qa-c9.md`, `notes/review-harness-qa-c7.md`,
`notes/ship-review-2026-09-02-c9.md`. No observations log exists for this agent (expected —
only pm and the orchestrator kept one); no `runs/` digests exist (gitignored, worktree removed).

## Relayed candidates — judged

**(a) accepted → craft Gotchas, displaced G-06.** "c9's discrimination proof did not carry across
the wholesale rewrite of `test-suite-independence.py` in `993ac997`, and had to be re-taken at the
new pin" (`qa-c9.md` §"All six in-file self-tests discriminate", corroborated by
`ship-review-2026-09-02-c9.md`'s "The file was rewritten wholesale... so the c8 proof did not
carry and I re-took it"). This is a durable trap independent of any one feature: a prior cycle's
discrimination proof is not transferable across a full rewrite even when test names/counts look
unchanged. New entry: G-06.

**(b) accepted → craft Gotchas, displaced G-09.** The harness half (validate-digest.py accepting
`severity_max: medium` against a `med` enum) is filed in `open_questions` below, not distilled —
that is a bug report, not Expertise. The surviving craft rule — always emit the literal contract
token, never a synonym, because a string-match validator accepts the synonym silently — passes
the six-spawns test on its own and generalizes past this one gate. New entry: G-09.

**(c) accepted → craft Patterns, displaced P-06.** Ship briefing B-15: `case_cache_exclusion` pins
only the `.pyc` leg, so a future narrowing of the `__pycache__` skip would pass unchanged. This is
the third time this exact class of gap surfaced in this feature alone (c7 MEDIUM finding on the
missing leg, c8's M4 restating it, c9 closing it, then B-15 re-flagging the surviving asymmetry) —
strong evidence of a recurring, generalizable pattern: multi-leg exclusion/inclusion rules need a
test per leg, not per rule. New entry: P-06.

## Self-derived candidates

**Accepted → repository Gotchas, added G-07.** Ship briefing B-9: the suite is green only with
`HARNESS_AGENT_TYPE` unset; with it set, `test-plan-merge.py` fails 11 checks and the run exits 1 —
a false regression tied to this repo's own env-var convention, not the diff under test. Directly
analogous to the existing repo-tier G-04/G-05 entries about `run-unit-tests.sh` quirks.

**Accepted → repository Gotchas, added G-08.** Across qa-c7, qa-c8 and the panel re-run, the
`bugfix` row's `when: match_bug_class` clause was checked and found to never fire (no bug-class
taxonomy entry resolves for any diff seen yet) — recorded so a future gate run does not assume the
clause silently widens the floor.

## Rejected

None of the three relayed candidates were rejected — all three passed the six-spawns test after
independent judgment (see above; (b) required carving the harness-defect half out first).

## Before / after counts

**Craft** (`.harness/expertise/harness-qa.md`) — before: Patterns 15/15, Gotchas 15/15,
Outcomes 10/10, Open 1/5. After: Patterns 15/15 (unchanged count, P-06 text replaced), Gotchas
15/15 (unchanged count, G-06 and G-09 text replaced), Outcomes 10/10 unchanged, Open 1/5 unchanged.

**Repository** (`.harness/harness/expertise/harness-qa.md`) — before: Patterns 0/15, Gotchas 6/15,
Outcomes 0/10, Open 0/5. After: Patterns 0/15 unchanged, Gotchas 8/15 (+G-07, +G-08), Outcomes
0/10 unchanged, Open 0/5 unchanged.

## Mechanism note

`expertise-merge.py apply` performs an additive union merge only — it has no delete/replace verb.
Submitting the two full-section craft entries under their existing IDs correctly produced
`exit 7` (CONFLICT, same id/different text) rather than silently discarding the displacement; I
resolved it myself, as the exit-7 contract instructs, via a targeted 3-line `edit` (not a
whole-file rewrite) swapping exactly those three bullets in place. The repository-tier additions
went through `expertise-merge.py apply` cleanly (`exit 0`, `ADDED G-07`, `ADDED G-08`,
`PRESERVED G-01..G-06`) since that section had headroom.
