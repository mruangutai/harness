# SIMPLIFY / altitude — BUG-151

## Examined
- `tests/integration/test-check-domain.py:5182-5292` (`_AggTee`, `_aggregation_verdict`,
  `run_bug151_selfcheck_cases`, `main()`) and its imports at `:1-28`.
- Shared-home candidates: `.claude/skills/harness/bin/run-unit-tests.sh` (full text),
  `.claude/skills/harness/bin/run_pool.py` (`run_one`, `_emit_result`, `_run_scripts`,
  `_print_summary`, `main`).
- Sibling column-0 `ok`/`FAIL` print convention: grepped across all of `tests/integration/`
  and `tests/unit/` — 60+ verbatim-duplicated blocks across 20+ files (`test-bash-write-guard.py`,
  `test-check-expertise.py`, `test-dispatch-guard.py`, `test-factory-*.py`, `test-gen-decisions-index.py`,
  etc.), no shared helper module (`glob` for `helpers*.py`/`conftest.py` under `tests/` found none).
- Plan history for the naming-prefix residual: `BRIEF.md:53-56`, `plan.yaml` D-02,
  `notes/research-BUG-151-goalcheck-plan-c0.md` (F-3), `notes/review-harness-code-reviewer-planpanel-c0.md:64-66`.

## Findings

### F-1 — the safeguard's capability sits below its natural home
- **File/lines**: `tests/integration/test-check-domain.py:5182-5210` (`_AggTee`,
  `_aggregation_verdict`).
- **Summary**: the safeguard is a generic property — "a script's printed column-0 `FAIL`
  count must agree on zeroness with its own returned total" — that applies to the same
  print convention used verbatim in 60+ blocks across 20+ other test files, but it is
  wired to protect only this one file's own `run_*` blocks.
- **Cost**: the defect class this exists to catch (a block whose `fails +=` silently
  drops, so it prints `FAIL` on screen while the aggregate stays green — the exact bug
  the old hand-written `main()` comment at line 5207-5210, pre-diff, warned about by
  hand) is equally reachable in every other test file that uses the identical
  print convention, and none of them get this protection. The fix's blast radius is
  1 file out of 90+ in `tests/`.
- **Alternative**: this file already imports shared bin modules by `sys.path.insert`
  (`from isolated_bin import isolated_bin`, line 27) — the pattern for a shared helper
  already exists and is already used here for a different cross-cutting concern.
  `_AggTee`/`_aggregation_verdict` could live in `.claude/skills/harness/bin/` as an
  importable module, or the equivalent check could run once, centrally, in
  `run_pool.py:_emit_result`, which already captures every script's full `stdout`
  centrally and would need no per-file opt-in.
- **Recommendation**: `briefing-row`. Requires a new/shared module and touches the
  pool runner or a second file — outside "one file, applicable right now."

### F-2 — the column-0 convention itself has no single authoritative statement
- **File/lines**: `tests/integration/test-check-domain.py:5207` (`printed = sum(1 for
  line in ... if line.startswith("FAIL"))`), plus the 60+ duplicated print sites
  suite-wide.
- **Summary**: `_aggregation_verdict`'s detector is now load-bearing on every future
  `run_*` block obeying an unwritten convention (column-0, literal `"FAIL"` prefix,
  distinct from an indented `"      | FAIL ..."` detail line). Nothing in the repo
  states this convention as a rule; it is reconstructed independently, block by block,
  by whoever writes the next test file.
- **Cost**: a future block that reports failure a different way (e.g. `"FAILED "`,
  or indents its verdict line) silently defeats the safeguard exactly as convincingly
  as the bug it exists to catch — no error, just a printed `FAIL` the safeguard no
  longer notices, because it never had a definition to enforce against.
- **Alternative**: none applicable inside this one file — the convention's scope is
  suite-wide, and a single-file docstring can't be the authoritative statement for 90
  other files. A shared doc/lint (e.g. a note in `run-unit-tests.sh` or a `suite_layout.py`
  check) is the right level, but is new machinery outside this file.
- **Recommendation**: `briefing-row`.

### Residual — `run_` prefix discovery leaves a misnamed block invisible
- **Judgement**: correctly accepted, and its compensating control is already named,
  twice: `BRIEF.md:53-56` states "The naming convention is load-bearing and must be
  preserved" and enumerates the two existing non-`run_` helpers by name so a reviewer
  can check the boundary is intact; and `notes/research-BUG-151-goalcheck-plan-c0.md`
  raises this exact mirror-image defect as F-3, which
  `notes/review-harness-code-reviewer-planpanel-c0.md:64-66` records as already
  ruled/accepted by the operator's prior cycle. This is a settled residual with a
  named compensating control, not an open altitude gap. I am not reopening it.
- **Recommendation**: `leave`.

## Summary
2 altitude findings, both `briefing-row` (neither is a same-file fold-in: both need a
shared module or a second file, which is out of this feature's closed, one-file scope).
1 residual judged correctly accepted with its control already named in the plan record —
`leave`. Zero `fold-in`-eligible findings: nothing here is small enough to land inside
`tests/integration/test-check-domain.py` alone without becoming a new module or scope
change.
