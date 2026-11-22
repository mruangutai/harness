# Operator signature: BUG-2253, 2026-11-21

The operator pre-approved this patch at grilling ("presigned"), together with the three settled decisions:
- a 30s named hang budget at all six call sites,
- FAIL/MUTATED lines before the tail in the gate's refusal,
- main-session-direct execution.

The intake (run `2026-11-21-01-patch-product`, PASS) carries those decisions as SC-01 and SC-02 under T-01, which runs main-session-direct under DEC-174.

Rework ruling: 1 round, 45 minutes. No panel ran (patch mission), so nothing is overruled.
- Amendment during build: T-01 verify now uses the existing `--only run_bug2253_cases` selector instead of a new `--patch-2253-regressions` flag (amendment judgement on T-01.verify). Operator chose "amend".
