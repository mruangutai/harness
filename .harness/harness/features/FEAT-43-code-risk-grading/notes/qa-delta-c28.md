# QA delta review — FEAT-43 cycle 28 (pin `baa96b7e`)

**BLUF:** The delta genuinely binds — each of the three guards, mutated alone, crashes a **named**
test in `check_optional_field_guards` (not merely a non-zero exit), and each restore is
byte-identical, proven independently in a disposable `git clone` (never the worktree). The three
literal-metric assertions are correct by my own term-by-term re-derivation from `_Counter`'s actual
code, including the two identity claims (`except:`≡`except Exception:`; bare `x: int`≡`x: int =
None`) and the one deliberate non-identity (bare `with lock:` vs `with lock as x:` differ by
`abc_a=1`, since `as x` is a `Store`-context `Name` and `visit_Name` counts exactly that). My own
99-file sweep reproduces 99/0 exactly. Delta **PASSES**. `matrix_ok: true`. No `must_fix`.

## Item 2 — per-guard mutation binding (disposable clone, never the worktree)
Clone: `git clone file://<worktree> $tmp/clone` → `rev-parse HEAD` = `baa96b7ee1cf…` (pin
confirmed). Baseline `python3 test-code-grade.py` in the clone: **exit 0**, `PASS
test-code-grade`; `sha256(code_grade.py)` = `e2fe943d…` (saved as the restore reference).

| # | guard removed | run | result |
|---|---|---|---|
| 1 | `visit_AnnAssign`/`node.value` | `python3 test-code-grade.py` | **exit 1**, traceback names `check_optional_field_guards` at `test-code-grade.py:675` (`ann_record = code_grade.grade_source("def f():\n    x: int\n", …)`), `AttributeError: 'NoneType' object has no attribute '_fields'` |
| 2 | `visit_With`/`item.optional_vars` | same | **exit 1**, names `check_optional_field_guards` at `:657` (`with_record = …`), same `AttributeError` |
| 3 | `visit_Try`/`handler.type` | same | **exit 1**, names `check_optional_field_guards` at `:662` (`try_record = …`), same `AttributeError` |

Each traceback pinpoints the exact assertion line inside the one named check function the delta
added — the crash happens building the fixture the test needs, before `check()` even runs, which is
the strongest possible binding (no chance of a silently-wrong metric slipping past — the guard's
absence is loud). After each single mutation, restored from the saved copy: `sha256` matched
`e2fe943d…` all three times, `python3 test-code-grade.py` → exit 0 again each time. `git -C
$tmp/clone status --porcelain` empty after final restore. **Worktree file was never opened for
write** — confirmed by `git -C <worktree> status --porcelain -- .claude/skills/harness/bin/` →
empty, both before and after this exercise.

## Item 3 — metric correctness, re-derived from `_Counter` term by term
`_record()` seeds `cyclomatic=1, cognitive=0, a=b=c=0`, calls `counter._visit_block(node.body)`
directly (function's own `FunctionDef` node is never visited, so it contributes nothing).

**Bare `with lock:` `(1,0,0,0,0)`:** body = `[With(items=[withitem(Name('lock',Load), None)],
[Pass])]`. `visit_With`: visits `Name('lock', Load)` → `visit_Name` only bumps `a` on `Store` ctx,
so `+0`; `optional_vars is None` → guard skips; `depth±1` no-op; `Pass` has no visitor → no-op.
No `_decision()` call anywhere → `cyclomatic` stays `1`. **Matches asserted `(1,0,0,0,0)`.**

**Bare `except:` `(2,1,0,0,1)`, vs `except Exception:` — identical:** `visit_Try`: body `Pass` →
no-op; one handler → `_decision()`: `cyclomatic 1→2`, `c 0→1`, `cognitive += 1+depth(0) = 1`,
`depth 0→1`; `a += int(name is not None) = 0`; bare case `handler.type is None` → skip; typed case
visits `Name('Exception', Load)` → `Load` ctx, `visit_Name` no-ops → **identical contribution**;
handler body `Pass` no-op; `depth -=1`. No `finalbody`/`orelse`. **Both `(2,1,0,0,1)`, confirmed
identical** — the `Load`-context claim holds exactly because `visit_Name` only increments `a` under
`ast.Store`.

**Bare `x: int` `(1,0,1,0,0)`, vs `x: int = None` — identical:** `visit_AnnAssign` only ever visits
`node.target` and (guarded) `node.value` — **`node.annotation` is never visited at all**, so `int`
costs nothing either way. `target = Name('x', Store)` → `a 0→1`. Bare: `value is None` → skip.
`= None` case: `value = Constant(None)`, not `None`-guard-skipped, visited via `generic_visit`
(no `visit_Constant` override) → no AST children → no-op. **Both `(1,0,1,0,0)`, confirmed
identical** — `None` is a zero-cost `Constant` node, distinct from Python's `None` object skipping
the guard.

**The deliberately-excluded claim, independently checked (not asserted by the tests, correctly):**
`with lock as x:` adds `visit(Name('x', Store))` → `visit_Name` **does** increment `a` under
`Store` → `abc_a = 1`, vs bare form's `abc_a = 0`. The +41 diff contains no assertion of identity
between these two — confirmed by re-reading the diff; only `with`-bare-vs-itself literal values,
`except`-identity, and `AnnAssign`-identity are asserted. Correct per the governing ruling.

No assertion is a tautology: every expected tuple is a hand-written literal, not a second call
through `grade_source`, so it cannot pass merely because both sides share a bug.

## Item 5 — scope
`git -C <worktree> diff --stat 4adb2219..baa96b7e`: exactly `code_grade.py` (+9/−… collapsed by
`diff --stat`, matches the reported +6/−3 hunk count) and `test-code-grade.py` (+41), plus this
feature's own `.harness/harness/features/…` bookkeeping (`STATE.md`, `feature.json`,
`answers/Q11-…`, `notes/qa-delta-c27.md`, ship-review artifacts) — all pre-existing cycle-27
admin/doc churn, not source. **No third `bin/` file touched.** Grepped the diff body for `B26`/`B27`
and any fail-open/containment vocabulary: no hits — both untouched, per the ruling.

