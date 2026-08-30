# Receipt — harness-dev-ops — validate-ci-hermetic-c27

**BLUF: The contradiction is resolved. Both halves of the prior receipt were true measurements of
DIFFERENT df63193-less clones (depth 22 vs depth 26) — not of the same run. Building the run
honestly, `check_reviewed_range`'s three ambient-repo `n_a` assertions carried a SECOND, real,
pre-existing dependency on `df63193` (as base of the digest's own `reviewed:` field) that
`code_grade_bound_to_review` short-circuits past before the wave-4 derived-range logic ever runs —
and a THIRD, larger dependency on the module-level `REVIEW_SHA` constant resolving at all, shared by
~5 more `check_*` functions in the same suite, that a real `--depth 1` GitHub checkout also does not
satisfy (proven below). Both are fixed, hermetically, inside `test-validate-digest.py` only, by the
same pattern `check_derived_base_range`/`check_unresolvable_default_branch`/`check_no_merge_base`
already use: a purpose-built `/tmp` repo. `ALL PASSED` now holds in a genuine `--depth 1` clone, a
depth-N clone that includes `df63193`, and the ambient worktree alike. No production code change.**

## The contradiction, resolved

The prior receipt's "Hermeticity proof" section ran a **depth-22** clone and reported `ALL PASSED`;
its "second dependency" section separately built a depth-22 clone too and reported one failure. Both
cannot be true of the literally same command — and on re-measurement they are not: the "ALL PASSED"
figure was actually produced by the **depth-26** clone described two paragraphs later (df63193
present), pasted under the wrong heading. Re-running BOTH, side by side, with the identical overlay
and construction command (`git clone --depth N --single-branch --branch
feat/FEAT-43-code-risk-grading file://<worktree> <scratch>`, uncommitted changes overlaid via
`rsync`, `python3 -P test-validate-digest.py`):

```
$ (cd depth22 && python3 -P .claude/skills/harness/bin/test-validate-digest.py | tail -3)
1 FAILING.
$ (cd depth26 && python3 -P .claude/skills/harness/bin/test-validate-digest.py | tail -3)
ALL PASSED.
```

Root cause of the depth-22 failure, found by instrumenting `validate()` directly (not guessed):
`check_reviewed_range`'s first case uses `reviewed: "{PRE_FEATURE_REVISION}..HEAD"` — a **digest
field**, not the wave-4 derivation. `validate()` calls `reviewed_python_change(seen["reviewed"])` on
that literal string BEFORE ever reaching the derived-base logic (`validate-digest.py:1142-1154`); when
`df63193` (the base of that literal string) does not resolve, `reviewed_python_change` returns its own
`shape_error` ("reviewed range could not be resolved to commit revisions.") and the code takes the
`if shape_error:` branch, **never running** `_derived_reviewed_python_change` — so the "default
branch could not be resolved" message (which matches `N_A_REFUSAL_SUBSTRINGS`) never fires, and
neither of the two errors that DO fire matches any of the four wave-4 substrings the assertion checks
for. At depth 26, `df63193` resolves, `shape_error` is `None`, the `else` branch runs the derived
logic, and its "default branch" refusal supplies the match. **Depth alone decides pass/fail** — this
was never about df63193 crashing anything; it silently changed WHICH code path produced the
rejection, and only one of the two paths happens to name a substring the test recognizes.

## A third, larger dependency — found by reproducing GitHub's real shape

`REVIEW_SHA` (`94383e6...`, the constant `check_reviewed_range`/`check_review_sha_binding`/
`check_code_grade_state`/`check_review_policy`/`check_branch_corroboration` all resolve as a git
commit, directly or via `reviewer_digest()`'s default `reviewed: "HEAD..{REVIEW_SHA}"`) is 20 commits
back in this branch's real history. A genuine `actions/checkout@v4` default clone is `--depth 1`,
which does not carry it either:

```
$ git clone --depth 1 --branch feat/FEAT-43-code-risk-grading file://<worktree> <scratch>
$ cd <scratch>
$ git show df63193f7ec9798d9660904e0e4e7c78d52358f5:.claude/skills/harness/bin/validate-digest.py
fatal: path '...' exists on disk, but not in 'df63193f7ec9798d9660904e0e4e7c78d52358f5'
$ git cat-file -t df63193f7ec9798d9660904e0e4e7c78d52358f5
fatal: git cat-file: could not get object info
$ git show 94383e671e51f95d142f3220f97c8e453721d516
fatal: bad object 94383e671e51f95d142f3220f97c8e453721d516
$ git rev-parse --abbrev-ref origin/HEAD
fatal: ambiguous argument 'origin/HEAD': unknown revision or path not in the working tree.
```

Running the (then-unfixed) suite in this exact depth-1 clone produced **eight** distinct failures
spanning four functions (`check_code_grade_state`, `check_reviewed_range` x3, `check_review_sha_binding`
x2, `check_review_policy` x2, `check_branch_corroboration`) — every assertion that, directly or via
`reviewer_digest()`'s default, needed `REVIEW_SHA` to resolve as a real commit. This is the true
shape of the CI blocker: not one message in one function, but the whole `run_code_grade_cases()`
suite's shared reliance on a fixed historical SHA that shallow CI checkouts do not carry — the eng
lead's "second dependency in the SAME test file that reddens the SAME CI run" scope call, sized
correctly by measurement rather than by the earlier guess.

## The fix — one purpose-built repo, the pattern already in the file

`test-validate-digest.py` (`.claude/skills/harness/bin/`), no production code touched:

1. **`make_review_sha_repo(td)`** (new, next to `make_derived_base_repo`): a real `/tmp` git repo —
   `origin/main`/`origin/HEAD` at commit A; `review_sha` a REAL child of A touching a `.py` file (so
   its TRUE derived range genuinely changes Python, the exact property the module constant's own
   docstring already documented); the repo's checked-out `HEAD` a further, unrelated child, so `HEAD`
   and `review_sha` differ by construction (SEC-01 binds `head`, not `base` — the `HEAD..HEAD` forged
   no-op cases still need to reject).
2. **`_hermetic_review_sha_cwd(td)`** (new `@contextlib.contextmanager`): builds that repo, re-points
   the module-level `PRE_FEATURE_REVISION`/`REVIEW_SHA` names at its real oids, `chdir`s into it, and
   restores both (names and cwd) on exit. Isolated from `run_code_grade_cases` itself so that
   function keeps its pre-existing flat shape — extracted specifically because inlining the
   repo-build/chdir/global dance pushed `run_code_grade_cases`'s own grade below the test bar (3);
   with the extraction it grades exactly 3 (`abc=25.7`), same driver, same shape as before.
3. **`run_code_grade_cases()`**: one line changed — `with tempfile.TemporaryDirectory() as td:` becomes
   `with tempfile.TemporaryDirectory() as td, _hermetic_review_sha_cwd(td) as _cwd_marker:` — every
   `check_*` call below it is byte-for-byte unchanged. (The `as _cwd_marker` is load-bearing, not
   decorative: `code_grade.py`'s own `visit_With` — `code_grade.py:150-153` — calls
   `self.visit(item.optional_vars)` unconditionally for every `with` item, and `optional_vars` is
   `None` for a bare `with X():`; visiting `None` crashes with `AttributeError:
   'NoneType' object has no attribute '_fields'`. Reproduced directly against `code_grade.grade_source`
   before adding the binding, confirmed gone after — a genuine pre-existing bug in `code_grade.py`,
   worked around here rather than touched, since production code is out of scope this cycle.)

No function's *assertions* changed — every `check_*` call, its arguments, and its failure message are
identical to before this fix. Only the ground each one runs against became real, controlled git
plumbing instead of ambient repository history.

## Verification — quoted, exit statuses named

**Real `--depth 1` clone (GitHub's actual shape), after the fix:**
```
$ git clone --depth 1 --branch feat/FEAT-43-code-risk-grading file://<worktree> <scratch>
$ cd <scratch> && git show df63193...:.claude/skills/harness/bin/validate-digest.py
fatal: path '...' exists on disk, but not in 'df63193f7ec9798d9660904e0e4e7c78d52358f5'
$ git show 94383e671e51f95d142f3220f97c8e453721d516
fatal: bad object 94383e671e51f95d142f3220f97c8e453721d516
$ python3 -P .claude/skills/harness/bin/test-validate-digest.py
...
ALL PASSED.
$ echo $?
0
```

**A depth-N clone that includes `df63193`** (`--depth 30`, `df63193` confirmed present via `git
cat-file -t` → `commit`):
```
$ python3 -P .claude/skills/harness/bin/test-validate-digest.py
...
ALL PASSED.
$ echo $?
0
```

**Ambient worktree** (full history):
```
$ python3 -P .claude/skills/harness/bin/test-validate-digest.py
...
ALL PASSED.
$ echo $?
0
```

**Mutation proof — `check_reviewed_range` still discriminates**, run against the FINAL file state, in
the ambient worktree: changed `validate-digest.py:1153` from `elif python_changed:` to `elif False and
python_changed:` (the wave-4 n_a rejection disabled):
```
$ python3 -P .claude/skills/harness/bin/test-validate-digest.py
FAIL  code-grade and review-policy gates
        n_a with a reviewed Python diff must reject: ["reviewed head 'HEAD' does not resolve to
        this feature's pinned review_sha (...) — write the range that ends at review_sha
        (feature.json), not a convenient no-op."]
        a forged no-op AT review_sha itself must reject — the n_a decision must never read the
        digest's own reviewed:: []
        <review_sha>~1..<review_sha> is inside the class Q8 closes and must also reject: []
        a forged no-op AT review_sha whose TRUE derived range changed Python must still reject: []
        <review_sha>~1..<review_sha> against a real repo must also reject: []
```
Restored (`git diff --stat .claude/skills/harness/bin/validate-digest.py` → empty afterward), suite
re-verified `ALL PASSED` again.

**The five focused suites, each named with exit status** (`.claude/skills/harness/bin/`, ambient
worktree):
```
$ python3 -P test-validate-digest.py    → exit 0  (ALL PASSED)
$ python3 -P test-code-grade.py         → exit 0  (PASS test-code-grade)
$ python3 test-code-grade-cli.py        → exit 0  (PASS test-code-grade-cli — run WITHOUT -P,
                                                     matching run-unit-tests.sh; unrelated, unchanged)
$ python3 -P test-gate-policy.py        → exit 0
$ python3 -P test-check-plan-routes.py  → exit 0  (ALL PASS)
```

**Fixture byte-identity, re-quoted** (unchanged from the first pass, re-verified this cycle):
```
$ git show df63193...:.claude/skills/harness/bin/validate-digest.py | shasum -a 256
4933c60c55458085db535dd32efa5702ba9516a871a7f1114645cd1e1edb1646  -
$ shasum -a 256 .claude/skills/harness/bin/fixtures/prior-validate-digest.py.fixture
4933c60c55458085db535dd32efa5702ba9516a871a7f1114645cd1e1edb1646  <fixture>
$ git show df63193...:.claude/skills/harness/bin/harness_yaml.py | shasum -a 256
ca261f649a23d34d6bd9334bf174453fdcfea25091ca23f1c30a1c360fcd112f  -
$ shasum -a 256 .claude/skills/harness/bin/fixtures/prior-harness_yaml.py.fixture
ca261f649a23d34d6bd9334bf174453fdcfea25091ca23f1c30a1c360fcd112f  <fixture>
```

**`code_grade.py`'s own bar, unchanged** (`code_grade.py` was not touched this cycle):
`code_grade.grade_source` on `code_grade.py` itself → **53 functions graded, zero below grade 4**.

**New/changed qualnames in `test-validate-digest.py`, graded**:
- `make_review_sha_repo` — grade 4 (cyclomatic 1, cognitive 0, abc 8.1)
- `_hermetic_review_sha_cwd` — grade 4 (cyclomatic 1, cognitive 1, abc 10.8)
- `run_code_grade_cases` — grade 3 (cyclomatic 3, cognitive 3, abc 25.7) — meets the test-file bar
  (3, per `code_grade_cli._is_test`); confirmed via `test-code-grade.py`'s own `check_self_grading`,
  which failed once (`grade >= 3: expected True, got False`) on an earlier, unextracted version of
  this same fix and now passes.

`git diff --stat .claude/skills/harness/bin/test-validate-digest.py`: `79 insertions(+)/8 deletions(-)
across 1 file` (net `+71/-8`) — the two new functions, the one-line `with` change in
`run_code_grade_cases`, and the `contextlib` import.

## Tree state

```
$ git -C <worktree> status --porcelain
 M .claude/skills/harness/bin/test-validate-digest.py
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .claude/skills/harness/bin/fixtures/
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q11-ci-hermeticity-cycle-27.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-2026-08-29-01-validate-ci-hermetic-c27-eng.md
$ git -C /Users/molchairuangutai/GitHub/harness status --porcelain
```
(main checkout: only pre-existing untracked `??` entries from other work, no `M` lines — no tracked
modification). `feature.json`'s `M` predates this session (not touched by me, matching the first
pass). No scratch files anywhere under the worktree. All throwaway clones lived under `mktemp -d` in
`/tmp` and were `rm -rf`'d — two were missed mid-investigation and removed before this receipt was
written; none remain (verified by directory-existence check after cleanup). HEAD never moved; no
destructive git command was run.
