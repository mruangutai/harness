# EFFICIENCY angle — B-3 fixture diff (`tests/unit/test-factory-claim.py`)

**BLUF: no findings. The diff adds no measurable wasted work — declined after measuring.**

## Measurements

- Suite wall-clock: `time python3 tests/unit/test-factory-claim.py` → `real 0m0.131s` (user
  0.078s, sys 0.073s), 124/124 checks passed. Not a candidate for scrutiny at any threshold this
  skill sets ("hot-path milliseconds" — 131ms for the whole file, one process start included, is
  noise).
- `build_features_root()` call count: `grep -n "build_features_root()"` → exactly one call site,
  line 388 (`FIXTURE_HARNESS_ROOT = build_features_root()`, module load time), plus the `def` at
  324 and a prose comment at line 68. It is built once for the whole file, not per-case.

## Findings

None. Reasoning against the three prompts in the dispatch:

1. **Suite timing** — measured directly above; 0.131s wall-clock for the full 124-check file is
   not slow by any standard this skill applies, and the diff adds zero new test cases (5b already
   existed; the change only enriches its fixture data and asserts an extra field). Nothing to
   flag.

2. **Repeated I/O in `build_features_root()`** — the two new `write_json` calls the diff adds
   (`kaya_seg/feature.json` line 378, `harness_seg/feature.json` line 383) execute exactly once,
   at module import, alongside the four `write_yaml`/`write_json` pairs already there before this
   diff. Two extra one-shot file writes at suite load, not a per-case cost — not worth flagging
   even before timing it, and the 0.131s total confirms it.

3. **Case 5b's added `issue_view(REPO_HARNESS_SEG, 954, ...)` call** — this is the point of the
   test, not overhead. 5b's whole purpose (per its own docstring, lines 1179–1183) is proving the
   per-repository resolver reaches *each segment's own issue map*, not a shared or cached one.
   Registering `rec.issue_data[954]` with `state="CLOSED"` and having the tool legitimately reach
   `issue_view` for it is what makes the harness-segment candidate resolve "clear" instead of
   "no plan could be read" — the exact discriminator the case exists to prove. Suppressing that
   call would remove the assertion's teeth, which this pass may not do anyway (SKILL.md:
   "The apply may not delete or weaken an assertion").

No plan-surface content in scope (this is a code-surface-only diff to one test file); the "same
file read repeatedly across sequential tasks" prompt does not apply here.
