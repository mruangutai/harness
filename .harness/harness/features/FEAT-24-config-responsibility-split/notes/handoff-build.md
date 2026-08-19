# Handoff — FEAT-24, build → validate — written at 2e60cc2, seq-2

## Next

**The qa gate FAILED and the remaining fix is the operator's, by hand.** T-05's verify cannot reach
green for two reasons, both in DEC-174 carve-out files: `check-state.sh` has no `INV-26 BEGINS`/
`ENDS` markers so the verify's slice is EMPTY, and `test-check-state.py` emits none of the five
required ok-lines, two of which (`backlog`, `building` per-key) have no case at all. Exact
instructions: `notes/segment-03-t05-verify.md`. When it returns green: re-check the matrix, then the
four-angle simplify pass to `harness-eng-lead`, **re-pin `review_sha` after any apply commit**, then
the review panel, then pm's goal-check on all 13 SCs through `harness-product-lead`.

## Trust

- All ten tasks `done` and committed; every sub-issue closed; parent derived to `Review`;
  `review_sha` pinned at `b0604c3` — `plan.yaml`, `feature.json` — verified-at 2e60cc2
- FEAT-24's own `check-state.sh` violations are **zero** — verified-at 2e60cc2
- Full suite: zero `FAIL` lines — `run-unit-tests.sh --kind all` — verified-at 2e60cc2
- I re-ran T-01, T-02, T-08, T-09, T-10's `verify:` myself; all GREEN. **T-05's FAILS** at its first
  assertion — verified-at 2e60cc2
- **SC-06 met and checked LIVE:** `board_for` returns kaya's board from `master` with a checkout
  present on disk, which also proves the no-fallback rule — verified-at 2e60cc2
- `INV-26 BEGINS` and `INV-26 ENDS` each occur **0 times** in `check-state.sh`; the five ok-lines
  T-05's verify greps occur **0 times** in `test-check-state.py` — verified-at 2e60cc2
- v.13/v.14/v.15 DO exist and pass, so "the tests were never written" is false; they are named
  differently and two per-key cases are absent — verified-at 2e60cc2
- The `validate=True` fail-open is closed: under `validate=False` exactly one case reddens, the
  named one. I proved it by runtime patch, editing no file — verified-at 2e60cc2

## Dead ends

- Do not read an empty grep as a clean result. My own "the INV-26 block is clean" was a read of an
  EMPTY slice, because the markers do not exist — source: this session, corrected in segment-03
- Do not trust a green suite as evidence an integration works — it was green through two live
  defects; call the real thing — source: this session, two fix cycles
- Do not re-run T-01 through T-10; all are committed and independently verified — source: this session
- Do not edit `check-state.sh`, `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `test-check-state.py` from a team run — source: DEC-174 carve-out, T-05 main-session-direct
- Do not stage with `git add -A`, `git add .` or `git add .harness`; explicit pathspecs, and confirm
  `git status --short` before every commit — source: #433, live foreign reconciliation
- Do not touch or report on `FEAT-25-*`, `FEAT-26-*`, `FEAT-27-*`; their violation count is moving
  under another pen and that is not a regression — source: this session's dispatch
- **Simplify hazard:** before applying any finding to a file a verify clause reads, check whether the
  clause greps words the edit changes — source: a pass did exactly that today, gates stayed green

## Working set

- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/segment-03-t05-verify.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/STATE.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/notes/qa-2026-08-19-matrix-gate.md`
- `.harness/harness/features/FEAT-24-config-responsibility-split/plan.yaml`
- `.harness/harness/features/FEAT-24-config-responsibility-split/BRIEF.md`
