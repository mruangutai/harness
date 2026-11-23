# Receipt — simplify · efficiency — FEAT-2397 (plan surface, flag-only)

BLUF: 2 low findings, 0 blockers. Verification cost is proportionate: T-01 already parallelizes its seven suites, T-05's cumulative gates and T-02's baseline+final transient check are deliberate boundary runs (not flagged). All costs below are read-derived estimates; nothing was run (read-only pass).

## Findings

1. T-03 · plan.yaml:458-462 (verify) — low
   - Summary: T-03's verify re-runs `check-plan-routes.py --canonical-reader-audit`, which T-05 (plan.yaml:527) runs again as the declared cumulative gate.
   - Cost: the audit AST-scans every Python file under the reader tree (`check-plan-routes.py:1663-1690`, `_scan_reader_tree`), so it is a whole-tree pass, not a targeted one. Duplicate run is seconds-scale, unmeasured. T-03 only strips CLAUDE_PROJECT_DIR assignments in tests; the audit's scan target is the same tree T-05 re-scans after all mutations.
   - Alternative: keep `--check-layout` and `test-hooks-install.py` in T-03 (they bind its changes) and leave the canonical audit to T-05. Or keep it as an early tripwire if the author wants T-03's red localized; advisory either way.

2. T-02 · plan.yaml:421-425 (verify) — low
   - Summary: five standalone suites run serially, while T-01's verify runs seven suites through a ThreadPoolExecutor (plan.yaml:361-370).
   - Cost: wall-clock only, sum-of-five instead of max-of-five; per-suite times unmeasured, likely seconds each. The transient check runs twice (baseline, final pin), so the serial tail is paid twice.
   - Alternative: reuse T-01's concurrent-runner shape for the five test files. Note T-01's 45s per-process timeout under 7-way contention is a flake risk, not waste; keep T-02 serial if the author prefers no timeout tuning.

## Not flagged (deliberate or verified fine)

- `bun run typecheck` in T-01, T-04, T-05: T-01/T-04 edit TypeScript; T-05 is the cumulative boundary. `--check-layout` in T-03 and T-04 is a cheap structural check each task's file set could break.
- T-05 repository-state gate (`check-state.py` over the real corpus, `git ls-files` positive control): the standing CI invocation and a settled panel ruling; boundary evidence.
- T-02 baseline-vs-final transient check, retained per-target results: settled (SC-04 receipt, not a permanent topology test); `ast`/`yaml` parse of six files is milliseconds.
- T-06: MANUAL verify, one observation, no executable hashing or provenance dossier; `gh issue view` is a single call. Force-adding runs/** adds no repeated I/O.
- T-01 `_capped_body` single-pass rewrite, in-process checker replacing a subprocess, one decoded stdout parse in `classifyPolicyRun`, one `getContextUsage()` call on the existing task-result trigger: these REMOVE hot-path work (a spawn per SubagentStart, a double JSON.parse, a JSONL tail read) and are efficiency-positive.
- T-02→T-03 and T-04 sequencing: Main is the single main-session-direct executor, so dependency edges cost no parallelism.

## Missing guidance

No `docs/spec.md`, `docs/decisions.md` or `docs/architecture.md` exists at the product root; the plan consults `.harness/harness/docs/SPEC.md`/`DECISIONS.md` instead (plan states this). Nothing in the efficiency angle depended on them.

## Principles applied

None cited (no craft leaf read for this angle).

## Open questions

none
