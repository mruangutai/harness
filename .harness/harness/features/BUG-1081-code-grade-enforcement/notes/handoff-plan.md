# Handoff — BUG-1081, plan → build — written at b4cb23c0, seq-1

<!-- Written retrospectively at the ship gate: the plan seam was crossed by the main
     session before this orchestrator was spawned, so no note existed. Reconstructed
     from the approved artifacts and the plan-phase reviews, and every claim carries the
     pointer that was actually checked. -->

## Next

Dispatch T-01 to `harness-eng-lead` (build team, `harness-backend-dev` by the plan's own
`execution_agent`), then execute T-02 and T-03 directly under DEC-174, then T-04 to
`harness-product-lead`. Inputs: `plan.yaml` tasks T-01..T-04 and `BRIEF.md` SC-01..SC-12.

## Trust

- BRIEF and plan are both `approved` by the operator, 2026-09-01 — `BRIEF.md` `## Approval`
  and `plan.yaml` `approval.status` — verified-at 965c0e35
- The adversarial plan panel ran three readers and every finding is `resolved` —
  `plan.yaml` `panel.findings` (8 findings, dispositions all `resolved`) — verified-at 965c0e35
- T-02 and T-03 are `main-session-direct` and may NOT be delegated: `validate-digest.py` and
  its test are the enforcement layer being changed, and `harness-code-review/SKILL.md`
  resolves NOBODY — `plan.yaml` `lanes.rows` — verified-at 965c0e35
- The result vocabulary and grade bars from FEAT-43 are retained; this defect changes who
  computes and verifies the result, not what grades mean — `BRIEF.md` `## Constraints` —
  verified-at 965c0e35

## Dead ends

- A second, independent grading implementation is OUT OF SCOPE — `plan.yaml` D-07 — verified-at 965c0e35
- Calling `code-grade.py` as a subprocess was considered and REFUSED: the hook already imports
  `code_grade`, exit 0 combines pass with grade 2 — `plan.yaml` D-03 — verified-at 965c0e35
- Removing `code_grade` from the digest schema was considered and refused; it stays as a
  readable audit claim — `plan.yaml` D-01 — verified-at 965c0e35

## Working set

- `.harness/harness/features/BUG-1081-code-grade-enforcement/plan.yaml`
- `.harness/harness/features/BUG-1081-code-grade-enforcement/BRIEF.md`
- `.claude/skills/harness/bin/validate-digest.py`
- `.claude/skills/harness/bin/code_grade.py`
