# STATE

## Current

- feature: FEAT-27-expertise-repository-tier
- run: none — awaiting the main session's layer-0 batch and two adoption rulings
- squad: none
- status: awaiting-layer-0

Mission ship, build phase, **paused at the layer-0 boundary, not blocked.** Branch
`feat/FEAT-27-expertise-repository-tier`; `review_sha` pinned at `2117a46`. Mirror: milestone 17,
parent #494 adopted, sub-issues T-01 #565, T-02 #566 (closed), T-03 #567 (closed), T-04 #568,
T-05 #569, T-06 #570. `cycles_used` 0 of 10; four runs recorded against a 20-run budget.

**T-02 and T-03 are done and the blocking gate is discharged for them.** Eng returned PASS with zero
send-backs (`6edb911`, `2117a46`); qa returned PASS with `matrix_ok: true`, `must_fix: []`,
`severity_max: med`, zero send-backs. SC-01, SC-04, SC-05, SC-06, SC-09 and SC-10 were shown to bind
by MUTATION, not by reading assertions. I re-measured both suites at my own tier (unit exit 0, 137
PASS, 0 FAIL; integration exit 0, 90 PASS, 0 FAIL) and probed the hook end to end in a temp root: two
segments inject under scope-only headers in sorted order, the precedence line appears exactly once
before the first repository block, and the 40- and 150-line truncation notices each name their own
budget.

**What is NOT proven: the feature.** SC-02, SC-03, SC-07 and SC-08 depend on T-01 and T-04, which are
unbuilt. A qa PASS here is a PASS on two tasks.

**E1 is ruled (`runs/e1-judgment-product/digest.md`).** Neither coverage gap qa raised is a delivery
gap — no approved criterion is unmet and both tasks' code is correct as shipped. Gap (a), the `[ -r ]`
guard, SPLITS: REQ-05 commits the behaviour ("never blocked or **degraded** ... **including** when no
repository tier exists" — non-exhaustive), but no SC operationalizes it, and `plan.yaml:240`
specifies "nullglob semantics **or** an `[ -r "$f" ]` guard", so a fully conforming implementation
could carry no unreadable-file protection at all. Gap (b), the suffix rule, is NEW at every level and
its unique catch is narrower than first reported — path traversal with a valid prefix, which case 12
already carries and one fixture file would make discriminate. pm recommends one T-07 this cycle
(lane team/`harness-dev-ops`, `change_type: logic`), using a **dangling symlink** rather than
`chmod 000`, which is a no-op as root and not preserved by git. Adoption of either criterion is the
operator's. I verified all four of pm's anchors at source myself.

**Next, and it is the main session's:** the layer-0 batch — T-01, then T-04, then T-06, in that
order, per `notes/layer0-segments-FEAT-27.md`. No agent may write those surfaces. Leave the result
UNCOMMITTED; the commit pen is the orchestrator's, and the `[harness:t-NN]` commit, the `plan.yaml`
status write and `gh-sync close-task` must happen as one ordered act per task.

**Then, on resume:** T-05 (documentor, needs T-01), any adopted T-07, simplify over the full diff,
re-pin `review_sha`, review panel, goal-check, close-out (ship-refresh and distillation in ONE
turn), CEO briefing.

Two plan-phase reconciliations, so a resume does not re-litigate them. `runs:` omits the
`2026-08-18-1-eng` dir: the architecture review it holds was a STEP INSIDE the product run (step
S-04), not a second run, and that dir holds no digest or state of its own. `cycles_used` stays 0 —
that phase's step cycles were reported to the plan-phase orchestrator, and the crashed E1 attempt
wrote nothing and is not a cycle either.

The qa digest was REVISED after I first read it: the copy I read carried `severity_max: low` and
`escalations: []`; the final artifact carries `med` and E1. My first STATE.md write repeated the
stale value and is corrected. `med` changes no routing — `gates.review` is `advisory_unless_high`.
`validate-digest.py validator-lead <path>` reports `digest ok`.

`notes/handoff-plan.md` was written by me at build time, not at the seam; INV-17 reported the missing
seam note as a VIOLATION. It is labelled reconstructed, with per-claim evidence pointers.

## Open Questions

- **Q1 (blocking the amendment, not the ship).** Adopt a new success criterion under REQ-05 pinning
  the `[ -r ]` guard against an unreadable-but-present repository-tier file? Declining ships a
  hard-constraint behaviour correct-but-unpinned, on a hook that fires at every `SubagentStart`
  including nested spawns.
- **Q2 (non-blocking).** Adopt a discriminating test for T-02 intent 1c's `^harness-[a-z0-9-]+$`
  suffix rule? Cheap to close, thin to decline.
- The `[ -r ]` guard is double-covered for its specified duty and uncovered for its unspecified one:
  the segment filter at `inject-expertise.sh:75-77` independently rejects an unexpanded glob word,
  which is why the guard-removal mutant survived all 18 cases. Verified at source. Mutation survival
  there means masked by a sibling guard, not dead code.
- `harness.json`'s `integration.detect` omits `test-check-expertise.py` and `test-check-domain.py`
  though `run-unit-tests.sh --kind integration` executes both — measured, not inferred. Stale
  metadata, not a gate; the file belongs to another live flow. Backlog.
- T-03 case 2's `FEAT-\d+` sub-assertion cannot discriminate the new advisory from the pre-existing
  hard violation; 9 of 10 token sub-cases bind. Follows from the approved intent. Backlog.
- T-03's `verify:` greps the LIVE craft corpus for `^ADVISORY `. It survives T-04 only because five
  entries were adjudicated to REMAIN craft. Nothing pins that coupling.
- All sixteen of T-04's anchor strings were re-verified at `253287f`. Re-check before T-04 executes.
- A plan-seam handoff note was authored after the fact. If that reads as closing the gap rather than
  recording it, the operator should say so.
