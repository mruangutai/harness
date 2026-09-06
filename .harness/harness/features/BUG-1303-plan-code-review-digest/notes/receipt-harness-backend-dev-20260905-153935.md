# Receipt — harness-backend-dev — BUG-1303 MF-2

**BLUF:** `_reviewer_plan_mode_results` no longer hardcodes `n_a`. A new helper,
`_derive_plan_mode_code_grade(validator)`, probes the validator's own plan-mode rule
(`_pending_plan_review_error`, `validate-digest.py:1026-1032`) across every member of
`validator.CODE_GRADE_VALUES` (`validate-digest.py:616`) and keeps the single member that
rule does not reject with a "code_grade must be" error. That derived value is what the
`code_grade:` regex now searches for. Renaming the accepted grade in `CODE_GRADE_VALUES`
now changes what the test looks for, closing the SC-03 gap.

## Probe shape used

Option 2 from the dispatch: call `validator._pending_plan_review_error`'s governing path
directly through `validator.validate(...)` (via the existing `_plan_review_errors` helper),
driven by the existing fixture helpers `_plan_review_fixture` and `reviewer_digest`, varying
`code_grade` across `sorted(validator.CODE_GRADE_VALUES)` and keeping whichever member's
error list contains no `"code_grade must be"` message. The probe builds its own tempdir,
`write_review_config`, and `_plan_review_fixture` feature dir/plan.yaml internally, so
`_reviewer_plan_mode_results`'s signature and its single call site (`run_documented_contract_cases`,
line ~483) did not need to change.

Failure mode: if zero or more than one member qualifies, or the probe itself raises,
`_derive_plan_mode_code_grade` returns `(None, reason)`; `_reviewer_plan_mode_results` then
appends exactly one named FAIL result — `"plan-mode code_grade derivation from
CODE_GRADE_VALUES failed: <reason>"` — instead of building a regex from `None` or falling
back to a default.

## Literal-`n_a` scope check

`grep -n 'n_a' tests/integration/test-validate-digest.py:394-463` (the new function plus the
rewritten `_reviewer_plan_mode_results`): **no matches**. The derived value is discovered at
runtime; the string `n_a` never appears as a literal in the changed region. (Other
pre-existing `n_a` literals elsewhere in the file, e.g. near line 2686, are untouched and
out of scope per the dispatch.)

## Red-capability demonstration

Mutated the **derived value** in-memory (imported the test module via `importlib`,
monkeypatched `mod._derive_plan_mode_code_grade` to return `("bogus_grade_value", None)`,
called `mod.run_documented_contract_cases()`, then restored the original — no file left
mutated). Observed:

```
FAILS= 3
FAIL  [documented contract] .claude/agents/harness-code-reviewer.md plan-mode token 'code_grade: ... bogus_grade_value'
FAIL  [documented contract] .omp/agents/harness-code-reviewer.md plan-mode token 'code_grade: ... bogus_grade_value'
FAIL  [documented contract] .claude/skills/harness-code-review/SKILL.md plan-mode token 'code_grade: ... bogus_grade_value'
```

All three reviewer sources reddened as required. `git status --porcelain` after the demo
still names only `tests/integration/test-validate-digest.py` (plus unrelated sibling-squad
files — see below) — no mutated file was left on disk.

## Acceptance evidence

`env -u HARNESS_AGENT_TYPE python3 tests/integration/test-validate-digest.py` (run from
worktree root):
- exit status: `0`
- `^FAIL ` match count: `0`
- final line: `ALL PASSED.`

`git -C <worktree> status --porcelain`:
```
 M .harness/harness/docs/DECISIONS-INDEX.md
 M .harness/harness/features/BUG-1303-plan-code-review-digest/observations/harness-documentor.md
 M tests/integration/test-validate-digest.py
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/receipt-harness-documentor-2026-09-05-mf1.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-code-reviewer-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-qa-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-security-reviewer-c4.md
?? .harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-ui-reviewer-c4.md
```
Only `tests/integration/test-validate-digest.py` is the file I touched; the
`DECISIONS-INDEX.md` change and the `harness-documentor` notes/observations are the
concurrent sibling squad (MF-1) working the same worktree — confirmed via `hub` roster
(`ValidateBug1303.PricklyTurtle.MF1IndexRegen`), not my edit.

## Task

No PLAN task id was carried in this dispatch (a must_fix fix, not a PLAN task) — `task: none`.

send_backs: 0
