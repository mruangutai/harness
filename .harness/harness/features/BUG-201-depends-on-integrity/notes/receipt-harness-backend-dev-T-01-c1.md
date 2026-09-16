# Receipt — harness-backend-dev — T-01 — c1

## Task

BUG-201 T-01: write the failing unit test for the `depends_on` reference rule.
File created: `tests/unit/test-plan-depends-on.py` (new). No other file touched.

`verify:` cross-checked against plan.yaml's T-01 entry (line 307-308): exact match
with the dispatch — `python3 tests/unit/test-plan-depends-on.py`. No mismatch.

## Run

```
env -u HARNESS_AGENT_TYPE python3 tests/unit/test-plan-depends-on.py
```

Exit code: `1`

## Literal FAIL lines observed

```
  FAIL a depends_on entry naming an absent task id is rejected, naming both ids
      | no exception raised
  FAIL two dangling edges in one document raise ONE exception naming BOTH (D-02)
      | no exception raised
  FAIL a bare-string depends_on is rejected, naming the task id and the field, with no single-character phantom id from iterating the string
      | no exception raised
  FAIL 6c: integer ids with a genuinely absent integer dependency (3) is rejected
      | no exception raised
```

## Literal final line

```
4 of 10 FAILING.
```

## Case-by-case disposition (matches the spec's predicted asymmetry exactly)

- Case 1 (single dangling edge, T-02→T-99) — **FAIL**. Correct: `validate_plan_doc`
  has no `depends_on` rule yet, so nothing is rejected.
- Case 2 (paired allow, T-02→T-01) — **ok**. Correct: no rule exists to reject
  it, and none should — T-01 is present. This is the case that would catch a
  deny-everything stand-in for the missing rule.
- Case 3 (two dangling edges, T-98 + T-99) — **FAIL**. Correct: same reason as
  case 1; also proves D-02 (report all missing edges in one exception) is unmet.
- Case 4 (absent / `null` / `[]`) — **ok, ok, ok**. Correct: none of the three
  shapes carries a dangling reference, so today's absence of a rule and
  tomorrow's presence of one agree.
- Case 5 (bare string `"T-01"` instead of a list) — **FAIL**. Correct: no
  non-list-shape check exists yet either.
- Case 6a (int id `1`, referenced as `"1"`) — **ok**. Correct: no rule exists to
  reject it, and a correct str-coercing rule would not reject it either.
- Case 6b (string id `"1"`, referenced as `1`) — **ok**. Correct: same reasoning,
  mirrored.
- Case 6c (int ids, referencing absent `3`) — **FAIL**. Correct: genuinely
  dangling edge, no rule exists yet to catch it.

Observed FAIL set: exactly `{1, 3, 5, 6c}`, matching the task's predicted red
exactly. The file imported cleanly (no `ModuleNotFoundError`), every one of the
10 checks was reached and printed a distinct `ok`/`FAIL` line (no
`ImportError`/fixture crash), so this is a genuine red, not a broken test.

## Notes

- `git status --porcelain` in the worktree also shows
  `.harness/harness/features/BUG-201-depends-on-integrity/plan.yaml` modified —
  not touched by this task; reported as observed per O-06, not investigated.
- `harness_yaml.py` was not opened for editing (T-03's task, dispatched after
  this one); only imported read-only to call `validate_plan_doc` directly, as
  instructed.
