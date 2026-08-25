# QA gate — T-01: PASS

**Conclusion:** The pinned change adds seven red-capable real-process cases, registers them as integration-only, and leaves `merge-gitignore.sh` byte-identical. The required matrix commands passed with no runner configuration or kind-drift finding.

## Scope and matrix

- Reviewed `ac8533876d5539bfa5db50802b3a3c321add89a8` against `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`.
- Actual behavioral asset crosses the test/process boundary; its floor is `unit` and `integration` (`.harness/harness.json:22-26`). The accompanying runner/config registration is config only and adds no kind. No UI interaction exists, so the feature UI predicate does not fire.
- The added test is explicitly registered in `INTEGRATION_SCRIPTS` (`run-unit-tests.sh:18`) and in `test_kinds.integration.detect` (`harness.json:118-122`); it is intentionally absent from `UNIT_SCRIPTS`, as the explicit integration entry takes precedence over the catch-all unit detector.
- The plan scalar exactly matches the supplied command at `plan.yaml:55-57`. Per-kind commands were run individually rather than redundantly running the all-kinds wrapper.

## Phase 1 expectations and coverage delta

Before reading the diff, the brief required independent real-utility cases for: preserving existing bytes/order; complete and incomplete read-only `--check`; absent and partial target rule uniqueness; second-merge byte idempotence; and explicit-root/caller-cwd independence. It also required integration registration and unchanged production unless a failing pre-production test justified a fix.

All expectations are present in the added test, with assertions at:

- SC-01: `test-merge-gitignore.py:36-47` — `preserves_existing_content`.
- SC-02: `:50-59` and `:62-73` — `check_complete_is_read_only`, `check_incomplete_reports_missing_and_is_read_only` (including every missing rule and byte equality).
- SC-03: `:76-84` and `:87-98` — absent and partial cases, each rule exactly once plus retained unrelated content.
- SC-04: `:101-110` — `second_merge_is_byte_identical`.
- SC-05: `:113-123` — `explicit_project_root_ignores_caller_cwd`.
- SC-06: registration above plus production tree-object/history evidence below.

Delta: none. No missing behavioral case or assertion gap found.

## Required-kind results

| Kind | Presence and named evidence | Exact command | Result |
|---|---|---|---|
| unit | The `--kind unit` invocation itself runs the changed runner/config binding before any unit script: its union drift scan includes `test-merge-gitignore.py` and its kind cross-check requires the exact integration-detect literal (`run-unit-tests.sh:42-127`). The successful command is concrete presence evidence for the two changed registrations; all 23 named unit scripts then printed `PASS`. The behavioral case remains integration-only by explicit precedence. | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | Exit 0; 23 named runner scripts passed; the binding checks returned 0 before them, so `test-merge-gitignore.py` was present in the union and its matching integration literal was present. No named assertion failures, load/import/collection errors, `MISCONFIGURED`, or `KIND-DRIFT`. |
| integration | Changed `test-merge-gitignore.py`; seven named cases listed above. The integration runner directly invoked it and printed all seven PASS lines. | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | Exit 0; all 23 runner script entries passed. Changed-surface transcript: `PASS preserves_existing_content`; `PASS check_complete_is_read_only`; `PASS check_incomplete_reports_missing_and_is_read_only`; `PASS absent_target_receives_each_rule_once`; `PASS partial_target_retains_present_rule_and_adds_missing_once`; `PASS second_merge_is_byte_identical`; `PASS explicit_project_root_ignores_caller_cwd`; `7 passed; 0 failed`; `PASS test-merge-gitignore.py`. No `MISCONFIGURED` or `KIND-DRIFT` output. |

Both commands ran named tests and returned normally; there was no no-match, collection, import, syntax, or tooling failure. Thus neither a MISCONFIGURED state nor kind drift occurred.

## Test-first and production-scope audit

A temporary executable wrapper, outside the checkout, delegated to the real utility but changed only successful `--check` exits to `1`. Running:

```sh
MERGE_GITIGNORE_BIN=/tmp/feat36-merge-gitignore-mutant.sh python3 .agents/skills/harness/bin/test-merge-gitignore.py
```

returned exit **1** with this changed-surface transcript: six PASS cases; `FAIL check_complete_is_read_only:`; `6 passed; 1 failed`. The wrapper was removed immediately. This proves the complete-check assertion can redden under its intended controlled mutant, rather than merely passing vacuously.

Git history contains exactly one commit in range, `ac8533876… [harness:t-01] cover merge-gitignore behavior`; its changed-path list contains the new test, runner, config, and feature records, but not `merge-gitignore.sh`. More strongly, both base and target resolve `.agents/skills/harness/bin/merge-gitignore.sh` to identical tree object `4610430764205c16a627edc9764a37dcb54af75c`. There is therefore no production edit whose ordering could violate test-first; the red-capable test and untouched-production history satisfy the audit.

No files besides this QA artifact were modified.
