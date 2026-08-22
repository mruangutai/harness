# T-05 receipt — upgrade-config.py budgets-key propagation

## Answer

`budgets` keys already propagate generically. No production change to
`upgrade-config.py`. Settled by reading:

- `.claude/skills/harness/bin/upgrade-config.py:86-88` — `merge()` recurses into
  any key that is a dict on both sides (`isinstance(tv, dict) and
  isinstance(out[k], dict)`), with `budgets` given no special case anywhere in
  the file (no occurrence of the string `budgets` in the file before this task).
- `.claude/skills/harness/bin/upgrade-config.py:79-83` — inside that recursion, a
  key absent from the project's dict is added at the template's value
  (`if k not in out: ... out[k] = tv`).

A project's `budgets` object is exactly such a nested dict, so a new leaf key
(`orchestrator_context_warn_tokens`) travels the same path that already adds a
new top-level key like `schema_version`'s siblings. This is stated in
`test-upgrade-config.py`'s module docstring per the dispatch's instruction.

## Deliverable

Added one case (case 8, `check(...)` at the end of the CASES list) to
`.claude/skills/harness/bin/test-upgrade-config.py`, exercising the CLI
subprocess path (not `merge()` in-process): a fixture project's
`.harness/harness.json` carries `"budgets": {}`, the fixture template's
`harness.json` carries `"budgets": {"orchestrator_context_warn_tokens": 200000}`,
`upgrade-config.py <root> --templates <fixture_tdir>` is run (no `--check`, so
it actually writes), and the merged file on disk is read back and asserted to
equal `200000` for that key (value, not presence).

## TDD proof (no-production-change branch)

1. Clean run against the real `upgrade-config.py`, case included: **10/10, exit 0.**
2. Mutant: copied `upgrade-config.py` and `harness_yaml.py` to the scratchpad
   (`/private/tmp/.../scratchpad/upgrade-config-mutant.py`), replaced the
   recursive-merge branch (`out[k] = merge(out[k], tv, here, added)`) with
   `pass  # MUTANT: nested-dict recursion disabled, T-05 red proof`. Read the
   mutated file back and grepped for that exact string to confirm the mutation
   applied before running tests.
3. Ran the suite with `UPGRADE_CONFIG_BIN` pointed at the mutant: **9/10, exit 1**
   — only case 8 (the new budgets case) reddened (`budgets={}` instead of
   `{"orchestrator_context_warn_tokens": 200000}`); every other case still
   passed, confirming the mutation was isolated to the targeted behavior.
4. Deleted the mutant copies. `git diff --stat -- .claude/skills/harness/bin/upgrade-config.py`
   is empty (verified below) — the real file is unmutated.

## Verify block (verbatim from plan.yaml T-05, all three lines)

```
python3 .claude/skills/harness/bin/test-upgrade-config.py
# -> 10/10 cases passed. exit 0

test "$(python3 .claude/skills/harness/bin/test-upgrade-config.py | grep -cE '^[0-9]+/[0-9]+ cases passed\.$')" = "1"
# -> exit 0

test "$(python3 .claude/skills/harness/bin/test-upgrade-config.py | grep -oE '^[0-9]+/[0-9]+' | head -1 | cut -d/ -f1)" -ge 10
# -> exit 0 (count is 10, floor was 9 baseline / 10 required)
```

Case-name proof (by name, per the dispatch's instruction not to trust the
count alone): the new case's name, printed by the harness itself, is exactly:

```
a new budgets key (orchestrator_context_warn_tokens) propagates from the template at the template's value, 200000
```

— visible as `ok` in the clean run and as `FAIL` (with `budgets={}` in the
detail) in the mutant run above.

## Kind-drift check (hard constraint 2)

`bash .claude/skills/harness/bin/run-unit-tests.sh --check-kinds` →
`check-kinds: the script arrays and test_kinds.integration.detect agree.`
exit 0. No new `bin/test-*.py` file was added — `test-upgrade-config.py` was
already registered — so no array/kind edit was needed or made.

## Hard constraint 1

`.harness/harness.json` was not touched. `git diff --stat` for it is empty
(not shown separately; only the two in-scope files were ever opened for
editing).

## Files touched

- `.claude/skills/harness/bin/test-upgrade-config.py` (added: docstring note +
  case 8)
- `.claude/skills/harness/bin/upgrade-config.py` — opened, read, **not
  modified** (diff --stat empty, confirmed above)
