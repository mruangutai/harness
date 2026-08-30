# Receipt — harness-dev-ops — ALTITUDE — validate-final-c13

**BLUF: R-01 REDUCES duplication, not relocates it. `commit_oid`'s home is right, and
`resolve_reviewed_commit` is a legitimate adapter, not a symptom-patch. No findings; PASS.**

## Verdict on the two named seams

**`commit_oid` (`code_grade.py:281`) is at the right altitude.** It is not a general-purpose
Git utility bolted onto a caller — it is `code_grade.py`'s own primitive for its own concern.
`gated_set` (the module's core entry point) calls it directly at `code_grade.py:369-370` to
resolve `base_ref`/`head_ref` before diffing. The two external callers — `code-grade.py:162-163`
(CLI) and `validate-digest.py:544` (hook, via `resolve_reviewed_commit`) — reuse the module's own
rule rather than restating it. Before R-01 this validation (reject `-`-leading revisions, then
`git rev-parse --verify --end-of-options`) existed in three places; now there is exactly one
authoritative statement, proven by `test-validate-digest.py:1798-1820`'s injection-guard test,
which asserts Git is never invoked for an option-like revision — a claim only checkable because
there is one seam to intercept. There is no dedicated git-utils module in `bin/` (no
`harness_git.py` alongside `harness_boundary.py`/`harness_yaml.py`), so the alternative home
would be a new module created for a single function with one non-owning consumer — that reopens
settled scope for no depth gained. **Leave.**

**`resolve_reviewed_commit` (`validate-digest.py:541-546`) is a thin, correctly-scoped adapter,
not a workaround.** It does two things, both legitimately local to this file: (1) translates the
seam's exception-based contract (`raise ValueError`) into this file's sentinel convention
(`return None`), matching how `reviewed_python_change` (`:549-566`) and its caller already thread
`(value, error)` tuples throughout `validate-digest.py`; (2) re-encodes to `bytes` because the
existing `git diff` call at `:560-562` is byte-mode (`capture_output=True`, no `text=True`) and
`result.stdout.split(b"\0")` at `:566` needs bytes patterns. Neither line re-implements or
second-guesses the validation rule itself — both branches (raise vs. `None`) still originate from
the one `commit_oid` call. This is calling-convention glue, not a compensating control patching a
symptom the underlying mechanism should refuse. **Leave.**

## Other candidates checked, no finding

- `code-grade.py:_git_text` (`:29-33`) vs `code_grade.py:_git_output` (`:295-302`): both wrap
  `subprocess.run(["git", ...])` + raise-on-failure, with different exception types (`ValueError`
  vs `check=True`/`CalledProcessError`). This is REUSE's lane (restated helper), not an altitude
  violation — neither restates a *rule* that can drift; they're mechanically similar plumbing with
  no shared invariant at stake. Noted, not flagged here.
- `test-check-plan-routes.py`: no `code_grade`/`commit_oid` reference — outside the R-01 seam,
  not evaluated for altitude.

## Findings

None. `must_fix: []`.

## Suite results (real, not n/a)

- `python3 .claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`, exit 0
- `python3 .claude/skills/harness/bin/test-code-grade-cli.py` → `PASS test-code-grade-cli`, exit 0
- `python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED` (65/65 CLI, 14/14
  hook, 24/24 T-09, 2/2 template cases), exit 0

## `git status --short` (last action, verbatim)

```
staged 0, unstaged 10, untracked 15
M .claude/skills/harness/bin/code-grade.py
M .claude/skills/harness/bin/code_grade.py
M .claude/skills/harness/bin/test-check-plan-routes.py
M .claude/skills/harness/bin/test-code-grade-cli.py
M .claude/skills/harness/bin/test-code-grade.py
M .claude/skills/harness/bin/test-validate-digest.py
M .claude/skills/harness/bin/validate-digest.py
M .harness/harness/features/FEAT-43-code-risk-grading/STATE.md
M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
M .harness/harness/features/FEAT-43-code-risk-grading/notes/handoff-validate.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q2-cycle-11-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q3-cycle-13-overrun.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q4-simplify-routing.md
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q5-simplify-apply-authorization.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-regate-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-fix-c13-qa-validator.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-efficiency-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-final-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c11.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.md
```

No source or test file under the seven-file scope was modified by this run — the pre-existing
dirty-tree state is unchanged by this read-only assessment.
