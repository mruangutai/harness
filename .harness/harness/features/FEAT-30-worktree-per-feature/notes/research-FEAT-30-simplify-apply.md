# FEAT-30 simplify apply — the single round

**L-1 is fixed by deleting the literal, not by keeping it: shape 2, widened.** Every fixture
directory a case treats as a worktree becomes a real linked worktree carrying both sides of the
git pointer pair. REQ-08 stays one mechanism replacing one mechanism in all four consumers. The
cost accepted, in these words: **a directory under `WORKTREES_SEGMENT` that is not a registered
linked worktree stops being reached by the shape sweep and stops being normalised by the shape
phase, so state files written into one are no longer budget-checked.** Recorded as `D-09`, with an
added T-04 case that asserts the narrowing instead of leaving it silent.

## Why not the fallback (shape 1)

Three independent reasons, in descending order of force.

1. **The fallback is not an extra tier — it is the depth-coupled strip, in the one consumer the
   settled ruling is about.** In `_norm` the fallback *is* `^\.claude/worktrees/[^/]+/(.+)$`. At the
   repo-and-id layout it strips one segment and yields a path matching none of `RE_FEATURE_JSON`,
   `RE_STATE_YAML`, `RE_HANDOFF`, `RE_STATE_MD` — so it is wrong there, not merely redundant.
2. **It falsifies a benefit T-04 states in writing** (the segment string read from the constant in
   one place, strengthening the `WORKTREES_SEGMENT` mutation proof). PRINCIPLES rule 15.
3. **The fixtures were the problem, not the constraint.** A bare directory under
   `.claude/worktrees` is not a worktree. `WORKTREE_REL_RE` (`harness_boundary.py:36`) is what let
   sixteen T-03 assertions claim "a worktree write resolves to the same grant" about something that
   is not a worktree. Converting is a strengthening, not a concession.

Shape 3 does not exist. Depth-agnostic + pointer-free + bounded per-write cost cannot all hold: the
single wildcard segment is exactly what made the old literal cheap and pointer-free. A recursive
`**` under `WORKTREES_SEGMENT` walks every worktree's full tree per governed write. That is the
forced constraint; everything else here was a choice.

## Two source corrections to the dispatch's own framing

- **Five assertions were at risk, not two.** `post Edit` on the worktree `CLAUDE.md`, `post Edit` on
  the worktree state file and `pre Write` on the worktree `CLAUDE.md` also go red: `_show` is
  unchanged, but they reach a state-file shape only through `_norm`'s strip, and without it
  `RE_CLAUDE_MD` (`^CLAUDE\.md$`) and the four state regexes match nothing. The conversion set is
  unchanged — both fixtures were already named — so the operator's cost is not larger.
- **T-03's own sixteen in-worktree cases were also at risk, and no angle saw it.** The resolve path
  at `check-domain.sh:212` matches `harness_boundary.WORKTREE_REL_RE`, which T-04 PART 2 replaces;
  T-03 builds its in-worktree half bare. This is why the fix touches T-03 as well as T-04, and it
  is the extra cost of shape 2 over shape 1: every worktree fixture now needs a pointer pair.
- **The pointer PAIR, not a pointer.** `checkout_relative` reads the worktree-side `.git` file;
  `linked_worktrees` enumerates the owner-side `.git/worktrees/<id>/gitdir`. The plan's own new
  cases said "a `.git` pointer file exists", which would have left `linked_worktrees` blind. Both
  sides are now spelled in every case that needs them. No git subprocess: `test-check-domain.py`
  already builds one by hand in `run_worktree`'s `_linked` helper.

## Residual risk, named where it lands

Converting changes what the issue #103 legitimacy branch answers for those paths — it returned
`None` before. A conversion is therefore not behaviour-neutral. Both T-03 and T-04 now instruct:
report a flipped verdict, never adjust the assertion. Each task's `verify` already requires the
whole file to pass, so it is caught inside the task, by the operator, before landing.

## Also applied

- **A-2** — T-06 gains case 8, a drift detector asserting `expertise-merge.py`'s four caps equal the
  `CAPS` mapping in `check-expertise.sh` (line 39, a file T-06 does not modify), the remedy
  `DECISIONS.md:5219-5225` recorded. `files:` unchanged.
- **Q8, answered** — D-08's choice is now the suite baseline alone, with the `check-state.sh` clause
  relabelled as an operator-run ship-time sanity check, explicitly not part of SC-09 and owned by no
  task. No verify invented. The count-form reasoning is kept: it is the lesson, not the assertion.
  The suite half now also carries its re-observation at HEAD (269 PASS, 0 FAIL, exit 0).
- **A-4** — the +0.22 ms per governed Bash write is recorded in T-04 PART 3 beside the PART 1 note.

## Not applied, as directed — and I disagree with none of the four

A-1, A-3, A-5, A-6 travel as briefing rows. A-1's compensating control (assert exactly 16, fail with
the names) is real; A-3's two intents have different executors and are consumed once; A-5 is
re-spelling without a drift window on a write path; A-6 needs a file outside T-01's `files:`.

## Route check

`check-plan-routes.py` — **exit 0, 0 violations across 1 plan.** The three `DEVIATION` lines on
T-03/T-04/T-05 are the DEC-174 carve-out, pre-existing and expected.
