# QA expertise distillation — FEAT-1821-ui-verification-lane

**HARNESS-MISSION: distill**

**BLUF:** Craft P-14 already exactly contains the accepted replacement; this restart applied no Expertise operation. Both owned QA Expertise files are format-clean.

## Sources reconciled

- `observations/harness-qa.md:3`
- `notes/review-harness-qa-c0.md:19-28`
- `notes/review-harness-qa-c9.md:29-31`
- `runs/validate-validator/digest.md:42,52`
- `runs/validate-c9-traces-validator/digest.md:32,37-39`
- `runs/validate-c9-fix-validator/digest.md:25-29`
- `runs/distill-validator/digest.md:17-18,21,27-30,35-45,77-85`

## Candidate dispositions

1. **Accepted historically — craft P-14 replacement; reconciled, not reapplied.** The observation's dynamic Playwright-title/static-extractor mismatch remains a durable producer/consumer field-shape risk. Current craft P-14 exactly matches the historical accepted text below.
2. **Rejected — discovery versus execution.** The c0 evidence is already required by QA protocol named-test and failure-kind evidence; a new Expertise entry would not change a future QA decision.
3. **Rejected — boundary mutant.** The c9 trace evidence is covered by craft P-09 (specific-mutant discrimination) and G-13 (actual regression precondition); a new entry would duplicate rather than sharpen them.

## Expertise reconciliation

| Tier | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft, historical before → after | 15 → 15 | 15 → 15 | 10 → 10 | 1 → 1 |
| Repository, historical before → after | 0 → 0 | 10 → 10 | 0 → 0 | 0 → 0 |
| Restart changes | 0 | 0 | 0 | 0 |

Historical exact operation, already applied through `expertise-merge.py`:

```yaml
- op: replace
  target: P-14
  section: Patterns
  entry: "WHEN a producer generates evidence fields consumed by a static extractor or gate DO test both the producer runtime output and the consumer accepted field shape — dynamic construction can satisfy runtime discovery while leaving static contract extraction with no usable values."
  why: "The observed dynamic-title/static-extractor mismatch is a durable producer-consumer contract risk; P-14 is the weaker, narrower coverage-binding rule at the full section cap."
```

Current craft P-14 is byte-for-byte the historical operation's `entry`; no merge was invoked on this restart. The repository Expertise remains unchanged.

## Scoped format check

- `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-qa.md` — exit 0: `OK`.
- `python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-qa.md` — exit 0: `OK`.

No suite, tests, diff review, build, lint, formatter, service, browser, or project-wide validation ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "QA Expertise is reconciled; P-14 was already applied and both owned files are format-clean."
  suite: n/a
  failures: 0
  matrix_ok: n/a
  kinds: []
  coverage_gaps: []
  sc_evidence: []
  fail_first: []
  open_questions: []
  files_touched: [/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-distill-validator.md]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-qa-distill-validator.md
```
