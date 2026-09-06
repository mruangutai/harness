## Code review — BUG-1303, cycle 5 (CONFIRMATION), review_sha e2c800f14560d272357beb5c0628389a3433ddd2
## base = 63404ef06cd798c6d933b52336bf73de7b248028 (`git merge-base main e2c800f1`, resolved this cycle — unchanged from cycle 4)

**VERDICT: PASS.** MF-1 **RESOLVED**. MF-2 **RESOLVED**. Both genuinely closed, not papered over — evidence
below is independently derived, not diff-observation. `code_grade: pass` for the whole pinned range.
No new `must_fix`. Q-A restated once, unchanged, `med`, advisory only (not re-raised as `must_fix`/`high`
per this cycle's contract).

Scope: this is the confirmation pass named in the dispatch, not a fresh full panel. I re-ran Stage
1 (spec compliance) and Stage 2 (quality) over the whole range `base..e2c800f1`, not just the fix
commit, per instruction 3.

### MF-1 — DECISIONS-INDEX.md DEC-217 row regenerated: RESOLVED

**(a) Tags are what `compute_tags()` actually computes from DEC-217's text — verified by independent
calculation, not by observing generator-vs-file agreement.** I read `compute_tags()`
(`gen-decisions-index.py:144-150`): substring-count each `TOPIC_VOCAB` term (31 terms) over
`body.lower()`, take the top 4 by `(-score, tag)`. I extracted DEC-217's actual body (the heading at
`DECISIONS.md:6818` through EOF — DEC-217 is the last entry, no DEC-218 exists) and counted substring
occurrences of the four candidate tags by hand (via a standalone script replicating the algorithm,
never invoking the real generator): `tests`=6 (all six are genuine occurrences: `fix_confined_to_tests…`
×2, `` `tests/**` `` ×2, `` `tests/unit/**` ``, `` `tests/integration/…` ``), `docs`=2 (both inside
`…_and_contract_docs`), `digest`=1 (`test-validate-digest.py`), `plan`=1 ("the signed plan"). Sorted
by `(-score, tag)`: `[tests, docs, digest, plan]` — exactly the committed row's new tags. This is a
derivation from the text and the algorithm, independent of the generator binary, so it is not the
circular "regeneration now matches the file" observation the dispatch warned against.

**(b) Ruling text after ` :: ` is byte-identical to 59c5de97.** Extracted both revisions via
`git show <sha>:path` (no working-tree read), split each DEC-217 row on `' :: '`: both sides equal
`"Bugfix test kinds follow the changed surface: runtime-code fixes require unit, while fixes confined
to tests and contract docs require integration."` — `==` is `True`.

