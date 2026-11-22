# Host findings for PM apply

## Literal task verification scalars

- reader: harness-product-lead
- kind: form
- severity: med
- scope: none
- summary: Task verify commands are serialized as quoted strings instead of mandatory literal blocks.
- Evidence: draft plan.yaml T-10 verify (lines 796–799) is a single-quoted multi-line YAML scalar. DEC-182 / harness-zero-micro-management step 2 requires `verify: |` so dispatch strings are unambiguous. Required plan check nevertheless passed; do not misreport that check as covering literal scalar style.
- Remedy: use the existing controlled plan writer's supported path to emit task verify as literal blocks while preserving exact command strings. No direct editor writes to plan.yaml and no unrelated writer change in this planning run. If the controlled writer cannot express required style, report the tooling conflict to the orchestrator instead of silently bypassing it.

## Approval questions

The PM's OQ-01 asks for the same batched plan signature requested by this assignment; represent it as `needs_approval: true`, not as an extra unresolved operator question. Carry the distinct Kaya merge authorization question if it remains a separate authority decision.
