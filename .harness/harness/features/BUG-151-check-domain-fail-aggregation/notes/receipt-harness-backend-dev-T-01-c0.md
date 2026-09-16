# Receipt — harness-backend-dev — T-01 (BUG-151-check-domain-fail-aggregation)

## What changed

Added to `tests/integration/test-check-domain.py` (only file touched, per scope):
- `_AggTee` (write-through capture tee; unused by T-01, scaffolding for T-02).
- `_aggregation_verdict(label, captured_text, total)` — implements D-01's
  agreement-of-zeroness predicate exactly: `bool(printed) == bool(total)` → `None`,
  else a one-line diagnostic naming label, printed count, total.
- `run_bug151_selfcheck_cases()` — six synthetic, in-memory cases (never a real
  suite run), each asserting `_aggregation_verdict`'s return.
- One line added to `main()`, immediately before `return fails + run_bug1305_cases()`:
  `fails += run_bug151_selfcheck_cases()`. Nothing else in `main()` changed; the
  false comment at the old 5207-5210 (now shifted, same text) was left untouched —
  T-02 owns its deletion.

## TDD: RED observed before GREEN

Step 1 required writing `run_bug151_selfcheck_cases()` FIRST, with
`_aggregation_verdict` and `_AggTee` **not yet defined**, and running it to observe
the failure. Command run and its exact output:

```
$ env -u HARNESS_AGENT_TYPE python3 -c "
import importlib.util as u
s = u.spec_from_file_location('tcd', 'tests/integration/test-check-domain.py')
m = u.module_from_spec(s)
s.loader.exec_module(m)
m.run_bug151_selfcheck_cases()
"
FAIL  [bug151-selfcheck] printed-fail-zero-total
      | raised NameError("name '_aggregation_verdict' is not defined")
FAIL  [bug151-selfcheck] printed-ok-zero-total
      | raised NameError("name '_aggregation_verdict' is not defined")
FAIL  [bug151-selfcheck] printed-fail-nonzero-total
      | raised NameError("name '_aggregation_verdict' is not defined")
FAIL  [bug151-selfcheck] printed-ok-nonzero-total
      | raised NameError("name '_aggregation_verdict' is not defined")
FAIL  [bug151-selfcheck] indented-fail-does-not-count
      | raised NameError("name '_aggregation_verdict' is not defined")
FAIL  [bug151-selfcheck] two-printed-one-counted-agrees-on-zeroness
      | raised NameError("name '_aggregation_verdict' is not defined")
```

All six cases failed with the observed `NameError` — production code (`_AggTee`,
`_aggregation_verdict`) was written only after this RED was observed, never before.

After adding `_AggTee` and `_aggregation_verdict`, the same call is GREEN:

```
ok    [bug151-selfcheck] printed-fail-zero-total
ok    [bug151-selfcheck] printed-ok-zero-total
ok    [bug151-selfcheck] printed-fail-nonzero-total
ok    [bug151-selfcheck] printed-ok-nonzero-total
ok    [bug151-selfcheck] indented-fail-does-not-count
ok    [bug151-selfcheck] two-printed-one-counted-agrees-on-zeroness
RETURN 0
```

## The six cases (names, per the intent's requirement to name (f) so the tolerance reads deliberate)

| case name | fixture | total | expect diagnostic |
|---|---|---|---|
| `printed-fail-zero-total` | `FAIL  x\n` | 0 | yes (a) |
| `printed-ok-zero-total` | `ok    x\n` | 0 | no (b) |
| `printed-fail-nonzero-total` | `FAIL  x\n` | 1 | no (c) |
| `printed-ok-nonzero-total` | `ok    x\n` | 1 | yes (d) |
| `indented-fail-does-not-count` | `ok    x\n      \| FAIL inside a detail line\n` | 0 | no (e) |
| `two-printed-one-counted-agrees-on-zeroness` | `FAIL  x\nFAIL  y\n` | 1 | no (f) — D-01 tolerates the 2-vs-1 count mismatch unconditionally because both sides are non-zero and therefore agree on zeroness |

No case's own `ok`/`FAIL` output ever echoes fixture text at column 0: on the
expected-agree path only `ok    [bug151-selfcheck] <name>` prints; on an
unexpected mismatch, the diagnostic string (never the raw fixture) is printed
indented inside a `      | verdict=...` detail line. Confirmed by inspection of
the GREEN run above — zero column-0 `FAIL` lines, six column-0 `ok` lines.

## No baseline measurement taken

Per the amended intent, T-01 is purely additive and takes no pre-edit baseline of
any kind (fail/ok line counts, block counts, etc.). SC-03's no-regression equality
is entirely T-02's responsibility (step 8(a), against the pinned commit
`6d969ed3`). Nothing here was transcribed toward it.

## Verify — task T-01's declared `verify:`, run verbatim from the worktree root

Command (cross-checked against `plan.yaml`'s `tasks[0].verify` for T-01 — matches
verbatim):

```
env -u HARNESS_AGENT_TYPE python3 -c "import importlib.util as u; s=u.spec_from_file_location('tcd','tests/integration/test-check-domain.py'); m=u.module_from_spec(s); s.loader.exec_module(m); assert callable(m._aggregation_verdict); assert m.run_bug151_selfcheck_cases()==0; print('PASS')"
```

Output:

```
ok    [bug151-selfcheck] printed-fail-zero-total
ok    [bug151-selfcheck] printed-ok-zero-total
ok    [bug151-selfcheck] printed-fail-nonzero-total
ok    [bug151-selfcheck] printed-ok-nonzero-total
ok    [bug151-selfcheck] indented-fail-does-not-count
ok    [bug151-selfcheck] two-printed-one-counted-agrees-on-zeroness
PASS
```

## Scope / cleanliness

`git status --porcelain` on the worktree shows only:
```
 M .harness/harness/features/BUG-151-check-domain-fail-aggregation/BRIEF.md
 M .harness/harness/features/BUG-151-check-domain-fail-aggregation/plan.yaml
 M tests/integration/test-check-domain.py
```
The two feature-dir files were already modified before this dispatch began (plan
approval / seeding by the lead), not touched by me. Only
`tests/integration/test-check-domain.py` was edited by this task. No second test
file touched. No commit made. No scratch files created or left behind.

## D-01 / D-02 compliance

- D-01 (signed): predicate is agreement-of-zeroness, `bool(printed) == bool(total)`.
  Case (f) returns `None` unconditionally on a 2-vs-1 count mismatch, per spec —
  strict equality was NOT implemented.
- D-02: untouched by this task; block discovery and `run_bug1305_cases` deletion
  are T-02's work.
