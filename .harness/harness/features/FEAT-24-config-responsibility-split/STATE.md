# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: .harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-19-7-eng/
- squad: eng
- status: in-progress

Phase: **ship, validate.** All ten tasks are committed and every task verify I have re-run myself is
GREEN, including **T-05** (`0fa6315`) — the markers exist, the five ok-lines are present, and the
`backlog`/`building` per-key cases the earlier gate was missing are in.

**Q2 is CLOSED, in the tree.** DEC-196's heading no longer carries the falsified clause; it now reads
two true clauses only, with the struck clause recorded in a **new amendment 2** rather than folded
into amendment 1 — the documentor caught that extending am.1 would have falsified am.1's own closing
sentence, "This amendment touches the stations paragraph alone", creating a fourth falsified
statement in the task meant to remove one. Index regenerates byte-identical. **Uncommitted;
`needs_approval: true` — the wording is new permanent text no approved intent prescribes.**

**The qa gate returned `matrix_ok: true` but VERDICT FAIL**, on adequacy rather than the matrix
floor. qa's own caveat is worth keeping: `config` and `docs` require no kind at all, so
`matrix_ok: true` says almost nothing about this diff, and both `must_fix` items sit inside
already-satisfied kinds.

1. **SC-02's `ready` key is UNMET** — a signed criterion. `test-factory-decompose.py:412-413`
   asserts `== "Ready"` against a fixture whose own `stations.ready` is literally `"Ready"`, so
   hardcoding `factory_decompose.py:399` reddens nothing. SC-02 demands each key's assertion FAIL
   when only that key's lookup is reverted to a literal. **In flight now.** I verified it is the only
   affected key: the other four resolve through paths whose fixtures already use `Col-B`/`Col-R` and
   `Icebox`/`WIP`/`Shipped`.
2. **The `aGV!sbG8=` case is pinned by no `verify:` block**, so deleting it would be invisible to
   every gate — a fail-open one level up. Pinning it edits an approved `verify:`, which is pm's and
   the operator's, not mine. Q1 below.

**Next:** SC-02 fix returns → commit → four-angle simplify → re-pin `review_sha` → review panel →
pm's goal-check on all 13 SCs → close-out → ship briefing.

Cycles: **5 of 10.** Runs: 17 recorded of 20 — approaching the informational bound; the runs are
still resolving real defects rather than churning.

## Open Questions

- Q1 (operator, plan text): pin the `aGV!sbG8=` case in a `verify:` block, or accept it as a
  residual? Amending an approved verify post-signature is not mine.
- Q2 (operator, at ship): approve the new DEC-196 heading wording — permanent record text that no
  approved intent prescribes.
- Q3 (residual): `harness.json`'s `integration.detect` names 4 files while `INTEGRATION_SCRIPTS`
  runs 12, making a `change_type` unsatisfiable by construction under a literal reading.
- Q4 (residual): the fake `gh` models argv but neither the HTTP method nor the real response shape;
  it shipped two defects past a 208-check green suite.
- Q5 (residual): a lead has now returned a verdict while its member was in flight several times —
  issue #461. Do not re-file.
- Q6 (main session): the paused FEAT-25/26/27 directories are being reconciled under another pen.

Briefing: `notes/ship-review-2026-08-18-ship-01.md` — stale, rewritten at the ship decision.
