# Code review — BUG-1302-suite-layout-fail-closed — pinned SHA ac8dd671742dc20cea91c03715a9579c7c879e31

## BLUF
PASS, no findings. Both stages clean. The two dead-code removals (B-4, B-5) are re-derived here
algebraically AND empirically as fully behaviour-preserving; the fail-open fix (B-6), the read guard
(B-14) and the widened sentinel assertion (B-8) each do exactly what their REQ demands with no
over-catch and no new fail-open path. 23/23 changed Python functions grade PASS at the pin, zero
grade-2, zero FAIL.

## Stage 1 — spec compliance

| REQ | Change | Verdict |
|---|---|---|
| REQ-01 (B-4) | `_literal_key_present` conjunct `and not any(ch in trailing for ch in "*?[")` removed (`tests/unit/test-suite-layout.py:497` region, pin) | PASS — re-derived below |
| REQ-02 (B-5) | `_is_inside_tests` guard `normalized in (".", "..")` → `normalized == "."` (`:450` region) | PASS — re-derived below |
| REQ-03 (B-6) | case 11 `else:` branch: `print(INAPPLICABLE...)` → `check(name, False, two-remedy detail)` (`:643-647`) | PASS |
| REQ-04 (B-14) | `_violations_callers` guards `read_text()` with `except (OSError, UnicodeDecodeError)`, appends named entry, docstring rewritten (`:160-192`) | PASS |
| REQ-05 (B-8) | integration case 2 clause `"PASS test-unit.py" not in p.stdout` → `"PASS test-" not in p.stdout` (`tests/integration/test-run-unit-tests-layout.py:93`) | PASS |
| REQ-06 | Both suites pass live, no existing `check()` removed/weakened | PASS — ran both suites myself (below) |

**Re-derived behaviour-preservation, B-4** (`_literal_key_present`): `trailing = core[last_wildcard+1:]`
where `last_wildcard` is the *maximum* index of any char in `"*?["`. By construction no character at an
index > `last_wildcard` is in `"*?["` — that's what "maximum" means — so `trailing` can never contain a
wildcard char. The removed conjunct `not any(ch in trailing for ch in "*?[")` is a tautology: True for
every possible `core`. Verified empirically too: extracted both the base (`c369fb1f`) and pin functions
into an isolated namespace with the *real* `suite_layout.SOURCE_EXTENSIONS = (".py",".sh",".ts",".tsx",
".js",".mjs",".cjs")` (no `.md`!) and ran all 13 `B4_CORPUS` entries against both — zero mismatches
against expected, and base-verdict == pin-verdict for every entry, including `probe-*.md` (correctly
`False` because `.md` is not a SOURCE_EXTENSION).

**Re-derived behaviour-preservation, B-5** (`_is_inside_tests`): the earlier guard `if ".." in segments:
return False` runs over the *full, unsplit* `segments` list. `prefix_segments` is built by scanning
`segments` in order and stopping at the first wildcard-bearing segment — it is always a **front slice**
of `segments`. Therefore any `".."` element that could end up in `prefix` was already in `segments`,
and the function already returned `False` at the first guard. `posixpath.normpath` cannot fabricate a
`".."` result from segments that contain no literal `".."` (it only introduces leading `".."`
components when up-levels exceed real ones already present as `".."` segments). So `normalized ==
".."` is unreachable whenever we reach the second guard — the removed disjunct never fires on any
input. Verified empirically against all 15 `B5_CORPUS` entries (including the three `".."`-bearing
patterns `../x/*.py`, `tests/../evil/*.py`, `a/../tests/*.py`) against both base and pin: zero
mismatches, base == pin for every entry.

**AST pin counts, re-counted independently** (not trusted from the corpus, computed with a fresh
`ast.walk`): `_literal_key_present` base = 2 `any()` calls / 2 `"*?["` constants, pin = 1/1.
`_is_inside_tests` base `".."` constants = 2, pin = 1. Matches BRIEF's claimed counts and SC-02/SC-04
exactly.

SC-05: `git show <pin>:tests/unit/test-suite-layout.py | grep -c INAPPLICABLE` → 0. Confirmed.
SC-08: narrow clause count → 0; generic `"PASS test-"` clause count → 2 (cases 2 and 4). Confirmed —
and traced the two sentinel-producing lines (`test-unit.py`, `test-integration.py`) to confirm the
widened prefix catches exactly both and nothing else in that file's stdout vocabulary.

**Live runs** (`env -u HARNESS_AGENT_TYPE python3 <file>`): unit suite → 54 PASS, 0 FAIL, exit 0.
Integration suite → 14 PASS, 0 FAIL, exit 0. Both match the orchestrator's claimed measurements.

