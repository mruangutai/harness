# Receipt — harness-backend-dev — T-01 — c1

## Task

FEAT-55-issue-types-created-work · T-01 · "Write the failing unit test for the issue-type
mapping and capability classifier" · change_type: scaffolding.

Files created (only these two, per the dispatch's non-goals):
- `tests/unit/test-issue-types.py`
- `tests/unit/test-issue-types-pin.py`

`gh_issue_types.py` was NOT created (T-02's job). No other file was touched.

## Note on a mid-task write-location correction

My first pass wrote both files with a relative path, which resolved against the OMP session's
default cwd (the main checkout, not this worktree) instead of the worktree — the exact failure
mode Expertise G-18 names. Caught it before running verify (the files were missing from the
worktree), removed the two stray untracked files from the main checkout (`git status --porcelain`
there showed only `??` on both, so nothing tracked was touched), and rewrote both files with the
full absolute worktree path. Confirmed via `git status --porcelain` in both trees: main checkout
clean of these two names; worktree shows only the two new `??` entries.

## Verify (verbatim, cross-checked against plan.yaml's own T-01 `verify:` block — identical)

Run from the worktree root:

```
$ python3 -c "import ast; ast.parse(open('tests/unit/test-issue-types.py').read())" || exit 1
for w in bugfix feature logic api cross_module frontend ai_behavior docs config scaffolding infra ci bug chore enhancement; do
  grep -q "[\"']$w[\"']" tests/unit/test-issue-types.py || { echo "MISSING enumerated value: $w"; exit 1; }
done
grep -q "UnknownWorkNature" tests/unit/test-issue-types.py || { echo "MISSING the unrecognised-value assertion"; exit 1; }
for s in type_for_change_type type_for_nature type_for_parent overrides_from_config classify_capability query_failed capability_query_args node_id_args apply_type_args missing_types refusal_text Defect Story Epic Maintenance; do
  grep -qF "$s" tests/unit/test-issue-types.py || { echo "MISSING the assertion group naming: $s - every numbered assertion group in this task's intent must be present, so an OMITTED group fails this gate as loudly as a failing one"; exit 1; }
done
python3 tests/unit/test-issue-types.py && { echo "UNEXPECTED PASS: this test must be RED before T-02"; exit 1; }
python3 -c "import ast; ast.parse(open('tests/unit/test-issue-types-pin.py').read())" || exit 1
grep -qF ".harness/harness/docs/DECISIONS.md" tests/unit/test-issue-types-pin.py || { echo "MISSING the DECISIONS.md half of the pin guard"; exit 1; }
grep -qF ".claude/skills/harness/references/github-mirror.md" tests/unit/test-issue-types-pin.py || { echo "MISSING the github-mirror.md half of the pin guard"; exit 1; }
grep -qF "whether a target repository supports native Issue Types" tests/unit/test-issue-types-pin.py || { echo "MISSING the pinned-row extraction pattern"; exit 1; }
grep -qF "DRIFTED" tests/unit/test-issue-types-pin.py || { echo "MISSING the drift failure - a missing pin and a drifted pin must fail separately"; exit 1; }
python3 tests/unit/test-issue-types-pin.py && { echo "UNEXPECTED PASS: the pin guard must be RED until T-11 and T-12 write the row"; exit 1; }
echo "RED as required - all twelve assertion groups plus the standing pin guard present"
```

**Output:**

```
Traceback (most recent call last):
  File ".../tests/unit/test-issue-types.py", line 36, in <module>
    import gh_issue_types
ModuleNotFoundError: No module named 'gh_issue_types'
ok    MISSING PIN: .../.harness/harness/docs/DECISIONS.md carries the row
FAIL  MISSING PIN: .../.claude/skills/harness/references/github-mirror.md carries the row
        pattern not found in .../.claude/skills/harness/references/github-mirror.md
FAIL  DRIFTED PIN: the two extracted rows are identical
        skipped — at least one pin is missing, see the MISSING PIN failures above

2 FAILED
RED as required - all twelve assertion groups plus the standing pin guard present
```

Exit code of the whole verify block: **0** (the intermediate `&& { ...; exit 1; }` traps never
fired, meaning both `python3 tests/unit/...py` runs correctly exited non-zero, and the block
reached its final `echo` — the documented success signal).

Note: the DECISIONS.md half of the pin already reports `ok` — a concurrent documentor segment
(`DocsT11`) appears to have already landed the pinned row into DECISIONS.md while this task ran.
That does not make the pin guard green: `github-mirror.md` (T-12, not yet run) still lacks the
row, so `classify_capability`'s sibling half correctly stays RED via the MISSING-PIN and the
skipped DRIFTED check. This is exactly the "one file writes first" case section 13 anticipated —
presence is asserted per file before equality, so a partially-landed pin fails loudly rather than
being masked by a two-absent-values-compare-equal false green.

## RED evidence, per file, standalone

### `tests/unit/test-issue-types.py` — red because `gh_issue_types` does not exist (T-02 writes it)

```
$ python3 tests/unit/test-issue-types.py
Traceback (most recent call last):
  File "/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work/tests/unit/test-issue-types.py", line 36, in <module>
    import gh_issue_types
ModuleNotFoundError: No module named 'gh_issue_types'
exit code: 1
```

### `tests/unit/test-issue-types-pin.py` — red because the pinned row is not (yet, in full) present in both files

```
$ python3 tests/unit/test-issue-types-pin.py
ok    MISSING PIN: /Users/.../FEAT-55-issue-types-created-work/.harness/harness/docs/DECISIONS.md carries the row
FAIL  MISSING PIN: /Users/.../FEAT-55-issue-types-created-work/.claude/skills/harness/references/github-mirror.md carries the row
        pattern not found in /Users/.../FEAT-55-issue-types-created-work/.claude/skills/harness/references/github-mirror.md
FAIL  DRIFTED PIN: the two extracted rows are identical
        skipped — at least one pin is missing, see the MISSING PIN failures above

2 FAILED
exit code: 1
```

## Coverage against the intent's twelve assertion groups + section 13

All twelve numbered groups present as one-assertion-per-value checks in
`test-issue-types.py`: (1) 12 separate `type_for_change_type` assertions, `feature -> "Task"`
called out by name as D-18; (2) 3 separate `type_for_nature` assertions; (3) `type_for_parent`;
(4) `UnknownWorkNature` raised (not a None return) for both resolvers, message asserted for both
the offending value and "no issue type is mapped"; (5) six override cases keyed by canonical
name, including the Bug-rename-leaves-Task-alone fall-through and the change_type-string-is-not-
a-key negative case; (6) `overrides_from_config` five cases including the out-of-vocabulary-key
drop; (7) `classify_capability`'s four discriminator cases, each field asserted separately;
(8)-(10) the three gh argv builders, each element-level assertion; (11) `missing_types` both
cases; (12) `refusal_text` asserting the type name, the canonical `github.issue_types.Task` key,
and the repo string as three separate checks.

Section 13 (`test-issue-types-pin.py`): the pin pattern used verbatim from the intent, three
separate failures (missing-in-DECISIONS.md, missing-in-github-mirror.md, drifted), presence
asserted before equality, and the row's full text never duplicated as a third copy.

## Non-goals honored

- `gh_issue_types.py` not created.
- No other file edited.
- Nothing staged or committed (confirmed via `git status --porcelain` showing only the two `??`
  entries under my control in the worktree; the four `M` entries — DECISIONS.md,
  DECISIONS-INDEX.md, BRIEF.md, plan.yaml — are concurrent sibling/documentor activity, not mine).
- No project-wide suite run; only this task's own `verify:` block, verbatim, was executed.
