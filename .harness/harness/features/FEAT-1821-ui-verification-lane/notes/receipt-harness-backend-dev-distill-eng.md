# Distillation receipt — harness-backend-dev

HARNESS-MISSION: distill

## Result

Craft retained two durable fail-closed verification rules; repository Expertise was unchanged.

| Layer | Before (Patterns/Gotchas/Outcomes/Open) | After (Patterns/Gotchas/Outcomes/Open) |
|---|---:|---:|
| Craft — `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-backend-dev.md` | 15/15/10/0 | 15/15/10/0 |
| Repository — `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-backend-dev.md` | 4/11/1/0 | 4/11/1/0 |

## Accepted

- Digest source `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/fix-c7-eng/digest.md`: craft `P-02` now requires reporter/inspection errors to become gate-rejected failed results. It survives six spawns and prevents fail-open verification.
- Digest source `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/build-eng-t08-t13-eng/digest.md`: craft `P-03` now requires configured-runner discovery proof for specs outside an established match. It survives six spawns and prevents focused runs masking nondiscovery.

Both entered the full Craft Patterns section by displacing weaker `P-02` (standalone-import smoke check) and `P-03` (wrapped-idiom counting) respectively.

## Rejected

- Observation source `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-backend-dev.md` (Node strip-types `.ts` extension): environment-specific import-resolution detail; direct runtime failure exposes it and it does not meet the six-spawns test.
- Observation source `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/observations/harness-backend-dev.md` (single Playwright matcher): transient feature configuration, not a durable repository invariant; its reusable lesson is captured by craft `P-03`.
- Digest source `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/runs/simplify-eng/digest.md`: shared WebP helper is frontend-local implementation cleanup, not a new durable backend rule.

## Applied ops

```yaml
- op: replace
  target: P-02
  section: Patterns
  entry: "WHEN a reporter or inspection step errors DO record it as a failed result that downstream gates reject, never as an empty successful result — converting operational failure into absence lets broken verification pass fail-open."
  why: "The repair demonstrates a durable fail-closed reporting rule stronger than the displaced standalone-import smoke-check entry."
- op: replace
  target: P-03
  section: Patterns
  entry: "WHEN adding a test spec outside a runner's established match DO prove configured discovery lists it before relying on focused execution — a focused command can pass while the configured lane silently runs none of the new coverage."
  why: "The configured browser lane excluded every new nested spec; this broadly prevents silent nondiscovery and displaces the narrower wrapped-idiom counting rule."
```

`expertise-merge.py ops` applied both replacements. Touched Expertise: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-backend-dev.md`; repository Expertise untouched. No suite, diff review, feature validation, checker, build, formatter, linter, or application test ran (`suite: n/a`, `matrix_ok: n/a`, `reviewed: none`, `code_grade: n_a`).
