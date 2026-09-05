# Handoff — BUG-1286-test-tree-enforcement, build → validate — written at 6a5e0e0b, seq-6

## Next

Dispatch the `review` team to `harness-validator-lead` at the pinned `review_sha`, naming the
exact file set: `.claude/skills/harness/bin/suite_layout.py`, `tests/unit/test-suite-layout.py`,
`tests/integration/test-run-unit-tests-layout.py`, `tests/manual/suite-census.py`,
`.harness/harness/docs/DECISIONS.md`. Then pm's goal-check over BRIEF's nineteen SC-NN through
`harness-product-lead`. All five plan tasks are at station `done` and the qa gate has passed, so
nothing in `plan.yaml tasks:` remains to build.

## Trust

- All five tasks built and each plan `verify:` re-run verbatim by the orchestrator, not relayed —
  unit 341 PASS / 0 FAIL / 27 files, integration 14/14, census `TOTAL 85 OUTSIDE 9 VIOLATIONS 0`,
  anchors 30/0 — re-run post-rebase — verified-at 6a5e0e0b.
- The plan-phase honest limit is CLOSED: case 11's four red cases and two green controls re-proved
  against the BUILT artifact by the orchestrator's own probe, and the wiring confirmed by reading
  `tests/unit/test-suite-layout.py:493,528` where the live `repo_cfg["test_kinds"]` reaches
  `hygiene_uncertified` — verified-at 6a5e0e0b.
- T-02 case 3's ordering assertion was TAUTOLOGICAL as first delivered and is now derived from the
  runner's actual output order — `tests/integration/test-run-unit-tests-layout.py:107` —
  verified-at 6a5e0e0b.
- `cycles_used` is 10 of 10, EXHAUSTED. `fable-advisor` ruled the counter does include the qa
  lead's send-back and that forward first-pass work continues, stopping at the first rework demand
  — `runs/2026-09-05-04-validator/digest.md` — verified-at 6a5e0e0b.
- BRIEF carries NO `verify: uat` criterion; all nineteen are `automated` or `inspection`, so
  `gates.uat` does not fire — BRIEF.md lines 69-173 — verified-at 6a5e0e0b.
- Two qa-gate low findings ride as advisory, neither gating — `notes/qa-matrix-gate-c2.md` —
  verified-at 6a5e0e0b.

## Dead ends

- Do not dispatch a fix for any FAIL, unmet SC or high finding — zero cycles remain; stop and
  return BLOCKED instead — `feature.json` `cycles_used` — verified-at 6a5e0e0b.
- Do not unify the three clauses' vocabularies and do not add a `tracked_paths_fn` seam —
  `notes/review-harness-eng-lead-plan-c0.md` — verified-at 6a5e0e0b.
- Do not remove case 11's positive control or its INAPPLICABLE branch, and add no cardinality or
  occupancy assertion — `plan.yaml` T-01 case 11 — verified-at 6a5e0e0b.
- Do not edit `.harness/harness.json`; SC-14 asserts the diff changes no byte of it — BRIEF.md:144
  — verified-at 6a5e0e0b.
- Do not `git rebase`, `checkout` or `reset` — `bash-write-guard.sh` refuses every HEAD move for a
  governed agent; the main session performed the rebase to 6a5e0e0b from outside — verified-at
  6a5e0e0b.

## Working set

- .harness/harness/features/BUG-1286-test-tree-enforcement/BRIEF.md
- .harness/harness/features/BUG-1286-test-tree-enforcement/plan.yaml
- .harness/harness/features/BUG-1286-test-tree-enforcement/feature.json
- .harness/harness/features/BUG-1286-test-tree-enforcement/notes/qa-matrix-gate-c2.md
- .claude/skills/harness/bin/suite_layout.py

## Done when

Scope: The validation panel has graded the pinned revision and pm has judged every SC-NN
Authority: finding:.claude/worktrees/harness/BUG-1286-test-tree-enforcement/.harness/harness/features/BUG-1286-test-tree-enforcement/notes/receipt-harness-dev-ops-simplify-simplification-build-c1.md#F-1
