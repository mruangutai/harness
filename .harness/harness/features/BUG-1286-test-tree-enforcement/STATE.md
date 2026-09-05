# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: entering validate — panel not yet dispatched
- squad: none
- status: review

Build phase COMPLETE. All five tasks T-01..T-05 are at station `done` and committed. The
orchestrator re-ran every plan `verify:` verbatim rather than accepting a digest: unit 341 PASS /
0 FAIL / 27 files (316 before this feature), integration 14 PASS / 0 FAIL, `--check-layout` exit 0,
census `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` with the `--against` round-trip at exit 0, decision anchors
30 examined / 0 failed.

The plan phase's stated honest limit is CLOSED. Case 11's four red cases and two green controls were
re-proved against the BUILT artifact by the orchestrator's own probe, and the wiring was confirmed by
reading `tests/unit/test-suite-layout.py:493,528`, where the live `repo_cfg["test_kinds"]` reaches
`hygiene_uncertified`. Every earlier result on record was a hand-simulation of the specification.

The qa `test_matrix` gate PASSED with `must_fix` empty. It surfaced one real defect: T-02 case 3's
ordering assertion was tautological and could not report red. That was fixed as forward work and the
assertion now derives from the runner's actual output order. SIMPLIFY then ran its four angles and
applied two behaviour-preserving changes.

The main session rebased onto origin/main from outside the worktree — `bash-write-guard.sh` refuses
every HEAD move for a governed agent. HEAD is `6a5e0e0b`, tree clean, all suites re-run green after
the rebase.

`cycles_used` is 10 of 10, EXHAUSTED. `runs` is 35 against an informational `max_total_runs: 20`;
INV-22 notes it and never gates.

## Open Questions

- The budget ruling, from `fable-advisor` via the validator lead: the qa lead's send-back DOES
  increment `cycles_used` under DEC-157 however the lead characterised it, and at 10 of 10 forward
  first-pass work continues while the branch stops at the first actual rework demand. Practical
  effect: any FAIL, unmet SC or high panel finding from here is `BLOCKED`, not a fix dispatch.
- Doctrine residual for the operator: "exhausts" is undefined as reached-versus-crossed in both
  DEC-157 and the orchestrator playbook, and there is no mechanical check on `max_total_cycles` at
  all — `check-state.sh` only enforces INV-7. A one-line decision clarification retires it.
- Two qa-gate advisory lows ride into the panel: the latent non-gating `INAPPLICABLE` branch at
  `tests/unit/test-suite-layout.py:524`, and SIMPLIFY's two verified-dead conditions backlogged as
  F-1 and F-2 in `notes/receipt-harness-dev-ops-simplify-simplification-build-c1.md`.
- Harness defect carried from the plan phase: `validate-digest.py` requires `code_grade` on a
  code-reviewer digest and rejects every value while `review_sha` reads `none`, so a plan-phase panel
  reader that did its job settles as `failed`. Out of this feature's scope.
- Harness hazard observed twice this run: members assigned to a worktree edited the MAIN checkout by
  passing bare relative paths to file tools. Both incidents were caught and reverted, and the main
  checkout is clean of feature paths. Worth a guard.
