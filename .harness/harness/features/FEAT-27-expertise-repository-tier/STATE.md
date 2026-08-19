# STATE

## Current

- feature: FEAT-27-expertise-repository-tier
- run: .harness/harness/features/FEAT-27-expertise-repository-tier/runs/qa-validator/state.yaml
- squad: validator
- status: in-flight

Mission ship, build phase. Branch `feat/FEAT-27-expertise-repository-tier`; `review_sha` pinned at
`2117a46`, the commit whose tree contains T-02 and T-03. Mirror: milestone 17, parent #494 adopted,
sub-issues T-01 #565, T-02 #566 (closed), T-03 #567 (closed), T-04 #568, T-05 #569, T-06 #570.

**T-02 and T-03 are done.** The eng segment returned PASS with zero send-backs. Committed as
`6edb911` and `2117a46`. Independently re-measured at my own tier, not relayed: unit suite exit 0,
137 PASS, zero FAIL; integration suite exit 0, 90 PASS, zero FAIL. The repository tier was probed end
to end in a temp root — two segments inject under scope-only headers in sorted order, the precedence
line appears exactly once before the first repository block, and the 40- and 150-line truncation
notices each name their own budget. On the live tree, post-T-02 injected context is unchanged in size
for every agent (qa 134, orchestrator 149, dev-ops 35, frontend-dev 0) against the baseline captured
before the change; only the header wording moved.

Next: the qa segment (the project's only blocking gate) over the pinned commit, then the layer-0
batch hands to the main session — T-01, then T-04, then T-06, in that order, per
`notes/layer0-segments-FEAT-27.md`. On resume: T-05 (documentor), simplify over the full diff,
re-pin, review panel, goal-check, close-out, briefing.

Two reconciliations of the plan phase, recorded so a resume does not re-litigate them. `runs:` omits
the `2026-08-18-1-eng` dir: the architecture review it holds was a STEP INSIDE the product run (its
`state.yaml` step S-04), not a second run, and that dir holds no digest or state of its own.
`cycles_used` stays 0 — the plan run's internal step cycles were reported to the plan-phase
orchestrator, not to me, and DEC-157 counts only rework I route or a lead reports from inside a run I
dispatched.

`notes/handoff-plan.md` was written by me at build time, not at the seam; the plan phase crossed into
build without one and INV-17 reported it as a VIOLATION. It is labelled reconstructed and every claim
carries its evidence pointer and verification status.

## Open Questions

- `harness.json`'s `integration.detect` glob does not name `test-check-expertise.py` or
  `test-check-domain.py`, though `run-unit-tests.sh --kind integration` executes both — I measured it
  (`PASS test-check-expertise.py` in the run output; `INTEGRATION_SCRIPTS`, line 18). The obligation
  is genuinely discharged and the glob is stale metadata, not a gate. `harness.json` belongs to
  another live flow this cycle, so it is raised, not fixed. Non-blocking; backlog.
- T-03 case 2's `FEAT-\d+` sub-assertion cannot discriminate the new advisory from the pre-existing
  hard violation, so that one of ten token sub-cases passes against the unchanged checker. It follows
  from the approved intent, which forbids special-casing that token; strengthening it is a plan
  change. Non-blocking; backlog.
- All sixteen of T-04's anchor strings were re-verified at `253287f`. Re-check before T-04 executes.
- A plan-seam handoff note was authored after the fact by the build-phase orchestrator. If that reads
  as closing the gap rather than recording it, the operator should say so.
