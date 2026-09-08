# SIMPLIFY / REUSE — BUG-151 check-domain-fail-aggregation

## Verdict
Zero findings. The three new definitions (`_AggTee`, `_aggregation_verdict`,
`run_bug151_selfcheck_cases`) and the discovery loop in `main()` do not re-implement anything the
tree already carries in importable form.

## What was examined
- Pinned diff: `git diff 6d969ed3 fffc62d9 -- tests/integration/test-check-domain.py` (149 lines).
- `tests/integration/test-check-domain.py:5182-5291` (`_AggTee`, `_aggregation_verdict`,
  `run_bug151_selfcheck_cases`, `main()`), plus the file's import header (line 20, the new
  `contextlib` import) and its `_anchor_*` sys.path setup (lines 15-19) for whether a shared helper
  module was already importable from here.
- `tests/unit/test-factory-cli.py` (plan-cited prior art) — every `redirect_stdout` occurrence:
  lines 42, 102, 175, 194, 217, 229.
- `tests/unit/test-factory-gh.py` (plan-cited prior art) — `silent_stdout` at lines 80-87.
- Broader sweep for tee/capture patterns: grep `redirect_stdout` and `def write(self` across
  `tests/`, `.claude/skills/harness/bin/`, `.agents/skills/harness/bin/`. Hits in
  `tests/integration/test-factory-decompose.py:362,454`, `tests/integration/test-layout-migration.py:118,308`,
  `tests/unit/test-factory-claim-mutation.py:59,86`, `tests/unit/test-factory-claim.py:428`,
  `tests/unit/test-factory-config.py:952,978`, `tests/unit/test-factory-land.py:248`,
  `tests/unit/test-factory-workspace.py:130`.
- Sweep for `class \w*[Tt]ee` repo-wide — no hits.
- Sweep for `startswith("FAIL")` / `startswith('FAIL')` repo-wide — no hits outside the new code.
- Sweep for a `run_`-prefix discovery idiom (`globals().items()` filtered by `startswith("run_")`)
  repo-wide — no hits outside the new code.
- `.claude/skills/harness/bin/run-unit-tests.sh` (the only other place a "block of tests failed"
  aggregation rule could plausibly already live) — its pass/fail signal is each script's process
  exit code via `run_pool.py --mutation-check`, not a printed-line convention. No FAIL-line counting
  rule to duplicate.

## Findings
None.

## Near-misses considered and rejected

1. **`_AggTee` vs. the plan-cited `redirect_stdout` capture sites.** Every one of the ~14 existing
   `redirect_stdout` call sites across `tests/unit/` and `tests/integration/` (see list above)
   redirects into a plain `io.StringIO()` — a pure sink. None of them write through to the real
   stream while capturing. `_AggTee` exists specifically so a human watching the live 38s run still
   sees each block's verdict lines as they print, which is exactly the property `io.StringIO()`
   does not have (`.write()` only appends to its internal buffer; nothing downstream ever sees it
   until `.getvalue()` is read after the `with` block exits). Reusing `io.StringIO()` here would
   silence the live run for its ~24s+ duration and defeat the reason this safeguard exists. Not a
   finding — `_AggTee` delivers a distinct, previously-absent capability, not a restatement of one.

2. **The column-0 `FAIL`/`ok` counting convention vs. `run-unit-tests.sh` or another test's own
   aggregation.** `run-unit-tests.sh` aggregates by process exit code through `run_pool.py`, never
   by scanning printed text for a `FAIL` prefix. No other file in the tree parses `FAIL` lines by
   column-0 prefix for a self-check. `_aggregation_verdict`'s zeroness-agreement rule (D-01) is
   novel to this change; there is nothing existing to import instead.

3. **A shared helper module `test-check-domain.py` already imports that could have hosted these
   three definitions.** The file's only local-path addition is `_anchor_bin`
   (`.claude/skills/harness/bin`), added to `sys.path` for hook/module imports specific to the
   check-domain hook under test — not a shared test-scaffolding module. No existing module on that
   path (or elsewhere) exposes a tee-with-writethrough or a FAIL-zeroness verdict helper to import.

4. **The `run_*`-discovery loop in `main()` vs. an existing discovery idiom elsewhere.** No other
   test file or runner in the tree enumerates `globals()` for a naming-convention prefix; every
   other integration test module hand-enumerates its blocks (as this file's `main()` itself used to,
   pre-BUG-151). D-02 (already settled, not reopened here) is a genuinely new idiom in this tree,
   not a restatement of one.

## Open questions
None.
