# FEAT-43 goal-check at the ship pin `baa96b7e`

**BLUF: 20 met, 0 not_met, 0 partial, 0 open. No criterion moved, up or down.** Both post-`cd8dae47`
changes are behaviour-preserving on every input that previously graded — **measured, not argued**: on
all 83 `bin/*.py` files the pre-guard engine could grade, every record tuple (all three metrics,
per-letter ABC, grade and driver) is identical under both revisions. The SC-11 UAT's four numbers
re-grade to 6/5/16/14 at *this* pin, so the UAT executed at `cd8dae47` still evidences SC-11 here.

Cycles/send-backs inside my own run: **0**.

## 0. Delta bound — exactly as contracted, nothing wider

`git diff --name-only cd8dae47..baa96b7e` → 25 paths, of which **five** are non-`.harness/`:
`code_grade.py` (+6/-3), `test-code-grade.py` (+41/-0), `test-validate-digest.py` (+71/-8),
`fixtures/prior-validate-digest.py.fixture` and `fixtures/prior-harness_yaml.py.fixture` (both
added, 0 deletions). The other 20 are `.harness/` bookkeeping and notes. **The stated delta is the
real delta; it is not wider.** `HEAD` **equals** the pin `baa96b7ee1cf…` — I did not move it.

## 1. Change 1 — the cycle-27 hermetic CI fix. SC-19 and SC-20 confirmed at `baa96b7e`

My run: `python3 .agents/skills/harness/bin/test-validate-digest.py` → **`ALL PASSED`, exit 0**
(66/66 CLI, 24/24 T-09, 2/2 template, 18/18 enum, plus the code-grade block).

- **SC-19 — met.** Cases `code reviewer omission of code_grade is rejected`
  (`test-validate-digest.py:1783`) and `code_grade's missing-field hint names the four legal values`
  (`:1800`); the second asserts the rejection message names the field and its enum, not list wording.
- **SC-20 — met, all four clauses, each with its function:** reject `must_fix` + PASS under
  `advisory_unless_high` → `check_review_policy` (`:1946`); accept the same digest under `advisory`
  → `check_config_errors` (`:2559-2561`); a config with **no** `gates` block raises naming `gates`
  → `check_config_errors` (`:2562-2569`); **the fourth clause — the prior revision must accept the
  guarded digest — is `check_prior_validator` (`:1961`).** It now reads the two `.fixture` files,
  writes them under their real module names into a temp dir, and runs that validator as a
  subprocess. **No `git`, no repository history** — I read the function in full to confirm the live
  `git show` is gone, not merely unused.
  **Fidelity of the substitution, verified rather than trusted:** `git show df63193f:<path> | cmp -`
  against each fixture → **IDENTICAL** for both `validate-digest.py` and `harness_yaml.py`. The
  control still runs the same bytes it ran before. The `.fixture` suffix keeps them out of
  `_changed_python_files`, and the gated set below confirms it (no fixture record appears).

## 2. Change 2 — the cycle-28 `None` guards. Behaviour-preserving, measured

My runs: `python3 .agents/skills/harness/bin/test-code-grade.py` → **`PASS test-code-grade`, exit 0**;
`python3 .agents/skills/harness/bin/test-code-grade-cli.py` → **`PASS test-code-grade-cli`, exit 0**.
Both files print only a summary line, so I also loaded each module and invoked every carrying case
individually — **all returned 0 failures** (named in §5).

The three guards (`code_grade.py` @88 `AnnAssign.value`, @151 `withitem.optional_vars`, @164
`ExceptHandler.type`) wrap an existing `self.visit(...)` in `if … is not None`. **On any input where
the field is non-`None` the guard is a no-op by construction; where it was `None` the old code raised
`AttributeError` inside `visit`.** The decisive measurement, run read-only against a `/tmp` copy of
the `cd8dae47` engine: over all 99 `bin/*.py`, the old engine graded **83** and crashed on **16**; for
all 83, `dataclasses.astuple` over every `FunctionGrade` is **identical** between revisions —
**0 differing files**. No graded value moves.

**And the old failure was a hard crash, never a silent pass.** `code-grade.py` catches only
`(OSError, SyntaxError)` into `ungraded` (`:82`, `:127`), so `AttributeError` escaped uncaught. That
matters twice: REQ-07/SC-06 were never satisfied vacuously by a crashing file, and any run that
previously *succeeded* provably contained no crashing file.

