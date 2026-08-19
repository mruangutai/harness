# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: none in flight
- squad: none
- status: awaiting-user

Phase: **ship, validate. All ten tasks are committed. The qa gate — the project's only blocking
gate — returned FAIL, and the remaining fix is the operator's by hand.**

**What blocks: T-05's verify cannot reach green.** Two parts, both in DEC-174 carve-out files, both
`main-session-direct`:
1. `check-state.sh` has **no `INV-26 BEGINS`/`INV-26 ENDS` markers** (`grep -c` returns 0 for each).
   T-05's verify slices between them, so the slice is EMPTY and every literal-absence grep below it
   proves nothing. The verify's positive control exists to catch exactly this and does.
2. `test-check-state.py` emits none of the five ok-lines the approved verify requires. Its three
   cases (v.13, v.14, v.15) exist and PASS, but under different names — and **two of the five have
   no case at all** (`backlog` and `building` per-key). That second half is a coverage shortfall,
   not a rename.

Exact instructions, with the correction to my own earlier misreading, at
`notes/segment-03-t05-verify.md`.

**Closed this session:** T-10 committed (`b0604c3`), all ten tasks `done`, every sub-issue closed,
parent derived to `Review`, `review_sha` pinned at `b0604c3`, the build-seam handoff written, and
FEAT-24's own `check-state.sh` violation count taken to **zero**. Two live defects in
`factory_gh.file_at_ref` fixed and proven (`574f73c`), and the `validate=True` fail-open closed with
a case I independently proved reddens.

**Not yet run, in order:** matrix re-check after T-05 → four-angle simplify → re-pin `review_sha` →
review panel → pm's goal-check on all 13 SCs → close-out → the ship briefing.

Cycles: **4 of 10**. Runs: 14 recorded of 20.

## Open Questions

- Q1 (operator, BLOCKING): T-05's two-part fix — `notes/segment-03-t05-verify.md`.
- Q2 (operator, recommend taking): `DECISIONS.md:6090` — DEC-196's own heading still reads "its own
  board declares no stations", falsified by T-06. A heading is unreachable by an amendment body and
  DEC-188 forbids a quiet rewrite, so retitling with a strike record is a decision-level act. SC-11
  is met either way.
- Q3 (team dev, after T-05): SC-02's `ready` is non-discriminating —
  `test-factory-decompose.py:413` asserts the DEC-192 literal itself, so a reverted lookup passes.
- Q4 (one-line config): `harness.json`'s `integration.detect` names 4 files while
  `INTEGRATION_SCRIPTS` runs 12, which makes a `change_type` unsatisfiable by construction.
- Q5 (pm, non-blocking): the new ok-line closing the `validate` fail-open is pinned by no `verify:`
  block, so deleting the case would be invisible to every gate — the same shape one level up.
- Q6 (backlog): the fake `gh` models argv but neither the HTTP method nor the real response shape;
  it shipped two defects past a 208-check green suite.
- Q7 (main session): the paused FEAT-25/26/27 directories are being reconciled under another pen.

Briefing: `notes/ship-review-2026-08-18-ship-01.md` — stale, rewritten at the ship decision.
