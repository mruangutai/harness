# Scope review — plan-panel c4 — FEAT-54

## BLUF

The c4 amendment holds up under adversarial spot-check. Every anchor I independently re-measured
(check-domain.sh/check-state.sh line citations, `suite_layout.py`'s two globs, `code_grade.py`'s
`_is_test_path`, `test-suite-layout.py:101-102/:105`, `omp_session_accessor.exclude`, the
`^PASS planted` line) matches the goal-check's table exactly. D-04's and D-06's restated `because`
clauses are TRUE at the cited sources — no newer unfounded rationale. `depends_on` forms a valid
DAG, no cycles, all ten REQs traced. One new finding: T-12's new file can trip an UNRELATED guard
(`test-suite-layout.py`'s sole-implementation sweep) depending on implementation style, and no task
in scope could repair that if it fires — raised by should-not-exist, verified independently.
Recommend PASS with one med finding to carry forward as an implementer warning, not a plan repair.

## Obligation 2 — per-item path resolution (spot-checked rows, adversarial)

| Path | Exists at HEAD? | Verb match | My verification |
|---|---|---|---|
| `tests/manual/probe-handoff-comprehension.py` (T-09) | No | "Create" ✔ | `suite_layout.py`'s planted-check globs only `bin_dir` directly (non-recursive); its `shaped_tests` rglob only matches `test-*.py`/`test_*.py`/`*_test.py`, never `probe-*` — a probe under `tests/manual/` is invisible to `violations()` regardless of directory. Confirmed by reading `suite_layout.py` in full. |
| `tests/integration/test-run-unit-tests-kinds.py` (T-12) | No | "Create … a NEW file" ✔ | Confirmed absent via glob. `harness_boundary.resolve_root` reads `HARNESS_PROJECT_DIR` only when the override carries `.harness/team-config.yaml` (`harness_boundary.py:66-84`) — the exact mechanism `test-run-unit-tests-layout.py`'s `tree()`/`run()` already use successfully, so T-12(c)'s fixture-root technique is proven, not novel. |
| `.claude/skills/harness/bin/handoff_done_when.py`, `tests/unit/test-handoff-done-when.py` (T-01/T-02) | No | "Create" ✔ | Confirmed absent via glob. |
| `check-domain.sh` prose sites (T-04) | Exists | "extend" ✔ | Grepped `[Ff]our` across the whole file: exactly 2 live contract claims outside the required-list message — DEC-159 comment (:1547-1548) and the 60-line cap message's item enumeration (:1552-1553, no literal "four" but 4 items). A THIRD site, the missing-required-section message (:1557-1559, literal "the four sections are the contract"), is separately covered by T-04's *first* bullet ("update that message's wording from 'the four sections' to 'the five sections'"). All three real sites are covered across the two bullet groups — initially looked like a gap, resolved on close reading. Not a finding. |
| `check-state.sh` `HANDOFF_HEADINGS` (T-07) | Exists | "extend" ✔ | Confirmed exactly two readers: `:1199` (`miss = [h for h in HANDOFF_HEADINGS if h not in hl]`) and `:1219` (`if _l not in HANDOFF_HEADINGS:`), matching the intent's claim of "read twice." SC-08's two exempt narrative sites ("Measured at cf51dce…All 74 carry the four headings…" and "…nothing under any of them passed") confirmed present at :1185-1188 and :1203 — past-measurement prose, correctly outside T-07's rename scope. |

## Obligation 3 — per-mechanism citations (all requested, spot-checked)

| Mechanism | Cited at | Exists? |
|---|---|---|
| `suite_layout.violations` | `suite_layout.py:6-34` | Yes, read in full |
| `run-unit-tests.sh --check-layout` | — | Yes (`:18-19,32-38`) |
| two suite globs | `run-unit-tests.sh:25-27` | Yes, exact — the `case "$KIND" in` unit/integration/all branches |
| `test-suite-layout.py:101-102` / `:105` | — | Yes, exact — `:101-102` loop pins BOTH unit and integration `detect` byte-for-byte to `templates/harness.json`; `:105` forbids an active kind's `detect` naming `tests/manual` |
| `code_grade.py:458-472` / `:488` | `_is_test_path`, bar-3 claim | Yes, exact — file is `code_grade.py` (underscore), not `code-grade.py` (hyphen, a separate CLI file) — dispatch's spelling is correct, worth noting the two coexist |
| `check-state.sh:1059/:1199/:1219` | `HANDOFF_HEADINGS` | Yes, exact, exactly two readers confirmed |
| `check-domain.sh` `RE_HANDOFF` + two prose sites | `:1096,1546-1547,1552-1553` | Yes, all confirmed |
| `test_kinds.omp_session_accessor` + `exclude` | `.harness/harness.json:277-282` | Yes — `exclude: ".claude/worktrees/**"` exact match to what T-09 sets for `handoff_comprehension` |
| `^PASS planted` line | `test-run-unit-tests-layout.py` | Yes — `check("planted", ...)` prints `"PASS" if condition else "FAIL", name, ...` → literal `PASS planted ` |

## Obligation 4 — red-capability, independently re-derived (not just re-read)

Traced T-01's and T-07's verify scripts by hand against current source (not just trusting the
goal-check's rc numbers): T-01's `grep -q handoff_done_when` (underscore) cannot match the
interpreter's "No such file" message, which only names the hyphenated filename — so the verify is
RED today for a reason *unrelated* to the module, and only turns green once the test exists and its
own ImportError names the module. T-07's `grep -qi 'done when' check-state.sh` conjunct is RED
independent of the suite (confirmed zero matches at HEAD). Both match the goal-check's conclusions;
no disagreement found. T-12(c)'s fixture is buildable from `test-run-unit-tests-layout.py`'s `tree()`
pattern (confirmed above) and its three cases are reachable and discriminating as specified.

## Obligation 5 — rationale truth

| Clause | Verdict | Source |
|---|---|---|
| D-04: registration grades the probe at bar 3 via `_is_test_path` | TRUE | `code_grade.py:458-472,488` |
| D-04: must be `locally_run`, never `active`, because `:105` forbids an active kind detecting `tests/manual` | TRUE | `test-suite-layout.py:105` exact |
| D-06: placement under `tests/unit` is the whole registration | TRUE | `run-unit-tests.sh:25` glob |
| D-06: `integration.detect` is the single glob `tests/integration/**`, no per-file list | TRUE | `.harness/harness.json:285` |
| D-06: `test-suite-layout.py:101-102` pins that value byte-for-byte to `templates/harness.json` | TRUE | exact, loop covers both `unit` and `integration` |

SC-09's two acceptance clauses (rerunnable on demand; absent from normal suites) survive unchanged
in substance and are now gradable — confirmed independently by reading D-04/T-09/T-12 together: the
old mechanism (`UNIT_SCRIPTS`/`KIND-DRIFT`) is provably absent (0 occurrences, corroborated by my own
read of `run-unit-tests.sh` in full — it globs and reads no test kinds at all), and the new mechanism
(`test_kinds.handoff_comprehension` + `--kind all` over a fixture) is real, present, and exercised by
T-12's own new test.

## Findings

1. **[med] T-12's new file risks tripping `test-suite-layout.py`'s sole-implementation sweep, a
   guard no task in scope can repair.** (Credit: raised by should-not-exist, verified independently.)
   `tests/unit/test-suite-layout.py:17-30` flags any tracked `*.py` file, not on a 4-entry exemption
   list (`:17-22`, not extended by this plan), whose source text matches BOTH `KIND_PATTERNS` (a
   `tests` token immediately followed by a separator and `unit`/`integration`, e.g. literal
   `"tests" / "unit"`) AND contains any of `DISCOVERY_FRAGMENTS` (`os.listdir`, `os.walk`,
   `.glob(`, `iterdir`, `rglob`, etc.) — checked at `:113`. T-12(c)'s fixture builder must create
   files under both `tests/unit` and `tests/integration`; if a doer writes that with literal
   pathlib segments (`r / "tests" / "unit"`, a common idiom) *and* uses any directory-listing call
   anywhere in the file (e.g. to confirm a fixture file landed), the unit suite's sole-
   implementation check newly fails on `tests/integration/test-run-unit-tests-kinds.py` — a
   regression in a file (`test-suite-layout.py`) that is in none of the ten amended items' `files:`
   lists, so T-12 cannot fix it in scope and the plan gives no warning against this specific
   coupling (unlike its explicit "do not modify test-run-unit-tests-layout.py" guardrail). Mitigated
   if the doer instead mirrors `tree()`'s existing style (`r/"tests"/kind` with a loop variable,
   which does not trigger `KIND_PATTERNS`) and avoids any glob/iterdir call, which the task does not
   structurally require — so this is conditional on implementation choice, not certain, and is
   reported as an implementer-facing risk rather than a plan defect requiring repair.

No other findings. Zero scope-creep, zero omissions, zero orphan REQ/SC traces found in the eight
amended tasks/decisions and their `depends_on` neighbours (T-05, T-08, T-10, T-11); `depends_on`
forms a valid DAG (traced by hand: `T-07 → {T-06→T-02→T-01, T-11→{T-04→T-03→T-02→T-01, T-05}}`,
`T-10 → {T-04, T-07}`, `T-12 → T-09 → T-05`; no cycle).
