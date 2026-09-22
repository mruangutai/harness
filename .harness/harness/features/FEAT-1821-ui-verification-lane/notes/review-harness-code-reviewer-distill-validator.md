# Code-reviewer expertise distillation reconciliation — FEAT-1821

HARNESS-MISSION: distill

**BLUF: PASS.** The previously accepted craft P-10 replacement exactly matches current Expertise, so this restart applied no operation. The two rejected candidates remain fully represented by stronger current entries. Both owned Expertise files are format-clean. This was Expertise reconciliation only: no current code diff was inspected or reviewed, and no code grading, suite, tests, build, lint, formatter, service, browser, feature validation, or project-wide validation ran.

## Sources judged

Only the previously cited code-reviewer sources were reassessed:

- `notes/review-harness-code-reviewer-c0.md`
- `runs/validate-validator/digest.md`
- `notes/review-harness-code-reviewer-c9.md`
- `runs/validate-c9-traces-validator/digest.md`
- `notes/review-harness-code-reviewer-c9-fix.md`
- `runs/validate-c9-fix-validator/digest.md`
- Prior distillation record: this note's pre-restart content
- Blocked lead reconciliation: `runs/distill-validator/digest.md`

No observation log exists for this persona.

## Candidate dispositions

1. **Cross-reader c0 — rejected, unchanged.** The structurally complete records contradicted by setup failures and inspected pixels remain covered by craft P-03 (verify asserted facts against code), P-14 (treat token/phrase evidence as claims), and O-02 (trace false downstream artifacts to their authoring source). A producer/consumer-semantics entry would duplicate current durable rules.
2. **Cross-reader c9 — accepted historically; reconciled idempotently.** The custom four-byte ZIP validator accepted an almost-valid PK-prefix artifact rejected by the canonical parser. Current craft `Patterns/P-10` exactly equals the owner-approved replacement. It remains durable, repository-independent evidence and has not drifted. It was not applied again.
3. **Lead c9-fix — rejected, unchanged.** Focused changed-range grading versus broader unchanged grade-2 records remains covered by craft G-11 (read the gate's selection rule before partitioning records) and repository G-06 (the grader emits only new or worsened functions). No new durable rule is warranted.

## Counts and touch reconciliation

| Layer | Patterns before→after | Gotchas before→after | Outcomes before→after | Open before→after |
|---|---:|---:|---:|---:|
| Craft | `15→15` | `15→15` | `10→10` | `0→0` |
| Repository | `1→1` | `11→11` | `0→0` | `0→0` |

Historical Expertise touch: `/Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md` only. The repository Expertise file was historically and currently untouched. This restart changed neither Expertise file and ran no `expertise-merge.py` command because the approved operation was already present exactly.

## Historical exact operation

```yaml
- op: replace
  target: P-10
  section: Patterns
  entry: "WHEN a custom validator recognizes a standard format DO compare it with the canonical parser using almost-valid mutants — magic bytes or shallow shape checks can accept artifacts the real consumer cannot open."
  why: "The c9 review and validator digest independently showed a four-byte ZIP signature check accepting data rejected by the canonical parser; this general fail-open discriminator is more durable than the displaced document-regex convention rule."
```

Current craft P-10 matches that entry byte-for-byte. This is historical provenance, not a current-run `expertise_update`.

## Scoped format check

The only command run was the permitted checker scoped to the two owned files:

`python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-expertise.py /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md /Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-code-reviewer.md`

Exit `0`:

- `OK   /Users/molchairuangutai/GitHub/harness/.harness/expertise/harness-code-reviewer.md`
- `OK   /Users/molchairuangutai/GitHub/harness/.harness/harness/expertise/harness-code-reviewer.md`

No diff review, code grading, suite, tests, build, lint, formatter, service, browser, feature validation, or project-wide validation ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "Craft P-10 exactly matches the approved historical replacement; both owned Expertise files are format-clean and this restart applied no operation."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: n_a
  reviewed: none
  human_commits_in_scope: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-distill-validator.md
```
