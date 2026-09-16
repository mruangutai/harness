# Handoff — FEAT-1714-reject-verb, build → validate — written at 51e605f9b6a5be3bda667d2d3c62439fd4ab2434, seq-3

## Next

Validate over review_sha 51e605f9b6a5be3bda667d2d3c62439fd4ab2434: one validate dispatch to harness-validator-lead (qa, code, security, ui, goalcheck); any fix is main-session-direct (DEC-174).

## Trust

- T-01/T-03/T-05 built direct by Main; T-02 by harness-backend-dev under the eng-lead build team (its ESCALATE on T-02→T-03 ordering was answered by Main building T-03 in the same act); T-04 by harness-documentor — .harness/harness/features/FEAT-1714-reject-verb/plan.yaml — VERIFIED
- Both matrices pass on the rebased branch (unit 40 files, integration 72 files) — run-unit-tests.py — VERIFIED
- The invariant is INV-44, not the drafted INV-43 (BUG-1723 owns INV-43) — .claude/skills/harness/bin/check-state.py — VERIFIED

## Dead ends

- A block-form judgement mapping is not the contract; parse_digest keeps only inline flow mappings for the reject judgement — .claude/skills/harness/bin/validate-digest.py — VERIFIED
- The universal preload sits at 1895/1900 words after harness-handoff was trimmed to fit the rejected-return sentence; harness-eng-lead's preload reads 5509/5500 on main already (5499 before) — check-skill-weight.py — VERIFIED

## Working set

- .harness/harness/features/FEAT-1714-reject-verb/BRIEF.md
- .harness/harness/features/FEAT-1714-reject-verb/plan.yaml
- .harness/harness/features/FEAT-1714-reject-verb/feature.json
- .harness/harness/features/FEAT-1714-reject-verb/notes/receipt-main-session-T-01-fail-first.md
- .harness/harness/features/FEAT-1714-reject-verb/notes/receipt-main-session-T-03-fail-first.md

## Done when

Scope: validate segment
Authority: brief-perspective:.harness/harness/features/FEAT-1714-reject-verb/BRIEF.md#orchestrator
Authority: brief-sc:SC-01
