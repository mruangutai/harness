# FEAT-43 · validate-delta-c25 — QA gate on T-01's self-bar closure — PASS

**BLUF:** All four assignment items are answered by runs I performed myself. The eight resolution
cases inside `check_changed_function_resolution` are each individually observable and passing. Both
new characterization tests clear the grade-3 bar (grade 4 each) and each genuinely discriminates —
proven by two mutations distinct from the code reviewer's hash-first swap, both restored
byte-identically. All five focused suites pass individually. The delta's `change_type: logic`
requires `unit` at the floor, and that floor is met — but I found two real coverage gaps in the six
new helpers that no test would catch if regressed, confirmed by mutation. No send-back was spent in
this run (solo QA pass, no team members to send back to).

## Item 1 — the eight resolution cases, individually

`check_changed_function_resolution`'s aggregate `check()` calls only print on mismatch, so I
instrumented it (`/tmp/qa_instrument_case1.py`, imports `test-code-grade.py` via
`importlib.util`, monkeypatches `check` to also print on success, then calls
`check_changed_function_resolution()` directly — no source file touched):

```
$ python3 qa_instrument_case1.py
PASS gated set: {'newly_added', 'worsened'}
PASS gated source paths: {'main.py'}
PASS informational source paths: {'relocated.py', 'main.py'}
PASS improved absent from gated: False
PASS renamed absent from gated: False
PASS reformatted absent from gated: False
PASS signature change absent from gated: False
PASS moved file absent from gated: False
PASS untouched grade one absent from gated: False
PASS untouched grade one informational: True
TOTAL FAILURES: 0
EXIT:0
```

All eight cases are present and individually pass: **worsened** and **newly_added** are the two
names covered by the `gated set` assertion (both required present); **improved**, **renamed_new**
(labeled `renamed absent from gated`), **reformatted**, **signature_changed**, and **moved** are
each individually asserted absent from gated; **already_bad** is asserted both absent from gated
and present in informational (two named assertions).

## Item 2 — new test integrity and discrimination

**Grade measurement** (`code-grade.py test-code-grade.py`, EXIT 0):

| qualname | cyc | cog | abc | grade | bar |
|---|---|---|---|---|---|
| `check_pre_image_resolution_priority` | 1 | 0 | 14.4 | **4** | 3 |
| `check_base_source_rename_fallback` | 1 | 0 | 16.1 | **4** | 3 |

Both clear the grade-3 test-file bar with margin.

**Discrimination mutation 1 — `_resolve_base_source`'s `old_path` fallback dropped** (distinct
target from the reviewer's mutation, which targeted `_resolve_pre_image` only):

```
$ md5sum code_grade.py test-code-grade.py
c5db829f96b3b8dc8d144a1466392e4d  code_grade.py
a25e2fcd0733aca406b358653d1fa416  test-code-grade.py
```
Edited `_resolve_base_source` to drop the `old_path` fallback entirely:
```python
def _resolve_base_source(repo_root, base_oid, path, old_path):
    base_source = _git_show(repo_root, base_oid, path)
    return base_source
```
```
$ python3 test-code-grade.py
FAIL gated set: expected {'newly_added', 'worsened'}, got {'newly_added', 'moved', 'worsened'}
FAIL gated source paths: expected {'main.py'}, got {'relocated.py', 'main.py'}
FAIL informational source paths: expected {'relocated.py', 'main.py'}, got {'main.py'}
FAIL moved file absent from gated: expected False, got True
FAIL rename resolves pre-image via old_path: expected 'def kept():\n    return 1\n', got None
5 failures
EXIT:1
```
The named case **"rename resolves pre-image via old_path"** (inside
`check_base_source_rename_fallback`) fails by name, alongside the pre-existing `moved` case in
`check_changed_function_resolution` — both seams catch the regression independently. Restored:
```
$ git checkout -- code_grade.py
$ md5sum code_grade.py
c5db829f96b3b8dc8d144a1466392e4d   # identical to pre-mutation
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
```

