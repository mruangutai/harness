# T-01 corrective fail-first receipt — c1-r1

## Result

PASS — QA-03's four missing criterion-specific reds are reconstructed without changing final shipped behavior. The relevant pre-T-01 source is `d054384e^` (`60b8d4d99f50edab6a63352ea43ebbc4ffc09750`); its direct `test-gh-sync-record.py` and `test-gh-sync-ship.py` runners both exited 0, so the named preservation properties required narrow controlled live mutants. Each mutant was restored and its original SHA-256 reverified before its fixed-tip run.

## Criterion-specific controlled REDs and fixed-tip GREENs

| SC | Exact direct command | Controlled source state and actual RED | Fixed-tip counterpart |
| --- | --- | --- | --- |
| SC-08 — every eligible card reaches Done | `python3 tests/integration/test-gh-sync-ship.py` | **Reconstructed mutation proof** in `.claude/skills/harness/bin/gh-sync.py:2235`: changed `for num in sources + parents:` to `for num in sources:`, omitting the parent write. Exit **1**. Actual target failure: `FAIL  ship: card #40 reaches the done station` with `done=[41, 42, 50]` (the recorded parent `#40` is absent). | The same direct command at fixed tip exited **0**, including `ok    ship: card #40 reaches the done station` and `ALL PASSED`. |
| SC-12 — abandoned cards are excluded | `python3 tests/integration/test-gh-sync-record.py` | **Reconstructed mutation proof** in `.claude/skills/harness/bin/gh_board.py:211`: changed the terminal exclusion to `if station in factory_config.TERMINAL_STATIONS and station != "abandoned":`, admitting abandoned task `#43`. Exit **1**. Actual target failures, one for each active phase, were `FAIL  status <phase>: writes the exact shared projection without duplicates`; each fake write list contains `ITEM_43` (for example `OPT_PLAN` for plan). | The same direct command at fixed tip exited **0**, including `ok    status plan|ready|building|review: writes the exact shared projection without duplicates` and `ALL PASSED`; no expected-id set includes `ITEM_43`. |
| SC-13 — lifecycle transitions do not directly close ordinary issues | `python3 tests/integration/test-gh-sync-ship.py` | **Reconstructed mutation proof** in `cmd_ship.write_done` at `.claude/skills/harness/bin/gh-sync.py:2194`: after each Done placement, added `gh(["issue", "close", str(num), "--repo", repo], capture=False)`. Exit **1**. Actual target failure: `FAIL  ship: closes NO issue - no \`issue close\` argv anywhere in the run`; fake log contains `issue close 41 --repo implentio/fake`, `issue close 42 --repo implentio/fake`, `issue close 50 --repo implentio/fake`, and `issue close 40 --repo implentio/fake`. | The same direct command at fixed tip exited **0**, including `ok    ship: closes NO issue - no \`issue close\` argv anywhere in the run` and `ALL PASSED`. |
| SC-14 — open-child hold and in-run refresh prevent an incorrect parent result | `python3 tests/integration/test-gh-sync-ship.py` | **Reconstructed mutation proof** in `.claude/skills/harness/bin/gh-sync.py:2194`: removed `stations=stations` from the shared Done writer, leaving the station snapshot stale after writes. Exit **1**. Actual target failures: `FAIL  ship ORDERING: a parent whose only open children are cards THIS RUN lands reaches Done in that same run` with `done=[41, 42]` and `HELD — #40 waiting on open child #41 (not at done)`; and `FAIL  ship REFRESH: a source_issues entry that is itself a child of the parent, moved in step 5's own pass, still lets the parent land in the same run` with `done=[41, 50]` and the same stale hold. | The same direct command at fixed tip exited **0**, including both `ok    ship ORDERING...` and `ok    ship REFRESH...` assertions and `ALL PASSED`. |

The historical direct commands were intentionally executed separately, with no `&&` predecessor: `python3 tests/integration/test-gh-sync-record.py` (exit 0) and `python3 tests/integration/test-gh-sync-ship.py` (exit 0). That establishes why these are honestly labelled reconstruction mutation proofs rather than claimed historical failures.

## Restoration and signed verification

After every `gh-sync.py` mutation, SHA-256 restored to `1a3f6c7541aa1559cee9e82bcc995657a27ea5f0f737ff429fdd7855ce7e62b3`; after the `gh_board.py` mutation, SHA-256 restored to `93dace6fde685a38b2686561b0d55e899392fcaba83f6384619a2924114e4921`. `git status --porcelain --` for each mutated source path was empty after restoration.

The signed T-01 command was then run exactly at fixed tip and exited 0:

```sh
python3 tests/unit/test-gh-board.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-check-state-inv26.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-abandon.py
```

Every named integration runner ended `ALL PASSED`; the unit runner ended `all pass`.

## Scope and head

No production or test change remains from these probes. The full fixed-behavior HEAD exercised by the direct green counterparts and signed gate was `0e1fdc22f6f9f139cb79bc69c66e1185650864c1`; this corrective receipt is committed separately.
