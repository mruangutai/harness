# STATE

## Current

- feature: FEAT-27-expertise-repository-tier
- run: none — awaiting the main session's layer-0 batch
- squad: none
- status: awaiting-layer-0

Mission ship, build phase, **paused at the layer-0 boundary, not blocked.** Branch
`feat/FEAT-27-expertise-repository-tier`; `review_sha` pinned at `2117a46`. Mirror: milestone 17,
parent #494 adopted, sub-issues T-01 #565, T-02 #566 (closed), T-03 #567 (closed), T-04 #568,
T-05 #569, T-06 #570.

**Two of six tasks are done and the blocking gate is discharged for them.** The eng segment returned
PASS with zero send-backs (`6edb911` T-02, `2117a46` T-03); the qa segment returned PASS with
`matrix_ok: true`, `must_fix: []`, `severity_max: low` and zero send-backs. Six success criteria —
SC-01, SC-04, SC-05, SC-06, SC-09, SC-10 — were shown to bind by MUTATION, not by reading
assertions. I independently re-measured both suites at my own tier (unit exit 0, 137 PASS, 0 FAIL;
integration exit 0, 90 PASS, 0 FAIL) and probed the hook end to end in a temp root: two segments
inject under scope-only headers in sorted order, the precedence line appears exactly once before the
first repository block, and the 40- and 150-line truncation notices each name their own budget.

**What is NOT proven: the feature.** SC-02, SC-03, SC-07 and SC-08 depend on T-01 and T-04, which are
unbuilt. A qa PASS here is a PASS on two tasks.

**Next, and it is the main session's:** the layer-0 batch — T-01, then T-04, then T-06, in that
order, per `notes/layer0-segments-FEAT-27.md`. No agent may write those surfaces; the domain guard
resolves them to NOBODY or to six different owners. Leave the result UNCOMMITTED — the commit pen is
the orchestrator's, and the `[harness:t-NN]` commit, the `plan.yaml` status write and
`gh-sync close-task` must happen as one ordered act per task.

**Then, on resume:** T-05 (documentor, needs T-01), simplify over the full diff, re-pin `review_sha`
at the new tip, review panel, goal-check, close-out (ship-refresh and distillation dispatched in ONE
turn), CEO briefing.

Two plan-phase reconciliations, recorded so a resume does not re-litigate them. `runs:` omits the
`2026-08-18-1-eng` dir: the architecture review it holds was a STEP INSIDE the product run (its
`state.yaml` step S-04), not a second run, and that dir holds no digest or state of its own.
`cycles_used` stays 0 — the plan run's internal step cycles were reported to the plan-phase
orchestrator, not to me, and DEC-157 counts only rework I route or a lead reports from inside a run I
dispatched.

## Open Questions

- Two coverage gaps found by qa, both OUTSIDE the SC text for T-02/T-03 and therefore correctly
  non-gating. Ranked by irreversibility: (a) no fixture builds an UNREADABLE repository-tier file, so
  `inject-expertise.sh`'s `[ -r ]` guard is unpinned — the code is correct, but a mutant removing it
  emits a phantom repository header with no body, which bears on REQ-05's hard constraint that the
  hook never degrades a spawn; (b) T-02 intent 1c's `^harness-[a-z0-9-]+$` SUFFIX rule has zero
  discriminating coverage — all four hostile fixtures are vacuous both before and after the change,
  because `"$agent.md"` is a quoted expansion so a `*` in the value never becomes glob-active.
  Closing either is new-test authoring, i.e. pm's under the operator's approval, not a build
  decision. **Needs a ruling: follow-up task this cycle, or backlog?**
- `harness.json`'s `integration.detect` glob does not name `test-check-expertise.py` or
  `test-check-domain.py`, though `run-unit-tests.sh --kind integration` executes both — measured, not
  inferred. Non-gating; the glob is stale metadata and the runner is the authority. `harness.json`
  belongs to another live flow this cycle. Backlog.
- T-03 case 2's `FEAT-\d+` sub-assertion cannot discriminate the new advisory from the pre-existing
  hard violation, so one of ten token sub-cases passes against the unchanged checker. It follows from
  the approved intent, which forbids special-casing that token. Backlog.
- T-03's `verify:` greps the LIVE craft corpus for `^ADVISORY `. It stays green after T-04 only
  because five entries were adjudicated to REMAIN craft. Nothing pins that coupling.
- All sixteen of T-04's anchor strings were re-verified at `253287f`. Re-check before T-04 executes.
- A plan-seam handoff note was authored after the fact by the build-phase orchestrator. If that reads
  as closing the gap rather than recording it, the operator should say so.
