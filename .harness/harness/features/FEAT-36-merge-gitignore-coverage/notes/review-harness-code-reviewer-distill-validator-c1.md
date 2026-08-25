# Code-reviewer distillation close-out reassessment — FEAT-36

**BLUF: PASS.** P-04, P-06, and G-13 remain unapplied and are each **not permitted** in this c1 run. The operator permits only operations expressible through the mandated `expertise-merge.py`; that tool implements lock-safe additive union, while direct or whole-file replacement is forbidden. The earlier BLOCKED result is therefore closed by disposition, not by applying or retrying any replacement.

## Individual dispositions

| Target | Prior record | Current evidence | c1 disposition |
|---|---|---|---|
| P-04 | Recorded as a same-ID `replace` and refused with exit 7 (`runs/distill-validator/digest.md:84-89`; prior note:35-39,52-54). | The original entry remains at `.harness/expertise/harness-code-reviewer.md:6`; scoped `git diff` over both reviewer Expertise paths is empty. | **Unapplied / not permitted.** Additive union cannot replace an existing ID, and no direct/whole-file replacement is allowed. |
| P-06 | Recorded as a same-ID `replace` and refused with exit 7 (`runs/distill-validator/digest.md:90-95`; prior note:40-44,52-54). | The original entry remains at `.harness/expertise/harness-code-reviewer.md:8`; scoped `git diff` over both reviewer Expertise paths is empty. | **Unapplied / not permitted.** Its stale `HEAD` wording remains a non-gating close-out disposition; it is not retried or applied. |
| G-13 | Recorded as a same-ID `replace` and refused with exit 7 (`runs/distill-validator/digest.md:96-101`; prior note:45-49,52-54). | The original entry remains at `.harness/expertise/harness-code-reviewer.md:31`; scoped `git diff` over both reviewer Expertise paths is empty. | **Unapplied / not permitted.** Additive union cannot replace an existing ID, and no direct/whole-file replacement is allowed. |

## Governing contract and close-out

`expertise-merge.py` describes its operation as a lock-safe union and applies nothing when the same section/ID carries different text (`.agents/skills/harness/bin/expertise-merge.py:2-18,220-230`); its CLI exposes only `apply` for union merge (`:281-285`). The immutable prior run likewise records that the only mandated merge path cannot express replacement/displacement and whole-file write would violate the distillation contract (`runs/distill-validator/digest.md:167`). Under the operator's explicit permitted-results rule, these three refused replacements are valid unapplied/not-permitted outcomes rather than a remaining gate.

The stale P-06 wording and the tool capability gap are recorded only as non-gating disposition/proposed follow-up. There is no `must_fix` and no blocking open question. The already-applied security/UI additions are outside this reassessment and were not touched. No Expertise file changed; no project-wide validation, formatter, linter, build, or test ran.

```yaml
VERDICT: PASS
DIGEST:
  headline: "P-04, P-06, and G-13 remain unapplied and are individually closed as not permitted under the operator's additive-union-only rule."
  severity_max: info
  findings: 0
  must_fix: []
  spec_violations: []
  reviewed: "FEAT-36 distill-validator prior digest/note and the mandated expertise-merge.py capability"
  human_commits_in_scope: []
  open_questions: []
  files_touched:
    - .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator-c1.md
  expertise_update: []
artifact: .harness/harness/features/FEAT-36-merge-gitignore-coverage/notes/review-harness-code-reviewer-distill-validator-c1.md
```
