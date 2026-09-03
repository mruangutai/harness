# EFFICIENCY receipt — FEAT-54 validation c1/c2 repairs

Verdict: PASS — one engineering-owned advisory candidate; no enforcement-surface candidate and no minutes-scale suite duplication.

## Findings

- id: EFF-01
  disposition: candidate
  ownership: engineering-owned probe
  file: tests/manual/probe-handoff-comprehension.py
  line: 207
  summary: A note with no `Done when` facts still launches both live-model arms.
  concrete_cost: `measure_note` calls `measure_arm` twice even when `done_when_facts` returned `[]`; each call permits a 600-second timeout, so an accepted legacy/requested note with no `## Done when` can spend up to 20 minutes while producing only `0/0` evidence from two effectively identical inputs.
  alternative: Detect an empty `facts` list before constructing/running the arms, print that the note is not measurable, and return empty evidence without invoking `omp`.

## Assessed without findings

- `.claude/skills/harness/bin/check-domain.sh`: authority resolution is restricted to handoff writes/edits and bounded to four pointers; its pre-mutation checks and post-write sweep are security/evidence work, not removable hot-path waste in this repair.
- `.claude/skills/harness/bin/handoff_done_when.py`: target reads are bounded to four authority lines and 1 MiB each. Re-reading a shared target is possible but too small and uncommon to justify a speculative cache.
- `tests/integration/test-check-domain.py`, `tests/integration/test-check-state.py`, and `tests/unit/test-handoff-done-when.py`: overlapping cases bind distinct security, ordering, resolution, baseline, and pre-mutation boundaries. The exact duplicate-looking 60-line cases are sub-second process work, not minutes-scale suite duplication, and every individual case is settled.
- `tests/unit/test-probe-handoff-comprehension.py`: temporary-file setup and two-arm assertion are bounded and directly defend probe input safety and experiment shape.

## Scope read

- `.claude/skills/harness/bin/check-domain.sh`
- `.claude/skills/harness/bin/handoff_done_when.py`
- `tests/integration/test-check-domain.py`
- `tests/integration/test-check-state.py`
- `tests/unit/test-handoff-done-when.py`
- `tests/manual/probe-handoff-comprehension.py`
- `tests/unit/test-probe-handoff-comprehension.py`

No source was edited and no formatter, linter, test, build, or validation command was run, as required for this read-only pass.
