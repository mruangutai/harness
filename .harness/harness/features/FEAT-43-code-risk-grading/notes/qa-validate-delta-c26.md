# QA — validate-delta-c26 — bind-by-mutation on the B21 tests

**Verdict: the two new tests bind, for the right reason, at the correct kind of failure (assertion,
not crash), with no self-grading exemption purchased for them. Both mutations independently confirmed;
both restores byte-identical. All five focused suites and both cited grader measurements reproduced
exactly. One residual gap named in §7 — narrow, does not warrant another cycle.**

Pin `cd8dae4767…` at worktree
`/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-43-code-risk-grading`.
`code_grade.py` confirmed byte-identical to prior pin `e12d53b1…` (`git diff … -- code_grade.py` = 0
lines; md5 `c5db829f96b3b8dc8d144a1466392e4d` both before and after every mutation below). The only
source delta between pins is `.claude/skills/harness/bin/test-code-grade.py`, +68/-0 lines (pure
addition, confirmed by `git diff --stat e12d53b1.. cd8dae47`).

## 1–2. Do the tests bind, and is it an assertion or a crash?

**Mutation (a) `_qualname` → `return name`.**
`python3 test-code-grade.py` → exit 1:
```
FAIL qualname collision gated set: expected set(), got {'dispatch'}
FAIL qualname collision informational set: expected {'dispatch', 'Alpha.run', 'Beta.run'}, got {'Alpha.run', 'Beta.run'}
2 failures
```
This is `check_method_qualname_collision_pre_images` (the two `check(...)` calls it makes, per
`main()`'s registration list). **Named assertion failures, exit 1 — no `KeyError`, no traceback.**
Restore: md5 back to `c5db829f…`, `git status --porcelain -- code_grade.py` empty,
`python3 test-code-grade.py` → `PASS test-code-grade`, exit 0.

**Mutation (b) `_strip_docstring` → `return body`.**
`python3 test-code-grade.py` → exit 1:
```
FAIL docstring-only rename gated set: expected set(), got {'renamed'}
FAIL docstring-only rename informational set: expected {'renamed'}, got set()
2 failures
```
Matches the orchestrator's cited measurement verbatim (`check_docstring_only_rename_not_gated`).
Restore: md5 back to `c5db829f…`, `git status --porcelain -- code_grade.py` empty, suite exit 0.

Mutations were applied and restored **one at a time**, never together, exactly as required.

**On the design-constraint concern (`_pre_images:380` `KeyError`):** traced it — it does not fire for
this fixture. Under the mutation, `_body_hashes` collapses to a single bare key `"run"` (three
same-named defs overwrite each other in insertion order, last write wins = Beta's hash), but
`by_name["run"]` still resolves because the **top-level** function is *also* named `"run"` in the
base commit and its qualname was never dotted to begin with (`_child_qualname`, used by
`grade_source`/`by_name`, is untouched by this mutation). So the lookup succeeds but returns the
*wrong* record — which is exactly what makes the failure an assertion, not a crash. Reported per the
"whichever you observe" instruction: **assertion, not exception.**

## 3. Do they bind for the right reason?

**Docstring test — proving the rename is load-bearing, not incidental.** Built an out-of-tree variant
(temp script importing `code_grade`, not touching `test-code-grade.py`): same docstring-only edit,
**no rename**.
- Against real `code_grade.py`: `gated=set()`, `informational={'documented'}`.
- Re-applied the `_strip_docstring` mutation and reran the identical variant: `gated=set()`,
  `informational={'documented'}` — **bit-for-bit identical to the unmutated run.**

Why: `_resolve_pre_image` does `before_names.get(record.qualname)` first: name-match short-circuits
before any hash lookup, so a no-rename fixture never reaches `_hash_body`/`_strip_docstring` at all —
it would pass identically whether the mutation is live or not, proving nothing. The shipped fixture
renames `documented`→`renamed` specifically to defeat the name-match and force resolution through
`by_hash`, which is what the mutation run in §1 demonstrates binds. Restored code_grade.py after this
probe; md5 and `git status --porcelain` reconfirmed clean before proceeding.

**Collision test — grades and bodies at both refs**, computed directly via `code_grade.grade_source`/
`_body_hashes` (out-of-tree, unmutated code_grade.py):

| qualname | base grade | head grade | base body-hash (12c) | head body-hash (12c) |
|---|---|---|---|---|
| `run`/`dispatch` (top-level) | 5 | 5 | `cf05c3aeb3c0` | `cf05c3aeb3c0` |
| `Alpha.run` | 5 | 5 | `d5d2f0716a5b` | `d5d2f0716a5b` |
| `Beta.run` | 5 | 5 | `f49deb4fc9f9` | `f49deb4fc9f9` |

All three grades are identical (trivial one-line bodies, no branching) and all three bodies are
textually distinct (`"top"`/`"alpha"`/`"beta"`) — **there is no real hash collision between bodies.**
The "collision" is entirely in `_qualname`'s *key space* under the mutation: three same-named defs
(`run`/`run`/`run` in base) collapse to one dict key, so two of three hashes are clobbered before
`_pre_images` ever runs. Traced the consequence for the top-level rename (`run`→`dispatch`): under
the mutation, `by_hash` in the base pre-image ends up containing only Beta's hash keyed against the
*top-level* record (a wrong pairing), so when head's `dispatch` looks up its own hash it finds no
match at all (`before=None`) and — **because `_resolve_pre_image` returning `None` routes to
`gated`** — `dispatch` is wrongly gated instead of landing informational. Since all three grades are
equal, a correct resolution would never gate it; the wrong resolution produces a **visibly wrong
partition** (a false "needs human sign-off" flag on an unremarkable rename), not merely an incidental
pass. The assertion in §1 (`expected set(), got {'dispatch'}`) is exactly this signal, not a
coincidence of the grade-comparison path.

## 4. Self-grading bar

Graded `test-code-grade.py` itself (`code_grade.grade_source`, test-file bar = 3):
- `check_docstring_only_rename_not_gated`: **grade 4**
- `check_method_qualname_collision_pre_images`: **grade 4**
- `check_method_qualname_collision_pre_images.source` (nested fixture helper): **grade 5**

24 functions total in the file; 2 below bar — both pre-existing, both allowlisted:
`check_commit_resolution` (grade 2, SC-15 item 11) and `check_changed_function_resolution` (grade 2,
SC-15 item 12). Neither is new to this delta.

`git diff e12d53b1.. cd8dae47 -- test-code-grade.py`: **+68/-0, a pure addition** — the
`SELF_GRADING_ALLOWLIST` block (lines ~207–226) does not appear in the diff at all.
**No allowlist entry was added for either new test or its helper.**

## 5. Five focused suites (each run individually)

| suite | exit |
|---|---|
| `test-code-grade.py` | 0 (`PASS test-code-grade`) |
| `test-code-grade-cli.py` | 0 (`PASS test-code-grade-cli`) |
| `test-gate-policy.py` | 0 (all `ok`) |
| `test-check-plan-routes.py` | 0 (`ALL PASS`) |
| `test-validate-digest.py` | 0 (`18/18 …`, `ALL PASSED.`) |

## 6. Orchestrator's three measurements — reproduced, not adopted

1. `code-grade.py --base 7ccfae8d --head cd8dae47`: exit **0**. `grep -c '^FUNCTION$'` → **198**.
   `RESULT: FAIL` count → **12** (all twelve carry a `REASON REQUIRED:` line — allowlisted, not
   blocking). `RESULT: PASS` → 186. 186+12=198. **Matches: 198 records, 12 REASON REQUIRED, zero
   blocking (exit 0).**
2. `code-grade.py .../code_grade.py`: exit 0, `grep -c '^FUNCTION$'` → **53**. `GRADE:` distribution:
   11×4, 42×5 — **zero below grade 4. Matches.**
3. The `_strip_docstring` mutation reproduction is §1 above — output byte-for-byte matches the cited
   `expected set(), got {'renamed'}` line. Restore verified by md5 + `git status --porcelain` +
   suite exit 0. **Matches.**

## 7. Adequacy — what's still unexercised

The two branches close the B21 mutation gap for their **primary** call sites (the only two call sites
either function has). Not exercised by these two tests, and worth naming rather than quietly closing:

- **`AsyncFunctionDef`** is not exercised in either fixture (both use plain `def`) — `_qualname` and
  `_strip_docstring` are reached identically for async defs via the same code paths, so this is a
  parallel-path gap, not a distinct branch, but it is untested by this delta specifically.
- **Nested classes** (a class defined inside a class) exercise the `_qualname` class-branch
  (`code_grade.py:369`) with a *non-empty* incoming prefix; the collision fixture's two classes are
  both top-level (`prefix=""` going in), so that branch is only exercised trivially. A
  class-in-class collision (e.g. two methods of the same name on classes nested under a shared outer
  class) is not covered.
- **Multi-hash-candidate tie-breaking** (`_resolve_pre_image`'s `matches[0]`, i.e. two *different*
  base functions truly sharing one body hash) is not exercised by either new test; it is a
  pre-existing path (`check_pre_image_resolution_priority` in the suite covers a related but
  distinct scenario) and out of scope for this delta per the B21 ruling.

None of these are branches B21 named — B21 named exactly the two lines these two tests bind, and both
bind correctly, for the right reason, at the right failure kind. The gaps above are pre-existing
surface area of `_qualname`/`_strip_docstring`, not unproven parts of the B21 contract. **I do not
read this as leaving B21 open.**

## Housekeeping note (not source, not reviewed as such)

`feature.json` and `notes/uat-sc11-c21.md` carry tracked modifications, and
`observations/harness-pm.md` picked up a further one during this run — all from the concurrent
product/goal-check run named in the dispatch context, not from this QA pass. `code_grade.py` is
confirmed unmodified (md5-verified) at every checkpoint above.
