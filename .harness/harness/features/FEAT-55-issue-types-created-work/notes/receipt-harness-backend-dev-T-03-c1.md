# Receipt — harness-backend-dev — T-03 — FEAT-55-issue-types-created-work

## Task
T-03: Write the failing integration test for gh-sync open — typing, label suppression,
refusal and rerun. `change_type: scaffolding`.

## File created
`tests/integration/test-gh-issue-types.py` (only file touched; new, ~500 lines).

It replicates the fake-`gh` idiom from `tests/integration/test-gh-sync.py:31-56,177-178`
(same log-append convention, `\001`-joined argv, `issue create` numbering off
`grep -c`) and adds the three new call shapes T-03's intent specifies: `issueTypes`
(capability query, five `FAKE_TYPES` states — absent/available/partial/nobug/failed),
`--jq .node_id` (returns `I_node<n>`), and `updateIssue` (honors `FAKE_TYPE_APPLY=fail`).
The feature-directory fixture is a BRIEF + a four-task `plan.yaml` (bugfix/config/logic/
feature change_types) + a `sync:true` harness.json, with a `stage(..., github=...)`
hook for pre-seeding `feature.json`'s `github` block per case (F, G(rerun), H, J, K).

All twelve cases (A B C D E F G H H2 I J K) are present, each labelled with the literal
`CASE <letter>:` marker inside a `check()` message (grepped by this task's verify).
Assertions are per-issue (node id + type id pairs, or exact label lists), never a total
count, per the intent's explicit instruction.

## Pre-edit note
`.claude/skills/harness/bin/gh-sync.py` and `tests/integration/test-gh-sync.py` were
read but not modified — confirmed by the `git status --porcelain` below. T-04 (not this
task) implements the behaviour; T-03's product is red by design.

## Why the RED is for the right reason, per case (not a fixture crash)
Ran `python3 tests/integration/test-gh-issue-types.py` directly (full transcript below,
also reproduced by the verify block). No traceback, no case skipped after an unguarded
exception — every one of the 33 failing `check()` lines is a genuine boolean mismatch:

- **A/E**: `updates=[]` — gh-sync.py never calls the `issueTypes`/`updateIssue` route at
  all today, so no per-issue type id exists to find (parent/Bug/Feature/Task/override
  cases all empty).
- **B/C/I**: today's `bug`/`chore` labels are still present on every create — the
  label-suppression-under-`available` and the one-line diagnostic (`^gh-sync: issue
  types `) don't exist yet, so the count is exactly 0, not 1.
- **D**: same — the rerun still prints zero diagnostic lines (rerun itself is
  correctly a no-create no-op already, which is why that assertion is `ok`).
- **F/K**: today's code never detects capability or refuses — it exits 0 and proceeds
  to create every not-yet-recorded issue, so "zero creates" and "non-zero exit" both
  fail for the true reason (refusal logic is simply absent). The remnant's provenance
  assertion also fails, but for an even sharper reason than "stays 'created'": today's
  `save_recorded` (gh-sync.py:857-863) rewrites `github:` from only
  `{milestone,parent,attached,issues,source_issues}` and drops any `typed` key
  entirely on every write — so the pre-seeded remnant's provenance is not merely
  un-promoted, it is erased outright. That is exactly the ordering/preservation defect
  T-04 section 6 exists to fix, not a fixture bug (the seeded `github.issues["T-01"]`
  itself IS preserved correctly, confirming the fixture and read path are sound).
- **G/H/H2**: same erasure — `typed` never round-trips today, so "created" is never
  observed, the backfill call never happens (log shows only `label create`/`auth
  status`), and the parent's `adopted` marker is likewise absent after the run.
- **J**: this is the one case where the current absence of `typed`-handling happens to
  match the assertion (absent stays absent) — hence J is `ok` throughout. That is
  correct and expected: J is the fail-safe direction, and it is the one behavior
  today's code already gets right by having no `typed` logic at all. It stays in the
  suite as the regression guard for T-04, which must not start writing to it.

Every case ran to completion and reported a real, attributable failure (or, for J, a
real pass for the right reason) — none crashed on a fixture bug, import error, or
unguarded exception.

## Verify — run verbatim from the worktree root

Cross-checked against plan.yaml's own T-03 `verify:` block (`plan.yaml:665-674`) —
identical to the dispatched string.

```
$ python3 -c "import ast; ast.parse(open('tests/integration/test-gh-issue-types.py').read())" || exit 1
$ for c in A B C D E F G H H2 I J K; do
    grep -qF "CASE $c:" tests/integration/test-gh-issue-types.py || { echo "MISSING case $c ..."; exit 1; }
  done
$ for s in IT_feature IT_bug IT_task IT_defect IT_epic IT_maintenance updateIssue issueTypes 4242 adopted created partial nobug github.issue_types; do
    grep -qF "$s" tests/integration/test-gh-issue-types.py || { echo "MISSING required assertion string: $s"; exit 1; }
  done
$ python3 tests/integration/test-gh-issue-types.py && { echo "UNEXPECTED PASS: this test must be RED before T-04"; exit 1; }
[... full case-by-case FAIL/ok transcript, 33 FAILED, exit 1 ...]
$ echo "RED as required - all twelve cases present"
RED as required - all twelve cases present
```

Full raw transcript captured this run (33 FAILED, script exit 1); the verify script's
final echo fired and the whole block exited 0, matching acceptance.

## Scope confirmation

```
$ git -C /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-55-issue-types-created-work status --porcelain -- tests/integration/test-gh-sync.py .claude/skills/harness/bin/gh-sync.py tests/integration/test-gh-issue-types.py
?? tests/integration/test-gh-issue-types.py
```

Only the new file is untracked/changed. `gh-sync.py` and `test-gh-sync.py` are
byte-identical to HEAD.

## Nothing committed, nothing staged.

## Open questions
None.
