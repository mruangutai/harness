# Receipt — T-01, main session (DEC-174 direct) — 2026-11-27

Executed at the worktree tip (base 7694fa0f) with every T-01 file written, `HARNESS_AGENT_TYPE`
and `CLAUDE_PROJECT_DIR` unset.

## verify (verbatim from plan.yaml T-01)

Run as `bash` over the block extracted from plan.yaml. Result:

- `T-01 structure and smoke PASS; the baseline-passing corpus is graded in T-03`
- `tests/unit/test-feature-record.py`: `Ran 130 tests … OK`
- `tests/integration/test-validate-feature-json.py`: `ALL PASS`
- `check-plan-routes.py --canonical-reader-audit`: `0 unresolved reader site(s) across 110 Python file(s)`, exit 0

## Prescribed suite gate

- `run-unit-tests.py --kind unit`: exit 0. Every per-file line PASS; the only FAIL-prefixed lines
  are the four `BUG-1290 5a/5b/5c/5b` lines `tests/unit/test-factory-claim-mutation.py` prints at
  exit 0, as at e12381fd.
- `run-unit-tests.py --kind integration`: every file PASS except
  `tests/integration/test-typescript-typecheck.py` (no `node_modules/.bin/tsc`), the baseline's
  own failure.
- `check-plan-routes.py --canonical-reader-audit`: exit 0, zero unresolved sites.

## Deviations, recorded for the ship review

1. **Registrars are finer than one per module family.** `feature-record.py` registers through
   `_register_run_start`, `_register_run_end`, `_register_close_run`, `_register_judgements`,
   `_register_budget`, `_register_mission_and_pin`, `_register_spend` and `_register_proposal`:
   the runs family is split to hold grade 4, and budget is split so `propose-rework` keeps its
   place after `spend`. Argparse help and every usage error are byte-identical to e12381fd
   (checked against a `git archive` of the baseline).
2. **`plan-merge.py`'s `signed_task_hash` re-export is removed** (the verify requires it, #2569);
   its docstring no longer names the INV-40 import surface, and
   `check_state/feature_record.py`'s INV-40 comment names `plan_merge/approval.py` as the owner.
3. **`integration-durations.json`**: deleting the `test-feature-json-merge.py` weight moved the
   median, so `default_seconds` is the recomputed median (`5.515000000000001`), which
   `test-run-unit-tests-shards.py` pins as `statistics.median(weights)`.
4. **`test-check-plan-routes.py` case_19b** copies `feature_record/` (without `__pycache__`) beside
   its selectively copied modules. case_21 already copies every top-level `.py` and needed no
   change, so it stays at its baseline bytes and grade.
5. **Census and allow-list names**: `test-broad-catch-census.py` and
   `test-checker-structure-locks.py` name `feature_record/schema.py` (the census keys files by
   bin-relative path); `test-harness-yaml.py`'s guarded-import allow-list names `schema.py`.
6. **PF-42a75f8f**: the signed T-01 intent and BRIEF already carry the D-01 exception and do not
   say "only file and id" anywhere, so neither file was edited. The signed plan text stays as signed.
