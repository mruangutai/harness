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

## Round 3 (2026-08-22) — #673's constraint folded in as a second accepted cost

**Outcome: `## Accepted costs` now records that the board workflows this feature's closing behaviour
depends on cannot be enabled by any API the harness can call, so `Closes #N` is the automation
rather than a convenience over one.** 151 -> 170 lines. One hunk, 19 insertions, 0 deletions, all
between the existing entry and `## Approval`.

Source verified, not relayed: `gh issue view 673` read end to end. Every figure the dispatch handed
down matches the issue at source — the 31 `ProjectV2` mutations with `deleteProjectV2Workflow`
present and no creator, `copyProjectV2`'s four arguments, `ProjectV2Workflow`'s eight exposed fields
with neither trigger nor action, the three workflow names, board 3's 509 items and 222 of 222 at
`Station: Done`, the zero-result `grep` for `projectV2Workflow` in `bin/`, and the eight
`harness-init/SKILL.md` prerequisites. No contradiction to report.

One nuance the entry preserves rather than flattens: #673 attributes the 222 of 222 to two
workflows (`Item closed`, `Auto-close issue`) and lists `Pull request merged` as the third enabled
one, not as a third producer of that number. The entry says "produced by those enabled workflows"
about the set, which the issue supports; it does not claim all three produce the station value.

**The 14-line ceiling could not be met, and no load was dropped to fake it.** The eight content
loads are 12 enumerated API identifiers, three workflow names and three independent measurements.
Two drafts were measured: the first wrapped to 19 lines at 1801 characters, and an aggressively
tightened second — same eight loads, glue prose stripped — also wrapped to 19, at 1649. Backticked
identifiers do not break across lines, so the observed density is about 87 characters per line and
14 lines hold roughly 1220; the identifiers, workflow names and three measurements alone exceed
that. No 14-line variant retaining all eight loads was produced, and none appears reachable. Per the accept-criteria's own
pre-resolution ("if pm cannot fit them in 14 it reports the tension rather than dropping a load"),
the entry ships at 19 and the overrun is reported.

Not touched, verified after the edit: `## Requirements`..`## Verification gaps` md5
`4a76e0b616b0ed0f3a69cec66c1fa789` and `## Approval`..EOF md5
`c380e46b2c62bd5dede69a2c96810c44`, both identical to their pre-edit values. `plan.yaml` shows 0
changed lines. `STATE.md` never opened. The existing accepted-cost entry is byte-identical.

Pre-existing dirt worth naming so nobody attributes it here: `notes/q1-pr-attribution-evidence.md`
was already modified in the working tree before this round began, and
`notes/answers-Q1-pr-attribution.md` is untracked. Neither was written this round.

A measurement that killed a self-imposed constraint: I briefly reflowed for a 99-column limit, then
checked and found 13 pre-existing `BRIEF.md` lines already over it (`awk` counts bytes, and em
dashes cost three each). There is no 99-column rule in this file. The reflow was kept because it is
harmless, but width is not a containment criterion and should not be treated as one next round.