**(c) Exactly one line changed, no other row moved.** Line-by-line diff of the full 217-line file
(both revisions have 217 lines) shows exactly one differing index (216, the DEC-217 row) — matches
`git show e2c800f1 -- DECISIONS-INDEX.md`'s own reported stat, "1 file changed, 1 insertion(+), 1
deletion(-)". Confirmed mechanically: `gen-decisions-index.py --stdout | diff -q -
DECISIONS-INDEX.md` is silent, exit 0.

### MF-2 — plan-mode `code_grade` derived from `CODE_GRADE_VALUES`: RESOLVED

Ran the real derivation live (`_derive_plan_mode_code_grade(validator)`, both modules loaded exactly
as the suite loads them, `importlib.util.spec_from_file_location`) plus targeted in-memory
perturbations of the validator — zero files touched, git status confirmed clean throughout.

**(a) Cannot return a wrong-but-plausible value on 0 or 2+ qualifying members.** Monkeypatched
`validator._pending_plan_review_error` to two synthetic rules: one that rejects every member
(`qualifying=[]`) and one that accepts two (`n_a` and `pass`, `qualifying=['n_a','pass']`). Both are
caught by the `len(qualifying) != 1` guard and return `(None, "expected exactly one qualifying member
… found […]")` — never a silently-chosen value from either end of the sort order.

**(b) The failure path is reachable and loud.** `_reviewer_plan_mode_results` short-circuits on
`derive_error`, appending exactly one `(False, "plan-mode code_grade derivation from
CODE_GRADE_VALUES failed: <reason>")` and returning early — it does skip the other seven plan-mode
checks for that call, but the one result it does emit is a named, readable FAIL line reaching
`main()`'s FAIL count the same way every other result in this file does; it is not swallowed into a
`True`/pass.

**(c) `except Exception` — concrete swallowed-exception scenario, and why it is defensible rather
than a defect.** Monkeypatched `t.reviewer_digest` (a helper shared by ~30 other cases in this same
file) to raise `TypeError('reviewer_digest() missing required keyword-only arg: severity_max')` —
simulating an unrelated future regression in a shared fixture helper, not a `CODE_GRADE_VALUES`/`n_a`
issue at all. Result: `_derive_plan_mode_code_grade` returns `(None, "probe raised
TypeError('reviewer_digest() missing required keyword-only arg: severity_max')")` — the exception's
full `repr()` is preserved verbatim in the surfaced message, not discarded. This is a real trade
(reframes an unrelated crash as a "derivation failure" rather than an unhandled traceback), but it is
fail-**closed**, not fail-open: every path either derives exactly the one correct value or reports a
named FAIL carrying the real exception text. Without the `try/except`, the same unrelated regression
would raise unhandled inside `_reviewer_plan_mode_results`, likely aborting the rest of
`run_documented_contract_cases` (a broader blast radius, not a narrower one). Advisory only, not a
finding: no concrete input reaches a *wrong* PASS through this path.

**(d) The fixture genuinely exercises the real branch, not `_resolve_feature_dir`'s early return —
verified with real error text, plus a red-capability demonstration.** `_plan_review_fixture` always
passes a concrete `feature_dir` into `_plan_review_errors` → `validator.validate(...,
feature_dir, ...)` → `_pending_plan_review_error(text, reviewed, code_grade, feature_dir,
branch_override)`; `_resolve_feature_dir` returns `(feature_dir, None)` immediately whenever
`feature_dir is not None` (`validate-digest.py:865-866`) — so `dir_error` is `None` on every call
here, and the early-return path the dispatch warned about (which would reject **every** member
uniformly with a *different* message, "code_grade cannot be bound to review_sha: no checkout root…")
never fires. I read the actual error text returned for every member, live:
```
'fail'    -> ["a plan review has no code diff; code_grade must be 'n_a'.", "code_grade='fail' reports a gate as FAILED, but VERDICT is PASS…"]
'grade_2' -> ["a plan review has no code diff; code_grade must be 'n_a'.", "code_grade='grade_2' requires non-empty grade_2_reasons."]
'n_a'     -> []
'pass'    -> ["a plan review has no code diff; code_grade must be 'n_a'."]
```
Every non-`n_a` member's error list contains the literal string `"code_grade must be 'n_a'."` — the
real, targeted rejection from `_pending_plan_review_error`'s own `code_grade != "n_a"` check
(`validate-digest.py:1030`) — not the early-return message. `n_a` alone returns `[]`. **Red-capability
demonstrated:** monkeypatched `_pending_plan_review_error` in memory to accept `'pass'` instead of
`'n_a'` (preserving every other check — pending status, pinned-feature, branch corroboration — via
the real helper functions, changing only the literal comparison). Re-ran the derivation:
`derived_grade` flipped from `n_a` to `pass`, confirming the probe genuinely tracks whichever member
the validator's live rule accepts rather than returning a hardcoded/memoized value. Restored the
original function; derivation reverted to `n_a`. Zero files touched throughout (`git status
--porcelain` before/after this sequence: unchanged from the ambient dirty set, no new modifications).

### Whole-range re-review (base..e2c800f1) — Stage 1, spec compliance

Diffstat `59c5de97..e2c800f1`: two source-of-truth changes exactly matching the commit's own MF-1/MF-2
claims (`DECISIONS-INDEX.md` 1 line, `test-validate-digest.py` 46 lines) plus seven feature-directory
process artifacts (receipts, cycle-4 review-note copies, one observations append) — no scope creep,
nothing here that either must_fix did not ask for, no requirement left unimplemented. This matches
D-01..D-07 unchanged from cycle 4 (no decision touched). Panel findings (all `disposition: resolved`
in `plan.yaml`) unaffected — this commit is pure remediation of the panel's own prior review, not new
feature surface.

### Whole-range re-review — Stage 2, code quality

`code_grade` over `base..e2c800f14560d272357beb5c0628389a3433ddd2`: **20 gated functions, PASSING: 20,
0 FAIL.** The one new function (`_derive_plan_mode_code_grade`, line 394: cyclomatic 6, cognitive 7,
ABC 17.7, **grade 4**) and the one changed function (`_reviewer_plan_mode_results`, line 430:
cyclomatic 5, cognitive 6, ABC 15.2, **grade 4**) both clear the grade-3 test-code bar with margin — no
grade-2 or below-bar record, nothing needing a written reason. `code_grade: pass`.

No new Stage-2 finding beyond the advisory in MF-2(c) above (explicitly not a `must_fix`).

### Gate re-confirmation (per this cycle's contract; independently re-run, not merely trusted)

- `python3 tests/integration/test-validate-digest.py`: exit 0, 0 `^FAIL ` lines, `ALL PASSED.`,
  24.91s (contract cited ~19s; timing variance only, same shape — no disagreement in substance).
- `python3 tests/unit/test-config-shape-matrix.py`: 19/19, exit 0.
- `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` (env -u HARNESS_AGENT_TYPE, `rc`
  captured immediately): exit 0, 46 files, wall 62.35s, 0 `^FAIL ` lines (grepped the full captured
  output). Contract cited 60.9s — consistent.
- `gen-decisions-index.py --stdout | diff -q - DECISIONS-INDEX.md`: silent, exit 0.
- `check-state.sh`: exit 0 (many pre-existing repo-wide `note`-level items unrelated to BUG-1303, no
  `INV`-numbered violation naming this feature).

No disagreement with the orchestrator's pre-measured numbers.

### Q-A — restated once, unchanged, advisory (per this cycle's contract — NOT must_fix)

DEC-217's predicates (`touches_runtime_code`, `fix_confined_to_tests_and_contract_docs`) remain
undocumented in `harness-qa-gate/SKILL.md` and `harness-verification-rules/SKILL.md` (confirmed still
zero matches for either name or `DEC-217` in both files at this pin). Severity **med** — reconciled at
cycle 4 to a main-session-only remedy since both candidate files resolve to NOBODY under
`check-domain.sh`. This is an operator briefing row, not a gating finding this cycle.

## DIGEST

```yaml
VERDICT: PASS
DIGEST:
  headline: MF-1 and MF-2 both RESOLVED at e2c800f1, independently verified (not diff-observation) — MF-1's tags reproduce from compute_tags() applied to DEC-217's own text, MF-2's derivation genuinely tracks the validator's live rule (real error text read, red-capability demonstrated via in-memory perturbation) and fails loud-and-closed on 0/2+ qualifying members and on an unrelated helper exception. code_grade: pass over the whole pin. Q-A restated once, med, advisory only.
  mf1_status: RESOLVED
  mf2_status: RESOLVED
  code_grade: pass
  base: 63404ef06cd798c6d933b52336bf73de7b248028
  severity_max: med
  findings: 1
  must_fix: []
  spec_violations: []
  reviewed: "63404ef06cd798c6d933b52336bf73de7b248028..e2c800f14560d272357beb5c0628389a3433ddd2"
  human_commits_in_scope: []
  open_questions:
    - { id: Q1, question: "MF-2(c): _derive_plan_mode_code_grade's except Exception reframes any unrelated helper regression (demonstrated with a monkeypatched reviewer_digest raising TypeError) as a generic 'derivation failed' FAIL rather than an unhandled crash naming the real call site. The exception repr is preserved verbatim so nothing is silently lost, and the alternative (no try/except) has a broader blast radius, so this is advisory rather than a finding — flagging for the record only.", blocking: false }
    - { id: Q-A, question: "DEC-217's predicates (touches_runtime_code, fix_confined_to_tests_and_contract_docs) remain undocumented in harness-qa-gate/SKILL.md and harness-verification-rules/SKILL.md. Reconciled at cycle 4 to med/advisory: both candidate remedy files resolve to NOBODY under check-domain.sh, so this is a main-session-only fix routed to the operator, not re-raised as must_fix here.", blocking: false }
  files_touched: []
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1303-plan-code-review-digest/.harness/harness/features/BUG-1303-plan-code-review-digest/notes/review-harness-code-reviewer-c5.md
```
