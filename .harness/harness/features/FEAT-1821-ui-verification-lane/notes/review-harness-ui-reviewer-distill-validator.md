# UI reviewer expertise distillation

**HARNESS-MISSION: distill. PASS.** Three independently durable visual-review rules passed the six-spawns test and replaced weaker craft entries. No observation log exists for this persona. No repository entry was warranted: each accepted rule applies across repositories.

## Counts

| Layer | Patterns | Gotchas | Outcomes | Open |
|---|---:|---:|---:|---:|
| Craft before | 15 | 15 | 10 | 0 |
| Craft after | 15 | 15 | 10 | 0 |
| Repository before | 4 | 0 | 0 | 0 |
| Repository after | 4 | 0 | 0 | 0 |

## Candidate dispositions

1. **Accepted → craft P-04 (replace).** Source: `notes/review-harness-ui-reviewer-c0.md`, corroborated by `runs/validate-validator/digest.md`. Forty-one readable, count-complete WebPs still contained blank or wrong-state captures after setup failure. Durable rule: correlate pixels with every signed route, fixture, interaction, viewport, and setup result rather than accepting structural accounting. Replaces a less UI-specific detector/scorer rule.
2. **Accepted → craft P-11 (replace).** Source: `notes/review-harness-ui-reviewer-c9.md`, corroborated by `runs/validate-c9-traces-validator/digest.md` and preserved by `runs/validate-c9-fix-validator/digest.md`. Each trace required its own action list, filmstrip, DOM snapshot, and assertion context. Durable rule: never transfer execution evidence across project/state traces. Replaces a narrower pre-existing-message scope rule.
3. **Accepted → craft O-07 (replace).** Source: `notes/review-harness-ui-reviewer-c9.md` and `runs/validate-c9-traces-validator/digest.md`. The bundle was intentionally RED yet structurally complete, explicit, and replayable. Durable rule: grade evidence truthfulness separately from product success. Replaces a narrower carry-forward rule.

## Exact expertise operations

```yaml
- op: replace
  target: P-04
  section: Patterns
  entry: "WHEN auditing screenshot evidence DO correlate visible pixels with every signed route, fixture, interaction, viewport, and setup result — readable files and complete counts can still conceal blank or wrong-state captures."
  why: "Cycle-zero review found 41/41 readable, count-complete WebPs while setup failures produced blank or mismatched states."
- op: replace
  target: P-11
  section: Patterns
  entry: "WHEN judging replayable UI evidence DO inspect each trace's own action list, filmstrip, DOM snapshot, and assertion context — never infer one project's or state's execution from another trace."
  why: "Cycle-nine review established distinct evidence for all eight project-specific traces rather than transferring conclusions between them."
- op: replace
  target: O-07
  section: Outcomes
  entry: "WHEN an intentionally failing visual bundle is structurally complete, explicit, and replayable DO judge evidence truthfulness separately from product success — honest RED can pass the evidence audit without certifying the UI."
  why: "Cycle-nine UI review and validator digest accepted complete replayable evidence while preserving explicit product and setup failures."
```

Applied only through `expertise-merge.py`. Expertise file touched: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md`. Repository Expertise files touched: none. No feature validation, test suite, build, lint, formatter, service, browser, or global expertise checker ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: UI expertise distillation is complete with three durable replacements preserved.
  mode: B
  in_scope: true
  severity_max: none
  findings: []
  must_fix: []
  states_unspecified: []
  contract_violations: []
  a11y: []
  open_questions: []
  files_touched: [/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-ui-reviewer.md]
  expertise_update:
    - op: replace
      target: P-04
      section: Patterns
      entry: "WHEN auditing screenshot evidence DO correlate visible pixels with every signed route, fixture, interaction, viewport, and setup result — readable files and complete counts can still conceal blank or wrong-state captures."
      why: "Cycle-zero review found 41/41 readable, count-complete WebPs while setup failures produced blank or mismatched states."
    - op: replace
      target: P-11
      section: Patterns
      entry: "WHEN judging replayable UI evidence DO inspect each trace's own action list, filmstrip, DOM snapshot, and assertion context — never infer one project's or state's execution from another trace."
      why: "Cycle-nine review established distinct evidence for all eight project-specific traces rather than transferring conclusions between them."
    - op: replace
      target: O-07
      section: Outcomes
      entry: "WHEN an intentionally failing visual bundle is structurally complete, explicit, and replayable DO judge evidence truthfulness separately from product success — honest RED can pass the evidence audit without certifying the UI."
      why: "Cycle-nine UI review and validator digest accepted complete replayable evidence while preserving explicit product and setup failures."
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-ui-reviewer-distill-validator.md
```
