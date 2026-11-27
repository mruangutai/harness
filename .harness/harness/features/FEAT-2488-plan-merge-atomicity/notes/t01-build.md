# T-01 build: journaled pair write and journal recovery in harness_merge

Built main-session-direct under DEC-174 by BuildE_T01, the ungoverned builder for the main session. Worktree HEAD `3b954ec2`, base `2491336e`. No git writes were made. HARNESS_AGENT_TYPE and CLAUDE_PROJECT_DIR were unset for every run. Every receipt below is whole stdout+stderr with its exit code. Files sit in `notes/` and `notes/t01-build/` (C6).

## Files changed
- `.claude/skills/harness/bin/harness_merge.py`: adds the journal protocol (items 1–10).
- `tests/unit/test-harness-merge-journal.py`: new house-shape suite with 101 checks.
- `tests/integration/canonical-reader-classification.json`: adds one row, `harness_merge.py::_read_journal::json_string#1`. It sits immediately before the first `harness_yaml.py` row.
- `notes/red-t01-journal-unit.txt`: the red receipt.

`check-plan-routes.py`, `test-check-plan-routes.py`, `check_state/` and `union.py` are untouched (`t01-build/07-changed-files.txt`).

## Red (C3)
`red-t01-journal-unit.txt` was captured before any production edit. Its header records that `harness_merge.py` was byte-identical to `2491336e` at capture. Result: `FAIL - 22/25 checks failed`, exit code 1. Every case fails on the missing API (AttributeError, reported per case), or on behaviour: at base, `locked_update` writes straight through a diverged journal.

After the red, `case_journal_shape_refusals` was added (14 checks on malformed journals: schema, empty members, separator and `..` names, uppercase hex, hash mismatch, non-base64). To prove the final test file is also red at base, `t01-build/05-red-final-test-vs-base.txt` runs the final file against base `harness_merge.py`, both copied into a scratch tree: `FAIL - 23/26`, exit code 1.

## Green
- `t01-build/01-green-journal-unit.txt`: `PASS - 101/101`, exit code 0.
- Existing callers (SC-07), unedited, each exit code 0:
  - test-harness-merge: 28/28
  - test-feature-json-merge: 41/41
  - test-observations-merge: PASS
  - test-expertise-merge: PASS
  - test-inflight-registry: 168/168

  Receipts are `t01-build/02-*.txt`.

## Verify (literal, from plan.yaml)
- `t01-build/06-verify-T-01.txt` exits 0. The run_pool covers all 6 files (4 workers, 12.83s). The audit reports `0 unresolved reader site(s) across 101 Python file(s)`, and the API/docstring word check passes. The command text is in `t01-build/06-verify-T-01.command.sh`.
- Canonical-reader audit on its own: `t01-build/03-canonical-reader-audit.txt` reports 0 unresolved, exit code 0. Before the row was added, it reported `_read_journal json_string … live AST row absent from migration inventory`. That is the category the plan pinned, so the row was added as specified.

## Grade
`t01-build/04-code-grade-base-to-worktree.txt` uses code_grade's own gate semantics, with the head read from the working tree because commits are barred. The script that ran it is in `04-…command.py`. It mirrors D's c2 method. Result: `gated=71 high=0 reason_required=0 result=pass`.
- Every new or changed production function grades ≥ 4.
- Every test function grades ≥ 3. Four test cases sit at grade 3 on ABC: `case_pair_pending_after_publish`, `case_diverged_member`, `case_truncated_journal` and `case_replay_failure`.
- `locked_update` was 3 at base and is 4 now, so it is not gated. `_acquire_flock` (3 at base, unchanged) was not split.

## How the build maps to the spec (C5: no new journal surface)
- **Journal fields:** `schema` and `members[]`, each member carrying `name`, `before_sha256`, `after_sha256` and `after_b64`. Serialized with `json.dumps(sort_keys=True)` into `mkstemp(prefix=".harness-merge-tmp-")`, then flushed, fsync'd and moved into place with `os.replace` onto `<primary>.harness-merge.journal`.
- **fsync** happens on exactly two things: the journal's descriptor, and its directory after the rename. There is none in `replace_bytes`, none after either unlink, and none in `locked_update`.
- **Outcome classes:**
  - `MergeRefusal(5)` with JOURNAL UNREADABLE or JOURNAL DIVERGED.
  - `JournalPending`, raised with replay false by `_commit_published` after the journal is published, or with replay true by `_replay`.
  - Plain propagation for anything before the rename. The ValueError for a bad pair is a plain error of this kind.
- **Recovery entry point:** there is one, `recover_journals`. `locked_update` and `locked_pair_update` call it, and `_recover_journal` stays module-private.
- **Lock order:** the primary's lock first, then the other members' locks in journal order. The docstring names `plan.yaml.lock` before `feature.json.lock`.

## Choices inside the shapes, noted for review
- **`stat` import:** the task text lists `stat` among the new imports, but nothing in the pinned behaviour uses it, so it is not imported. An unused import would be dead weight. `base64`, `hashlib` and `json` were added. `binascii` is not needed, because `binascii.Error` is a `ValueError`.
- **Journal read failures:** `_read_journal` lets `FileNotFoundError` from the journal read propagate (the vanish case in `_journals_naming`). Any other `OSError` on that read becomes the existing UNREADABLE refusal ("anything else"), so the directory still fails closed through the same exit-5 class. JSON `RecursionError` gets the same treatment.
- **Same directory test:** `locked_pair_update` compares the two directories with `realpath`, so the same directory reached through a symlink is not refused. A pair with the same basename is refused as the same file.
- **Small helpers:** these keep every function at grade ≥ 4:
  - `_read_base` holds locked_update's read, unchanged, and is shared with the pair.
  - `_member_hashes`, `_member_image`, `_journal_member`, `_journal_bytes` and `_journal_names` support journal parsing and discovery.
  - `_replay_targets` and `_replay` run the replay.
  - `_pair_directory`, `_publish_journal` and `_commit_published` serve the pair write.
- **Module constants:** `JOURNAL_SCHEMA`, `_JOURNAL_TMP_PREFIX`, `_HEX_DIGITS` and `_UNREADABLE_HINT`. These name values the spec already pins and add no surface.
- **Fail-closed reach:** the test file checks that an unreadable journal also refuses a third file's `locked_update`, which is item 9's "every writer in the directory only when it is unreadable".
