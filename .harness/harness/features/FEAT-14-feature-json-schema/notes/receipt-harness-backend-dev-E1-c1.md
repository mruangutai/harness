# Receipt — harness-backend-dev — FEAT-14 E1 fix (guarded-import assertion)

## What changed

`.claude/skills/harness/bin/test-harness-yaml.py`,
`test_exactly_one_guarded_import_in_the_tree` (name unchanged). Replaced the single
`assert set(hits) == {"harness_yaml.py"}` with two assertions:

- **Assertion 1 (D-12, full strength, `==`)**: files where the `except ImportError` needle AND
  a yaml import token (`import yaml` / `from yaml`) co-occur in the SAME file — exact set
  `{"harness_yaml.py"}`.
- **Assertion 2 (general anti-fallback rule, `<=` subset)**: files where the needle occurs at
  all — subset of `{"harness_yaml.py", "feature_schema.py", "check-domain.sh"}`.

Docstring rewritten to describe the two-assertion rule instead of the old superseded
single-assertion contract. No other file touched.

## Verify

Invocation 1: `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`
Observed exit code: **0**
`test-harness-yaml.py` ran within this suite (it is registered in `INTEGRATION_SCRIPTS`); its
`test_exactly_one_guarded_import_in_the_tree` line reported `ok` and the file reported
`PASS test-harness-yaml.py`.

Invocation 2: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`
Observed exit code: **0**

## Confirmations

- Assertion 2 uses subset semantics — the literal line in the edited file is
  `assert set(guarded_hits) <= allowed, (...)`, not `==`.
- Assertion 1 remains exact-set equality (`==`), preserving D-12's original teeth at its correct
  (yaml-scoped) boundary.
- `feature_schema.py`, `validate-feature-json.py`, `feature-schema.json`,
  `test-validate-feature-json.py`, `run-unit-tests.sh`, `harness_yaml.py`, `check-domain.sh`,
  `check-state.sh`, `bash-write-guard.sh`, `validate-digest.py` were not opened for editing.
- No commit made (orchestrator holds the pen per DEC-153).

## Additional checks (P-07/P-09 — a green suite alone does not prove an assertion redden-able)

- **Latent-conflict check on `check-domain.sh`**: `git show HEAD:.claude/skills/harness/bin/check-domain.sh`
  contains only `import harness_yaml` (3 occurrences, lines 338/502/530), never a bare `import yaml`
  or `from yaml`. When T-06 adds its guarded `import feature_schema`, Assertion 1 (yaml-scoped) will
  not be affected — no conflict between the two assertions is latent today.
- **Substring safety re-verified, not assumed**: `python3 -c 'print("import yaml" in "import harness_yaml")'`
  → `False`.
- **Non-vacuity of both sets, replicated the scan standalone**: `guarded_hits = ['feature_schema.py',
  'harness_yaml.py']`, `yaml_guarded_hits = ['harness_yaml.py']` — both assertions are exercising a
  real, non-empty membership today, not passing on an empty set.
- **Mutant proof that Assertion 2 can redden** (P-07/P-09 protocol): appended `# mutant probe: except
  ImportError` to `.claude/skills/harness/bin/wayfind.py` (sha256 before:
  `007895f4...` full value recorded, see below). Predicted Assertion 2 would name `wayfind.py` as the
  offender. Ran `--kind integration`: reddened exactly as predicted —
  `FAIL test_exactly_one_guarded_import_in_the_tree: unexpected guarded-import file(s) outside the
  allowed set: {'wayfind.py'}`. Restored the file from a pre-mutation backup, re-hashed
  (`007895f48107ee3cf8f0d17164499281abee1efc442fb73b198e690c15ff9e07` before and after, identical),
  and confirmed `git status --porcelain` shows no entry for `wayfind.py`. Re-ran `--kind integration`
  afterward: exit 0, `test-harness-yaml.py` green again. This mutation was transient and fully
  reverted before this receipt was written — disclosed here per policy, not part of the delivered
  diff (delivered diff is exactly one file, `test-harness-yaml.py`).
