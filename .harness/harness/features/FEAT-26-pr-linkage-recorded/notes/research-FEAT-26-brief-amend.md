# BRIEF amend — FEAT-26 — figures, Goal sentence, accepted cost, citation repair

**Outcome: the BRIEF is amended and ready for signature.** 127 -> 147 lines. Five edits, touching
`## Problem`, `## Goal`, `## Constraints`, plus one new `## Accepted costs` section. No `REQ-NN` and
no `SC-NN` was touched; `## Approval` is byte-identical (`status: pending`) and still the last
section.

## What changed

1. `## Problem` figures now read **12 of 27 `Done` features `pr: null`** (FEAT-01, 02, 03, 04, 05,
   08, 10, 20, 21, 22, 23, 24), fifteen with an integer, each count carrying `6d1e34f` inline.
   Folded in the two hand-typed repairs (`7dbb0f1` FEAT-30, `c924c6d` FEAT-29) and the rate — about
   one omission per shipped feature. Argument, structure and closing line kept. `github:` key counts
   (19/20/18/16/18) also carry the sha.
2. `## Problem` gained one sentence recording REQ-04's live case: `5d9b428` merged PR #601 while
   FEAT-29 read `status: Building, pr: null` with all nine tasks `done`; 30 hours 45 minutes to
   `c924c6d`, nothing reported it. REQ-04's own text untouched.
3. `## Goal`'s closing sentence now says the closing keywords are a string the operator pastes and
   that nothing in this feature ever posts, edits or closes anything on GitHub. Prose, in the Goal,
   once — not an SC, no `gh pr` subcommand constraint, no restatement elsewhere.
4. New `## Accepted costs`, exactly one entry, after `## Constraints` and before `## Approval`:
   prose in a Goal is asserted by nothing; the `tests.yml` false-citation repairs are the same
   shape; ACCEPTED by the operator over a criterion.
5. DEC-153's stale anchor repaired to a rot-proof form — cited by id with `DECISIONS-INDEX.md` as
   the lookup. Staleness verified: `DECISIONS.md:3660` sits inside DEC-152's bash-write-guard text,
   DEC-153 begins at 3717.

## Citation spot-check — the other three are sound at `6d1e34f`

- DEC-138 amendment 6 exists at `DECISIONS.md:4292` and does forbid "the mirror composing its own
  text at post time" — the constraint's claim is exact.
- DEC-196 @6266: "MOVES any card it is pointed at, and CLOSES only cards it created" — matches.
- DEC-191 @5830: closed key set, `additionalProperties: false` — matches.

No silent substantive repair was made anywhere.

## Left alone, deliberately

REQ-05 ("the eleven...") and SC-08 ("twenty-three features this plan enumerates") still carry the
pre-amend counts. They describe this plan's enumerated scope set, not the corpus; `plan.yaml:511`
names FEAT-24 as deliberately untouched and SC-08 excludes features in flight at plan time. The
scope reads internally coherent; it travels to the operator as a non-blocking question, not a fix.
`## Verification gaps` untouched. `plan.yaml` was never opened for edit.

## Round 2 (2026-08-22) — the accepted-cost entry was overstated, and is narrowed

**Outcome: the single `## Accepted costs` entry no longer claims the Goal's closing sentence is
unasserted, because half of it is.** 147 -> 151 lines. One hunk, `BRIEF.md:137-147`, entirely inside
`## Accepted costs`.

Re-verified at source in this worktree before editing:

- `BRIEF.md:41-42` — Goal closes "nothing in this feature ever posts, edits or closes anything on
  GitHub."
- `BRIEF.md:80-83` — SC-06 ends "It never posts anything to GitHub." carrying
  `verify: automated` / `evidence: integration`. So the renderer half **does** bind.
- SC-01..SC-11 read end to end (`BRIEF.md:59-104`): no criterion quantifies over every task, and
  none mentions *edits* or *closes* at all. SC-06 speaks only of **posting** — so edits and closes
  are unasserted even for the renderer, not just feature-wide.

The rewritten entry therefore names what binds (SC-06, automated, integration evidence), what does
not (whole-feature scope; edits/closes), and why the remainder is accepted (a sweep over every task
for a negative is not a cheaply writable check).

Nothing else in `BRIEF.md` moved: no `REQ-NN`, no `SC-NN` definition, not the Goal, not
`## Verification gaps`, not `## Constraints`. `## Approval` is byte-identical, `status: pending`.
The added lines do cite `SC-06` and `SC-01..SC-11` by name — that was an explicit requirement of the
dispatch, and it collides with the dispatch's own "no added line carries an `SC-` token" check. The
content requirement was taken as the governing one; flagged rather than silently resolved.
