# Handoff — BUG-151-check-domain-fail-aggregation, build → validate — written at 9b7b27d0, seq-1

## Next

Ship BUG-151 once its PR merges: `gh-sync.py ship
.harness/harness/features/BUG-151-check-domain-fail-aggregation`. Validate is already
complete (cycle-1 panel PASS, must_fix empty) — this note documents the build seam that
could not get a normal handoff note when it was crossed (worktree handoff defect, same root
cause diagnosed across all five parallel BUG flows this session).

## Trust

- T-01 and T-02 landed (test-check-domain.py's 21 hand-written aggregation sites replaced
  with discovery plus a printed-vs-counted safeguard), verified against both tasks' own
  `verify:` after a host-side timeout crash, committed at 36446eb5.
- The blocking qa gate passed, code byte-identical after SIMPLIFY (sha256-verified) —
  committed at fffc62d9.
- The validate panel's one gating blocker (the safeguard's predicate was pinned but the
  capture seam was not — deleting `redirect_stdout` around a discovered block stayed green)
  was fixed by extracting `_run_block_captured`, shared by the discovery loop and one new
  permanent case, then independently re-verified by mutation — committed at 9b7b27d0.

## Dead ends

- Do not expand scope to the two sibling suites with the identical un-safeguarded shape
  (test-validate-digest.py, test-bash-write-guard.py) — out of scope by an approved BRIEF
  constraint — source: STATE.md, verified-at 9b7b27d0.

## Working set

- .harness/harness/features/BUG-151-check-domain-fail-aggregation/STATE.md
- .harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml
- tests/integration/test-check-domain.py

## Done when

Scope: ship BUG-151 once its PR merges
Authority: approval:.harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml#approval
