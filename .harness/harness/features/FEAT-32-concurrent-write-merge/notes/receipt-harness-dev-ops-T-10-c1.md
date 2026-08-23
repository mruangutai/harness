# Receipt — harness-dev-ops — T-10 (c1)

## Conclusion

PASS. Both edits made, verify exits 0, runner restored (`--kind unit` and `--kind integration` both
run and exit 0), `--check-kinds` reports agreement, `test-run-unit-tests-kinds.py` is 23/23.

## Premise correction (confirmed at the current tree, not taken on faith)

The dispatch's intent instructed appending SEVEN paths to `test_kinds.integration.detect`, including
`test-validate-digest.py` and `test-check-domain.py`, on the stated grounds those two were absent
(measured at `c32f332`/`62f861c`). At the current tree both are **already present**:

```
$ python3 -c "... split('.harness/harness.json')['test_kinds']['integration']['detect'] on '|' ..."
.claude/skills/harness/bin/test-validate-digest.py   (position 7 of 18)
.claude/skills/harness/bin/test-check-domain.py       (position 11 of 18)
```

DEC-197's recorded fix ("name each file in `integration.detect` explicitly") had already landed
since that measurement. I appended only the **5** genuinely-absent paths, not 7. The dispatch itself
authorized this: "Verify this yourself... Append only the paths that are genuinely absent... Do NOT
append a duplicate."

**Count: 5 appended, 2 already present (not touched).**

## Files touched

- `.claude/skills/harness/bin/run-unit-tests.sh:18` — appended `"test-harness-merge.py"
  "test-plan-merge.py" "test-observations-merge.py" "test-inflight-registry.py"
  "test-dispatch-guard.py"` to `INTEGRATION_SCRIPTS`. `UNIT_SCRIPTS` (:17), drift detector, and
  everything else in the file: byte-unchanged (confirmed via `git diff` — single-line diff only).
- `.harness/harness.json` — appended the same five paths (each prefixed
  `.claude/skills/harness/bin/`) to `test_kinds.integration.detect`. `test_matrix`, `budgets`,
  `github`, and everything else: byte-unchanged (confirmed via `git diff` — single-line diff only).

Drift-detector inventory check (bin/test-*.py present in neither array, before this edit): exactly
`test-dispatch-guard.py`, `test-harness-merge.py`, `test-inflight-registry.py`,
`test-observations-merge.py`, `test-plan-merge.py` — 5, matching the dispatch's prediction. No sixth
found.

## Task's `verify:` — cross-checked against plan.yaml T-10 before running, byte-identical

Ran under the worktree's default shell (Bash tool defaults to zsh; verified with `bash -c` per
G-02):

```
$ bash -c '<verify block>'
VERIFY EXIT: 0
```

The script only echoes captured output on any failure branch; on success it prints nothing but the
final `VERIFY EXIT: 0` — that is by design, not a truncation (confirmed: `wc -l` on the output = 3
lines total: blank, `VERIFY EXIT: 0`, `[exited with code 0]`).

## Three extra measurements

1. **`--check-kinds` verbatim, after edit:**
   ```
   check-kinds: the script arrays and test_kinds.integration.detect agree.
   ```
   Exit code: 0. Matches the dispatch's prediction exactly — no unregistered-name error, no
   KIND-DRIFT lines.

2. **`test-run-unit-tests-kinds.py`: 23 of 23 cases passed** (full output captured; all `ok` lines,
   including case 1's "exactly zero KIND-DRIFT lines" and case 2/3's drift-direction assertions on
   synthetic mutants). Full 23/23 restored.

3. **`--kind unit`: runs tests again, exit code 0.** 187 `^PASS ` lines, 0 `^FAIL ` lines across the
   full unit run (19 registered scripts, output ~65KB, tail confirms
   `81 of 81 cases passed` / `PASS test-context-watch.py` / `UNIT EXIT CODE: 0`).

## Word "ERROR" — not gated

Per the dispatch's explicit instruction, no grep for `ERROR` was added anywhere; the mechanical gate
used is exactly: exit 0 from the runner, no `^FAIL ` line, and the five per-file `^PASS` assertions.
Confirmed 0 `FAIL` lines in the full integration output captured during earlier ad-hoc runs.

## DEC-197 citation (for the main session's commit message — I do not commit)

`DEC-197 — A test file matching two detect globs resolves to the explicit kind, and the record is the
enforcement`

## Scope

Did not touch: `dispatch-guard.sh`, `test-dispatch-guard.py` (content), `validate-digest.py`,
`test-validate-digest.py` (content), `check-domain.sh`, `test-check-domain.py` (content),
`feature_schema.py`, `.gitignore`, `.harness/team-config.yaml`, `.claude/agents/*.md`,
`harness-spec-driven/SKILL.md`, `harness-expertise/SKILL.md`,
`.claude/skills/harness/templates/plan.yaml`, `plan-merge.py`, `harness_yaml.py`,
`inflight_registry.py`, `test-inflight-registry.py` (content), `feature.json`, `STATE.md`, task
statuses in `plan.yaml`. Did not enumerate issue #639's files anywhere in either edited file or this
receipt.

## Open questions

None. No boundary crossings, no ambiguity requiring escalation.
