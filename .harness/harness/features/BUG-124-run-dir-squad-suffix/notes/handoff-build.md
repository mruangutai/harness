# Handoff — BUG-124-run-dir-squad-suffix, build → validate — written at 4ed8b095, seq-1

## Next

Ship BUG-124 once its PR merges: `gh-sync.py ship
.harness/harness/features/BUG-124-run-dir-squad-suffix`. Validate is already complete
(panel PASS, severity_max med, must_fix empty) — this note documents the build seam that
could not get a normal handoff note when it was crossed (worktree handoff defect, STATE.md
Open Questions Q2).

## Trust

- T-01/T-02 landed and the blocking qa gate passed; a real full-sweep regression found by
  qa (a fixture missing harness_yaml.py) was root-caused to one line and fixed with a lazy
  import, independently re-verified by full sweep — verified-at 418a9eb6.
- SIMPLIFY ran and the validate panel passed at the pin, must_fix empty — verified-at
  6c037de4.
- T-03 (the main-session-direct SKILL.md doc task) landed and its phrase-exact verify
  passes — verified-at 4ed8b095.

## Dead ends

- Do not open a fix cycle for Q7 (F-1, the read-grant fail-open in run_dir_grant_globs) —
  the panel rated it med and non-gating, latent with no live trigger; it is a scope
  question for the operator, not this feature's fix cycle — source: STATE.md, verified-at
  4ed8b095.

## Working set

- .harness/harness/features/BUG-124-run-dir-squad-suffix/STATE.md
- .harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml
- .claude/skills/harness/bin/dispatch-guard.sh

## Done when

Scope: ship BUG-124 once its PR merges
Authority: approval:.harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml#approval
