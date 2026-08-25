# Receipt — harness-backend-dev — T-02 (c1, this dispatch: red-first case for classify from a linked worktree)

## BLUF

Added two new cases (m) and (n) to
`.claude/skills/harness/bin/test-worktree-terminal.py`, scoped to that ONE file per the
dispatch. Case (m) — `classify()` called with `root` set to a real linked worktree (built with a
real `git worktree add`, not just a directory tree) — is **RED against today's unfixed
`worktree_terminal.py`**, exactly reproducing the operator's measured defect: the main checkout
survives the skip check, fails `_split_owner_segment_id`, and is emitted as an `unresolved`
record with `feature_id=None`. Case (n) (empty-repository clause) passes on both fixed and
unfixed code, as expected — there is no bug on that path.

Did NOT touch `worktree_terminal.py` (T-01's scope, not this dispatch's).

## What was added

`case_classify_from_linked_worktree()` — new function, appended near the end of the file, wired
into `main()`'s results list. Builds a real repo (`_repo`), lands a Done feature
(`_commit_feature`), adds a real linked worktree (`_add_wt`), then calls
`w.classify(dest)` where `dest` IS the linked worktree — never the repo root. Two clauses, each
its own assertion (never a combined count):

1. `(m) classify(<linked worktree as root>) never returns a record for the main checkout` —
   filters `recs` for any record whose realpath equals the main checkout's realpath and asserts
   the filtered list is empty.
2. `(m) the linked worktree passed as root IS itself classified (landed Done -> terminal), not
   silently skipped` — the settled consequence from the dispatch: under the fix, `root` (the
   linked worktree) is no longer skipped and must appear as its own terminal record. Asserted as
   its own clause per the dispatch's explicit instruction, not folded into (1).

`case_classify_empty_repo_no_linked_worktrees()` — new function, also wired into `main()`. A
repo with no linked worktrees at all (only the main checkout, which `git worktree list` always
reports) yields `recs == []` and raises nothing.

**No existing case was edited.** All 31 pre-existing lines still print PASS (verified below) —
confirming the rule the new assertions encode is a genuine addition, not a rewrite of settled
behavior.

## RED proof — verbatim output against today's unfixed `worktree_terminal.py`

Command: `python3 .claude/skills/harness/bin/test-worktree-terminal.py`

Exit code: `1`

Full tail of output (all 31 pre-existing cases PASS, unmodified; the two new (m) clauses FAIL;
(n) PASSES):

```
PASS: (l) fleet.yaml unloadable: classify_all returns an unresolved record whose path is the fleet path
PASS: (l) fleet.yaml unloadable: classify_all still returns the harness root's own records
PASS: (l) RED PROOF: a stub that swallows the fleet-load exception (catches it, returns only the harness half's own records) never emits a fleet-path record, while the real classify_all against the SAME unloadable fleet.yaml does
FAIL: (m) classify(<linked worktree as root>) never returns a record for the main checkout
  records: [{'path': '/private/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmppye3tkdb/R', 'feature_id': None, 'klass': 'unresolved', 'dirty': True, 'reason': 'worktree path is not under WORKTREES_SEGMENT', 'repo': None}]
FAIL: (m) the linked worktree passed as root IS itself classified (landed Done -> terminal), not silently skipped
  record: None
PASS: (n) repository with no linked worktrees yields no records and does not raise
```

The first FAIL's `records:` payload is the exact defect the operator measured: an `unresolved`
record for the main checkout, `feature_id=None`, `reason: worktree path is not under
WORKTREES_SEGMENT` — because the main checkout's realpath never equals `root_real` when `root` is
the linked worktree, so `worktree_terminal.py:196`'s skip check never fires for it.

All 31 pre-existing PASS lines (not reproduced in full here — every one still reads PASS, none
flipped) confirm the new cases add coverage without disturbing settled behavior.

## `task_verify`

Command (verbatim from dispatch, cross-checked against `plan.yaml` T-02 `verify:` — matches):

```
python3 .claude/skills/harness/bin/test-worktree-terminal.py
```

Result: **fail**, exit 1 — expected and correct for THIS dispatch. The task is to make the hole
RED, not to close it (T-01, a separate dispatch, fixes `worktree_terminal.py` afterward). Reporting
`task_verify: fail` here is the honest answer to "did the plan's verify command pass", not a
claim that the work is incomplete — the two new clauses are SUPPOSED to fail until T-01 lands its
fix.

## Residual findings (not fixed, out of scope for this dispatch)

- The defect itself, `worktree_terminal.py:195-197`'s `os.path.realpath(path) == root_real`
  check, is T-01's fix to land, not this dispatch's.
