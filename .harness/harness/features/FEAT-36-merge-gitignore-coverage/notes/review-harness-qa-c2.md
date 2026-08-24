# QA gate — FEAT-36 — c2

**BLUF: PASS.** The exact T-01 verification command passed at review SHA `f494553bd9fbb987b4a19f91dcf4c3f37253fe38`; the required `feature` matrix is non-vacuous with exactly 23 unit plus 23 integration registrations (46 total), all executed and passing. No `MISCONFIGURED` or `KIND-DRIFT` output occurred.

## Pin and matrix

- Base: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e`
- Review: `f494553bd9fbb987b4a19f91dcf4c3f37253fe38`
- Reviewed range: `0fa8f336e55dc57bca09a9f7df0524a35195ee7e..f494553`
- T-01 `change_type`: `feature` (`plan.yaml:41-57`)
- Required kinds: `unit`, `integration` (`.harness/harness.json:40-49`); no UI predicate fires for this non-interaction, real-subprocess test/config delta.
- Exact required command and result (exit 0, 146.91s):

  ```sh
  python3 .agents/skills/harness/bin/test-merge-gitignore.py &&
  .agents/skills/harness/bin/run-unit-tests.sh --kind all
  ```

## Non-vacuous per-kind evidence

| Kind | Configured command | Registration / execution result |
| --- | --- | --- |
| unit | `.agents/skills/harness/bin/run-unit-tests.sh --kind unit` | PASS; 23 explicit registrations, all executed through `--kind all` |
| integration | `.agents/skills/harness/bin/run-unit-tests.sh --kind integration` | PASS; 23 explicit registrations, all executed through `--kind all` |

`run-unit-tests.sh:17-18,35-39` defines the two arrays and makes `all` execute their concatenation; its pre-execution drift checks fail loudly for unlisted `test-*.py` (`:47-60`) or disagreement with `integration.detect` (`:84-127`). The green exact command therefore establishes non-zero discovery/execution for both kinds, 46 total registrations, and no `MISCONFIGURED` or `KIND-DRIFT` finding. This corrects c1's inherited, incorrect integration count of 24.

The changed behavioral program independently passed all seven named cases (`7 passed; 0 failed`) before passing again as registered integration program `PASS test-merge-gitignore.py` in the same required command.

## Success-criterion coverage

- SC-01: `case_preserves_existing_content` asserts original distinctive bytes/order and one copy of every rule (`test-merge-gitignore.py:36-47`).
- SC-02: complete and incomplete `--check` cases assert exits, missing-rule diagnostics, and byte identity (`:50-73`).
- SC-03: absent and partial cases assert every rule exactly once and retained unrelated content (`:76-98`).
- SC-04: the second merge is byte-identical (`:101-110`).
- SC-05: c2's changed assertion is two-sided: a real invocation from the unrelated caller with an explicit target root creates/changes the initially absent requested target (`:113-125`), while the pre-existing caller `.gitignore` is byte-identical (`:120-126`). The c2 delta specifically replaces mere caller-file absence with this preservation assertion.
- SC-06: the named program is integration-only in the runner and represented in the integration configuration; this is exercised by the passing kind cross-check (`run-unit-tests.sh:17-18,84-127`).

## Continuity

F-02 remains an advisory, unchanged by the c2 delta: incomplete-check diagnostic validation still uses substring membership for every expected rule (`test-merge-gitignore.py:69-72`), so it would accept a fabricated superset diagnostic. This is neither a required-matrix failure nor evidence of a current production defect.

## Gate disposition

- `matrix_ok`: `true`
- Suite: `pass`; failures: `0`; exact gate exit status: `0`
- Coverage gaps: none for Phase-1 expectations (preservation, both check outcomes/read-only behavior, absent/partial targets, idempotence, and explicit-target/caller isolation).
- Findings / must-fix: none; F-02 retained as non-blocking advisory.
- Files touched: this note only.
