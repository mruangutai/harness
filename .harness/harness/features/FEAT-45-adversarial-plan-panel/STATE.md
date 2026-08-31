# STATE

## Current

- feature: FEAT-45-adversarial-plan-panel
- run: .harness/harness/features/FEAT-45-adversarial-plan-panel/runs/2026-08-31-01-eng/state.yaml
- squad: none
- status: Building

Build opened on the signed plan; both approval fragments read `approved`, so the plan handoff's
STOP precondition is discharged. TWO of eleven tasks are done, verified and committed: T-01 at
2d7cbac (DEC-206 and DEC-207, index regeneration a fixed point) and T-09 at 5178bb1
(`panel_findings.py`, its test proved RED by five single-defect mutants, registered in UNIT_SCRIPTS).
The orchestrator re-ran each task's `verify:` verbatim itself; both exit 0 and the unit suite reads
0 `^FAIL ` lines at runner exit 0.

The build cannot advance further under agent authority. NINE tasks remain and none is dispatchable:

- T-02, T-03, T-04, T-05, T-06 are `main-session-direct` because their paths resolve to NOBODY —
  confirmed by running `check-domain.sh --resolve` on each, not by reading the plan's claim.
- T-07 and T-08 are the DEC-174 enforcement layer, which enumerates `check-state.sh` **and the test
  file of each** gate. DEC-174's ruling is that such a change is made directly and never dispatched
  through a team run whose gates are the thing being changed.
- T-11 and T-10 are squad-routable but their dependencies are real, and measured rather than
  assumed: T-11's `verify:` asserts `'fable-advisor' in shipped` against
  `.omp/agents/harness-validator-lead.md`, where the shipped `spawns:` list holds four harness
  entries and no advisor until T-06 lands; T-10's test opens `plan-panel.yaml` and greps
  `plan-panel` in `SKILL.md` and `harness-plan.md`, all three currently absent or zero-match.

The QA gate and SIMPLIFY are deliberately NOT run. SIMPLIFY is defined as the last build step before
`review_sha` pins, and a matrix verdict taken at 2 of 11 tasks is invalidated by the seven that
follow. `review_sha` stays 1d3e5db and is NOT re-pinned: pinning belongs to validate entry.

Cycles 4 of 10. Two were spent here — one re-dispatching T-01 after the DEC number collision, one
send-back inside the eng run for mutation-RED evidence. Runs 9 of 20 informational.

## Open Questions

- The DEC numbering collision is closed but its cause is not. `main` gained DEC-205 via PR #1032
  after this branch was cut, so "the next free number" read from inside a branch is wrong by
  construction whenever another branch lands a decision first. Nothing checks this; the collision
  was caught by hand. Whether the fix is a cross-branch number check in
  `gen-decisions-index.py --check`, a reserve-at-plan-time allocation, or accepting merge-time
  repair is undecided. — harness-orchestrator
- Accept the absent-persona trade as REQ-14 and SC-17 define it: where fable-advisor does not
  resolve, the panel records a skip that WARNS rather than fails, so the gate stays usable in a
  project lacking the operator's HOME definition. The alternative is a hard failure there. Not
  blocking. — harness-pm
- SC-16 remains the only thing that can settle whether the host RESOLVES fable-advisor to a runnable
  agent once the allowlist admits it. The stakes moved: the persona now carries REQ-02's model
  claim, not merely the spawn. Not blocking. — harness-pm