## 3. The corpus-coverage question — derived answer: **no criterion's evidence changes**

The 16 formerly-crashing files (`harness_boundary.py`, `harness_merge.py`, and 14 `test-*.py` —
enumerated by my own probe) are now gradeable, so the engine covers 99/99. Three independent reasons
this cannot move a verdict:

1. **No criterion grades the ambient repository.** SC-01/02/03/09/10/17 use in-test fixtures;
   SC-04/05/06/07/08/14 use purpose-built fixture repositories. Their corpora are unaffected by what
   the engine can now additionally parse.
2. **SC-14's live half and SC-15 run over a gated *diff*, and none of the 16 is in it.** I checked
   each of the 16 against `git diff --name-only 7ccfae8d..baa96b7e` → **zero overlap**. A file that
   is not in the diff cannot enter the gated set however well it parses.
3. **The demand set is measured identical.** `code-grade.py --base 7ccfae8d --head baa96b7e` →
   exit 0, 201 records, `PASSING: 189`, 0 blocking, **12 `REASON REQUIRED`**. I extracted
   (path, qualname) for all 12: `check-plan-routes.py:main`, `code-grade.py:main`,
   `_case_27_owner_manifest`, `test_paths`, `test_rejected_revisions`, `test_control_paths`,
   `test_bars_follow_test_kinds`, `test_diff_and_determinism`, `check_commit_resolution`,
   `check_changed_function_resolution`, `check_policy_loading`, `reviewed_python_change` — **set
   equality with the 12 in `research-goalcheck-c26.md:§3`**. The three new functions the c27/c28
   work added grade at or above bar and emit no demand (records 198 → 201, passing 186 → 189, FAIL
   count unchanged at 12).

So **SC-15 is met at the ship pin on a stronger basis than at c26**: the answer set in
`review-harness-code-reviewer-validate-delta-c25.md:148-188` still matches demand-for-demand at
`baa96b7e`, proven by set equality rather than by superset reasoning. Non-vacuous (12 > 0).

The dispatching lead's read was correct, and the derivation above is why — not because criteria are
"about constructs, not corpus", but because every corpus a criterion actually uses is either a
fixture or a diff that excludes all 16 files.

## 4. SC-11 — **met**, and the pin question is settled by measurement

`notes/uat-sc11-c21.md` still reads `status: passed` (`:2`); raw numbers at `:146` are `a1 = 6`,
`a2 = 5`, `b1 = 16`, `b2 = 14`, and the MAXIMA arithmetic (`worst_A 6`, `worst_B 16`, `spread_A 1`,
`spread_B 2`, `gap 10`; both conditions hold) is **unchanged** from `research-goalcheck-final.md:§1`.
Its `review_sha:` header names `cd8dae47` (`:3`) — the pin the operator ran it at. I did not run,
edit or re-execute the UAT.

**Ruling: the UAT executed at `cd8dae47` still evidences SC-11 at `baa96b7e`.** The reasoning had to
engage with the fact that the UAT's outputs were graded by `code_grade.py`, which changed — so the
argument is not "the changes look small". The four surviving arm outputs exist at
`/tmp/sc11-uat/arm_{a1,a2,b1,b2}.py`, and I re-graded all four **read-only at this pin** (from the
scratch repo root, since the CLI refuses paths outside its repository):

| variant | worst cognitive | functions | `ungraded` |
|---|---|---|---|
| a1 | **6** | 21 | [] |
| a2 | **5** | 25 | [] |
| b1 | **16** | 15 | [] |
| b2 | **14** | 11 | [] |

**All four reproduce the UAT's transcribed values exactly at `baa96b7e`.** The measurement the UAT
took is invariant across both intervening changes, so its verdict transfers. This is a re-grade, not
a re-run of the experiment: the residual limitation named in `research-goalcheck-final.md:§2` —
that the arm files are the neutral run's on the operator's disclosure rather than by inspection —
is **unchanged and still testimonial**. My ruling inherits that limitation and does not remove it.

## 5. Verdict per criterion — what I re-derived, and what is carried forward

**Re-derived here, by a run I performed** (`test-code-grade.py`, `test-code-grade-cli.py`,
`test-validate-digest.py`, plus per-case invocation; every case 0 failures):

