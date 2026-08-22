# QA distillation — FEAT-31

## BLUF

Distillation applied for candidates 1 and 2 from the lead relay; candidate 3 recorded as
**retracted by the lead before judgement — premise false at source** (no op). While applying, found
and corrected a false entry (`O-05`) that a prior spawn had already written from candidate 3's false
premise before the retraction reached it — reverted to the entry it displaced.

## Candidate disposition

- **Candidate 1 (PASS-line count is not a coverage measure):** accepted. `P-13` replaced —
  now states a total/baseline-matching PASS count is never coverage evidence for the current diff,
  only a named test exercising the changed lines is.
- **Candidate 2 (matrix floor literal-adequate vs substantively thin → config finding, not a FAIL):**
  already present on disk under `P-15` (a concurrent distillation pass had applied equivalent text —
  "file the gap as a non-blocking config question ... not a suite FAIL"). No further op needed;
  judged on its merits and found already correctly captured.
- **Candidate 3 (qa did not rule on Q-IRONLAW/Q-FOOTERCOV):** **retracted by the lead before
  judgement — premise false at source.** `qa-20260822-065648.md` lines 49–60 (`## Q-IRONLAW ruling`)
  and lines 83–88 (`## Q-FOOTERCOV`) show both were explicitly ruled on. No op produced.

## Correction found mid-task

On reading the current file, `O-05` (Outcomes) had already been overwritten — presumably by an
earlier spawn of this same distillation dispatch, before the retraction — with an entry built
directly on candidate 3's false premise ("an unruled question that was answerable forces the tier
above to re-derive... marks a calibration gap"). Since the premise is false (the questions were
ruled on in the same artifact), that entry would enshrine a false record. **Reverted `O-05` to the
entry it displaced** (the Phase-1-prescriptive-plan entry), via a targeted `Edit`, not a whole-file
write. Section counts unchanged before/after (Patterns 15/15, Gotchas 15/15, Outcomes 10/10,
Open 1/5).

## Mechanism note

`expertise-merge.py apply` is a pure additive union keyed by section+id — it has no `replace`
subcommand; a same-id/different-text proposal is refused as `CONFLICT` (exit 7), consistent with
"resolve it yourself" in the exit-7 row of `harness-distill`. With both `Patterns` and `Outcomes` at
cap, resolving the two edits here (`P-13` replace, `O-05` revert) required a targeted `Edit` on the
matched line rather than the merge tool. `check-expertise.sh` reports `OK` on the result.

## Per-section counts

Patterns 15/15, Gotchas 15/15, Outcomes 10/10, Open 1/5 — unchanged before and after (both edits
were text swaps on existing ids, not additions).
