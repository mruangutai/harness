# Pinned code review — FEAT-1821 T-14 V9-01 repair

**BLUF: PASS at immutable pin `ea4916518eea1c8f73901d372ad8e1e38595e64b`.** The T-14 repair replaces the fail-open four-byte signature check with `zipfile.is_zipfile`, the exact PK-prefix garbage mutant now fails, all eight committed trace archives remain accepted, and no substantive spec-compliance or code-quality finding remains.

## Scope and pin

Reviewed only T-14 source, test, and receipt changes in `c5fab95615c035e97109f90bd4aa91fc2e4b78a5..ea4916518eea1c8f73901d372ad8e1e38595e64b`: `.claude/skills/harness/bin/ui_contract.py`, `tests/unit/test-ui-verification-contract.py`, and `notes/receipt-main-direct-T-14-c0.md`. Intervening governance/review/run records were excluded as directed. `feature.json` pins the same `review_sha`. The worktree had dirty orchestration-owned `STATE.md`, `feature.json`, and `plan.yaml`; `git diff --quiet ea491651... --` over the three reviewed paths passed, so every implementation conclusion is bound to pinned bytes. No `[harness:human]` commit occurs in the repair range.

## Stage 1 — spec compliance: PASS

`ui_contract.py:261-267` now delegates archive recognition to `zipfile.is_zipfile`, which reads/parses the ZIP central directory rather than accepting a local-header prefix. `_trace_file_problem` still checks repository-relative containment inside the same run `ui/`, existence, regular-file status, and non-empty size before ZIP parsing (`ui_contract.py:382-392`). The surrounding record logic still requires traces for every applicable traced check and rejects traces on untraced checks (`ui_contract.py:369-380`). The changed test adds exactly `b"PK\x03\x04" + b"\xff" * 64` and expects the existing `not a ZIP` refusal (`tests/unit/test-ui-verification-contract.py:361-364`), alongside the unchanged positive ZIP, absent, absolute, escaping, outside-ui, empty, ordinary non-ZIP, and wrong-record cases (`:326-369`). The unchanged suite also preserves Traces-table validation (`:182-189`) and SC-04 fail-closed pixel-baseline enforcement (`:371-394`). T-14's exact location-based ignore probe passed.

The receipt's appended V9-01 proof is consistent with the pinned diff and rerun evidence: the baseline implementation at `c5fab956...` is exactly `path.read_bytes()[:4] == b"PK\x03\x04"`; replaying the pinned test with that baseline predicate produced one failure because the corrupt trace incorrectly returned PASS. At the repair pin, all 27 tests pass. No previous T-14 rule was weakened or removed.

## Stage 2 — code quality: PASS

The fix is the boring standard-library implementation. It removes the avoidable whole-file `read_bytes()` allocation/copy, adds no fallback, and preserves fail-closed behavior: an `OSError` returns false. There is no broad exception catch; only filesystem errors are converted to rejection. No new branch can accept an unreadable or malformed archive.

Mechanical grading over canonical `23d6745b888b492b92ae61e5dcaa5992c066f9c4..ea4916518eea1c8f73901d372ad8e1e38595e64b` reports the same two non-blocking grade-2 test functions already recorded at c9: `test-suite-layout.py::_literal_key_present` and `test-ui-reviewer-policy.py::main`; neither is changed by this repair. The repaired `_is_zip` and changed trace test remain above their applicable bars.

## Executed evidence

- Exact T-14 verify command from the plan: PASS — `Ran 27 tests ... OK`; receipt token assertion and all three git-ignore location probes passed.
- Exact mutant direct probe against the pinned `_is_zip`: printed `False`.
- Baseline-predicate replay of `GateEvidence.test_traced_results_require_replayable_zip_inside_run_ui`: expected RED — `FAILED (failures=1)`, with the corrupt-trace mutation receiving gate status `PASS` instead of required `FAIL`.
- `glob` plus `zipfile.is_zipfile` over committed `FEAT-1821-initial-red/ui/traces/*.zip`: `8 8`; all eight real archives accepted.
- `git diff --name-status c5fab956...ea491651...`: only the three scoped T-14 paths contain the repair; governance/review/run records were inspected for scope and excluded.

```yaml
VERDICT: PASS
DIGEST:
  headline: "V9-01 is closed at ea491651: central-directory ZIP parsing rejects PK-prefix garbage while all eight committed traces and every prior T-14 fail-closed rule pass."
  severity_max: none
  findings: []
  must_fix: []
  spec_violations: []
  code_grade: grade_2
  grade_2_reasons:
    - "tests/unit/test-suite-layout.py::_literal_key_present is an unchanged declarative test helper outside the T-14 V9-01 repair."
    - "tests/unit/test-ui-reviewer-policy.py::main is an unchanged declarative policy-contract runner outside the T-14 V9-01 repair."
  reviewed: "c5fab95615c035e97109f90bd4aa91fc2e4b78a5..ea4916518eea1c8f73901d372ad8e1e38595e64b"
  human_commits_in_scope: []
  open_questions: []
  files_touched: [".harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c9-fix.md"]
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-1821-ui-verification-lane/.harness/harness/features/FEAT-1821-ui-verification-lane/notes/review-harness-code-reviewer-c9-fix.md
```
