# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: none in flight
- squad: none
- status: awaiting-user

Phase: **ship, building, stopped on a plan-ordering defect.** Two tasks are done, verified and
committed on `feat/FEAT-24-config-responsibility-split`: `000934b` `[harness:t-01]` (factory_gh
gains `file_at_ref`, red-first proven per case with sha256 restore checks) and `22814c7`
`[harness:t-08]` (the config template's `_board_note`, executed by hand by the main session). I
re-ran both verifies myself on disk: `T-01 GREEN`, `T-08 GREEN`.

**The blocker, measured by the eng lead and re-verified by me.** T-02's `factory_config.py` change
and `fleet.yaml`'s board removal are ONE atomic change that the plan splits across two lanes five
tasks apart. `harness_boundary.classify()` calls `resolve_fleet` as its FIRST statement for every
governed write, which calls `load_fleet` on the live `fleet.yaml` and `sys.exit(2)` on any
exception. The current loader REQUIRES `repos[].board`; the new one REJECTS it. No state of that
file satisfies both, so the transition cannot be crossed by any agent's write in either direction.
The main session is ungoverned (`check-domain.sh:271`) and is the only actor that can cross it.

**Three options, costed, at `notes/segment-02-ordering-decision.md`** — my recommendation is A:
merge T-09 first, dispatch T-02 with `factory_config.py` as the member's final write, then the
operator deletes the board block from `fleet.yaml`, then a continuation run finishes T-02's
mutation proofs and carries into T-03, T-06, T-04.

**Segment 01 is still open:** T-09 has not merged — kaya's `master` still carries all four
pre-FEAT-18 pinned ids. It is now on the critical path twice over, because merging it before the
cutover makes D-10's window zero. Commands unchanged at `notes/segment-01-main-session.md`.

`plan.yaml` reconciled to what actually ran: T-02, T-03, T-04 and T-06 were marked `building` at
dispatch and never executed, so they are back to `pending`. Their board cards were returned to
`Backlog` with `board-station.py` — INV-26 caught that drift as four real violations first.

Cycles: 1 of 10, unchanged — zero send-backs reported. Runs: 7 of 20.

## Open Questions

- Q1 (operator, BLOCKING): which of the three orderings for the T-02 cutover —
  `notes/segment-02-ordering-decision.md`. A and B are yours alone; C is a plan amendment needing pm.
- Q2 (operator, BLOCKING): T-09 executed and merged. Segment 01, still accurate.
- Q3 (operator, may ride the above): D-10's `because` still reads "nothing in this repository can
  enforce" the merge-before-T-07 ordering. T-07's verify now enforces it (`plan.yaml:1117-1121`).
- Q4 (operator): D-06 records no reversibility cost — a sixth station key later is N
  cross-repository pull requests, one operator merge each.
- Q5 (carried, undispositioned): the plan-phase architecture review asked that T-04's rewritten
  `load_board` docstring state it raises `FleetError`. T-04 did not run.
- Q6 (carried): `validate_board`'s `what` slot reads "fleet key invalid" at five raise sites
  (`factory_config.py:80,84,90,95,105`); after T-02 neither surviving caller reads `fleet.yaml`.
- Q7 (harness defect): `feature.json`'s schema declares no `phase` property under
  `additionalProperties: false`, so the playbook's "record your phase there" is unsatisfiable.
- Q8 (harness defect): `validate-digest.py` rejected read-only members' returns over `suite: n/a` /
  `task: none`, and one member ran a full suite purely to populate the field.
- Q9 (main session): two feature directories both claim FEAT-25, alongside
  `FEAT-27-expertise-repository-tier`. An id collision from concurrent planning, not FEAT-24's.
