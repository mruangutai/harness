# STATE

## Current

- feature: FEAT-28-ci-wiring-asserted
- run: .harness/harness/features/FEAT-28-ci-wiring-asserted/runs/2026-08-19-03-product/state.yaml
- squad: product
- status: awaiting-user

Plan phase complete. BRIEF.md (8 REQ, 11 SC) and plan.yaml (3 tasks, D-01..D-05) written,
both `pending`. Four product runs, 3 rework cycles of 10. Both gates exit 0 at 6bbd706.
No build dispatched, no git command run, nothing written outside this feature dir. Seam
note at notes/handoff-plan.md (seq-2, re-verified at 6bbd706).

## Open Questions

- BLOCKING, for the owner: DEC-183 settled that the CI step stays unguarded and deleted 39
  assertions to make that true — "not pending, settled". FEAT-28 reverses that one clause at a
  lower ceiling: a pure predicate over `yaml.safe_load`, no workspace clone, no workflow-body
  execution, amended not struck. If the owner still wants it unguarded the feature is void, not
  reduced — that reversal is the whole of FEAT-28.
- BLOCKING, for the owner: DEC-174's width is stated two ways that disagree about this file.
  DECISIONS.md @4627 enumerates four enforcement-layer files (check-domain.sh,
  bash-write-guard.sh, validate-digest.py, check-state.sh), excluding check-plan-routes.py;
  DECISIONS-INDEX.md states the CATEGORY "its own hooks, validators or gate scripts", which
  would include it. DEC-183 made check-plan-routes.py a CI gate AFTER DEC-174 was written, so
  the enumeration predates the fact. FEAT-28 edits the gate's TEST, not the gate. If the broad
  reading governs and a gate script's test inherits the carve-out, Route B is foreclosed and the
  work must be done directly instead. `check-domain.sh --resolve` answers only who may WRITE;
  the EXECUTION carve-out is mechanized nowhere.
- Non-blocking, scope to sign or strike: BRIEF gained REQ-08 and SC-10 to grade the three
  restored assertions (Unit suite present, continue-on-error absent, step-level if absent), and
  SC-05 was restated because it had encoded the old truncating rule verbatim — the broken
  implementation satisfied its own criterion. T-02 moved from change_type docs to logic.
- Non-blocking, harness defect, THREE occurrences: no `SendMessage` at orchestrator or lead
  tier, so a correction to an in-flight agent becomes a second spawn against the same unlocked
  file. Four run dirs exist for three intended runs; two pm spawns held plan.yaml and BRIEF.md
  concurrently. Nothing detects a second author and Write has no compare-and-swap.
- Non-blocking, harness defect: `harness.json` `test_kinds.unit.detect` (glob
  `.claude/skills/harness/bin/test-*.py`) and `test_kinds.integration.detect` (explicit list
  naming test-check-plan-routes.py) BOTH match the host file. Precedence is unread code, so the
  BRIEF asserts no kind.
- Non-blocking, harness defect: the orchestrator playbook says to record `phase:` in
  feature.json; feature-schema.json is additionalProperties:false and deliberately has no
  `phase` key (D-09/D-10). The Write hook blocks it.
- Non-blocking, still open from FEAT-25: `verify: automated` is ambiguous between "graded by
  running code" and "a standing assertion exists". This BRIEF works around it in prose.
- SETTLED by measurement, no longer a question: `tests.yml` is clean and no commit on this
  branch ever touched it, so FEAT-28 has no file conflict with FEAT-27. The wait is a landing
  constraint (one checkout, HEAD on their branch), not a contested file.