**Scope**: `git diff 54f01854..ac8dd671 --stat` touches only the two test files plus six
BUG-1302-feature-tree lifecycle artifacts (STATE.md, feature.json, plan.yaml, notes/*). None of
`suite_layout.py`, `run-unit-tests.sh`, `code_grade.py`, `.harness/harness.json`,
`.harness/team-config.yaml` appear. No scope finding.

**SC-10 / DEC-174 routing**: ran `check-plan-routes.py` myself — 5 DEVIATION lines (one per task,
naming only the two carve-out paths), 0 VIOLATION, exit 0. Matches claim.

**Human commits in scope**: only commit after the pin is `ee1eeb67` ("Pin BUG-1302 review SHA"),
touching one line of `feature.json` only — no `[harness:human]` implementation commit exists in this
range.

## Stage 2 — code quality

- **B-14 guard**: `except (OSError, UnicodeDecodeError)` catches both named hazards
  (`FileNotFoundError` ⊂ `OSError` for the tracked-then-deleted case; `UnicodeDecodeError` for the
  non-UTF-8 case) without over-catching into unrelated exception classes (no bare `Exception`).
  Reported entry names the offending path and error type. Docstring rewritten to match. The new T-04
  test case wraps the call itself in `except Exception` — appropriate there, since that's the test's
  own oracle for "does this still raise," not the production guard.
- **B-6 AST match**: locates the sole `if control_candidate is not None:` (confirmed unique via
  independent grep — `control_candidate` used as a bare Name in a comparison exactly once in the
  file) and requires exactly one `check()` call in its `orelse`; ambiguity (0 or >1 matches) yields
  `b6_call is None`, which fails the assertion closed rather than passing vacuously.
  `b6_condition.value is False` is the correct fail-closed anchor: a future rewrite to
  `check(name, some_truthy_expr, ...)` would satisfy the phrase clauses but not this one.
- **No fail-open branches introduced.** Traced every new/changed branch: B-6's old print/no-assert
  branch is now a hard `check(..., False, ...)`; B-14's guard converts an unguarded crash into a
  named, assertable failure (the repo-wide caller-equality check downstream still catches a real
  unreadable file, since the extra list entry breaks that equality).
  Confirmed on all 23 changed/graded functions repo-wide.
- **No helper duplication.** `_self_fn`/`SELF_AST` are new (file had no prior `ast` usage); nothing
  in `suite_layout.py` (read-only, unmodified) offers equivalent AST introspection.
- **Docstring/code match.** `_violations_callers`'s rewritten docstring accurately states the new
  contract; verified against the implementation.

### Code-risk grades (all changed functions, computed at the pin with the repo's own `code_grade.py` /
`code-grade.py`, 23 total records, 0 FAIL, 0 grade-2):

| Function | Grade | Driver | Bar | Result |
|---|---|---|---|---|
| `_self_fn` (new) | 5 | cyc+cog+abc | 3 | PASS |
| `_violations_callers` | 3 (base 3: cyc7/cog13/abc14.5 → pin: cyc8/cog15/abc18.4) | cognitive | 3 | PASS |
| `_is_inside_tests` | 3 (base and pin identical: cyc9/cog9/abc15.9) | cyclomatic | 3 | PASS |
| `_literal_key_present` | base 2 (cyc12/cog13/abc18.4, was `severity: med`, FAIL) → **pin 3** (cyc10/cog13/abc15.1) | cyclomatic+cognitive | 3 | PASS — matches BRIEF non-goals' pinned numbers exactly, clears the previously-gating record |

The repo's `code-grade.py --base <merge-base> --head <pin>` CLI reports only `_self_fn` as "gated"
(new function; the other three improved-or-held functions are classified informational by
`gated_set`, per this repo's own G-06 gotcha) — I did not rely on that alone; I ran `code_grade.
grade_source`/`classify` directly over both files at the pin and confirm the full 23-function,
0-FAIL, 0-grade-2 count matches the orchestrator's claim.

Integration file: the one changed line sits at module scope inside a `try/finally`, not inside any
`FunctionDef` (confirmed via `ast.walk` — the file's five functions are `check`, `tree`, `git_tree`,
`git_commit`, `run`, none touched) — correctly ungraded by the tool, nothing to report.

## Findings
None. `must_fix`: `[]`. Advisory-only observation (not a finding, already recorded and accepted in
BRIEF's own "AST PIN FALSE POSITIVES" residual-risk section): the b4/b5/b6 structural AST assertions
are module-level script code, so `code_grade.py` never grades their density — that's an accepted,
pre-signed trade, not something I'm re-litigating.
