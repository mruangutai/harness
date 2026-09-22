# Code-reviewer expertise distillation — FEAT-1821

HARNESS-MISSION: distill

**BLUF: PASS.** One of three candidates passed the six-spawns test and replaced a weaker full-section craft entry. The other two were rejected as already represented by current Expertise. No observation log exists for this persona. No feature validation, suite, code review, code grading, build, lint, format, test, service, or global expertise checker ran.

## Counts

| Layer | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft before | 15 | 15 | 10 | 0 |
| Craft after | 15 | 15 | 10 | 0 |
| Repository before | 1 | 11 | 0 | 0 |
| Repository after | 1 | 11 | 0 | 0 |

## Candidate dispositions

1. **Cross-reader c0 — rejected.** Sources: `notes/review-harness-code-reviewer-c0.md`; `runs/validate-validator/digest.md`. The reports show structurally complete records contradicted by setup errors and inspected pixels, but the durable action is already covered by craft P-03 (independently verify asserted facts), P-14 (read structural/token results as claims), and O-02 (trace a false downstream artifact to its producer). A new producer/consumer-semantics entry would duplicate those rules rather than change conduct six spawns from now.
2. **Cross-reader c9 — accepted into craft Patterns.** Sources: `notes/review-harness-code-reviewer-c9.md`; `runs/validate-c9-traces-validator/digest.md`. The canonical ZIP parser rejected the almost-valid PK-prefix artifact accepted by the custom four-byte validator. This yields a repository-independent fail-open review method: compare custom format recognition with the canonical parser using almost-valid mutants. It displaced P-10 because Patterns was at cap and P-10's document-regex convention check was narrower and less consequential.
3. **Lead c9-fix — rejected.** Sources: `notes/review-harness-code-reviewer-c9-fix.md`; `runs/validate-c9-fix-validator/digest.md`. The focused repair passed its changed-range mechanical bar while a broader range retained unchanged grade-2 records, but repository G-06 already records the grader's selection semantics and craft G-11 already requires reading the selection rule before partitioning introduced versus inherited debt. A further scoping rule would be redundant.

## Accepted source-to-entry mapping

- `notes/review-harness-code-reviewer-c9.md` plus `runs/validate-c9-traces-validator/digest.md` → craft `Patterns/P-10`: “WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open.”

## Exact operation

```yaml
- op: replace
  target: P-10
  section: Patterns
  entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open."
  why: "The c9 review and validator digest independently showed a four-byte ZIP signature check accepting data rejected by the canonical parser; this general fail-open discriminator is more durable than the displaced document-regex convention rule."
```

Expertise files touched: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md`. Repository Expertise was read immediately before mutation and was not touched. `expertise-merge.py ops` reported `REPLACED P-10` and `APPLIED`; no whole-file Expertise write occurred.

```yaml
VERDICT: PASS
DIGEST:
  headline: "One durable canonical-parser mutant rule replaced a weaker full-section craft entry; two redundant candidates were rejected."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: none
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md
  expertise_update:
    - op: replace
      target: P-10
      section: Patterns
      entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open."
      why: "The c9 review and validator digest independently showed a four-byte ZIP signature check accepting data rejected by the canonical parser; this general fail-open discriminator is more durable than the displaced document-regex convention rule."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-distill-validator.md
```
