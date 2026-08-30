# QA delta review — FEAT-43 cycle 27 (pin 4adb2219)

**BLUF:** The delta (`test-validate-digest.py` + two `.fixture` files) is genuinely hermetic,
its vendored control genuinely discriminates, and the fixtures are genuinely inert to grading and
test discovery. Delta **PASSES**. Independently, `code_grade._Counter.visit_With`/`visit_Try` is a
real, reproducible crash bug in the feature's own grading engine — introduced by this feature's
first commit, not by cycle 27, and not currently intersecting the feature's own gated set — sized
below for the operator to rule on. It does not fail this delta.

## Item 1.2 — hermeticity, my own reproduction
- `git clone --depth 1 --branch feat/FEAT-43-code-risk-grading file://<worktree> $d/shallow` → exit 0.
  `git -C $d/shallow rev-list --count HEAD` = `1`; `.git/shallow` present; `rev-parse HEAD` =
  `4adb2219954aa132b1e8450cdd9e571dbedba309` — pin confirmed.
- `git -C $d/shallow cat-file -e df63193f7ec9798d9660904e0e4e7c78d52358f5` → **exit 1** (fails, as
  required). CI condition genuinely reproduced.
- `python3 $d/shallow/.claude/skills/harness/bin/test-validate-digest.py` → **exit 0**, tail
  `ALL PASSED.`
