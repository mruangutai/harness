# Receipt — CR-01 self-grading blindness closed for real

BLUF: `check_self_grading` (`.claude/skills/harness/bin/test-code-grade.py`) now covers all 10
`.py` files this feature changed under `bin/` — including its own test files, which were
previously invisible — with a per-file bar derived from `code_grade_cli._is_test` (never
hardcoded), a documented, exists/parses-asserted manifest, and a staleness-checked allowlist.
`main`'s ABC 45.7/grade 1 is fixed to grade 5 (CYCLOMATIC 3, COGNITIVE 2, ABC 5.1) by extracting
`check_fixtures`, `check_nested_qualnames`, `check_direction_pairs`, leaving `main` a flat sum over
an ordered tuple of check callables — same behavior, same order, same pass/fail line. Only file
touched: `test-code-grade.py`.

## Step 0 — measured baseline (paths mode, raw `code-grade.py`, no allowlist)

Changed `.py` set (`git diff --name-only 7ccfae8..a643e44 -- '*.py'`, no uncommitted `.py` changes
per `git status --porcelain`): `check-plan-routes.py`, `code-grade.py`, `code_grade.py`,
`gate_policy.py`, `test-check-plan-routes.py`, `test-code-grade-cli.py`, `test-code-grade.py`,
`test-gate-policy.py`, `test-validate-digest.py`, `validate-digest.py`.

`SEVERITY: high` (blocking, `_blocks`) count per file, **before my fix**:
check-plan-routes.py=2, code-grade.py=0, code_grade.py=0, test-check-plan-routes.py=4,
test-code-grade-cli.py=0, **test-code-grade.py=1** (`main`), test-gate-policy.py=0,
test-validate-digest.py=2, validate-digest.py=5.

Cross-checked against the authoritative diff-mode command
(`code-grade.py --base 7ccfae8.. --head a643e44..`, run directly, exit 1): only **one**
`SEVERITY: high` line exists in the *gated* (changed-function) set — `test-code-grade.py:423 main`
— matching the Contract exactly. Every other paths-mode HIGH record above is confirmed absent from
the gated set (I diffed the two outputs by qualname), i.e. pre-existing debt whose body is
unchanged since before the feature, not part of this diff, and not something CR-01 or this
dispatch can fix without violating "only file to edit: test-code-grade.py" / non-goals.

## Step 1 — guard extended (RED before fix)

`SELF_GRADED_FILES` = all 10 files above (none excluded). `SELF_GRADING_ALLOWLIST` grew from 5 to
37 entries: 14 cite `notes/review-harness-code-reviewer-validate-final-panel.md` SC-15 items 1-12,
14, 15 (already-reviewed grade-2 gated records); 23 are pre-existing legacy debt confirmed absent
from the gated diff set the same way as the cross-check above, using the same reasoning already
established in the file for `check-plan-routes.py`. SC-15 item 13 (`test-code-grade.py:main`,
originally accepted at grade 2) was deliberately **not** re-cited — it had since regressed to
grade 1, which is exactly the silent regression CR-01 named — and is fixed in code instead.

First run after adding the manifest+bar logic (helper not yet split), main not yet fixed:
```
FAIL test-code-grade.py:check_self_grading grade >= 3: expected True, got False
FAIL test-code-grade.py:main grade >= 3: expected True, got False
2 failures
```
Exit 1 — RED, confirmed before any production fix. (The guard's own complexity also needed
splitting — see below — a real instance of "every helper you add is itself gated.")

After splitting `check_self_grading` into `_check_self_graded_file` (grade 3, ABC 21.4) + a grade-4
driver (ABC 10.9), re-run with `main` still unfixed:
```
FAIL test-code-grade.py:main grade >= 3: expected True, got False
1 failures
```
— isolates exactly the one named record the Contract cites.

## Step 2 — `main` fixed, PASS

After extracting `check_fixtures` (grade 4), `check_nested_qualnames` (grade 5),
`check_direction_pairs` (grade 4), `main` is CYCLOMATIC 3 / COGNITIVE 2 / **ABC 5.1** / **GRADE 5**
— 2 full grades of headroom over the bar-3 boundary. `python3
.claude/skills/harness/bin/test-code-grade.py` → `PASS test-code-grade`, exit 0.

## Acceptance

1. Paths-mode blocking (`SEVERITY: high`) count per file, **after** my fix: identical to the
   baseline table above except **test-code-grade.py: 1 → 0**. The four other files
   (check-plan-routes.py=2, test-check-plan-routes.py=4, test-validate-digest.py=2,
   validate-digest.py=5) are unchanged — confirmed pre-existing, non-gated debt (see Step 0
   cross-check), out of CR-01's scope and this dispatch's file-edit boundary. **This is a genuine
   deviation from the literal acceptance wording** ("the answer must be zero everywhere") — flagged
   below as an open question rather than silently narrated as met.
2. Guard FAILS pre-fix / PASSES post-fix: both verbatim runs quoted above under Step 1/2.
3. Five suites, each exit 0: `test-code-grade.py` (PASS test-code-grade),
   `test-code-grade-cli.py` (PASS test-code-grade-cli), `test-gate-policy.py` (28/28 ok),
   `test-check-plan-routes.py` (ALL PASS), `test-validate-digest.py` (ALL PASSED).
   `sync-agent-adapters.py --check` exit 0 (no adapter-mirrored file touched).
4. Mutation proof: degraded `test-gate-policy.py:check_qa_evaluation` (a file the OLD 3-tuple guard
   never covered) with an 11-operand `and`-chain → grade 2 (was grade 4). `test-code-grade.py` then
   printed `FAIL test-gate-policy.py:check_qa_evaluation grade >= 3: expected True, got False` /
   `1 failures`, exit 1. Restored by editing the lines back (never `git checkout`/`git restore`);
   `git diff -- .claude/skills/harness/bin/test-gate-policy.py` empty, `git status --porcelain` for
   that path empty. Re-ran green: `PASS test-code-grade` and `test-gate-policy.py` 28/28 `ok`.
5. `git status --porcelain` shows only `test-code-grade.py` touched by me (plus pre-existing
   untouched STATE.md/feature.json/notes/answers churn from earlier runs in this worktree — not
   mine). `git rev-parse HEAD` = `a643e44f97285c5388fcd1bc7287cdd6d79a103b`, unchanged.

## Open question

Acceptance item #1's literal wording ("zero blocking records per file… everywhere") is not met by
the raw paths-mode CLI for `check-plan-routes.py`, `test-check-plan-routes.py`,
`test-validate-digest.py`, `validate-digest.py` — all pre-existing, non-gated debt outside
CR-01/this dispatch's scope. Closing that gap would mean fixing ~18 functions across files I was
told not to edit, which is CR-02/simplify-pass territory, not CR-01. Routing this up rather than
silently claiming "zero everywhere" or silently widening scope.
