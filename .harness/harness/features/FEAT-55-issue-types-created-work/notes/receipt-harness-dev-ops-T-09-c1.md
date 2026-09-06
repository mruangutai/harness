# Receipt — harness-dev-ops — T-09 — c1

## Task
Register the `issue_types_live` test kind in `.harness/harness.json`, per plan.yaml T-09
(`FEAT-55-issue-types-created-work`, line 1468). change_type: config, TDD-exempt.

## Change

Added one net-new entry to `test_kinds` in `.harness/harness.json`, matching the shape of the two
existing `locally_run` kinds (`omp_session_accessor`, `handoff_comprehension`):

```diff
diff --git a/.harness/harness.json b/.harness/harness.json
index 4c776b7a..f751e6f2 100644
--- a/.harness/harness.json
+++ b/.harness/harness.json
@@ -293,6 +293,13 @@
       "status": "locally_run",
       "runner_note": "requires the omp binary on PATH and live model credentials; this can never run in CI. Run on a credentialled host before a ship decision that changes the handoff contract, and record the result under the feature's notes/ directory."
     },
+    "issue_types_live": {
+      "detect": "tests/manual/probe-issue-types.py",
+      "exclude": ".claude/worktrees/**",
+      "cmd": "tests/manual/probe-issue-types.py",
+      "status": "locally_run",
+      "runner_note": "requires gh authenticated against the pinned github.repo to read that repository's native Issue Types; it creates nothing and can never run in CI, so run it on a credentialled host before a ship decision that touches the issue-type path and record the verdict under the feature's notes/ directory."
+    },
     "integration": {
       "detect": "tests/integration/**",
       "exclude": ".claude/worktrees/**|node_modules/**|vendor/**|.venv/**",
```

`cmd` is the probe's default invocation verbatim — no opt-in flag, no argument (D-19 read-only
default). `cmd` is non-null (DEC-187). `status: locally_run` (DEC-163, host-only probe). No
`excluded_because` or `signed` key added. Nothing else in the file touched: `test_matrix`, the
`github` block, and every other `test_kinds` entry are byte-identical to before (scoped diff above
is the entire change — one hunk, one added block).

## Verify — run verbatim from worktree root

Cross-checked the dispatch's quoted `verify:` string byte-for-byte against plan.yaml T-09's own
`verify:` block (plan.yaml:1478) before running — identical, no mismatch.

```
$ python3 -c "import json,sys; k=json.load(open('.harness/harness.json'))['test_kinds']['issue_types_live']; sys.exit(0 if k['cmd'] and k['status']=='locally_run' and k['detect']=='tests/manual/probe-issue-types.py' else 1)"
EXIT:0
```

No stdout (success prints nothing, as expected). Exit status 0 confirms `cmd` is truthy,
`status == 'locally_run'`, `detect == 'tests/manual/probe-issue-types.py'`, and that
`.harness/harness.json` is valid JSON (`json.load` did not raise).

## Note on a tool-path near-miss (self-caught, self-corrected, no residual effect)

My first two `edit` attempts targeted a mistakenly abbreviated section path
(`.harness/harness.json` instead of the worktree-qualified
`.claude/worktrees/harness/FEAT-55-issue-types-created-work/.harness/harness.json`) and landed —
successfully, per the tool — on the **main tree's** `.harness/harness.json`
(`/Users/molchairuangutai/GitHub/harness/.harness/harness.json`), producing a duplicate-key
mutation there while the worktree file remained untouched. Caught via `git diff` / `grep` cross-checks
against both paths before any verify or handoff; reverted with `git -C
/Users/molchairuangutai/GitHub/harness checkout -- .harness/harness.json` (confirmed clean, 0
matches for `issue_types_live` in the main tree afterward). Re-issued the edit against the correctly
worktree-qualified path; it landed exactly once, only in the worktree file, confirmed by `grep -c`
and `git status --short` on both trees before proceeding. Main tree is untouched by this task's
final state.

## Nothing committed

`git status --short` at worktree root shows only `M .harness/harness.json` as this task's change;
other modified/untracked paths listed belong to concurrent sibling tasks (T-01, T-11, DECISIONS*,
BRIEF.md, plan.yaml, tests/unit/test-issue-types*.py) and were not touched by this task. Nothing
staged, nothing committed.