**Discrimination mutation 2 — `_resolve_pre_image` made to ignore `before_hashes` entirely**
(distinct from the reviewer's hash-first-order swap; this makes the hash path dead code):

```python
def _resolve_pre_image(record, before_names, before_hashes, head_hashes):
    before = before_names.get(record.qualname)
    if before is not None:
        return before
    return None
```
```
$ python3 test-code-grade.py
FAIL gated set: expected {'worsened', 'newly_added'}, got {'newly_added', 'renamed_new', 'worsened'}
FAIL renamed absent from gated: expected False, got True
FAIL hash match wins when name absent: expected True, got False
3 failures
EXIT:1
```
The named case **"hash match wins when name absent"** (inside
`check_pre_image_resolution_priority`) fails by name, alongside `renamed_new`'s pre-existing
absence assertion — confirms the hash-fallback path is load-bearing, not dead. Restored:
```
$ git checkout -- code_grade.py
$ md5sum code_grade.py
c5db829f96b3b8dc8d144a1466392e4d   # identical to pre-mutation
$ python3 test-code-grade.py
PASS test-code-grade
EXIT:0
$ git -C <worktree> status --porcelain -- .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/test-code-grade.py
                                            # (empty)
```

**Guard integrity — does `check_self_grading` hold `test-code-grade.py` itself to the grade-3 bar?**
Not unconditionally: `test-code-grade.py` is in `SELF_GRADED_FILES` and graded at bar 3 like any
test file, but `SELF_GRADING_ALLOWLIST` carries two **pre-existing** entries for it —
`check_commit_resolution` and `check_changed_function_resolution`, both grade 2 (SC-15 items 11/12,
reasoned at an earlier review, untouched by this delta's diff). Confirmed directly:
```
$ python3 code-grade.py test-code-grade.py > /tmp/tcg_grade.txt
$ python3 -c "... sort by grade ..."
lowest 5: [(2, 'check_changed_function_resolution', bar=3), (2, 'check_commit_resolution', bar=3), (3, '_check_self_graded_file', bar=3), ...]
total functions: 21
FAIL RESULT count: 2
```
The two grade-2 functions are exactly the two allowlisted, reasoned entries — the guard's stale-entry
assertion (`check_self_grading`, exercised inside every green `test-code-grade.py` run above) would
fail loudly if either entry's grade drifted or its qualname vanished; it did not fire, so the
allowlist is current. Nothing new introduced by this delta needed an exemption — the delta's own two
new tests are grade 4, well clear of the bar.

## Item 3 — the five focused suites, individually

```
$ python3 test-code-grade.py            → PASS test-code-grade            EXIT:0
$ python3 test-code-grade-cli.py        → PASS test-code-grade-cli        EXIT:0
$ python3 test-gate-policy.py           → 27 ok lines, 0 FAIL              EXIT:0
$ python3 test-check-plan-routes.py     → ALL PASS                        EXIT:0
$ python3 test-validate-digest.py       → ALL PASSED (66+14+24+2+18 cases) EXIT:0
```

## Item 4 — test-matrix gate on this delta

`d2e3b5eb..e12d53b1` is a pure internal refactor of two graded functions in `code_grade.py`,
matching `plan.yaml` T-01/T-02's declared `change_type: logic`. `.harness/harness.json`'s
`test_matrix.logic` requires `always: [unit]` — a floor with no conditional `when` clause for this
change type. `test_kinds.unit.detect` matches
`.claude/skills/harness/bin/test-*.py`, which covers `test-code-grade.py`.

**State: satisfied.** A named unit-kind test exercises this exact change —
`check_changed_function_resolution` (pre-existing, unchanged by the diff, still exercises the
refactored `gated_set` end-to-end per Item 1) plus the two new helper-level unit tests
(`check_pre_image_resolution_priority`, `check_base_source_rename_fallback`) added by this delta.
The characterization expectation for a behaviour-preserving refactor — coverage of the seam that
existed before the refactor and still holds after — **is met**: the seven-case-plus-`already_bad`
fixture in `check_changed_function_resolution` predates this delta and still passes unmodified
against the decomposed `gated_set`.

**Coverage gaps found — two of the six new helpers, confirmed by mutation, not asserted:**

1. **`_qualname`'s prefix-joining branch** (the nested/class-qualname path used inside
   `_body_hashes.collect`'s recursion) is never exercised. Every `gated_set`/`_body_hashes` fixture
   in the test file uses only flat, top-level functions — no nested function or method ever flows
   through `_body_hashes`. Proof: mutated `_qualname` to `return name` (ignore `prefix` entirely) —
   ```
   $ python3 test-code-grade.py
   PASS test-code-grade
   EXIT:0
   ```
   Full suite still green with the join silently dropped. Restored (`git checkout --`, md5
   `c5db829f96b3b8dc8d144a1466392e4d` confirmed identical).

2. **`_strip_docstring`'s stripping branch** (removing a real docstring before hashing, so a
   docstring-only edit doesn't defeat rename/hash matching) is never exercised — no fixture function
   in the file carries a docstring. Proof: mutated `_strip_docstring` to a no-op (`return body`
   unconditionally) —
   ```
   $ python3 test-code-grade.py
   PASS test-code-grade
   EXIT:0
   $ python3 code-grade.py code_grade.py
   EXIT:0, 0 RESULT: FAIL
   ```
   Full suite and self-grade both still green with docstring-stripping silently disabled. Restored
   (`git checkout --`, md5 confirmed identical).

Both mutations were restored immediately after observation; final state re-confirmed clean:
```
$ git status --porcelain -- .claude/skills/harness/bin/code_grade.py .claude/skills/harness/bin/test-code-grade.py
                                            # (empty)
```

`_gate_file_records` has no *direct* unit test (only exercised transitively through `gated_set`'s
integration-level fixture) — I do not count this as a gap, since it is a thin per-file dispatcher
and its two branches (gate / don't-gate) are both exercised by the existing fixture's `worsened`
and `improved` cases respectively.

## What this delta QA did NOT cover

This is a **delta gate**, not a re-gate. Per the assignment's non-goals, I did not re-verify the five
blockers already closed in `runs/validate-final-panel-c21-validator/digest.md` and
`runs/validate-delta-c23-validator/digest.md` (T-02 through T-10, D-11, the bulk of the SC set, the
CLI, `gate_policy.py`, `validate-digest.py`'s wiring, the glossary, and the skill's worked examples) —
I relied on their prior verdicts and the code reviewer's re-confirmation in this same cycle, since
this delta's diff touches only `code_grade.py` and `test-code-grade.py`. I did not re-run the
canonical/project-wide suite or `check-state.sh` (excluded by the assignment; the orchestrator runs
those once, after this gate). I did not re-verify the 12-demand `REASON REQUIRED` SC-15 set or the
195-record/12-demand gated-output measurement — the code reviewer already reproduced both
independently in this run and the assignment says explicitly to build on that, not repeat it. SC-11's
UAT is untouched (`verify: uat`, out of scope, not yet judged per the operator's Q9 ruling). I did
not review the two `chore:` housekeeping commits (`ea61b5e`, `f3b31d8`) beyond what the code reviewer
already confirmed (`git show --stat`, no source touched). The two coverage gaps I found (`_qualname`
nesting, `_strip_docstring` stripping) are advisory findings against helpers this delta introduced —
they do not block the gate because the matrix's floor (`unit`, satisfied) does not require
exhaustive branch coverage of every internal helper, but they are real and I would not want a
successor to read "suite: pass" as "every line is proven."

```yaml
VERDICT: PASS
DIGEST:
  headline: T-01's self-bar closure is behaviourally sound — all eight resolution cases individually verified, both new characterization tests clear the grade-3 bar and discriminate under two mutations distinct from the code reviewer's, all five focused suites pass, and the unit floor for change_type logic is met; two real coverage gaps found in untested helper branches, non-blocking
  suite: pass
  failures: 0
  matrix_ok: true
  coverage_gaps:
    - "_qualname's prefix-joining (nested/class qualname) branch is never exercised through _body_hashes/gated_set — every fixture uses flat top-level functions only; confirmed by mutation (return name unconditionally) still passing the full suite"
    - "_strip_docstring's stripping branch is never exercised — no fixture function carries a docstring; confirmed by mutation (no-op passthrough) still passing the full suite and the self-grade"
  kinds:
    - { kind: unit, state: satisfied, cmd: "python3 .claude/skills/harness/bin/test-code-grade.py", named_tests: 3 }
  sc_evidence: []
  open_questions: []
  files_touched: []
  expertise_update: []
artifact: .harness/harness/features/FEAT-43-code-risk-grading/notes/qa-validate-delta-c25.md
```
