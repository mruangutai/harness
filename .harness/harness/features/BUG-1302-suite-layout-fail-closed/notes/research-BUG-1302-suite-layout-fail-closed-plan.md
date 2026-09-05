# Research — BUG-1302 plan basis (measured at c369fb1)

**BLUF.** All five defect premises hold at `c369fb1`, both removals are provably behaviour
preserving, and the B-6 branch is reachable under a config the plan names. One planned verify was
NON-DISCRIMINATING and was replaced; see the last section.

## Measured facts (re-derived, not inherited)

- `_is_inside_tests`: the early `if ".." in segments: return False` runs before normalization, so
  `normalized` can never be `".."`. Removing the `".."` element of `(".", "..")` is exact. Verdicts
  measured over the 15-pattern corpus now pinned in T-01's intent — including `../x/*.py`,
  `tests/../evil/*.py`, `a/../tests/*.py` (all False, via the early guard) and `./tests/*.py` (True).
- `_literal_key_present`: `trailing = core[last_wildcard + 1:]` is the span after the LAST wildcard,
  so `not any(ch in trailing for ch in "*?[")` is always True. Verdicts measured over the 13-core
  corpus pinned in T-02's intent. Note `probe-*.md` is False — `.md` is not in
  `suite_layout.SOURCE_EXTENSIONS` (`.py .sh .ts .tsx .js .mjs .cjs`).
- B-6 reachability, measured: under the live `test_kinds`, `select_control_candidate` returns
  `.harness/tools/test_dir/gen.py`; under `{"unit": {"status": "active", "detect": "tests/unit/**"}}`
  it returns `None`. That fixture is the plan's proof the converted branch can fire.
- B-14 hazards are both real for `read_text()`: a tracked-but-deleted path raises `FileNotFoundError`
  (an `OSError`), a non-UTF-8 tracked source raises `UnicodeDecodeError`. `git ls-files` lists the
  deleted path, and `_violations_callers` skips only `tests/` prefixes, so both reach the read.
- Routing: `check-plan-routes.py` on this plan exits 0 with five DEVIATION lines and
  `0 violation(s)` — exactly the shape D-01 predicts.

## The non-discriminating verify that was caught

The obvious B-8 check — grep the integration file for `"PASS test-" not in p.stdout` — ALREADY
passes at `c369fb1`, because case 4 carries that clause. The discriminating form, now in T-05's
`verify:` and SC-08, is the absence of the NARROW clause `"PASS test-unit.py" not in p.stdout`
(present today, so the check is red before the change) plus an occurrence count of exactly 2 for the
generic clause (cases 2 and 4).

## Edit ordering

`tests/unit/test-suite-layout.py` is touched by four tasks; they are chained
T-01 -> T-02 -> T-03 -> T-04 through `depends_on` so no two edit it concurrently. T-01 introduces the
`ast` import that T-02 and T-03 reuse. T-05 touches the other file and is independent.

## Open, not answered here

- Whether BUG-1302 should amend DEC-174's enumeration to name `run-unit-tests.sh` (Q1).
- Whether the operator accepts remedy (a) and the main-session ownership of the red it can produce
  (Q2). The BRIEF pins (a); a different answer re-plans T-03 only.
