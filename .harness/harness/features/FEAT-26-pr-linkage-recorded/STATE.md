# STATE

## Current

- feature: FEAT-26-pr-linkage-recorded
- phase: **ship / merge segment.** All eight tasks `done`. qa gate PASS (45 scripts, 0 FAIL).
  Simplify pass complete with its one fold-in applied. Validation panel run, all three
  must-fixes closed. `review_sha` pinned `bad32441dfc0`. `branch` reads `feat/FEAT-26`.
- status: Review, until the PR merges.
- BRIEF and plan are BOTH signed (`approved`, Mike Ruangutai, 2026-08-23), verified on disk at
  `plan.yaml:6-9` and `BRIEF.md:164-166`. This seat never writes an approval block.
- **Goal-check: 11 of 11 signed success criteria MET, 0 NOT MET, 0 UNVERIFIABLE.** Artifact
  `notes/research-FEAT-26-goal-check.md`. Every row cites a command run in this worktree or a
  `file:line` read.
- worktree `.claude/worktrees/harness/FEAT-26-pr-linkage-recorded`, current with `main` after
  #750 merged. HEAD is never moved by this seat.
- GitHub mirror: milestone **#22**, parent **#732** (`parent_origin: created`), sub-issues
  **#733-#740** for T-01..T-08, all attached. `gh-sync.py ship` will close #732.
  `gh-sync.py closes` renders `Closes #492`.
- `github.source_issues` is `[492]`. Its write was refused until **#749** landed — the schema
  that judged a worktree write came from `main`, so a key the worktree had just declared read
  as undeclared. Fixed and merged as `569d417`.
- **The T-07 false green, kept as the lesson.** Its verify was a single-line `grep` for a
  sentence that wraps across two lines, so it could never match and never fail. Only an
  **absence** assertion turns a line wrap into a false green; presence assertions break loudly.
  Grade the pattern's span against the matcher's unit.
- `check-state.sh` emits one INV-28 line, naming `FEAT-24-config-responsibility-split` — a
  `Done` feature with a null `pr`, outside this plan's twenty-three. REQ-04 working, not a
  regression.

### Owed after merge

`gh-sync.py record-pr` on this feature dir, then status `Done`, then `handoff-validate.md`.

### Budget

`cycles_used` 0 of 10. `runs` 1 of 20 (informational, DEC-134 / INV-22). Carve-out segments and
main-session-direct dispatches are not runs, so the count is a floor.

## Open Questions

- Q13 (non-blocking, operator — outlives this feature): **issue #673 still carries all
  four falsified claims** (31 mutations, 509 items / 222 of 222, "the three workflows on this
  board", and a #492 parentage its own graph contradicts). #673 is the ticket that will implement
  the detection work, so whoever picks it up inherits them. It needs correcting at source; nothing
  in this feature's scope does that.
- Q1 CLOSED. Genuine operator consent on the four PR numbers — FEAT-01 -> 4, FEAT-02 -> 4,
  FEAT-03-subissue-mirror -> 15, FEAT-04-decisions-index -> 15, attributed by PR title, not branch.
- Q2 (non-blocking, operator): should the harness open its own PRs? Contradicts DEC-153, so it is
  not the plan's to choose. The plan is correct under either answer.
- Q3 (non-blocking, operator) — **the render-only branch is now EVIDENCED, not merely chosen.** The
  question was whether `ship` should close the source issues directly instead of rendering `Closes`
  lines; D-04 takes render-only and crosses DEC-196. GitHub already performs the close correctly and
  unaided in about one second — #491's three issues closed within two seconds of merge from the
  keyword alone — so closing directly would replace a working platform mechanism with harness code
  that posts to GitHub, and the Goal's own sentence says nothing in this feature ever posts, edits or
  closes. The operator may still choose otherwise; what changed is that render-only is no longer a
  bare preference.
- Q4 (non-blocking, harness defect): FILED AS #670. Feature-id coinage collided twice and nothing
  detected it. The surviving pair is `FEAT-25-claim-feature-root` and
  `FEAT-27-expertise-repository-tier`.
- Q5 (non-blocking, correction): "check-state.sh carries 19 invariants" is FALSE — INV-1..INV-27 run,
  INV-20 is taken, INV-10 is retired. pm used INV-28 correctly. Sibling orchestrators may carry the
  same false premise.
- Q7 (non-blocking, operator): REQ-05 and SC-08 keep pre-amend counts ("eleven ... eleven",
  "twenty-three features this plan enumerates") while `## Problem` says twelve of twenty-seven.
  Left untouched deliberately — they describe the plan's enumerated scope, and the plan already
  carves out later features. Consequence, now realised rather than predicted: after FEAT-26 ships,
  FEAT-24 still carries `pr: null` and the new invariant names it — REQ-04 working, not a defect —
  and each feature shipped between signature and delivery adds another.
- Q8 (non-blocking, operator): the DEC-153 constraint bullet carries its own provenance (naming the
  defunct `DECISIONS.md:3660-3662` anchor). It stops someone re-pinning a line range later, but a
  signed brief now carries a paragraph about a dead anchor. Keep, or trim to id-only. **Moot for
  this feature — the BRIEF is signed and this seat never edits it.**
- Q11 (non-blocking, operator): the first accepted-cost entry names that *edits* and *closes* are
  unasserted even for the renderer — wider than the fix commissioned in that round. Accept, or narrow.
