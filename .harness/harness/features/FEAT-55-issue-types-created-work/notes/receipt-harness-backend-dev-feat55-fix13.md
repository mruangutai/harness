# Receipt — harness-backend-dev — FEAT-55 fix cycle 13

**Two edits, two files, both applied. Zero `SEVERITY: high` in the grader; all ten named
suites plus the unit driver are exit 0 / FAIL 0. Nothing committed.**

## Edit 1 — gating finding (SEVERITY high, T-08)

`.claude/skills/harness/bin/factory_decompose.py`: extracted the `doc["factory"] = {...}`
dict literal out of `write_factory`'s `transform` closure into a new module-level
`_factory_block(factory)` (placed immediately above `write_factory`, ~line 173). `transform`
now does `doc["factory"] = _factory_block(factory)`. Pure extraction — same keys, same sort
order on `issues`/`items`/`blocked_by`/`typed`, same `factory.get("typed", {})` default, same
`list(...)` materialisation of `edges.parent` and each `blocked_by` value.

## Edit 2 — falsified comment (low, T-10)

`tests/manual/probe-issue-types.py` `_classify` (~line 66): the comment claiming gh-sync's
`detect_issue_types` still appends `--repo` was false (F-02/D-22 removed the flag; `gh api`
has no `--repo` flag at all). Rewrote the sentence to state gh-sync.py now also calls
`capability_query_args(repo)` bare, same as this probe. Kept the still-true first clause
(never append `--repo` here). Comment-only; no test change, per the dispatch's own
instruction not to manufacture one.

## Verification

### 1. Grader

`code-grade.py --base/--head` needs an actual **commit** revision
(`rev-parse --verify <ref>^{commit}`), and nothing here may be committed. Convention used:
staged both files, `git write-tree` for the tree sha, `git commit-tree <tree> -p HEAD -m …`
for a **detached** commit object (never checked out — `git rev-parse HEAD` confirmed
`cd6a3c0d…` unchanged throughout), then `git reset` immediately to restore the unstaged
working tree.

```
$ git add .claude/skills/harness/bin/factory_decompose.py tests/manual/probe-issue-types.py
$ TREE=$(git write-tree)                      # cf0418f4917456090c6247da23abc8c0639ef874
$ git reset                                   # working tree restored to unstaged
$ COMMIT=$(git commit-tree $TREE -p $(git rev-parse HEAD) -m "wip: grading snapshot, not merged")
                                               # c99468bad3cd39dc5d4d897bd33ea88668c9c53f
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/code-grade.py \
    --base eb9d044e --head c99468bad3cd39dc5d4d897bd33ea88668c9c53f
rc=0
```

`grep -c "SEVERITY: high"` on the full output: **0**.

`write_factory.transform` does not appear in the diff-mode report at all — its edited body
hashes back to an earlier ancestor state now that the added `typed`-sort line moved into the
helper, so the diff-mode gate (body-hash change detection) no longer treats it as changed.
Confirmed both functions' grades directly with whole-file mode instead
(`code-grade.py .claude/skills/harness/bin/factory_decompose.py`, unaffected by diff
membership):

```
QUALNAME: write_factory.transform
CYCLOMATIC: 4
COGNITIVE: 4 (Sonar-style approximation)
ABC: 9.0
GRADE: 4
DRIVER: cognitive+abc
BAR: 4
RESULT: PASS

QUALNAME: _factory_block
CYCLOMATIC: 2
COGNITIVE: 0 (Sonar-style approximation)
ABC: 14.1
GRADE: 4
DRIVER: abc
BAR: 4
RESULT: PASS
```

Both grade 4 (bar is 4) — the mass moved into `_factory_block` and neither half re-fails.
(Whole-file mode also reports 3 pre-existing `SEVERITY: high` findings elsewhere in
`factory_decompose.py`, all predating this diff and outside the diff-mode gated set — consistent
with their absence from the `--base/--head` report above, and out of this task's scope.)

### 2. Ten suites, individually

| Suite | rc | `^FAIL ` count |
|---|---|---|
| tests/integration/test-factory-issue-types.py | 0 | 0 |
| tests/integration/test-factory-decompose.py | 0 | 0 |
| tests/integration/test-factory-integration.py | 0 | 0 |
| tests/unit/test-factory-gh.py | 0 | 0 |
| tests/integration/test-gh-issue-types.py | 0 | 0 |
| tests/integration/test-gh-sync.py | 0 | 0 |
| tests/integration/test-gh-backlog-issue-types.py | 0 | 0 |
| tests/unit/test-issue-types.py | 0 | 0 |
| tests/unit/test-issue-types-pin.py | 0 | 0 |
| tests/integration/test-anchor-directions.py | 0 | 0 |

### 3. Unit driver

`env -u HARNESS_AGENT_TYPE bash .claude/skills/harness/bin/run-unit-tests.sh`: rc captured in
a variable = **0**; `^FAIL ` line count = **0**.

### 5. `git status --porcelain`

```
 M .claude/skills/harness/bin/factory_decompose.py
 M .harness/harness/features/FEAT-55-issue-types-created-work/feature.json
 M .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-pm.md
 M .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-qa.md
 M tests/manual/probe-issue-types.py
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/research-FEAT-55-goalcheck-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-code-reviewer-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-qa-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-security-reviewer-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/notes/review-harness-ui-reviewer-c1.md
?? .harness/harness/features/FEAT-55-issue-types-created-work/observations/harness-code-reviewer.md
```

Exactly the two named source files are `M`. Everything else (`feature.json`, two
`observations/*.md`, five `notes/*.md` untracked, one `observations/*.md` untracked) is
sibling/tooling activity present before this dispatch started (this task never wrote to any
of them) — reported per O-06, not reverted.

## Outcome

Both edits landed and hold. No revert was needed.
