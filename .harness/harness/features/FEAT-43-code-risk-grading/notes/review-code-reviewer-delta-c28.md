# Code review — FEAT-43 cycle 28 delta (crash-class guards)

**BLUF: PASS.** The class is closed, not just the three instances — my own 30-construct probe
against every ASDL-optional field `_Counter` can reach finds zero remaining unguarded
dereferences. The three guards are exact copies of `visit_Assert`'s existing pattern, each is
independently load-bearing (mutating any one back to unconditional reproduces the crash), the
99-file sweep and the base/head gate both confirm the orchestrator's numbers, and the destructive
`git checkout` left no collateral damage — the hand-reapplied file is byte-identical to the
intended fix outside the three hunks. Two advisory items below, neither gating.

## Item 1 — is the class closed? (highest-value part of this review)

Mechanism confirmed by reading `_Counter` in full (`code_grade.py:55-220`, the module's one
`ast.NodeVisitor` subclass): `generic_visit` guards every field with `isinstance(value, AST)`
(and per-item for lists), so only a **custom `visit_*` override calling `self.visit(node.<field>)`
directly** can crash on `None`. Enumeration table, each row backed by an executed probe
(`grade_source` in a `mktemp -d` copy of the review-pin file, not the worktree):

| Field | Reached by `_Counter`? | Status |
|---|---|---|
| `Return.value` | not overridden → `generic_visit` | safe (probed clean) |
| `Raise.exc` / `.cause` | not overridden → `generic_visit` | safe (probed clean, both implicit and explicit `from`) |
| `Yield.value` / `YieldFrom` | not overridden → `generic_visit` | safe (probed clean) |
| `Starred` | not overridden → `generic_visit` | safe (probed clean) |
| `Slice.lower/upper/step` | not overridden → `generic_visit` | safe (probed clean, full and partial slice) |
| `Dict.keys` (`{**a}` None entry) | not overridden → `generic_visit` (per-item guard) | safe (probed clean) |
| comprehension `.ifs` | custom `_visit_comprehension`, but `ifs` is a required list, items never `None` | safe (probed clean, empty and populated) |
| `arguments` defaults/vararg/kwarg | signature never visited at all (`visit_FunctionDef` doesn't recurse into `node.args`) | unreached (probed clean) |
| `alias.asname` | not overridden; `visit_Import`/`ImportFrom` only count `len(node.names)` | safe (probed clean) |
| `keyword.arg` | not overridden → `generic_visit` on `Call` (arg is a string, skipped; value is required, visited) | safe (probed clean) |
| `Global`/`Nonlocal` names | not overridden → `generic_visit` (`identifier*`, strings not AST) | safe (probed clean) |
| `Match` patterns / `match_case.guard` | custom `visit_Match` visits `subject`+`case.body` only — pattern/guard never touched | safe from crash, but a known separate undercount gap (out of scope, matches QA's prior finding) |
| `ExceptHandler.name` | accessed via `handler.name is not None`, never `self.visit`ed | always safe (not a dispatch call) |
| `FunctionDef.returns` | signature never visited | unreached (probed clean) |
| `AnnAssign.value` | **guarded this cycle** (`:91`) | fixed |
| `withitem.optional_vars` | **guarded this cycle** (`:153`) | fixed |
| `ExceptHandler.type` | **guarded this cycle** (`:165`) | fixed |
| `Assert.msg` | guarded pre-existing (`:177`, the reference pattern) | already correct |

30 constructs run, `python3 probe.py` → **exit 0, 30/30 CLEAN**, zero raises at the review pin.
Cross-check: the same 3 constructs run against the **prior pin** (`4adb2219`) all raise
`AttributeError: 'NoneType' object has no attribute '_fields'` (exit 0, script completes,
raises captured) — confirms the fix is what changed the outcome, not an artifact of my harness.
**Verdict: the class is closed at this pin**, not merely three instances patched.

**Mutation-back, all three sites independently discriminating:** reverted each guard to
unconditional in a throwaway copy and re-probed — `MUTATION-REPRODUCES-CRASH` for `visit_With`,
`visit_Try`, `visit_AnnAssign`, each in isolation, `AttributeError: 'NoneType' object has no
attribute '_fields'`, exit 0 (script completed, exception caught and printed).

**99-file sweep, my own run:** `python3 sweep.py` over `.claude/skills/harness/bin/*.py` at the
review pin → `total=99 graded=99 crashed=0`, **exit 0**. Matches the orchestrator's 99/0 exactly
(was 83/16 at the prior pin).

## Item 4 — no collateral damage from the mid-run `git checkout`

- `git diff 4adb2219..baa96b7e -- code_grade.py` and an independent whole-file `diff -u` against
  `git show 4adb2219:...code_grade.py` (**exit 1**, meaning "differences found" — the only
  differences are the three intended hunks, confirmed line-for-line): **identical outside the
  three guards.**
- `test-code-grade.py` whole-file diff: `grep -c "^-"` against the diff = **1** (only the `---`
  header line — zero actual removed lines). Purely additive: one new `check_optional_field_guards`
  function plus its registration in `checks`.
- Six cycle-25 helpers confirmed present, bodies untouched (no hunks near them in either diff):
  `_qualname` (`:346`), `_strip_docstring` (`:350`), `_hash_body` (`:357`), `_resolve_base_source`
  (`:387`), `_resolve_pre_image` (`:394`), `_gate_file_records` (`:402`).
- `python3 test-code-grade.py` → **exit 0**, `PASS test-code-grade`.

## Item 5 — scope

`git diff --stat 4adb2219..baa96b7e` (**exit 0**): two `bin/` files (`code_grade.py` +9/−3,
`test-code-grade.py` +41) plus feature-bookkeeping-only files under
`.harness/harness/features/FEAT-43-code-risk-grading/` (STATE.md, feature.json, notes/answers
markdown/html) — **no third `bin/` file, no B26/B27 vocabulary** anywhere in the diff body (both
are tracked only as backlog rows in `ship-review-c27.md`, never touched by this delta).
`git status --porcelain -- .claude/skills/harness/bin` → **empty**, confirmed clean.

> **Corrected by Send-back 1 below: the `+9/−3` figure in this paragraph was wrong. The measured
> `code_grade.py` delta is `+6/−3`. See the dated section for the verbatim line-by-line
> accounting.**

## Two-stage review, +6/−3 source and +41 test lines

**Stage 1 (spec compliance vs. Q12):** exactly the three sites the ruling names, no more, no
less. Guards are textually the same shape as `visit_Assert`'s (`if X is not None: self.visit(X)`)
— no second convention introduced. Tests bind literal metrics, not just absence-of-crash, and
independently re-verified by me: `with` → `(cyc,cog,a,b,c)=(1,0,0,0,0)`; bare `except:` vs
`except Exception:` → identical `(2,1,0,0,1)`; bare `x: int` vs `x: int = None` → identical
`(1,0,1,0,0)`; and — correctly, per the corrected spec — the test does **not** assert `with lock:`
identical to `with lock as x:` (I confirmed they differ: `abc_a` 0 vs 1, `as` being a `Store`-
context `Name`). No omission, no mismatch, no scope creep.

**Stage 2 (quality):** no fail-open introduced — a guard that skips a field which is genuinely
absent is correct behavior, not error-suppression; nothing is silently swallowed since the
guarded branch does no counting for a field that doesn't exist. No dead code, no copy-paste
divergence from the reference pattern. The test's failure mode on regression is a crash-out-of-
`main()` (no per-check `try/except` in this harness) rather than a clean "N failures" line, but
that is the pre-existing harness convention (not introduced by this diff) and I confirmed it does
produce a loud, attributable, non-zero exit on regression — not a silent pass.

## Advisory (a) — `visit_Try` at grade 4, zero headroom

Confirmed by my own self-grade run (`code-grade.py code_grade.py`, exit 0): 53 functions, grade
distribution `{4: 12, 5: 41}`, zero below 4; `visit_AnnAssign` grade 5, `visit_With` grade 5,
`visit_Try` **grade 4** exactly `cyclomatic=4, cognitive=4, abc=8.7`, driver `cognitive+abc`,
`BAR: 4`, `RESULT: PASS`. Matches the orchestrator's figures exactly. **Recommend a backlog row**,
not a blocker: `visit_Try` is now equal to its own pass bar rather than above it, and it is the
one method in `_Counter` most likely to gain another branch (it's the crash-class's own repair
site). A low-severity tracking note is warranted so the next touch to `visit_Try` doesn't quietly
fail production self-grading.

## Advisory (b) — generic `visit()` override instead of three call-site guards

Agree it is the architecturally deeper fix — one choke point instead of three duplicated
invariants, and per this project's own codebase-design vocabulary, three sites repeating the same
guard is exactly the "pattern omitted twice" signal that a fourth site could omit it again.
**But it is not a strictly better trade**, and the difference matters: a per-callsite `if field is
not None:` only tolerates `None` on the *specific fields the ASDL declares optional* — it cannot
mask a bug where a required field is unexpectedly `None`, because there's no guard on required
fields anywhere. A generic `visit(self, node): if node is not None: super().visit(node)` override
would silently no-op on **any** `None` passed to `.visit(...)`, from *any* current or future
override — including a case where a required field is `None` because of a genuine bug elsewhere
(a typo'd attribute, a malformed synthetic AST) rather than legitimate ASDL optionality. That is
the same shape of risk QA's own doc flags for a blanket `except AttributeError` (section E of
`notes/qa-delta-c27.md`): it converts a *specific, diagnosed* class of null into a *general*
tolerance for null, trading one recurring bug for reduced ability to detect a different one later.
**Recommend backlog, not this cycle**: it is a real simplification worth doing once with its
trade-off written down (as QA already wrote for the `except AttributeError` alternative), not a
same-cycle change to a diff that Q12 scoped to exactly three guards.

## Not covered

Did not review B26 (fail-open) or B27 (containment) — explicitly out of scope per Q12. Did not
re-verify the eight previously-closed defects or the canonical project-wide suite. Did not audit
any file outside the two named `bin/` files. Did not run the full-suite/CI pipeline. Did not
independently re-derive the metric spec's math beyond the constructs this delta touches (deferred
to QaC28 per the stated division of labour) — my metric checks above are limited to confirming the
literal values the new test asserts, not re-deriving the ABC/cyclomatic/cognitive formulas from
scratch.

## Final state

`git -C <worktree> status --porcelain -- .claude/skills/harness/bin` → **empty** (quoted above).
All scratch mutations (probe scripts, guard-reversion mutations, prior-pin comparisons) were made
in `mktemp -d` throwaway copies, never in the worktree.

## Send-back 1 — line-level accounting of `code_grade.py`

**2026-08-30.** Dispatched to resolve a discrepancy: this artifact's own Item 5 above stated
`code_grade.py` `+9/−3`; the orchestrator's contract states `+6/−3`. Re-measured from scratch,
independent of both prior claims.

### 1. `--numstat`, exact command and output

```
$ git -C <worktree> diff --numstat 4adb2219954aa132b1e8450cdd9e571dbedba309 baa96b7ee1cfbc7fcbea8873692cc91751a0c171 -- .claude/skills/harness/bin/code_grade.py
6	3	.claude/skills/harness/bin/code_grade.py
```
Exit status: **0**.

**The `+9/−3` figure in this artifact's Item 5 is wrong. The true, measured figure is `+6/−3`,
matching the orchestrator's contract exactly.** I do not have a working hypothesis for how my
original count was produced beyond mis-tallying at the time (possibly conflating the
`test-code-grade.py` `+41` and `code_grade.py` `+9/−3` figures with a stray recount, or catching
an earlier in-flight state before the `git checkout` recovery mentioned in Item 4 stabilized this
file); the worktree today shows no trace of any larger diff, and `git status --porcelain` for this
path is clean (below), so there is no live discrepancy to explain away — only a stale number in my
own prior write-up, now corrected.

### 2. `-U0` diff, every `+`/`−` line verbatim

```
$ git -C <worktree> diff -U0 4adb2219954aa132b1e8450cdd9e571dbedba309 baa96b7ee1cfbc7fcbea8873692cc91751a0c171 -- .claude/skills/harness/bin/code_grade.py
```

```diff
@@ -91 +91,2 @@ class _Counter(ast.NodeVisitor):
-        self.visit(node.value)
+        if node.value is not None:
+            self.visit(node.value)
@@ -153 +154,2 @@ class _Counter(ast.NodeVisitor):
-            self.visit(item.optional_vars)
+            if item.optional_vars is not None:
+                self.visit(item.optional_vars)
@@ -165 +167,2 @@ class _Counter(ast.NodeVisitor):
-            self.visit(handler.type)
+            if handler.type is not None:
+                self.visit(handler.type)
```
Exit status: **0**.

Count check: 3 minus-lines, 6 plus-lines. Matches `--numstat`'s `6 3` exactly. **There is no ninth
added line anywhere in this diff** — the `+9` in my prior Item 5 does not correspond to any line
that actually exists in the repository at either pin.

### 3. Per-line classification

| # | Line | Hunk (source `visit_*`) | Part of a guard? | Live or inert |
|---|---|---|---|---|
| −1 | `        self.visit(node.value)` | `visit_AnnAssign` (`@@ -91`) | yes — the unconditional call the guard replaces | live (removed) |
| +1 | `        if node.value is not None:` | `visit_AnnAssign` | yes — guard condition | live (added) |
| +2 | `            self.visit(node.value)` | `visit_AnnAssign` | yes — same call, re-indented under the guard | live (added, but same call as removed line, now conditional) |
| −2 | `            self.visit(item.optional_vars)` | `visit_With` (`@@ -153`) | yes | live (removed) |
| +3 | `            if item.optional_vars is not None:` | `visit_With` | yes — guard condition | live (added) |
| +4 | `                self.visit(item.optional_vars)` | `visit_With` | yes — same call, re-indented | live (added, but same call as removed line, now conditional) |
| −3 | `            self.visit(handler.type)` | `visit_Try` (`@@ -165`) | yes | live (removed) |
| +5 | `            if handler.type is not None:` | `visit_Try` | yes — guard condition | live (added) |
| +6 | `                self.visit(handler.type)` | `visit_Try` | yes — same call, re-indented | live (added, but same call as removed line, now conditional) |

**All 6 added lines and all 3 removed lines belong to exactly one of the three named guards.
There is no non-guard line in this diff — none added, none removed.** No blank lines, no
whitespace-only changes, no unrelated statements. `CrashClassSpacingC28` (the sibling suspected of
a spacing change) left no trace in this file's diff at this pin: either its output was not
included in `baa96b7e`, or it produced no change to `code_grade.py` specifically. I did not
investigate further since the diff itself is dispositive — there is nothing left to attribute.

### 4. Scope-violation assessment

No finding. There is no non-guard change, live or inert, to classify as churn — the diff is
precisely three `if … is not None:` guards and nothing else, at the granularity of individual
lines, not just net counts. Q12's no-bundling instruction is honoured exactly at the line level,
not merely at the file-count or hunk-count level.

### 5. Function-body / self-grade re-confirmation

Every added and removed line sits inside one of the three guarded functions' bodies by
construction (that's what makes them guards), but since none of the 9 lines is *extraneous* to a
guard, there is no separate "non-guard line inside a function body" to check for a grade-shifting
side effect — the question in the dispatch is moot for this diff (it presupposes a non-guard line
exists; none does).

Re-ran the self-grade once, per the CLI wrapper (`code_grade.py` itself has no `__main__`; the
executable entrypoint is the co-located `code-grade.py`):

```
$ python3 <worktree>/.claude/skills/harness/bin/code-grade.py <worktree>/.claude/skills/harness/bin/code_grade.py
```
Relevant record:
```
QUALNAME: _Counter.visit_Try
CYCLOMATIC: 4
COGNITIVE: 4 (Sonar-style approximation)
ABC: 8.7
GRADE: 4
DRIVER: cognitive+abc
BAR: 4
RESULT: PASS
```
Full run: 53 functions, `PASSING: 53`, exit status **0**. `visit_Try` grades exactly
`cyclomatic=4, cognitive=4, abc=8.7 → GRADE 4`, identical to the figure already recorded in
Advisory (a) above. No function graded below 4; nothing dropped.

### Final state (re-confirmed)

```
$ git -C <worktree> status --porcelain -- .claude/skills/harness/bin/
```
(empty output) Exit status: **0**.

### Verdict

- **`+6/−3` is the correct figure for `code_grade.py`.** The orchestrator's contract is right;
  this artifact's earlier Item 5 (`+9/−3`) was a measurement error in my own prior write-up, now
  corrected here — it was not a discrepancy in the code or in the worktree.
- **Q12's no-bundling instruction is honoured at the line level**, not just at the file/hunk
  level: all 9 changed lines (6 added, 3 removed) belong to exactly one of the three named guards;
  zero non-guard lines, live or inert, exist in this diff.
- No new finding. `must_fix: []`, `severity_max: n/a` for this send-back — it resolves an
  artifact-accuracy question, not a code defect; the code itself remains PASS per the original
  Stage 1/Stage 2 review above.
</content>
