# REUSE angle — validate-final-c13

BLUF: R-01 genuinely reduced duplication — no third spelling of commit resolution survives in the
seven-file scope. One code-level REUSE finding remains outside R-01's scope: the git-repo-fixture
boilerplate is spelled twice (once inline, 3x within `test-code-grade.py`, once again as
`make_repo` in `test-code-grade-cli.py`). Nothing else in the seven files restates an importable
constant/helper.

## R-01 verdict: REDUCED, not relocated

Grep evidence (`rev-parse|^{commit}|end-of-options|commit_oid` across all seven files):

- `code_grade.py:281-292` — the ONE seam: `rev-parse --verify --end-of-options … ^{commit}`.
  Callers at `code_grade.py:369-370` (`gated_set`).
- `code-grade.py:162-163` — adapter A, calls `code_grade.commit_oid` directly, no re-spelling of
  git args.
- `validate-digest.py:32,541-546` — adapter B (`resolve_reviewed_commit`), calls the same
  `commit_oid`, wraps `ValueError`→`None`, appends `.encode()` to preserve a historical `bytes`
  return for its sole consumer `reviewed_python_change` (line 549, feeds `subprocess.run(["git",
  "diff", …], …)` argv at line 560-561 — no `text=True`, so `bytes` is the correct type there, not
  a wart).
- The other `rev-parse` hits are unrelated commands: `code-grade.py:17` is `--show-toplevel` (repo
  root, not commit resolution); `test-code-grade.py:211` and `test-code-grade-cli.py:38` are
  `rev-parse HEAD` inside test fixture helpers, reading a ref back out after committing — building
  test data, not re-implementing the validation seam. None of these duplicate the
  `--end-of-options … ^{commit}` validation logic.

Conclusion: one seam, two callers, zero surviving third implementation. The `.encode()` in the hook
adapter is a type-preservation shim for its one bytes-consuming call site, not evidence of a
mismatched seam — REUSE has no finding here.

## Findings

### F1 — chore — duplicated git-fixture boilerplate across two test files
- File/line: `test-code-grade.py:124-126` (repeated verbatim at `:217-219` and `:288-290`, all
  three inside the same file) vs. `test-code-grade-cli.py:30-32,41-44` (`git()` + `make_repo()`).
- Summary: both files independently spell "init a scratch git repo with a bound identity" — one as
  three inline copies of `_git(repo_root,"init")` / `config user.email` / `config user.name`, the
  other as a `make_repo()` helper doing the same three calls once.
- Concrete cost: four total spellings of one 3-line sequence (three inline, one helper). A future
  change to the fixture identity (e.g. adding `commit.gpgsign=false` for a CI box that has it on
  by default) has to be applied in four places; missing one leaves that call site silently exposed
  to the environment default it was trying to pin.
- Alternative: hoist one `_git_repo(directory)` helper (init + two config calls) into a shared
  test-support module the four test files already could import from (none currently share code —
  each `HERE`-relative `importlib` load pattern shows there is no existing shared test module to
  extend, so this is a new small one, not a restated existing one — noted as chore, not urgent).

No other REUSE finding: `test-validate-digest.py` and `test-check-plan-routes.py` use
`tempfile.TemporaryDirectory()` directly per case (not git repos) and do not restate any constant
or helper that has an importable home elsewhere in the seven files.

## Suite results (real, observed)
- `python3 .claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`, exit 0
- `python3 .claude/skills/harness/bin/test-code-grade-cli.py` → `PASS test-code-grade-cli`, exit 0
- `python3 .claude/skills/harness/bin/test-validate-digest.py` → `ALL PASSED.` (65/65 CLI, 14/14
  hook, 24/24 T-09, 2/2 template cases), exit 0

## git status --short (last action, proves no source/test file changed by this run)
```
staged 0, unstaged 10, untracked 14
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
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-reuse-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c11.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-validate-fix-c13-r01.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-altitude-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-simplification-validate-fix-c13.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.html
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/ship-review-validate-fix-c13-simplify-eng.md
```
All pre-existing (prior cycle's dirty tree, this run's own receipt not yet staged); no seven-file
scope entry was touched by this assessment.

must_fix: []
