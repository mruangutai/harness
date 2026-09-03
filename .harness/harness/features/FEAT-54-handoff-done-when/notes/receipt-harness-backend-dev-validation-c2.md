# Backend engineer receipt — validation c2

**PASS.** `_handoff_pre_edit_cases` is now a grade-5 aggregator over two adjacent, coherent scenario helpers. The valid-existing-file/invalid-candidate scenario is isolated in `_handoff_valid_pre_edit_cases`; the invalid-UTF-8 existing-file scenario is isolated in `_handoff_invalid_utf8_pre_edit_case`. No production file or other test file was changed.

## Scoped proof

### Existing behavioral baseline (before edit)

Command, run from the assigned worktree:

```sh
python3 tests/integration/test-check-domain.py
```

Exit: `0`. Discovery/execution: one integration script executed directly. Its FEAT-54 handoff runner printed all **33** individually named cases, including the three pre-Edit cases named below.

### Code-risk gate (after edit)

The first filtering attempt used jq's unsupported `IN` filter and exited `3`; it produced no grade claim:

```sh
python3 .claude/skills/harness/bin/code-grade.py --json tests/integration/test-check-domain.py | jq -e '[.records[] | select(.qualname | IN("_handoff_valid_pre_edit_cases", "_handoff_invalid_utf8_pre_edit_case", "_handoff_pre_edit_cases"))] as $records | if (($records | length) == 3 and all($records[]; .grade >= 3)) then $records else error("expected exactly 3 graded delta functions, all grade >= 3") end'
```

The corrected scoped assertion command exited `0`:

```sh
python3 .claude/skills/harness/bin/code-grade.py --json tests/integration/test-check-domain.py | jq -e '[.records[] | select(.qualname == "_handoff_valid_pre_edit_cases" or .qualname == "_handoff_invalid_utf8_pre_edit_case" or .qualname == "_handoff_pre_edit_cases")] as $records | if (($records | length) == 3 and ($records | map(.grade >= 3) | all)) then $records else error("expected exactly 3 graded delta functions, all grade >= 3") end'
```

Relevant records (test bar `3`):

| Function | Line | Cyclomatic | Cognitive | ABC | Grade | Result |
|---|---:|---:|---:|---:|---:|---|
| `_handoff_valid_pre_edit_cases` | 4114 | 1 | 0 | 12.7 | 4 | PASS |
| `_handoff_invalid_utf8_pre_edit_case` | 4132 | 3 | 2 | 14.8 | 4 | PASS |
| `_handoff_pre_edit_cases` | 4163 | 1 | 0 | 3.2 | 5 | PASS |

The jq assertion requires exactly three matching records and every record's `grade >= 3`; therefore no changed/new helper can be silently ungraded. The command intentionally does not claim the whole legacy file is clean.

### Behavioral preservation (after edit)

Command, run from the assigned worktree:

```sh
python3 tests/integration/test-check-domain.py
```

Exit: `0`; wall time reported by the script invocation was `23.58 seconds`. Discovery/execution remained one directly executed integration script. The FEAT-54 runner again printed all **33** named cases, unchanged from baseline.

The preserved pre-Edit outputs were:

- `handoff pre-Edit blocks invalid candidate`
- `handoff blocked pre-Edit leaves file unchanged`
- `handoff pre-Edit unreadable existing file fails closed`

The moved assertions remain exact: the reconstructable invalid candidate must exit `2` and contain `non-empty`; the blocked edit compares the file's bytes with the saved pre-edit bytes; the invalid-UTF-8 case jointly requires exit `2`, combined stdout/stderr containing `cannot be reconstructed`, and byte-identical non-mutation. Its `finally` still restores the saved valid bytes.

## Files touched

- `tests/integration/test-check-domain.py`
- `.harness/harness/features/FEAT-54-handoff-done-when/notes/receipt-harness-backend-dev-validation-c2.md`

No assertions or case names were added, removed, weakened, or reordered. No formatter, linter, broad suite, or unrelated validation ran.
