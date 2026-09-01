# QA — gate-only assurance audit — BUG-1081-code-grade-enforcement — review @ 827219b5

**VERDICT input: matrix_ok=true, both required kinds satisfied, 0 FAIL.** But the prior gate's
greenness rests on a **discovery-count blind spot** (finding 1) and the follow-up reachability
receipt's headline claim is **inaccurate for one of its three named fixtures** (finding 2) — I
closed that gap myself with a measured mutation rather than leaving it reasoned. Nothing here
blocks the pin; both are reported as findings for the record, per rule 15.

## 1. Matrix re-run (measured, this session)

`test_matrix` from `.harness/harness.json`, read directly (not from the prior note):
`cross_module → {unit, integration} always`; `bugfix → {unit} always` + `when: __bug_class__/
match_bug_class` (a placeholder predicate this project's `harness.json` never defines — same
non-firing shape as every prior feature's gate, DEC-35/DEC-187); `docs → {}`. T-01=cross_module,
T-02=bugfix, T-03/T-04=docs. **Union required = {unit, integration}.**

```
$ .agents/skills/harness/bin/run-unit-tests.sh --kind unit
exit=0   grep -c '^FAIL ' = 0
33 scripts run (distinct "PASS <name>.py" lines), ~924 "ok " lines + ~440 "PASS <case>" lines
≈ 1364 individual assertions

$ .agents/skills/harness/bin/run-unit-tests.sh --kind integration
exit=0   grep -c '^FAIL ' = 0
32 scripts run, ~1163 "ok " lines + ~556 "PASS <case>" lines ≈ 1719 individual assertions,
includes test-code-grade-cli.py and test-validate-digest.py
```

`matrix_ok: true`. Both counts are non-zero discovery, not a sweep-over-empty-set false green.

## 2. Assurance vs. vacuity — the three things I was asked to actually test

### 2a. Changed-unit-to-test binding

**`code_grade.py`** (7 new callables: `TestKindsError`, `_patterns`, `_is_test_path`, `_blocks`,
`_severity`, `_classify_record`, `classify`). 2/7 named directly by a unit test
(`classify`: `check_classify_bars/_grade_two_is_reasoned/_precedence`; `TestKindsError`:
`check_classify_rejects_bad_test_kinds`). The other 5 are exercised only through `classify()`'s
observable contract (bar selection, severity field, blocking rule) — never called by name. This
is the intended shape for one seam with no second implementation (D-03), not a gap.

**`validate-digest.py`** (11 new functions). **0 are called by name from any unit-kind test** —
`test-validate-digest.py` is registered under `INTEGRATION_SCRIPTS` only (confirmed by reading
`run-unit-tests.sh`'s arrays directly, not the `detect` glob). All 11 are reached only
transitively, through ~12 `check_*` fixture functions driving real `validator.validate()`/
`--hook` calls over purpose-built git repos (D-07's black-box strategy: re-execution over a
second implementation). I independently measured 3 of the 11 are genuinely reachable and
discriminating (§2c); the remaining 7 (`resolve_reviewed_commit`, `reviewed_python_change`,
`_git_line_or_none`, `_load_test_kinds`, `_mechanical_code_grade`, `code_grade_enforcement_error`,
`_repo_root_for_feature`) I confirmed non-orphaned by tracing every call site directly (`grep`),
not by running a mutation against each — reasoned, not measured, for those 7.

### 2b. Discovery count vs. exit code — the real finding

**Finding — severity: low.** `run-unit-tests.sh`'s raw output aggregates **all ~12** of
BUG-1081's `check_*` fixture functions (covering pass/fail/grade_2/n_a × multiple availability
and precedence scenarios — dozens of underlying assertions) into **one single line**:
`ok    code-grade and review-policy gates` (integration output, line 73). I traced the call graph
directly: `run_code_grade_cases()` (`test-validate-digest.py:3193`) calls
`_check_review_repository` (3 checks: `check_derived_base_range`, `check_unresolvable_
default_branch`, `check_no_merge_base`) and `_check_bug1081_enforcement` (9 checks:
`check_mechanical_result_discrimination`, `check_hook_rejects_false_pass`,
`check_committed_syntax_error`, `check_digest_base_cannot_move_result`,
`check_deletion_only_range`, `check_missing_test_kinds`, `check_malformed_test_kinds`,
`check_judgment_outranks_clean_grade`, `check_plan_review_never_grades`) = 12 total, all
unconditional, none skipped. **Concrete failure scenario:** a future edit that drops one call
line inside either helper (e.g. deletes `check_committed_syntax_error(td, failures)`) produces
the exact same "ok" line, the exact same `grep -c '^FAIL '` = 0, and the exact same exit 0 as
today's clean run — nothing in the standing gate's own signal distinguishes 12 checks running
from 11. I closed this by reading source, not by anything the runner itself reports. (The
`test-code-grade.py` unit script has the identical shape at a smaller scale: 19 internal
`check_*` functions collapse into one `PASS test-code-grade` line — lower severity there since
each still fails loud with a `N failures` count if triggered, just not named.)

### 2c. Reachability receipt — measured, not just re-read

`receipt-harness-orchestrator-reachability.md`'s BLUF claims to close **"the three fixtures the
prior gate could only reason about"** — which `qa-test-matrix-c1.md`'s Q2 names explicitly:
`check_unresolvable_default_branch`, `check_no_merge_base`, `check_malformed_test_kinds`. I
traced each of the receipt's three mutations (M5/M6/M7) to the fixture whose docstring/assertion
text it actually reproduces:

| Mutation | Assertion text it reproduces | Actual fixture |
|---|---|---|
| M5 (`_merge_base_or_none`→None, "grade the whole history") | `"no merge base"` | `check_no_merge_base` ✓ |
| M6 (grader exception→`"pass"`) | `"a grader exception must become a NAMED refusal"` | `check_malformed_test_kinds` ✓ |
| M7 (degenerate range→accept as empty) | `"a review_sha already merged into the default branch must refuse"` — **verbatim `check_derived_base_range`'s own docstring, `test-validate-digest.py:2752`** | `check_derived_base_range`'s degenerate case — **not one of the three named fixtures** |

**`check_unresolvable_default_branch` (the "no `origin/HEAD` at all" fixture,
`test-validate-digest.py:2770`) is targeted by none of M5/M6/M7.** The receipt's own table and
BLUF assert all three are closed; one of the three named is not. **Severity: med** — not because
the underlying code is wrong (I checked, §below), but because the receipt is now a record that
overstates its own coverage, which is exactly the class rule 15 exists to catch even when
unintentional.

I closed the actual gap myself rather than leaving it flagged. A monkeypatch-based probe
(in-memory only, zero worktree writes — same technique the prior qa note already validated for
`check_plan_review_never_grades`) against a freshly-imported `validate-digest.py` module,
faking `_default_branch_or_none` resolved on the fixture's real no-origin/HEAD repo:

- **First mutation** (fake default branch → a nonexistent ref): still refuses, but for a
  *different* reason ("no merge base…", since the fake ref can't be merge-based against). That
  message *also* contains the substring `"default branch"` — which means the fixture's own
  4-grade loop assertion (`_assert_grade_refused(..., "default branch", ...)`, run once per
  `pass/fail/grade_2/n_a`) is **not independently discriminating**: all three distinct
  default-branch-family refusal messages (unresolved origin/HEAD, no merge base, degenerate/
  already-merged range) contain that same phrase. **Severity: info** — the fixture's *trailing*
  assertion (checked once, only for `code_grade="pass"`) requires the more specific
  `"repair origin/HEAD"` substring, which only the true origin/HEAD-unresolved message carries.
- **Second mutation** (fake *both* default-branch and merge-base resolved, so the flow reaches
  the degenerate-range branch instead): errors = `"...already an ancestor of the default
  branch..."` — genuinely does **not** contain `"repair origin/HEAD"`. **This is the
  discriminating result**: if a regression silently bypassed the origin/HEAD-unresolved guard,
  this fixture's trailing assertion would catch it (fails, correctly), even though the loop's
  generic per-grade assertion would not. Coverage is real, once you read past the loop to the
  trailing check — but it fires for one enum value (`pass`) only, not per-grade; low severity
  since the same `_canonical_review_range` call executes identically ahead of every grade
  comparison, so `pass`-grade coverage transfers structurally to `fail`/`grade_2`/`n_a`.

I also independently **reproduced** M6 myself, not merely traced it: staged a full copy of
`bin/` to `/tmp`, applied the identical mutation (`_classify_canonical_range`'s catch-all
`except Exception` → `return "pass", None`), ran the real `test-validate-digest.py` against it
via `VALIDATE_DIGEST_BIN`, and measured a **staged-but-unmutated control** first (per the
receipt's own methodology — staging alone changes 4 unrelated checks via `harness_boundary`
resolution). Delta over that control: **exactly +1 new failure**, `FAIL  code-grade and
review-policy gates` — the same aggregate line as §2b, confirming M6/`check_malformed_test_kinds`
independently. Worktree file sha256 (`e1e8e6ec42ac5cd3…`) confirmed unchanged before and after;
scratch files were cleaned up at `/tmp`, never inside the worktree or checked in.

## 3. `bash-write-guard` — the Q2 blocker, tested directly this session

Prior note's Q2 states the guard blocks qa from scratch-copying files outside the worktree. I
tested it directly: `cp .../validate-digest.py /tmp/qa_scratch_probe/` **succeeded**, no denial.
A direct append-write to the same file **inside** the worktree was correctly **BLOCKED**
(`bash-write-guard: BLOCKED — harness-qa: ... outside your domain`). So the guard scopes by
domain-and-path, not by "any Bash write anywhere" — `/tmp` scratch copies were available to me
this session without a DEC-153 disposable worktree. This directly contradicts the prior note's
stated blocker and reproduces this repo's own open Expertise item (Q-01: "one QA session saw it
deny such writes, a later session saw it allow them"). I did not isolate a *cause* for the
discrepancy either — reporting as a harness-behavior finding for the operator (`open_questions`
below), not a defect in BUG-1081's shipped code. Practically: physical scratch-copy mutation
testing (as I did for M6, §2c) is available to qa today for `/tmp` targets; it is unclear whether
that generalizes across sessions.

## 4. T-01..T-04 `verify:` clauses — re-run directly, can-fail confirmed

- **T-01/T-02**: re-run the standing kind command wholesale (`run-unit-tests.sh --kind unit`/
  `--kind integration`) — not a token grep, genuinely fails on any regression. Re-run this
  session: both exit 0, 0 FAIL (§1).
- **T-03**: `python3 -c "...assert all(x in t for x in (...))"` over `SKILL.md`. Re-run: pass.
  Confirmed it CAN fail with an in-memory-only probe (no worktree write) — dropping any one of
  the four tokens trips the assertion. Read the four tokens directly in `SKILL.md`: all sit in
  real, load-bearing prose describing the enforced contract (lines 64-90), not a token dump —
  no later commit trivializes what this check protects.
- **T-04**: three steps — regenerate the index, diff generated stdout against the committed file
  (genuinely fails on drift, not a `git diff --quiet HEAD` self-reference — P-10 class avoided),
  and a python assertion requiring exactly one `DEC-209` heading match plus a non-empty
  corresponding index row. Re-ran all three directly: pass, `DEC-209` found. No `HEAD`-relative
  or whole-file-substring (P-11 class) shape in any of the four verify clauses.

## Coverage gaps

None beyond §2b/§2c (already detailed as findings, not silent gaps).

## Open questions

- Q1 (non-blocking, harness gap not a BUG-1081 defect): the reachability receipt's headline claim
  ("closes the three fixtures") is inaccurate for `check_unresolvable_default_branch` — M7 covers
  a fourth, unnamed fixture instead. I closed the actual coverage gap myself (§2c) with a
  measured mutation; the receipt's own record should be corrected to name the fixture it actually
  measured, per rule 15. Not blocking because the underlying code is now independently confirmed
  sound.
- Q2 (non-blocking, harness gap): `bash-write-guard`'s behavior toward `/tmp` scratch copies was
  permissive this session, contradicting the prior note's stated blocker and this repo's own open
  Expertise item (Q-01). Worth isolating for real rather than re-discovering per-session — belongs
  to whoever owns the guard, not this feature.

## Files touched

None — gate-only audit, author-nothing preserved. All scratch mutation probes ran in `/tmp`,
outside the worktree, and were deleted after use; the worktree's `validate-digest.py` sha256 was
confirmed unchanged before and after every probe.
