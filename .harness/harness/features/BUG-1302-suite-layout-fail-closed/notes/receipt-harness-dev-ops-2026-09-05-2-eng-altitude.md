# ALTITUDE angle — BUG-1302 build diff (pre-review_sha) — receipt

BLUF: no findings. The entire scoped diff (`tests/unit/test-suite-layout.py`,
`tests/integration/test-run-unit-tests-layout.py` against HEAD) decomposes into exactly the four
items the dispatch already names as settled/approved main-session-direct work under DEC-174 —
B-4, B-5, B-6, B-8, B-14 — and none of them raises an altitude question the plan-draft ALTITUDE
pass (`notes/receipt-harness-dev-ops-2026-09-05-1-eng-altitude.md`, item 2) didn't already settle.
Checked for a fifth, unaccounted-for change; found none.

## Diff → settled-item mapping (line-by-line accounting)

- `test-run-unit-tests-layout.py:90` (`"PASS test-unit.py"` → `"PASS test-"`) = **B-8**, the generic
  sentinel prefix.
- `test-suite-layout.py` `import ast` / `SELF_AST` / `_self_fn` (lines 2, 14-19) = shared
  infrastructure the B-4/B-5/B-6 structural pins need; not a separate item.
- `_is_inside_tests` comparison narrowed from `in (".", "..")` to `== "."`, plus `B5_CORPUS` and the
  `b5_dotdot_count` structural check (lines ~448-482, 108-137 in the earlier compact view) = **B-5**.
- `_literal_key_present`'s dropped tautological conjunct, `B4_CORPUS`, and the
  `b4_any_count`/`b4_wildcard_count` structural check (lines ~494-534) = **B-4**.
- Case-11 `INAPPLICABLE` print → `check(..., False, ...)` fail-closed conversion, the
  `CORPUS_BLIND_KINDS` reachability probe, and the `b6_*` structural check on the `control_candidate`
  branch (lines ~641-675) = **B-6**.
- `_violations_callers`'s `try/except (OSError, UnicodeDecodeError)` → named
  `unreadable tracked source <path>: <ErrorType>` entries, plus the new `td` fixture exercising a
  deleted and a binary tracked file (lines ~160-190, 651-671) = **B-14**.

No sixth bucket exists: every hunk in the diff is one of the five labels above (B-4/B-5/B-6/B-8/B-14
per the dispatch's naming — B-6 covers two hunks, the fail-closed conversion and its structural
pin).

## Altitude check performed anyway (not re-litigating settled correctness)

The one altitude-shaped question the settled list doesn't pre-empt is whether `_self_fn`/`SELF_AST`
should live somewhere other than this test file — a shared fixture module, given `layout_fixtures.py`
already exists and is imported by two other test files (`test-check-state.py`,
`test-layout-migration.py`). Re-confirmed against the current build (not just the plan draft):
`_is_inside_tests` and `_literal_key_present` still exist only inside `test-suite-layout.py`
(`grep`-confirmed absent from `suite_layout.py`), so the structural pins are a test file asserting
invariants about its own private helpers, not a capability that belongs in the module under test.
BUG-1302's file-lock constraint (only these two test files are writable) also forecloses a
third-file shared home. Same conclusion as the plan-draft pass: **leave**, not flaggable, not a
finding.

## Confirmations

Read-only: no edits, no formatter, no test suite run. Diff taken via
`git diff -U6 HEAD -- tests/unit/test-suite-layout.py tests/integration/test-run-unit-tests-layout.py`
in the BUG-1302 worktree; full file contents cross-checked with `read`/`grep` against
`.claude/skills/harness/bin/suite_layout.py` and the four sibling test files noted above.
