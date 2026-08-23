# STATE

## Current

- feature: FEAT-26-pr-linkage-recorded
- phase: **ship / build segment** (plan phase closed; seam note is `notes/handoff-plan.md`)
- status: Building — `feature.json` reconciled this cycle, `branch: none` -> `feat/FEAT-26`
  and `status: Ready` -> `Building`. Validated against `bin/feature-schema.json`, exit 0.
- BRIEF and plan are BOTH signed (`approved`, Mike Ruangutai, 2026-08-23). Verified on disk,
  not inherited: `plan.yaml:6-9` and `BRIEF.md:164-166`. Neither approval block is ever
  written by this seat.
- worktree: `.claude/worktrees/harness/FEAT-26-pr-linkage-recorded`, current with `main` at
  `8d56f97`. The main session merged eight commits in and resolved one conflict before this
  run began. Nothing further is merged here and HEAD is never moved.
- **Suite baseline taken BEFORE any build work: `run-unit-tests.sh --kind all` exits 0, green.**
  Any red at the end of the build segment is therefore a delta this feature caused.
- `check-plan-routes.py` re-run in the worktree: **0 violations across 1 plan**. T-05 and T-06
  report as DEVIATION, which is correct and deliberate — both are grantable to a lane but
  declared `main-session-direct` under the DEC-174 carve-out, i.e. more restrictive than
  routing requires.
- **GitHub mirror OPENED this cycle** (the orchestrator's sync point, immediately after the
  approval gate): milestone **#22**, parent **#732** (`parent_origin: created`), sub-issues
  **#733-#740** for T-01..T-08. All eight attached. Note for the ship step: `parent_origin` is
  `created`, so `gh-sync.py ship` will close #732.
- T-01..T-04 set to `status: building` in `plan.yaml` and `start-task` run for each, in that
  order (plan first, then the subcommand). Parent #732 derives to `Building`.
- **Build eng segment dispatched to `harness-eng-lead` as the `build` team: T-01, T-02, T-03,
  T-04, strictly serial.** T-03 and T-04 are concurrently ready in the DAG and both write
  `gh-sync.py` and `test-gh-sync.py`; nothing in the harness detects that collision (#730), so
  serialisation was ordered explicitly rather than left to `mutates_repo: true` alone.

### The three carve-out tasks are NOT dispatchable and are the next stop

T-05, T-06 and T-07 are `execution_mode: main-session-direct` under DEC-174. This seat routes
none of them; a lead would be refused by `check-domain.sh` and the spawn wasted.

- **T-05** (`depends_on: []`, ready now) — INV-28 in `bin/check-state.sh` + `test-check-state.py`.
  Inside the carve-out enumeration, widened again 2026-08-23 to include `dispatch-guard.sh`.
- **T-06** (`depends_on: [T-03]`) — backfill eleven shipped features' `pr`.
- **T-07** (`depends_on: [T-03, T-04]`) — `templates/plan.yaml` and `harness/SKILL.md`, both of
  which `check-domain.sh --resolve` returns NOBODY for.

T-08 (documentor, DECISIONS.md + index) depends on T-03, T-04 **and T-05**, so it cannot start
until the operator has landed T-05. All three carve-out tasks are therefore reported together in
one return rather than three.

### Sequence still owed after the carve-out tasks land

qa gate (`test_matrix`, the project's only blocking gate) -> four-angle simplify pass as the last
build step -> **re-pin `review_sha`** (currently `ada8e99`, stale, INV-6 fails an unpinned
validator run) -> the full `review.yaml` validation panel -> fix cycles -> pm goal-check against
SC-01..SC-11 -> CEO briefing.

### Budget

`cycles_used` 0 of `max_total_cycles` 10. `runs` 1 of `max_total_runs` 20 (informational, DEC-134
/ INV-22). Carve-out segments are not runs and never appear in `runs:`, so the count is a floor.

### Stale premises deliberately not inherited

- **Q5 is FALSE as written in the plan-phase dispatch**: `check-state.sh` runs INV-1..INV-27, not
  19. INV-20 is taken and INV-10 is retired and unreusable. pm used INV-28 correctly.
- **The four T-06 PR numbers are MEASURED, not derivable from branches.** FEAT-01 -> 4,
  FEAT-02 -> 4, FEAT-03-subissue-mirror -> 15, FEAT-04-decisions-index -> 15. Attribution is by
  PR *title*: #4's merge commit `04a57fc` adds both `FEAT-01/` and `FEAT-02/`; #15's title names
  FEAT-04 and FEAT-03 outright. Re-deriving these from branch names is the method that fails.
- **INV-28 belongs to FEAT-26.** FEAT-34 also claimed it; the operator ruled FEAT-26 builds first
  and FEAT-34 is moving to INV-29. T-05 builds INV-28 as planned.
- **`run-unit-tests.sh` DOES have a `--check-kinds` mode** (line 26). The plan-phase note saying
  it does not was true at `e56ee60` and is false at `8d56f97`; the merge brought it in.

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
