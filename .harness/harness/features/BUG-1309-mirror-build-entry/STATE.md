# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-06-t09-product/state.yaml
- squad: none
- status: in-flight
- station: building — ALL NINE tasks are built and each verified at the orchestrator tier.
  Team lane: T-01 98c650f0, T-02 a646a7bb (+ grade fix 7519cb74), T-03 e7569f01, T-09 ffceb68e.
  Main-session-direct: T-04 19aa670b, T-05 4338ee44, T-06 983ff852, T-07 13c44e90, T-08 147832ed,
  plus direct grade refactors 89cc686f and be8f764b.
- build entry outcome: opened — mirror receipt in feature.json github (milestone 54, parent 1407,
  sub-issues 1408-1416). github.build_entry did not exist when this feature's Build entry ran,
  which is why the plan declares BUG-1309 era-exempt.
- T-09 GRADE SUBSTITUTION, disclosed: its signed `verify:` calls
  `gen-decisions-index.py --check`, a flag that has never existed (exit 2; the tool's usage says
  so). T-09 was graded on the tool's documented equivalent, `--stdout | diff -`, plus the same
  DEC-220 and anchor assertions: VERIFY-PASS, zero index drift, one row appended. Whether to amend
  the signed string or accept the equivalence is the main session's decision.
- next, in order: the qa segment (test_matrix, the only blocking gate), then SIMPLIFY via
  eng-lead, then the review_sha pin with `gh-sync.py status <dir> review`. Held until the main
  session clears its three remaining grade-2 functions (merge-gate.py main,
  case_t06_build_entry_invariant, case_t07_build_entry_receipt) by refactor or by a written reason
  naming each — grade 2 is not an unconditional finding.

## Open Questions

- Backlog rows awaiting disposition at ship: B-1 gate-dispatcher consolidation plus
  gh-close-gate.sh/plan-sign-gate.sh missing from HOOK_SPECS; B-2 gh-sync.py:247 naming a remedy
  that pins no repo; B-3 the 17 unrecovered sync-enabled features; B-4 four features shipping the
  nonexistent `gen-decisions-index.py --check` clause in a signed verify.
