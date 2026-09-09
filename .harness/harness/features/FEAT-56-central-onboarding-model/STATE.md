# STATE

## Current

- feature: FEAT-56-central-onboarding-model
- run: .harness/harness/features/FEAT-56-central-onboarding-model/runs/goalcheck-ship-c2-product/state.yaml
- squad: none
- status: awaiting-user

Revised in place on the operator's re-scope of 2026-09-08, amended on their three signature
conditions, signed 2026-09-09, and built out. SHIP-READY at `review_sha` 8ff5197f, pushed, with
ZERO `check-state.sh` violations.

Onboarding is now two artifacts: `harness-init`, a six-step fresh-checkout procedure with no CLI
version check, and `harness-add-repo`, a three-step provider-neutral registration skill. `.omp/commands/`
is the canonical door root with generated `.claude/commands/` adapters, enforced by
`sync-command-adapters.py` and a `check-omp-port.py` door block — the defect being that the four
`/harness*` doors were invisible under OMP and fell through silently as prompt text. First BRIEF,
approval and design route to `/harness-plan`. The dead `cli_min_version` key is gone from all five
config sites and DEC-83 is amended.

Twenty tasks done. qa gate satisfied under D-14. SIMPLIFY applied before the pin. Review panel cycle
2: `must_fix: []`, severity_max med, all four cycle-1 findings independently closed; one further
advisory taken anyway, the door-delegation guard. Goal-check: eleven of sixteen criteria met, every
grade re-taken at this pin rather than inherited across the five pin moves. SC-07 red on exactly the
six D-14 cases. SC-09 struck. cycles_used 20 of 22.

Blocked only on the operator. No PR opened; no build work remains.

## Open Questions

- The UAT at `notes/uat-FEAT-56-c2.md` — three distinct walkthroughs, about fifteen minutes,
  PASS/FAIL only the operator sets. `gates.uat` is `blocking_when_uat_criteria_exist` and SC-11,
  SC-12 and SC-15 all exist, so it gates the merge. It is also the ONLY evidence that either
  procedure actually works: no runner grades an instruction being followed, and nothing observes a
  live provider resolving a door. This feature's UAT has failed three times — on ambiguous jargon,
  then misleading structure, then wrong scope — so it is not a formality.
- Backlog disposition, rows C-1..C-16 in `notes/ship-review-2026-09-09-ship.md`. Unstruck rows become
  issues; anything not listed dies silently. Seven are harness defects rather than this feature's
  residue.
- On a UAT FAIL there is room for exactly one fix cycle before `max_total_cycles` binds. The operator
  has already raised it twice. A FAIL line naming the specific misleading step lets one cycle close
  it; a bare FAIL may not.
