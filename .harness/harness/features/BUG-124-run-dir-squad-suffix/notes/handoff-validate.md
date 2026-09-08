# Handoff — BUG-124-run-dir-squad-suffix, validate → ship — written at 4ed8b095, seq-1

## Next

Ship BUG-124 via `gh-sync.py ship .harness/harness/features/BUG-124-run-dir-squad-suffix`
(already executed by the main session; this note documents the validate → ship seam that
could not get a normal handoff note when it was crossed, per the known worktree handoff
defect recorded in STATE.md Open Questions Q2).

## Trust

- The validation panel passed at the pinned commit, severity_max med, must_fix empty —
  verified-at 4ed8b095 (runs/panel-c4-validator/digest.md).
- T-03 (main-session-direct SKILL.md doc task) landed with its phrase-exact verify passing
  and the instruction-path anchor check clean — verified-at 57ca26fc.

## Dead ends

- Do not open a fix cycle for Q7 (F-1, the read-grant fail-open in run_dir_grant_globs) —
  the panel rated it med and non-gating; it is a scope question for the operator, not this
  feature — source: STATE.md, verified-at 4ed8b095.

## Working set

- .harness/harness/features/BUG-124-run-dir-squad-suffix/STATE.md
- .harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml
- .claude/skills/harness/bin/dispatch-guard.sh

## Done when

Scope: ship BUG-124
Authority: approval:.harness/harness/features/BUG-124-run-dir-squad-suffix/plan.yaml#approval
