# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: 2026-09-05-06-validator (panel, FAIL) and 2026-09-05-02-product (goal-check, FAIL)
- squad: none
- status: blocked

BLOCKED at the operator gate with the rework budget exhausted at 10 of 10. Not merged, no PR, the
worktree stands. `review_sha` is pinned at `9adbce6b690cd4b319c3758ab2a16505dd15900e`; the plan's
feature station is `review` and all five task stations are `done`.

The feature WORKS. Four reviewer lenses found zero behavioural defects, the blocking `test_matrix`
gate passed, and 17 of 19 success criteria are met. Every task `verify:` was re-run verbatim by the
orchestrator: unit 341 PASS / 0 FAIL / 27 files (316 before the feature), integration 14/0,
`--check-layout` exit 0, tree-audit `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`, anchors 30/0,
`check-state.sh` exit 0 with nothing for this feature. The plan phase's stated honest limit is
CLOSED: case 11's four red cases and two green controls were re-proved against the BUILT artifact by
the orchestrator's own probe, with the live-config wiring confirmed at
`tests/unit/test-suite-layout.py:493,528`.

Three things block, each verified by the orchestrator rather than relayed:
- B-1, high, gating: `code-grade.py` exits 1 at the pinned sha — `violations` grade 1 and
  `_registry_findings` grade 3 against a bar of 4. Re-run independently because the panel raised it
  on a single run it could not repeat. A COMPLEXITY finding, not a behavioural one.
- B-2, SC-12: `notes/qa-tree-audit.md` records `5f76d6b1…`, confirmed by `git merge-base
  --is-ancestor` NOT to be an ancestor of `review_sha`. It was orphaned by the origin/main rebase
  the main session performed at the orchestrator's request AFTER the note was written; the rows are
  byte-identical at both SHAs, so only the provenance token is wrong.
- B-3, SC-16: `violations()` does have exactly one caller (`run-unit-tests.sh:33`, verified by
  `git grep` at the pinned sha), but no unit assertion pins it repository-wide. Unproven, not wrong.

The briefing is `notes/ship-review-2026-09-05-ship.md`, rendered to `.html`. It carries twelve
backlog rows, B-1 through B-12; anything not listed there dies silently.

## Open Questions

- BLOCKING, for the operator: raise the cycle budget for one decomposition cycle, risk-accept B-1
  under DEC-176 and ship with two criteria UNMET, or stop. All three remedies are small and routable
  to squads that already own the files. Raising the budget is the operator's decision under DEC-157
  and accepting a high finding's risk is the operator's alone under DEC-176.
- Doctrine, non-blocking: "exhausts" is undefined as reached-versus-crossed in both DEC-157 and the
  playbook, and there is NO mechanical check on `max_total_cycles` — `check-state.sh` enforces only
  INV-7. `fable-advisor` ruled reached-does-not-stop and forward first-pass work continues; that
  ruling is what let validation run at all. A one-line decision retires the ambiguity.
- Harness defects observed this session, all in the briefing's backlog: members assigned to a
  worktree editing the MAIN checkout through bare relative paths (twice, both reverted);
  `check-domain.sh` refusing a first digest write as already-recorded; two runs' `state.yaml`
  clobbered by a later run and repaired from their surviving digests; and the carried-forward
  `validate-digest.py` `code_grade` deadlock for plan-phase readers.
