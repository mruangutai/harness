# Documentor expertise distillation receipt

All three fixed candidates pass the six-spawns test. Two replace weaker entries in capped craft sections; one records a Harness-specific repository invariant.

## Sources assessed

- `observations/harness-documentor.md`, both 2026-09-19 observations
- `runs/docs-product/digest.md`

No other candidates were sought or introduced.

## Candidate judgments

1. **Accepted — craft / Patterns, replace P-15.** Source: observation 2026-09-19 and `runs/docs-product/digest.md`. The amended-authority rule will change how a documentor handles stale signed prose in future repositories. It sharpens P-15 for an already-approved amendment and removes P-15's weaker re-signature advice.
2. **Accepted — craft / Gotchas, replace G-15.** Source: observation 2026-09-19 and `runs/docs-product/digest.md`. Discovery commands with teardown side effects are a recurring documentation-verification hazard across tools and repositories. This displaces the narrower git-grep word-boundary trap.
3. **Accepted — repository / Patterns, add P-08.** Source: `runs/docs-product/digest.md`. Manifest-listed committed evidence versus ignored local scratch is a durable Harness artifact-layout invariant, not portable craft.

Rejected candidates: none.

## Per-section counts

| Layer | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft before | 15 | 15 | 10 | 0 |
| Craft after | 15 | 15 | 10 | 0 |
| Repository before | 7 | 7 | 0 | 0 |
| Repository after | 8 | 7 | 0 | 0 |

## Exact expertise_update ops

```yaml
- op: replace
  target: P-15
  section: Patterns
  entry: "WHEN approved amendment authority supersedes stale signed prose DO state the amended rule in canonical operational docs, leave the signed record untouched, and identify its old wording as historical — editing history falsifies the record, while repeating it makes live guidance wrong."
  why: "Observation 2026-09-19 and runs/docs-product/digest.md; sharpens P-15 for an already-approved amendment and removes its weaker re-signature advice."
- op: replace
  target: G-15
  section: Gotchas
  entry: "WHEN verifying a documented discovery or list command DO provide the same explicit run context as execution, inspect lifecycle hooks for teardown side effects, and remove generated scratch — no tests ran does not mean nothing ran."
  why: "Observation 2026-09-19 and runs/docs-product/digest.md; displaces the narrower git-grep word-boundary trap with a cross-tool documentation-verification hazard."
- op: add
  target: P-08
  section: Patterns
  entry: "WHEN documenting Harness artifact layout DO distinguish manifest-listed committed evidence from ignored local scratch and name every committed exception to the ordinary ignore rule — path shape alone does not tell operators whether evidence survives."
  why: "runs/docs-product/digest.md; records the Harness-specific manifest and ignore invariant without carrying feature-local paths."
```

## Files changed

- `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-documentor.md`
- `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-documentor.md`

Both Expertise files were changed only through `expertise-merge.py ops`. Per dispatch, `check-expertise.py` did not run. Suite: n/a. Matrix: n/a. Code grade: n_a. Reviewed: none. No build, formatter, linter, test, feature validation, suite, or diff review ran.
