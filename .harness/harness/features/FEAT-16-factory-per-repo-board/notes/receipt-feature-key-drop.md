FEAT-16-factory-per-repo-board's feature.yaml lost no keys — it already carried only keys inside the closed set.

## status collapse (the pre-collapse pair survives only here)

- old status: `in_review`
- old phase: `plan`
- new status: `Ready`  (OPERATOR DEVIATION from the signed rule)

**OPERATOR DEVIATION from T-04's signed rule, recorded rather than disguised.** The rule places `in_review / plan` at `Review`. The operator placed it at `Ready` on 2026-08-11: this feature's plan is signed and undispatched, which is what `Ready` means, and no old value maps to `Ready` because the old vocabulary had no signed-and-waiting state. Following the rule would have left `Ready` empty on the harness board on day one.

## value normalization

- `pr`: `'none'` (string) -> `null`
