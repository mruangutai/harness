# Mutation figures for T-02 and T-04 — a relay, not a measurement

## What this note is

T-02 (`gh_board.py` / `test-gh-board.py`) and T-04 (`check-state.sh` INV-26) ran
**main-session-direct** under the DEC-174 carve-out. That lane writes no receipt by design, so the
mutation proofs run there left no artifact in this feature directory.

The figures relayed through the build handoff were:

- **T-02: 6 of 6 mutants killed** (`gh_board.py`, proved against `test-gh-board.py`)
- **T-04: 5 of 5 mutants killed** (`check-state.sh` INV-26, proved against `test-check-state.py`)

## Status of these figures: UNVERIFIED

**No artifact in this repository substantiates either number.** Two independent greps confirm it:

- The validator lead grepped `notes/` and `STATE.md` for `mutat`, `6 of 6`, `5 of 5`, `6/6`, `5/5` —
  zero hits (recorded in `notes/qa-test-matrix-gate.md`, "Mutation evidence").
- qa declined to re-run the proofs, correctly: both paths are DEC-174 carve-outs, and edits and
  proofs on them are reserved to the main session.

The figures exist only in a main-session transcript. Transcript retention is 30 days by default, so
they will become unrecoverable. This note is the durable record **of the claim**, not of the
measurement.

## The rule that follows

**Do not quote "6 of 6" or "5 of 5" as measured coverage.** Cite this note, which says a main-session
run reported them and that nothing on disk proves it. The only mutation record in FEAT-18 that rests
on an artifact is T-03's, in `notes/receipt-harness-backend-dev-T-03-c1.md`.

## Why this matters here specifically

This harness gave a false green twice on 2026-08-03 — four `.harness` YAML files did not parse and
the validator rejected its own normative template, while all four gates passed. A surviving-mutant
figure with no receipt cannot be told apart from a mutation harness that never applied the mutation.
That is the failure mode DEC-174 exists to catch, and an unrecorded proof reintroduces it.

## What was NOT harmed by this gap

The qa PASS does not rest on these figures. `matrix_ok: true` rests on the unit and integration
suites, which qa ran directly at pin `6d2d61b` (exit 0 both), plus each task's own verify command.
T-02 and T-04 each have a named test file binding their own change.

## To close this properly

Re-run the two proofs main-session-direct and replace this note with the receipt. Until someone does
that, the coverage claim for T-02 and T-04 is "suite green", not "mutants killed".
