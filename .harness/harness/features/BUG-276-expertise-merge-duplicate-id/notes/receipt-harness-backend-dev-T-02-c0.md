# Receipt — harness-backend-dev — BUG-276 T-02

## Task
Pin the duplicate-id refusal at the CLI boundary (exit 11, `AMBIGUOUS TARGET`, message
tokens, destination byte identity, absent-destination path) by adding
`case_duplicate_proposal_ids(root)` to `tests/integration/test-expertise-merge.py`,
registered in `_run_all_cases` immediately after `case_ops_target_grammar_well_formed(root)`.

## 1. Observed RED (before writing the case)

Ran the exact `verify:` block from plan.yaml before the case existed.

Command: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-expertise-merge.py` (bare
suite) exited **0** on its own — the pre-existing 211 checks were already green at this base,
as the task's own verify comment states ("The suite already exits 0 ... without these cases").

Running the **full** verify pipeline (three greps + the standalone `python3 -c` CLI probe)
failed at the first grep clause:

```
$ (out=$(env -u HARNESS_AGENT_TYPE python3 tests/integration/test-expertise-merge.py) &&
   printf '%s\n' "$out" | grep -q '^PASS  case27a: duplicate ids exit 11' && ...)
OVERALL_EXIT:1
```

Failing clause: `grep -q '^PASS  case27a: duplicate ids exit 11'` — no line by that name
existed because `case_duplicate_proposal_ids` had not been written yet. This is the expected
RED: the greps cannot match a case that does not exist.

## 2. Change

Added `case_duplicate_proposal_ids(root)` (three sub-cases a/b/c per intent) and one call site
`case_duplicate_proposal_ids(root)` in `_run_all_cases`, immediately after
`case_ops_target_grammar_well_formed(root)`. No other function, helper, fixture, or existing
`_run_all_cases` line touched. No new imports — reused `target`, `write_file`, `write_entries`,
`run_apply`, `check`, `hashlib` exactly as they already exist in the file.

## 3. Observed GREEN (after writing the case)

Re-ran the identical full verify pipeline:

```
OVERALL_EXIT:0
```

The three case27 marker lines, quoted verbatim from the run's stdout:

```
PASS  case27a: duplicate ids exit 11
PASS  case27b: identical duplicate ids exit 11
PASS  case27c: absent destination exits 11
```

Full sub-case check list from the same run (all PASS, 0 FAIL):
```
PASS  case27a: duplicate ids exit 11
PASS  case27a: message carries AMBIGUOUS TARGET, section, id and reason
PASS  case27a: destination bytes unchanged
PASS  case27b: identical duplicate ids exit 11
PASS  case27b: message carries AMBIGUOUS TARGET, section, id and reason
PASS  case27b: destination bytes unchanged
PASS  case27c: absent destination exits 11
PASS  case27c: message carries AMBIGUOUS TARGET
PASS  case27c: nothing created at the absent destination
```

## 4. No pre-existing case reddened

Bare suite run after the edit: 220 PASS, 0 FAIL (up from the pre-edit baseline of 211 PASS,
0 FAIL — the +9 delta is exactly the 9 new case27 checks; nothing else moved).

`git status --porcelain` shows only `tests/integration/test-expertise-merge.py` changed by me;
the other modified/untracked entries (`expertise-merge.py`, `plan.yaml`,
`test-expertise-ops.py`, T-01's receipt) are T-01's already-landed work, not mine.

## Non-goals honored

- Did not add a regression sub-case for exit 0/7/8 (already pinned by
  `case_add_only_compatibility` at line 614).
- Did not modify `case_ops_target_grammar_well_formed`, any other case, helper, or fixture.
- Did not touch `check-expertise.sh`, `expertise-merge.py`, or `test-expertise-ops.py`.
- No commit, no staging.

## Files touched
- `tests/integration/test-expertise-merge.py` (only file in scope)
