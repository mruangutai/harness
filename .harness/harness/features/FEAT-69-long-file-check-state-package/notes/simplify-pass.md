# FEAT-69 — simplify pass (harness-simplify, code surface), before the pin

Four read-only readers over `git diff a726bad8..HEAD` (transcripts `history://F69Reuse`, `F69Simplification`, `F69Efficiency`, `F69Altitude`). Applied by the main session (DEC-174); the suites re-ran green after the apply.

## Applied
- **R-02 / Eff-F2** — `broad_catch_census_paths` enumerates through `_reader_source_paths` (recursive, sorted, `__pycache__` skipped) instead of a third listing of `bin/` that read 252 KB of package text only to discard it. Any future package under `bin/` is ceiling-0 by construction.
- **S-F1** — `check_state/ctx.py`'s generated header no longer duplicates the moved `import factory_config` (the moved comment + import at its original place stay byte-for-byte).
- **S-F2** — the eleven package docstrings state the module's fact in one line, marked `(FEAT-69)`; the "moved byte-for-byte" narration is gone (it would have been silently false after the first edit).
- **S-F3** — `seams._handoff_done_when` is `functools.cache`d instead of a one-slot dict.
- **S-F4** — `_checker_trees` reports an unreadable package file directly instead of raising a synthetic `OSError` into its own handler.

## Skipped, with reason
- **R-01** (one shared `bin/` module for "entry + `check_state/*.py`", used by the lock and by `check-skill-refs`) — both derive membership by glob, so the only drift class is a package rename, which the lock's clean-tree case and the unit test both catch; a new bin module for a two-line glob fails the deletion test.
- **R-03** (`test-check-plan-routes._checker_files/_owning_checker_file` vs `check_state_support.check_state_owner`) — the routes harness resolves against an arbitrary mutated copy, the support helper against `SCRIPT`; sharing would couple two suites through a root parameter for two functions.
- **S-F5** (`from collections import namedtuple` mid-file in `table.py`) — moved byte-for-byte with its comment block; the rule wins.
- **Eff-F1** (memoise per-function AST analysis in `_PackageFunctions`; each helper reached by N rows is walked 4N times, sub-second per run, ~40 runs per routes suite) — a real saving of seconds in one suite, but not a one-fix apply; backlog row.
- **Alt-A1** (family docstrings restate their INV rosters, a second statement of `ROW_FAMILIES`) — reader's own disposition was briefing-row; left, noted for the orchestrator.

## Also fixed here (found by the two test kinds, not by the readers)
- `test-team-catalog.py` (6): the `PLACEHOLDER_UNSET` consumer is now `check_state/feature_record.py`.
- `test-suite-independence.py`: the new skill-refs case plants through `plant()` rather than opening a path built from the module's constant.
- `test-code-grade.py`: `_feat69_cross_module_checks` split so the test file stays at its self-graded bar.
- `test-check-decision-anchors.py`: four DECISIONS.md anchors into `check-state.py` (lines 105-107, 120, 1983-2018, 2270-2273 — all past the 97-line entry, and all pointing at code that had moved long before this feature) re-pointed to where the described content lives now, with the original line named as "at the time".
