# Validation panel — PR #1772

PASS: the pinned change satisfies the revoke-approval specification and has no blocking defect. Three low-severity advisories remain; under DEC-31 they are notes, not `must_fix`.

```yaml
VERDICT: PASS
DIGEST:
  headline: "PR #1772 is compliant and fail-closed; three low advisories do not block under DEC-31."
  team: validate
  steps_run: 1
  cycles_used: 0
  members:
    - { step: code, persona: harness-code-reviewer, verdict: PASS, headline: "Stage 1 and Stage 2 pass with three low advisories.", files_touched: [] }
  must_fix: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/notes/analysis-BUG-1675-revoke-approval.md
  branch: none
  open_questions: []
  escalations: []
  expertise_update: []
  adequacy_notes:
    - "QA was not independently rerun: the operator supplied green integration, unit-kind, code-grade, and CI evidence, and the changed runtime behavior is exercised in tests/integration/test-plan-merge.py:3321-3385 and 3487-3500."
    - "Security was scoped out because the new verb adds no trust boundary beyond CLI arguments and uses the same governed-agent guard as sign-approval at plan-merge.py:2053-2064 and 2084-2111."
    - "UI was scoped out because the pinned files are a Python CLI, YAML template, and integration test; no visual or interactive UI surface changed."
    - "PM goal-check was scoped out because this DEC-174 direct patch intentionally has no feature metadata; the code review's Stage 1 used the operator-supplied specification as authority."
  severity_max: low
  readers:
    - { reader: code-reviewer, status: ran, reason: "Runtime behavior and spec compliance required the two-stage code review." }
    - { reader: qa, status: skipped, reason: "Bugfix matrix evidence was already visibly satisfied by the integration regression, unit-kind run, and green CI supplied with the pin." }
    - { reader: security-reviewer, status: skipped, reason: "No new security boundary beyond governed CLI invocation; revoke shares the sign-approval identity guard." }
    - { reader: ui-reviewer, status: skipped, reason: "No UI surface changed." }
    - { reader: pm-goalcheck, status: skipped, reason: "No BRIEF or plan exists for this direct patch; the operator supplied the complete acceptance specification." }
  findings:
    - id: F-01
      severity: low
      kind: substance
      raised_by: harness-code-reviewer
      path: tests/integration/test-plan-merge.py:3358
      failure_scenario: "If revoke later deleted an unrelated approval ruling or comment while keeping signer/date, the current fixture and outside-approval comparison would still pass; the fixture contains no ruling/comment at test-plan-merge.py:3205-3208."
      disposition: "Advisory note; current implementation preserves unmodified approval-body lines at plan-merge.py:828-836."
    - id: F-02
      severity: low
      kind: substance
      raised_by: harness-code-reviewer
      path: tests/integration/test-plan-merge.py:3373-3384
      failure_scenario: "If the pending-plan refusal modified the file, the approved fixture rewritten at line 3376 would erase that evidence before the only byte-identity assertion at line 3384."
      disposition: "Advisory note; current implementation refuses the non-approved state before returning transformed bytes at plan-merge.py:2093-2102."
    - id: F-03
      severity: low
      kind: form
      raised_by: harness-code-reviewer
      path: .claude/skills/harness/bin/plan-merge.py:1992-1997
      failure_scenario: "A maintainer following the docstring can incorrectly conclude that every non-sign verb preserves approval bytes, although revoke-approval intentionally writes the downward transition at lines 2084-2111."
      disposition: "Advisory documentation correction; form findings do not gate."
artifact: /Users/molchairuangutai/GitHub/harness/.harness/notes/analysis-BUG-1675-revoke-approval.md
```

## Assessment

### Stage 1 — specification compliance: PASS

The pinned range is `8ef4731e..fd3ffe5a`, with review SHA `fd3ffe5a`. The reviewer found no omission, mismatch, scope creep, or unauthorized status. `cmd_revoke_approval` normalizes the reason, records `revoke-approval <by>: <reason>`, rejects non-approved state with exit 5, and verifies the reloaded reset before writing (`.claude/skills/harness/bin/plan-merge.py:2084-2111`). The shared identity guard retains exit 10 and the REQ-05/DEC-120 message shape (`plan-merge.py:2053-2064`).

### Stage 2 — code quality: PASS

The reset helper preserves unrelated approval lines and refuses shapes it cannot safely rewrite (`plan-merge.py:808-853`). Both call sites use the new `(lines, reason)` signature (`plan-merge.py:863,2100`). Flow-style approval is covered by a fail-closed regression that checks exit 5, byte identity, and no false receipt (`tests/integration/test-plan-merge.py:3487-3500`). INV-40 only grades signed task hashes while approval is `approved`, so retained `feature.json.signed_task_hashes` are inert after revoke; re-signing replaces them (`check-state.py:2900-2908`; `plan-merge.py:2034-2039`). No production consumer parses `reset_reason`; existing assertions treat it as an opaque value (`tests/integration/test-plan-merge.py:3226-3227,3330-3331`).

Evidence supplied with the pin: `tests/integration/test-plan-merge.py` PASS; `run-unit-tests.py --kind unit` exit 0; `code-grade.py` 9/9 PASS; CI integration green. These suites were not rerun, as directed.

The full code-review artifact is at `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1675-revoke-approval/.harness/harness/features/BUG-1675-revoke-approval/notes/review-harness-code-reviewer-c0.md`.
