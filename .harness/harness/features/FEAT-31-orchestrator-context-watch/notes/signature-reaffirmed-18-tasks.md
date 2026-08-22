# Signature re-affirmed at 18 tasks — 2026-08-21

The operator re-signed `plan.yaml` after the plan-amend round, having been shown the two things a
machine reads that changed since the original signature:

1. **D-21 gained 299 characters no loader could previously see.** A bare ` ##` opened a YAML comment
   inside a plain scalar, so `safe_load` — and therefore every gate — silently truncated the choice
   from the moment of the original signature. pm repaired it by quoting.
2. **The discovery clause now specifies the opposite depth** to the one the original signature covered.

The `approval:` block was never reset and is byte-identical to the original — `status: approved`,
`approved_by: operator`, `date: 2026-08-21`. **This note, not a field change, is what distinguishes a
signature taken at 14 tasks from one re-affirmed at 18.** Nothing else records that difference.

Plan commit at re-affirmation: `33d894e`. Task count 18, plan 1,550 lines, `safe_load` clean,
`run-unit-tests.sh --kind all` exit 0 with zero FAIL lines, measured in this worktree.

## Build order is constrained, not advisory

**T-18, then T-17, then T-12.** T-17 appends `test-context-watch-hook.py` to `INTEGRATION_SCRIPTS` in
`run-unit-tests.sh` — the same file T-12 edits. Until T-18 adds the matching path to
`test_kinds.integration.detect`, `absent from detect` is 1, which reds T-11's already-recorded PASS
and makes T-12's own `--check-kinds` exit 2, failing both required `tests.yml` steps for every kind.

T-04, T-10 and T-14 have no interaction with the four new tasks and are ready independently.

## One defect the re-signature carries forward

T-14's verify line 2 was written as `check-state.sh | grep -c 'handoff-' || true` against an expected
count of 0. The real count is **3** — three INV-17 exemption notes containing the literal `handoff-`.
The `|| true` meant the line could not fail in either direction, so the wrong baseline was never
caught. pm re-anchored it on the ` VIOLATION ` prefix. This is the third assertion found today that
was green and incapable of going red, which is the defect class this feature exists to close.