## Independent headline confirmation (my own runs, same clone)
- **99-file sweep** (import `code_grade`, `grade_source` over every `bin/*.py`): `total_files=99
  graded=99 crashed=0` — **confirms** 99/0, up from 83/16.
- **`code-grade.py --base 7ccfae8d --head baa96b7e`**: exit **0**; `201` `FUNCTION` records; `12` at
  `GRADE: 2` (non-blocking `REASON REQUIRED`); `0` at `GRADE: 1`. **Confirms** 201 gated / 0
  blocking.
- **Self-grade `code-grade.py code_grade.py`**: exit 0, `53` functions, `0` below grade 4;
  `visit_AnnAssign GRADE:5 (cyc2/cog1/abc2.8)`, `visit_With GRADE:5 (cyc3/cog3/abc4.4)`,
  `visit_Try GRADE:4 (cyc4/cog4/abc8.7)` — cyclomatic bands to 5 (`4≤4`), but cognitive bands to
  4 (`4≤9`, misses the `≤3` grade-5 cutoff) and abc bands to 4 (`8.7≤20`, misses the `≤8` grade-5
  cutoff by 0.7) than cyclomatic, so `min(5,4,4)=4` — matches the orchestrator's 53/0-below-4
  claim and each per-function grade exactly.
- **Five focused suites**, each run individually in the clone: `test-code-grade.py` → exit 0
  (`PASS test-code-grade`); `test-code-grade-cli.py` → exit 0 (`PASS test-code-grade-cli`);
  `test-gate-policy.py` → exit 0 (all `ok` lines); `test-check-plan-routes.py` → exit 0 (`ALL
  PASS`); `test-validate-digest.py` → exit 0 (`ALL PASSED.`). All five **confirmed**.

## Test-matrix gate
`harness.json`: `change_type: bugfix` → requires `unit` (always) + a test matching the bug class
(`when kind: __bug_class__`). **Satisfied**: `test-code-grade.py` is the project's unit suite for
this module, and `check_optional_field_guards` exercises the *exact* three crashing constructs
named in the ruling — not a proxy. Adequacy: the assertions are not happy-path-only — they assert
literal post-fix metrics (not just "doesn't raise"), and my own mutation exercise (Item 2) confirms
each one discriminates on the precise failure mode (an unguarded `self.visit(None)` on the exact
AST shape that used to crash). `matrix_ok: true`.

## Not covered by this pass
- Class-closure enumeration (all `visit_*` overrides re-audited for other unguarded optional
  fields) and the full-file line-by-line regression comparison — owned by `Feat43DeltaCrC28`
  (code review), not duplicated here beyond the scope diff in Item 5.
- The canonical project-wide suite, any formatter/linter, `check-state.sh`, B26, B27 — explicitly
  out of scope per the dispatch and the governing ruling.
- Did not re-verify the eight previously-closed defects.
- Did not audit files outside `.claude/skills/harness/bin/` for the same unguarded-optional-field
  pattern (out of scope; the ruling's exhaustive audit already covers `_Counter`, the module's only
  `NodeVisitor` subclass).

## Final state
`git -C <worktree> status --porcelain -- .claude/skills/harness/bin/` → **empty** (quoted above,
confirmed both before and after the mutation exercise, which ran entirely inside a `git clone` under
`mktemp -d`, never in the worktree).

```yaml
VERDICT: PASS
DIGEST:
  headline: All three C28 guards independently bind to a named test failure on mutation, restores byte-identical, asserted metrics re-derived and confirmed correct (including both identities and the one deliberate non-identity), 99/0 sweep and all five focused suites reproduced exactly — delta passes.
  suite: pass
  failures: 0
  matrix_ok: true
  coverage_gaps: []
  sc_evidence: []
  must_fix: []
  severity_max: info
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-delta-c28.md
```