- `grep -n "subprocess\|'git'\|\"git\""` over the file: the only real `subprocess.run(["git", …])`
  calls are `_git_quiet`/`_init_test_repo`/`make_derived_base_repo` (build fresh, purpose-built
  `/tmp` repos, no ambient history) and `check_prior_validator`'s own `subprocess.run([sys.executable,
  …])`, which invokes no git at all — it reads the two vendored fixtures off disk (`test-validate-
  digest.py:1961-1983`). No history-dependent git call found.

## Item 1.3 — control discrimination, my own mutation
All work done in the same disposable shallow clone above, never the worktree.
- Fixture sha256 before: `4933c60c…`. Inserted one line into `validate()`
  (`err.append('QA-MUTATION…')` right after `err = []`, `:531`) forcing the prior validator to
  reject everything.
- Reran the suite: **exit 1**, and the failures list names exactly
  `previous validator must accept the gated digest` (line 71 of output) — the control caught the
  corruption with its documented failure message.
- Restored the fixture from a pre-mutation copy. sha256 after: `4933c60c…` — **identical** to
  before.
- Reran the (now-restored) suite: exit 0, `ALL PASSED.`
- Worktree was never touched by this step: `git -C <worktree> status --porcelain -- .claude/skills/
  harness/bin` → empty; worktree fixture sha256 unchanged (`4933c60c…`).

## Item 1.4 — fixture inertness, my own runs
- `code-grade.py --base 7ccfae8d --head 4adb2219`: **exit 0**, **200** `FUNCTION` records, **12**
  `RESULT: FAIL` and all 12 are `GRADE: 2` (`REASON REQUIRED`, none below — 0 at a blocking grade),
  **12** `REASON REQUIRED` mentions. Confirms the orchestrator's 200/0-blocking/12 numbers.
- No `PATH:` in the 200-record output matches `*.fixture` (`grep -c "\.fixture"` = 0). Confirmed.
- `code-grade.py .claude/skills/harness/bin/code_grade.py`: **exit 0**, **53** functions, all
  `RESULT: PASS`, grade distribution `{4: 11, 5: 42}` — zero below grade 4. Confirms 53/0-below-4.
- Discovery: `run-unit-tests.sh` enumerates tests via two **explicit** arrays (`UNIT_SCRIPTS`,
  `INTEGRATION_SCRIPTS`, lines 30-32) — neither fixture name appears in either
  (`grep -c` = 0) — plus a drift-detector glob `"$BIN_DIR"/test-*.py` (line 62), which cannot match
  `prior-*.fixture` (wrong prefix, wrong suffix). `.github/workflows/tests.yml` calls only
  `run-unit-tests.sh --kind unit|integration` and named scripts; no independent glob. Fixtures are
  inert to both grading and discovery.

## Item 2 — engine defect sizing (operator decision, not a delta gate)
1. **Blast radius, my own count:** throwaway script under `mktemp -d` importing `code_grade` and
   calling `grade_source` on every `bin/*.py`: **99 files, 83 graded, 16 crashed** — matches the
   orchestrator's 83/16 exactly. Crash list includes production `harness_boundary.py` and
   `harness_merge.py`, plus 14 `test-*.py` files, all with `AttributeError: 'NoneType' object has no
   attribute '_fields'`.
2. **Loud crash, not a silent mis-grade.** `_records()` (`code_grade.py:235-248`) appends into one
   local list inside a single unwound call; when `_record()` raises mid-recursion the exception
   propagates out of `grade_source` before any `return` — no partial list is ever produced. Grepped
   every caller of `grade_source` (`code-grade.py`, `code_grade.py` itself, both test files) for
   `except`: only `except (OSError, SyntaxError)` (`code-grade.py:82`) and `except (SyntaxError,
   ValueError)` (`:127`) exist anywhere near a caller — neither catches `AttributeError`. Verdict:
   **raise, never a wrong grade.**
3. **Reachable through the shipped CLI — demonstrated.** Built a throwaway git repo under `mktemp -d`
   (base commit: function with `with lock:` no `as`; head commit: same function, body edited).
   `code-grade.py --base <base> --head <head>` → **traceback, exit 1** (uncaught
   `AttributeError`), crashing while computing the **base's pre-image** (`_pre_images` →
   `grade_source`, `code_grade.py:376`) — so this triggers on the unchanged old body of any touched
   function that contains the construct, not only on newly-added code.
4. **Zero intersection with FEAT-43's own gated set at this pin.** The 200-record output's distinct
   `PATH:` values (10 files, all under `.claude/skills/harness/bin/`) share no member with the
   16-file crash list — confirmed by direct comparison. The gate passing at 4adb2219 is not currently
   protected by anything; it is simply that this feature's own diff never touches a file containing
   a bare `with`/`except`.
5. **Introduced by this feature, first commit — not pre-existing, not cycle 27's fault.**
   `code_grade.py` does not exist at either `7ccfae8d` (feature base) or `df63193` (pre-feature) —
   `git cat-file -e` fails both. `git log -S"def visit_With"` and `-S"def visit_Try"` both name
   **`1ac1bd0` "feat: add code risk grading gate"** as sole introducer — the feature's very first
   commit, unmodified since across all 5 commits touching the file. It is inside `7ccfae8d..4adb2219`
   (the whole feature's reviewed range) but nowhere near cycle 27's actual delta.

**Smallest correct fix (spec only — not authorized to apply):**
`.claude/skills/harness/bin/code_grade.py`, class `_Counter`:
- `visit_With` (`:150-156`): guard the unconditional `self.visit(item.optional_vars)` (`:153`) with
  `if item.optional_vars is not None:`, exactly the pattern `visit_Assert` already uses for
  `node.msg` (`:177`).
- `visit_Try` (`:160-171`): guard `self.visit(handler.type)` (`:165`) with
  `if handler.type is not None:`.
- Binding test in `test-code-grade.py` (same file/module as existing `check_*` grade_source cases,
  e.g. near `check_direction_pairs`/the worked-examples checks): two new assertions —
  (a) `code_grade.grade_source("def f():\n    with lock:\n        pass\n", "f.py")` must not raise
  `AttributeError` and must return exactly one record, with cyclomatic/cognitive/ABC equal to
  grading `"def f():\n    with lock as _discard:\n        pass\n"` (a bare `Name` target visits to
  zero cost, so the two must be metric-identical — this is the exact assertion `visit_Assert`'s own
  `node.msg is not None` guard already licenses by analogy);
  (b) same shape for `"def f():\n    try:\n        pass\n    except:\n        pass\n"` vs.
  `"...except Exception:\n        pass\n"`. Both fail today with the AttributeError before the fix
  and pass after — a mutation of either guard back to unconditional reproduces the crash, proving
  discrimination.

## Not covered
- No fix was applied (out of scope, per dispatch).
- Did not re-verify the seven closed defects, the canonical project-wide suite, or any linter/formatter.
- Did not audit `code_grade.py` for other unguarded-`None` AST fields beyond `visit_With`/`visit_Try`
  (the dispatch named these two specifically; a broader audit was not requested).
- Did not investigate whether commits `3afaf4e`/`94383e6`/`a643e44`/`e12d53b` touched
  `visit_With`/`visit_Try` incidentally (git -S confirms only the *introducing* commit; did not diff
  each subsequent commit's hunks against these two functions since none appeared in the `-S` search
  results, which already rules out any later edit to those two lines).

## Final worktree state
`git -C <worktree> status --porcelain`:
```
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q11-ci-hermeticity-cycle-27.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-2026-08-29-01-validate-ci-hermetic-c27-eng.md
```
All three pre-date this run (present at first inspection, before any command of mine); none touched
by this review. All temporary mutations (fixture corruption, scratch repos) were made and undone
entirely inside `mktemp -d` throwaway clones/repos, never in the worktree.

## Item 2 addendum — exhaustive optional-field audit (send-back cycle 1)

**BLUF:** One additional crashing construct found — `visit_AnnAssign`'s unconditional
`self.visit(node.value)` on a bare annotation (`x: int`, no `=`), same `AttributeError:
'NoneType' object has no attribute '_fields'` shape as `visit_With`/`visit_Try`. It does **not**
change the 16-file crash count (re-confirmed exactly 16/16, same files) because no file in the
harness's own `bin/*.py` currently contains that construct inside a graded function body — it is
latent, not currently manifesting, and does not intersect the 200-record gated set either
(trivially: it doesn't fire on any of the 99 files scanned, gated-set files being a subset of
those 99). The pattern-omitted-twice hypothesis is otherwise a clean negative: 29 candidate
constructs tested against every `visit_*` override on `_Counter` (the module's only
`ast.NodeVisitor` subclass), only 3 raise, and all 3 share the identical root cause (a custom
`visit_*` override calling `self.visit(<optional-field>)` without a None guard). The three-site
fix below is what closes cycle 28 in one pass.

### A. Method inventory and mechanism
`_Counter` is the sole `ast.NodeVisitor` subclass `grade_source` drives (`code_grade.py:55`,
confirmed by grepping the module for `NodeVisitor` — one hit). Every `visit_*` method was read in
full (`:77-220`) and each explicit `self.visit(X)` call was checked against the `ast` ASDL for
whether `X`'s field is declared optional (`expr?`/`identifier?`).

The decisive mechanical fact: the base `ast.NodeVisitor.generic_visit` iterates fields with an
`isinstance(value, AST)` guard, so it silently skips `None` — including `None` entries inside a
list (which is what makes `Dict.keys` for `{**a}` safe). **Only a custom `visit_*` override that
calls `self.visit(node.<optional-field>)` directly, bypassing that guard, can crash.** This
reduces the audit to: for every custom override, list its explicit `self.visit(...)` calls, and
check whether that field's ASDL cardinality is `?`.

Custom overrides that visit only required fields (target/iter/test/value where value is
non-optional/subject, or route through `generic_visit`/`_visit_block` on a list): `visit_Name`,
`visit_Call`, `visit_Assign`, `visit_AugAssign`, `visit_NamedExpr`, `visit_Import`,
`visit_ImportFrom`, `visit_FunctionDef`/`AsyncFunctionDef`, `visit_ClassDef`, `visit_For`/
`AsyncFor`, `visit_While`, `visit_If`, `visit_IfExp`, `visit_BoolOp`, `visit_Compare`,
`visit_UnaryOp`, `visit_ListComp`/`SetComp`/`GeneratorExp`/`DictComp` (via
`_visit_comprehension`), `visit_Match`. `visit_Assert` visits an optional field (`node.msg`) but
is already correctly guarded (`:177`, `if node.msg is not None`) — this is the reference pattern.

Overrides that visit an optional field **without** a guard: `visit_With`/`AsyncWith`
(`item.optional_vars`, `withitem.optional_vars: expr?`), `visit_Try` (`handler.type`,
`ExceptHandler.type: expr?`) — both already found in pass 1 — plus, newly, `visit_AnnAssign`
(`node.value`, `AnnAssign.value: expr?` — optional specifically because `x: int` with no `=` is
valid Python and sets `value=None`; `AnnAssign.target`/`.annotation` are non-optional and stay
unguarded correctly).

### B. Construct → field → raises/clean (29 constructs run, every row executed)
All run via `grade_source(source, "f.py")` under a `mktemp -d`-adjacent scratch script (not in the
worktree); table lists source shape, the field it exercises, and the observed outcome.

| # | Construct | AST field | Outcome |
|---|---|---|---|
| 1 | `return` (bare) | `Return.value` | clean |
| 2 | `raise` (bare) | `Raise.exc` | clean |
| 3 | `raise ValueError('x')` | `Raise.cause` (implicit None) | clean |
| 4 | `raise ... from e` | `Raise.cause` | clean |
| 5 | `try/except:` (bare) | `ExceptHandler.type` | **RAISES** (`visit_Try`, known) |
| 6 | `try/except ValueError:` (no `as`) | `ExceptHandler.name` | clean (already guarded) |
| 7 | `with open('x'):` (no `as`) | `withitem.optional_vars` | **RAISES** (`visit_With`, known) |
| 8 | `a[:]` | `Slice.lower/upper/step` | clean |
| 9 | `a[1:]` | `Slice.lower` set, others None | clean |
| 10 | `d = {**a}` | `Dict.keys` (`None` list entry) | clean |
| 11 | `yield` (bare) | `Yield.value` | clean |
| 12 | `yield 1` | `Yield.value` set | clean |
| 13 | `def f() -> None:` | `FunctionDef.returns` | clean (never visited — `visit_FunctionDef` doesn't recurse into signature) |
| 14 | `x: int` (bare) | `AnnAssign.value` | **RAISES** (`visit_AnnAssign`, NEW) |
| 15 | `x: int = 1` | `AnnAssign.value` set | clean |
| 16 | `class A: pass` (nested) | `ClassDef` bases/keywords | clean (`visit_ClassDef` doesn't recurse) |
| 17 | `x = u'abc'` | `Constant.kind` | clean |
| 18 | `import os` | `alias.asname` (None) | clean |
| 19 | `import os as o` | `alias.asname` set | clean |
| 20 | `global x` | `Global.names` (strings, not nodes) | clean |
| 21 | `nonlocal x` | `Nonlocal.names` | clean |
| 22 | `[x for x in a]` | `comprehension.ifs` (empty list) | clean |
| 23 | `[x for x in a if x]` | `comprehension.ifs` (populated) | clean |
| 24 | `def f(*args, **kwargs)` | `arguments.vararg/kwarg` | clean (signature never visited) |
| 25 | `def f(a=1)` | `arguments.defaults` | clean (signature never visited) |
| 26 | `match a: case _: pass` | wildcard `MatchAs.pattern` | clean |
| 27 | `match a: case x if x>0: pass` | `match_case.guard` (`expr?`, not visited at all) | clean (undercounts, doesn't crash — separate correctness gap, not in scope) |
| 28 | `assert True` (no msg) | `Assert.msg` | clean (reference: correctly guarded) |
| 29 | `assert True, 'msg'` | `Assert.msg` set | clean |

3 of 29 raise; all 3 are the same root cause (unguarded `self.visit` on an ASDL-optional field in
a custom override), never a different exception shape, never a silent wrong grade.

### C. New-construct disposition (`AnnAssign.value`, bare `x: type`)
- **Appears in harness's own `bin/*.py`?** Checked with an AST walk for `AnnAssign` nodes with
  `value is None` across all 99 `.claude/skills/harness/bin/*.py` files: 11 hits, all 11 in
  `code_grade.py` lines 15–25 — the `FunctionGrade`/dataclass field declarations at class-body
  scope. None are inside a function body, and `_records()` only ever calls
  `counter._visit_block(node.body)` for `FunctionDef`/`AsyncFunctionDef` nodes — a dataclass's
  class-body annotations are never part of any graded function's body, so they're never reached.
  Empirically confirmed by patching in only the `AnnAssign` guard and re-running the full 99-file
  scan: the crash set is unchanged (still exactly the same 16 files) — the guard fixes zero of the
  current 16, because none of the 16 crash for this reason.
- **16-file crash count: re-confirmed, unchanged, root cause re-isolated.** Re-ran the full
  99-file scan (`graded=83`, `crashed=16`, identical file list to pass 1). Went one step further
  than pass 1 here: patched `visit_With` alone (leaving `visit_Try`/`visit_AnnAssign`
  unguarded) and reran — **crash count dropped to 0**. So all 16 real-world crashes in this
  codebase, both in pass 1 and now, are caused exclusively by the `with`-without-`as` construct;
  `visit_Try`'s bug and the new `visit_AnnAssign` bug are real and reproducible on synthetic
  sources (rows 5 and 14 above) but are not currently triggered by anything in `bin/*.py`. No
  count correction needed — 99/83/16 stands — but the *explanation* is now sharper: it was always
  one construct, not three, doing the damage against this specific tree.
- **Gated-set intersection.** Since the `AnnAssign` bug fires on zero of the 99 scanned files, and
  the 200-record gated set's 10 distinct `PATH:` values are a subset of those 99, intersection is
  zero by construction — no new check needed beyond confirming the subset relationship, already
  established in pass 1 item 2.4.
- **Loud or silent?** Same shape as `visit_With`/`visit_Try`: `self.visit(None)` →
  `generic_visit(None)` → `ast.iter_fields(None)` → `AttributeError` inside `_record`, which
  propagates unbuffered out of `_records`/`grade_source` (same call chain audited in pass 1 item
  2.2 — no caller catches `AttributeError`). **Loud raise, never a silent mis-grade.**

### D. Superseding fix spec (complete; supersedes pass 1's two-guard spec)
`.claude/skills/harness/bin/code_grade.py`, class `_Counter` — three guards, all the same pattern
`visit_Assert` already uses for `node.msg` (`:177`):
1. `visit_With` (`:150-156`): guard line `:153`, `self.visit(item.optional_vars)`, with
   `if item.optional_vars is not None:`.
2. `visit_Try` (`:160-171`): guard line `:165`, `self.visit(handler.type)`, with
   `if handler.type is not None:`.
3. `visit_AnnAssign` (`:89-91`): guard line `:91`, `self.visit(node.value)`, with
   `if node.value is not None:`.

No other site needs a guard — items A/B above are the exhaustive negative for every other
`visit_*` override on the module's one `ast.NodeVisitor` subclass.

Binding tests, `test-code-grade.py`, same location/style as pass 1's spec (near the existing
`check_*` grade_source cases): six assertions total, one crash-reproduction + one metric assertion
per site. **One correction to pass 1's own spec first:** pass 1 asserted the With fix should be
"metric-identical" to `with lock as _discard:` on the theory that "a bare Name target visits to
zero cost" — verified directly, that premise is **false**: `_discard` is a `Name` in `Store`
context, and `visit_Name` (`:77-79`) increments `abc_a` for exactly that context, so
`with lock as _discard:` legitimately scores `abc_a=1` against the bare form's `abc_a=0` — a real,
correct difference (an `as`-binding is a real assignment), not a bug. The Try case's identity
claim is unaffected and independently reconfirmed: `except Exception:` visits a `Name` in `Load`
context, which `visit_Name` does not count, so bare-`except:` and `except Exception:` are
genuinely metric-identical. Fixed assertions:
- With: `grade_source("def f():\n    with lock:\n        pass\n", "f.py")` must not raise, and
  after the fix must yield exactly `cyclomatic=1, cognitive=0, abc_a=0, abc_b=0, abc_c=0`
  (confirmed by direct run against the patched guard) — asserted as literal expected values, not
  as identity against an `as`-variant.
- Try: `grade_source("def f():\n    try:\n        pass\n    except:\n        pass\n", "f.py")`
  must not raise and must be metric-identical to
  `grade_source("def f():\n    try:\n        pass\n    except Exception:\n        pass\n", "f.py")`
  — confirmed identical: both `cyclomatic=2, cognitive=1, abc_a=0, abc_b=0, abc_c=1`.
- AnnAssign: `grade_source("def f():\n    x: int\n", "f.py")` must not raise and must be
  metric-identical to `grade_source("def f():\n    x: int = None\n", "f.py")` — `None` is itself a
  zero-cost `Constant`, so annotating with vs. without an assignment of a cost-free value produces
  identical metrics (confirmed by direct run: both `cyclomatic=1, cognitive=0, abc_a=1, abc_b=0,
  abc_c=0`).

Each of the three "before" sources raises `AttributeError` today (verified above); each is
expected to pass after its guard is added; reverting any one guard to unconditional reproduces
that construct's crash without affecting the other two — the standard discrimination proof.


### E. Should `grade_source` contain the failure?
**Recommendation: yes, but narrowly** — catch `AttributeError` (and, since the same
iter_fields-on-None mechanism is the only failure mode identified across this whole audit, no
broader exception class) at the single choke point, `_record()`'s call into `_Counter`, and
re-raise as a `GradeError`-style value carrying the file path and qualname, letting the CLI print
one "ungradeable: <path>::<qualname> — <original message>" line and continue grading the rest of
the file/repo rather than aborting the whole `--base/--head` run.

Trade-off, both directions:
- **For containing it:** a single unanticipated AST shape currently takes down the *entire* CLI
  invocation — for `--base/--head` mode that means zero grading output for a PR that touches 500
  functions because one of them (or one of its *pre-images*, per pass 1 item 2.3) hit an
  unguarded field, which is a worse operator experience than one function reported ungradeable.
  It also matches this feature's own stated posture in pass 1 item 2.2 ("loud raise, never a
  silent mis-grade") — containment preserves loudness (the line still prints, still fails CI) while
  removing the all-or-nothing blast radius.
- **Against containing it:** catching `AttributeError` broadly is a well-known footgun — it is the
  same exception Python raises for an *unrelated* programming mistake inside grading logic (e.g. a
  typo'd attribute access three calls deep), so a blanket `except AttributeError` around
  `_record()` would also swallow genuine internal bugs and report them as "ungradeable file" rather
  than surfacing them as the grader's own defect. The three guards in section D are the correct
  fix for the *known* cases; containment is insurance for the *next* unknown one, and insurance
  that hides a different class of bug is a net loss. If adopted, it should be scoped as tightly as
  possible (ideally the specific `iter_fields`/`_fields` `AttributeError`, not the whole class) and
  should still fail CI overall — it only changes single-function silence into partial-repo
  continuation, not into a passing grade.

This is a cycle 28 design decision, not applied here.

### Final worktree state (addendum pass)
`git -C <worktree> status --porcelain`:
```
 M .harness/harness/features/FEAT-43-code-risk-grading/feature.json
?? .harness/harness/features/FEAT-43-code-risk-grading/answers/Q11-ci-hermeticity-cycle-27.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-delta-c27.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/receipt-harness-dev-ops-2026-08-29-01-validate-ci-hermetic-c27-eng.md
?? .harness/harness/features/FEAT-43-code-risk-grading/notes/review-code-reviewer-delta-c27.md
```
Identical set to the pre-existing state recorded at the top of this file, plus this file's own
append (expected, since `qa-delta-c27.md` was already untracked) and one sibling reviewer's
artifact (`review-code-reviewer-delta-c27.md`, not written by this run, not touched by it). No
source file under `.claude/skills/harness/bin/` was edited; every probe ran against a monkey-patched
in-memory copy of `_Counter`'s methods inside throwaway scripts under `mktemp -d`, never against
the file on disk.
