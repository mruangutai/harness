# QA distillation — FEAT-29-graphql-budget

No `observations/harness-qa.md` exists for this feature — source is my own gate artifacts
(`notes/qa-matrix-gate.md`, `notes/qa-matrix-gate-regate-3fbfd0a.md`,
`notes/qa-matrix-gate-final-c472a02.md`, `runs/2026-08-19-07-validator/probe-rc-line-162.md`) plus
three candidates relayed at the lead tier. I am sole judge; all three judged below.

## Candidates — accept/reject

**1. "run_gh's half is thoroughly unit-tested" overclaim — ACCEPTED, as `O-10` (craft, new).**
The corrected lesson generalizes past this repo: crediting a component as tested from its own
dedicated test file, without independently checking each real caller's seam, can leave every
caller unbound (env var short-circuit, missing import) while the module's suite stays green. No
existing entry captured this exact failure mode — closest neighbors (`P-05` test-file-in-diff,
`O-06` mutate-each-site, `G-04` task-local-vs-full-bucket) are adjacent but none states "crediting
'tested' from the module's own suite is not evidence the callers are bound." Outcomes had one open
slot (9/10); filled it, no displacement needed.

**2. 172 vs 806 same-suite count divergence — ACCEPTED, as a `replace` of `P-13` (craft).**
`P-13` already covered provenance/granularity axes for test-count citation but did not name that
two *conventions* (per-check PASS lines vs each script's self-reported total) can diverge sharply
on the identical suite, nor that the delta is the only reliably-comparable figure across runs. This
is a sharper, same-domain refinement — replaced in place, same length budget, no net growth.

**3. Blind Phase 1 prediction later discharging SC-05's OFF+failing-invocation case —
REJECTED.** Real and load-bearing at the time (`qa-matrix-gate.md:11` → discharged at
`runs/2026-08-19-09-validator/digest.md:56-62`), but it fails the six-spawns test: Phase 1 blind
derivation is already a mandated step in `harness-verification-rules`, not a discretionary practice
this entry would newly cause me to adopt. It is confirmatory evidence that the existing protocol
works, not a new WHEN/DO rule that changes future behavior. Outcomes had no further room after
accepting #1 without displacing an existing entry, and nothing on the list was judged weaker than
this candidate — so even setting aside the six-spawns failure, it would not have displaced
anything. Recording the rejection here per instruction; not entered anywhere.

## Deliberately not distilled

Per the dispatch: the `check-domain.sh` disagreement (run 07) and the `test_kinds.integration`
glob naming 4/12 `INTEGRATION_SCRIPTS` are harness defects, not craft. Both already live in
`open_questions` across the cited gate notes (Q1 in `qa-matrix-gate-regate-3fbfd0a.md`, B-6/§4 in
the same file and in `qa-matrix-gate.md`) and are being carried up by the lead — not touched here.

## Files written

- `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md` (craft) —
  `P-13` replaced, `O-10` added.
- `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-qa.md` (repository) —
  unchanged; no candidate or observation was repository-scoped (all three concern general
  test-crediting/counting practice, true in any repo).

Both files pass `check-expertise.sh`.

## Per-section counts (craft, `.harness/expertise/harness-qa.md`)

| Section | Before | After |
|---|---|---|
| Patterns | 15/15 | 15/15 (P-13 replaced in place) |
| Gotchas | 15/15 | 15/15 (unchanged) |
| Outcomes | 9/10 | 10/10 (O-10 added) |
| Open | 1/5 | 1/5 (unchanged) |

## Per-section counts (repository, `.harness/harness/expertise/harness-qa.md`)

| Section | Before | After |
|---|---|---|
| Patterns | 0/15 | 0/15 |
| Gotchas | 3/15 | 3/15 |
| Outcomes | 0/10 | 0/10 |
| Open | 0/5 | 0/5 |
