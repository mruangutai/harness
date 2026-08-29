# STATE

## Current

- feature: FEAT-38-decisions-current-knowledge
- run: none — the resume segment closed at an operator ruling that reopens scope
- squad: none
- status: Review on the board, but **BLOCKED pending re-planning**. No PR, no merge, no ship.

**The thing to read is `notes/replan-remove-command-execution.md`.** The ship briefing
`notes/ship-review-2026-08-29-18.md` is still accurate about what was BUILT and VERIFIED, but its
recommendation to ship is **superseded** by the ruling below.

`review_sha` is `48bbe7e`; `base_sha` is `7ebfc9e`. Branch `feat/FEAT-38-decisions-current-knowledge`.

## The operator's rulings, 2026-08-29

**1. Cycle budget — crossing ACCEPTED, bound NOT raised.** `cycles_used` stays **11** and
`max_total_cycles` stays **10** in `feature.json`; neither was altered to make the record look
better. The crossing is accepted as recorded. Both over-budget cycles were lead-internal send-backs
during re-verification of already-passing gates (qa's self-caught false 6-`FAIL` baseline reading;
the ui-reviewer's self-corrected high→med rating); neither changed production code and no fix cycle
was routed to a builder. `feature.json`'s key set is closed (DEC-191, `additionalProperties: false`),
so this acceptance is recorded here rather than as a new key.

**2. The three signed `verify:` amendments — SIGNED, and deliberately NOT YET APPLIED.** The operator
signed the exact T-10/T-15/T-19 replacement text preserved in
`notes/research-verify-block-defects.md`. Application was dispatched and then **skipped before any
edit**, so `plan.yaml` is untouched and there is no half-applied state. It was not re-dispatched
because ruling 3 landed in between and entangles T-19's block with the redesign. **The signature is
preserved, not withdrawn** — the reasoning and the reversal cost are in
`notes/replan-remove-command-execution.md` under *What was NOT done, and why*. Note that
`notes/research-verify-block-defects.md` itself still reads "blocking on signature"; it was not
stamped, because it is pm's analysis and the status lives here.

**3. REMOVE COMMAND EXECUTION — new scope, supersedes the ship trajectory.** The operator does not
accept any document-driven subprocess risk. `check-decision-claims.py` must stop executing commands
taken from `DECISIONS.md` and be replaced with a non-executing verification design. **This is new
scope against an approved plan and must NOT be implemented under it** — it requires `BRIEF.md` and
`plan.yaml` updates, operator approval, and fresh security validation.

The full replanning handoff is `notes/replan-remove-command-execution.md`. Its decisive measurement:
**all eleven live claim markers are `grep` against one named file**, so a declarative
`contains` / `max_lines` vocabulary covers 11 of 11 with zero execution surface. The redesign is a
capability-preserving simplification, not a reduction.

## Where the work actually stands

All 23 tasks are `done` and committed; every automated gate is green at `48bbe7e` (qa PASS, review
panel PASS with `severity_max: med` and empty `must_fix`, goal-check 12 of 13 SCs met). SC-13's UAT
is `unrun` and stays unrun — **it must not be presented as a ship gate now**, because ruling 3 means
part of what it would accept is being redesigned.

**Budget: cycles 11 of 10 (crossed, accepted), runs 19 of an informational 20.** GitHub mirror:
milestone 31, parent #935, sub-issues #936–#958, all at the `Review` station. The board was NOT moved
to `Plan` — that station is written by `board-station.py` at the `/harness-plan` door, not by the
orchestrator.

## Open Questions

Three replanning questions for the operator are in `notes/replan-remove-command-execution.md`:
whether the marker mechanism survives at all in non-executing form, whether `contains`/`max_lines`
is the whole vocabulary, and whether the checker keeps its filename.

Backlog rows B-1…B-23 remain in `notes/ship-review-2026-08-29-18.md`. **Ruling 3 settles four of
them without an issue being filed:** B-8 and B-11 become MOOT (they harden or annotate an execution
path being deleted — do not implement then delete), B-10 is SUPERSEDED (that prose is rewritten
wholesale), and **B-9 SURVIVES and is now more important** — nobody has swept the rest of `bin/` for
the same shape, any script building an argv from document or config text.