| SC | carrying case (0 failures in my run) | verdict |
|---|---|---|
| SC-01 | `check_fixtures` | met |
| SC-02 | fixture-table md5 `df9f4fd0d1ade8601349af16a73b4bef`, 2 blocks, AST-dumped from `git show baa96b7e:…` — **identical to c26's**; `grep -c 'produced by the tool'` → 0 | met |
| SC-03 | `check_direction_pairs` | met |
| SC-04 | `test_diff_and_determinism` | met |
| SC-05 | `test_paths` (16 text fields + 12 JSON keys, one assertion each) | met |
| SC-06 | `test_parse_and_usage` (exit 3, `UNGRADED:`, `PASSING: 0`) | met |
| SC-07 | `check_changed_function_resolution` | met |
| SC-08 | `check_changed_function_resolution` (absence assertions) | met |
| SC-09 | `check_worked_examples` | met |
| SC-10 | `check_delivery` | met |
| SC-11 | `notes/uat-sc11-c21.md` `status: passed`; four arm outputs re-graded at this pin (§4) | met |
| SC-14 | `test_paths:80` demand present / `:95` demand absent — both directions; 12 live demands (§3) | met |
| SC-15 | set equality 12/12 vs `review-…-delta-c25.md:148-188`, measured at `baa96b7e` (§3) | met |
| SC-17 | `test_bars_follow_test_kinds` | met |
| SC-19 | `test-validate-digest.py:1783` + `:1800` (§1) | met |
| SC-20 | `check_review_policy` + `check_config_errors` + `check_prior_validator` (§1) | met |
| — | `check_optional_field_guards` (`test-code-grade.py:648`), `check_self_grading`, `check_case_27_grade` | 0 failures |

**Carried forward by reference — not re-derived, and named as carried forward.** Each of these rests
on a file that is not in the delta *and* has no dependency on `code_grade.py` (checked, not assumed):

- **SC-12, SC-13** — `test-gate-policy.py`, unchanged; it imports only `gate_policy.py`, never
  `code_grade`. Carried from `research-goalcheck-c26.md:§4`.
- **SC-16** — `test-check-plan-routes.py`, unchanged; no `code_grade` reference. Carried from
  `research-goalcheck-c26.md:§4`.
- **SC-18** — `harness-code-risk-grading/SKILL.md`, unchanged (not in the delta). Carried from
  `research-goalcheck-c26.md:§4`.

REQ coverage is unchanged: no requirement lost a trace, none was added.

## 6. Working tree — both checkouts

```
$ git -C <worktree> status --porcelain
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q12-cycle-28-crash-class.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-delta-c28.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-backend-dev-2026-08-30-validate-crashclass-c28-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/research-goalcheck-c28.md   # mine
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-code-reviewer-delta-c28.md
```
**No source, test or `BRIEF.md` modification** — every entry is `.harness/` bookkeeping that predates
me. My artifact (this file) is the only thing I wrote. Every probe ran on `/tmp` copies; HEAD was
never moved and no destructive git command was run.

```
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
?? .harness/harness/features/FEAT-38-decisions-current-knowledge/
?? .harness/harness/features/FEAT-43-code-risk-grading/
?? .harness/harness/features/PR-922-omp-supervision/
?? .harness/logs/2026-08-25.md
?? .harness/logs/2026-08-29.md
?? .harness/notes/analysis-path-accessors-2026-08-26.md
?? .harness/notes/analysis-pr-922-omp-supervision-2026-08-28.md
?? .harness/notes/analysis-pr-922-omp-supervision-c1-2026-08-28.md
?? .harness/notes/grilling-845-one-vocabulary-2026-08-25.md
?? .harness/notes/grilling-root-resolution-2026-08-26.md
?? .harness/notes/probe-746-foreground-dispatch-2026-08-26.md
?? .harness/notes/triage-decisions-authority-2026-08-26.md
```
**No tracked modification** — untracked `??` entries only.

## Open questions

- **Q1 (non-blocking, carried from `research-goalcheck-final.md`):** the operator's `passed`
  transcription in `notes/uat-sc11-c21.md` is now committed at the pin — I confirmed
  `git show HEAD:…/uat-sc11-c21.md` reads `status: passed`. That precision is **retired**; nothing to
  do. Recorded so a reader of the earlier note does not chase it.
- **Q2 (non-blocking, carried from c25/c26):** the stray untracked
  `FEAT-43-code-risk-grading/` directory in the MAIN checkout persists. Still not mine to delete.
