# Receipt — harness-backend-dev — T-03 — record PR number from branch

## Verify: PASS

```
$ out=$(python3 .claude/skills/harness/bin/test-gh-sync.py 2>&1) || { printf '%s\n' "$out"; exit 1; }
$ printf '%s\n' "$out" | grep -q '^ok    record-pr writes the number when the branch has exactly one merged PR' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    record-pr leaves pr null when the branch has no merged PR' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    record-pr leaves pr null when the branch has two merged PRs' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    record-pr never overwrites a pr that is already an integer' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    record-pr --pr writes the number given without querying' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    ship records the pr and then the status' || exit 1
$ printf '%s\n' "$out" | grep -q '^ok    record-pr exits 0 on every branch case' || exit 1
$ printf '%s\n' "$out" | grep -q 'ALL PASSED' || exit 1
$ echo VERIFY-OK
VERIFY-OK
```

Tail of the run, showing all seven `ok` lines plus `ALL PASSED`:

```
ok    record-pr writes the number when the branch has exactly one merged PR
ok    record-pr leaves pr null when the branch has no merged PR
ok    record-pr leaves pr null when the branch has two merged PRs
ok    record-pr never overwrites a pr that is already an integer
ok    record-pr --pr writes the number given without querying
ok    ship records the pr and then the status
ok    record-pr exits 0 on every branch case

ALL PASSED
```

## HAZARD — T-02's `source_issues` work, before/after

```
$ grep -c source_issues .claude/skills/harness/bin/gh-sync.py .claude/skills/harness/bin/test-gh-sync.py
```

| File | Before | After |
| --- | --- | --- |
| `gh-sync.py` | 12 | 12 |
| `test-gh-sync.py` | 25 | 25 |

Unchanged — every edit was additive, via `Edit` with tight anchors, never a whole-file `Write`.

## RED FIRST — the pre-edit run against the unmodified `gh-sync.py`

All seven new cases were run against the tree BEFORE any production edit. Result: `7 FAILED`.
Per-case assertion failure (verbatim from that run):

1. `record-pr writes the number when the branch has exactly one merged PR` —
   `rc=1 pr=None log=['auth status\x01']`. Failed on `r.returncode == 0` (there was no
   `record-pr` subcommand yet; `main()`'s `die()` on `unknown command` exits 1) — `docPR1.get("pr")`
   was also still `None`, and no `pr list` call was ever made.
2. `record-pr leaves pr null when the branch has no merged PR` — `rc=1 pr=None`. Same
   `returncode == 0` failure; `pr` happened to already be `None` for the wrong reason
   (nothing ran), so only the `returncode` conjunct is what actually reddens this case.
3. `record-pr leaves pr null when the branch has two merged PRs` — `rc=1 pr=None`. Same
   shape as case 2.
4. `record-pr never overwrites a pr that is already an integer` — `rc=1 pr=314`. Failed
   on `r.returncode == 0` only — the fixture's `pr` was already `314` on disk and nothing
   ran to change it, so this case's real defect coverage (never querying, never
   overwriting with the fake's 999) was not yet exercised; only the exit-code conjunct
   reddened.
5. `record-pr --pr writes the number given without querying` — `rc=1 pr=None log=['auth
   status\x01']`. Failed on `r.returncode == 0` and `docPR5.get("pr") == 88` both.
6. `ship records the pr and then the status` — `rc=0 pr=None status='Done'`. `ship`
   already existed (T-01/FEAT-23), so `returncode == 0` and `status == "Done"` both
   already passed; the case reddened purely on `docPR6.get("pr") == 55` — `pr` was never
   written because `cmd_ship` did not yet call anything to record it.
7. `record-pr exits 0 on every branch case` — `rcs=[1, 1, 1]` vs. expected `[0, 0, 0]`.
   Failed on the list-equality assertion, all three sub-cases sharing the same
   `unknown command 'record-pr'` -> exit 1 cause as case 1.

## Implementation

- `.claude/skills/harness/bin/gh-sync.py`: added `_record_pr(feat_dir, repo, pr_arg=None)`
  (mirrors `_record_status`'s read/write shape), wired `cmd_ship` to call it immediately
  before its final `_record_status(feat_dir, "Done")`, added the `record-pr` subcommand
  and `--pr <n>` flag parsing in `main()`, and updated the usage string and module
  docstring.
- The `gh pr list` query is issued via a raw `subprocess.run` (wrapped in
  `gh_cost_log.measured`, matching `gh()`'s cost-logging shape) rather than through the
  existing `gh()` helper — `gh()` calls `skip()` on a non-zero return code, which
  `sys.exit(0)`s the whole process. That would have violated the intent's "never skip the
  caller's remaining work" requirement inside `cmd_ship` (the trailing status write must
  still run). A gh failure here is treated exactly like the zero-results case: one printed
  line, no write, normal return.
- `.claude/skills/harness/bin/test-gh-sync.py`: added `FAKE_GH_PR_LIST` (a fake `gh`
  driven by the `PR_LIST_JSON` env var for `pr list`, falling back to the existing
  fixture's other cases), `_pr_fixture()`, and the seven cases named in the plan.

## Scope discipline

Did not touch `gh_board.py`, `load_board`, or the `gh_board` import. Did not add a
`harness.json` key. Did not touch `plan.yaml`, `BRIEF.md`, or T-04's `cmd_closes` work
(absent from both files). No new test file was added — both edits landed in the two
files this task owns.
