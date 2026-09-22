# QA expertise distillation — FEAT-1821-ui-verification-lane

**HARNESS-MISSION: distill**

**BLUF:** One durable craft rule was accepted by replacing the weaker full-capacity P-14; the repository tier is unchanged. No feature validation, suite, build, lint, format, service, or checker ran.

## Sources read

- `observations/harness-qa.md`
- `notes/review-harness-qa-c0.md`
- `notes/review-harness-qa-c9.md`
- `runs/validate-validator/digest.md`
- `runs/validate-c9-traces-validator/digest.md`
- `runs/validate-c9-fix-validator/digest.md`

## Candidate dispositions

1. **Accepted — craft P-14 replacement.** Source: `observations/harness-qa.md:3`. The runtime Playwright listing accepted dynamically generated titles while the static contract extractor found no literal titles. This passes the six-spawns test as a reusable producer/consumer field-shape failure mode. Accepted entry: `P-14`, keyed to `observations/harness-qa.md:3`: “WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values.” It replaces the weaker, narrower prior P-14 because `Patterns` was at its cap.
2. **Rejected — no new entry.** Source: `notes/review-harness-qa-c0.md:19-28`, corroborated by `runs/validate-validator/digest.md:42,52`. The distinction between discovery/listing and collection/execution is already prescribed by the QA verification protocol’s required named-test and failure-kind evidence. Repeating that operating procedure in Expertise would not change a sixth future spawn’s decision.
3. **Rejected — no new entry.** Source: `notes/review-harness-qa-c9.md:29-31`, `runs/validate-c9-traces-validator/digest.md:32,37-39`, and `runs/validate-c9-fix-validator/digest.md:25-29`. The boundary mutant was effective, but its durable core is already covered by craft P-09 (prove the specific mutant effect) and G-13 (reproduce the actual regression precondition). A separate entry would duplicate rather than sharpen those rules.

## Counts and mutation receipt

| Tier | Section | Before | After |
|---|---|---:|---:|
| Craft | Patterns | 15 | 15 |
| Craft | Gotchas | 15 | 15 |
| Craft | Outcomes | 10 | 10 |
| Craft | Open | 1 | 1 |
| Repository | Patterns | 0 | 0 |
| Repository | Gotchas | 10 | 10 |
| Repository | Outcomes | 0 | 0 |
| Repository | Open | 0 | 0 |

Exact `expertise_update` operation:

```yaml
- op: replace
  target: P-14
  section: Patterns
  entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values."
  why: "The observed dynamic-title/static-extractor mismatch is a durable producer-consumer contract risk; P-14 is the weaker, narrower coverage-binding rule at the full section cap."
```

Touched Expertise files:

- `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md`

The repository Expertise file `/Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-qa.md` was read immediately before mutation and was not changed. The craft file was likewise re-read immediately before the merge operation. The accepted operation was applied only with `expertise-merge.py`; `check-expertise.py` was not run per dispatch constraint.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Distillation completed; mandated did-nothing QA gate fields are n/a."
  suite: n/a
  failures: 0
  matrix_ok: n/a
  kinds: []
  coverage_gaps: []
  sc_evidence: []
  fail_first: []
  open_questions: []
  files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md]
  expertise_update:
    - op: replace
      target: P-14
      section: Patterns
      entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values."
      why: "The observed dynamic-title/static-extractor mismatch is a durable producer-consumer contract risk; P-14 is the weaker, narrower coverage-binding rule at the full section cap."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-distill-validator.md
```
