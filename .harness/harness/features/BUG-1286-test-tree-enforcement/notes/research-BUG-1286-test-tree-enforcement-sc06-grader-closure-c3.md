# SC-06 clause A now has a grader — BUG-1286, plan phase, fix cycle 3

**Closed, and the closure is measured rather than argued.** The cycle-2 goal-check's single surviving
gap — SC-06's leading "produces no violations" clause graded over a fixture that deliberately plants a
rogue — is closed by an exact-equality assertion inside T-01 case 1, with the registry finding that
would have made it unsatisfiable named and neutralized. No new fixture, no coverage loss, no split.
Both approvals remain `pending`; no implementation begun.

## What changed — three edits, nothing else

| File | Change |
|---|---|
| `plan.yaml` T-01 `intent:` | case 1 only, via `plan-merge.py amend` (compare-and-swap on `7c116175…`). Case 1 now spans `plan.yaml:185-216`; the new text is `plan.yaml:196-216` |
| `BRIEF.md` SC-06 | rewritten to state the observable and its failure mode (`BRIEF.md:77-92`); `verify: automated  evidence: unit` kept |
| `notes/research-…-goalcheck-plan-c2.md` | dated append at `:133-176`; body, verdict, gap table and "Surviving gaps" untouched |

## The satisfiability problem, and the measurement

The exact-equality assertion is unsatisfiable as case 1 stood. A faithful throwaway prototype of the
specified clauses, run against case 1's exact fixture, returned:

- **unrebound: 2 findings** — `tracked test-shaped file outside tests/: .harness/tools/test_rogue.py`
  **and** `documented exception is no longer tracked: …/FEAT-44-omp-context-advisory/evidence/probe-session-accessors.ts`.
  The seeded registry path is not tracked in the fixture, and the self-policing clause fires whenever
  the index is available.
- **with `DOCUMENTED_EXCEPTIONS` rebound to `()`: exactly 1 finding**, the rogue line.
- **live `suite_layout.violations()` alone (`suite_layout.py:6-33`, re-read at HEAD `1977ebd6`): 0.**

**Chosen: rebind `suite_layout.DOCUMENTED_EXCEPTIONS` to `()` in a try/finally** — case 6's existing
mechanism — for the duration of the assertion. Rejected alternative: creating and tracking the FEAT-44
path inside the fixture. That couples case 1 to the live registry's contents, which case 7 exists
specifically to isolate, so a later registry edit would redden a case about the file clause. Nothing
is lost: the registry is graded by cases 6 and 7.

**No other live clause fires on that fixture** — confirmed at source, not assumed. `unit`/`integration`
kind directories are non-empty, so neither "contains no test-*.py" fires; the under-`tests/` clause
rglobs only `root/tests` for `test-*.py`, `test_*.py`, `*_test.py`, and `probe-fixture.py` matches
none; the bin clause globs the fixture's `bin/`, which holds only the copied `suite_layout.py`
(no `test-*.py`, `*.test.*` or `probe-*` match). Hence the expected list is exactly one element.

## No split — the second claim is subsumed

Under equality on the whole list, "no finding names `tests/manual/probe-fixture.py`" cannot fail while
the equality holds: a list equal to the one-element rogue list contains nothing else. It is therefore
not independently failable, so no `SC-18` was appended and `SC-07`..`SC-17` are unrenumbered — every
citation in the c1/c2 notes and in `research-BUG-1286-plan-gap-closure-c2.md` still resolves.
Traceability unchanged: SC-06 → AC-05. The separate assertion stays in T-01 case 1 as a diagnostic.

## Mechanical re-verification — all five pass

1. `yaml.safe_load` on `plan.yaml`: OK, top keys `approval decisions feature lanes schema source_issues status tasks`.
2. `check-plan-routes.py` on this plan: `OK T-01`..`OK T-05`, `0 violation(s) across 1 plan(s)`, exit 0.
   Bare invocation (all live plans): `0 violation(s) across 5 plan(s)`, exit 0.
3. Every task carries all eleven keys — T-01..T-05 each `11 missing: [] extra: []`.
4. `status: plan`, `approval: {status: pending}`, `panel present= False`.
5. All 11 issue-#1286 ACs covered (`AC-01`..`AC-11`); 17 SCs, all present in the traceability table,
   each with exactly one `verify:`, every `automated` one naming a `test_kinds` kind with a non-null
   `cmd` (`unit`, `integration`) — malformed set empty. SC-06's traced work is T-01, which traces
   `REQ-04`.

## Open questions

None blocking. One advisory, unchanged from c2 and still the operator's call at approval: `unit.detect`
in `harness.json` stays extension-agnostic while D-01's vocabulary is extension-restricted
(`BRIEF.md:171-179` records the residual and its control).
