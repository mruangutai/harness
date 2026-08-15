Removed 8 key(s) from FEAT-02's feature.yaml because each had no reader; FEAT-14 closed the key set to eleven. This receipt is the only durable record of their values.

## status collapse (the pre-collapse pair survives only here)

- old status: `shipped`
- old phase: `None`
- new status: `Done`  (rule)

## value normalization

- `pr`: `'none'` (string) -> `null`

## removed keys, full values

```yaml
cost_usd: 49
max_cost_usd: 40
pending:
- pm goal-check on SC-01/SC-02 — not dispatched, budget exhausted; evidence ready
  at notes/qa-FEAT-02.md
runs[0].cost_usd: 5
runs[1].cost_usd: 2
runs[2].cost_usd: 21
runs[3].cost_usd: 21
skipped_segments:
- reason: design pass ruled no end-user interaction and no DESIGN.md exists — no contract
    to review (Expertise O-01)
  segment: 3-ui-reviewer-contract-check
```
