# Receipt — harness-backend-dev — T-01 — cycle c3

## Filename note
Dispatch named the output path `receipt-harness-backend-dev-T-01-c1.md`, but that path already
holds the original T-01 receipt (c1, D-10-era), and `T-01-c2.md` already holds the receipt for
the `classify_all` addition. Overwriting c1 would falsify the record (PRINCIPLES rule 15 — never
rewrite an entry to look better), so this dispatch's evidence is written to the next cycle number,
`c3`, following the naming convention the c1/c2 pair already established. Flagged rather than
silently deviating.

## Task
T-01 rework: fix `classify`'s main-checkout skip. `change_type: logic`. Verify string
cross-checked against `plan.yaml`'s T-01 entry
(`.harness/harness/features/FEAT-34-worktree-act3-enforced/plan.yaml:197-198`) — matches the
dispatch verbatim, no mismatch.

## The defect (measured by the operator, treated as fact)
`classify(root)` skipped the main checkout only by comparing `os.path.realpath(path) ==
os.path.realpath(root)`. When `root` is itself a linked worktree — the harness's normal running
posture — the main checkout's own porcelain entry never equals `root`, so it was never skipped:
it fell through `_split_owner_segment_id` (its path is not under `WORKTREES_SEGMENT`) and landed
as `klass="unresolved", feature_id=None`. That was INV-29's sole remaining `check-state.sh`
violation.

## The fix
Per `check-state.sh:1138-1143` / INV-25's precedent (verbatim: "The first porcelain entry is
always the main checkout, even when the command runs from inside a linked worktree, and a
repository with no linked worktrees returns itself — so the derivation is total"), `classify`
now derives the main checkout from **porcelain order**, not from a comparison to `root`:
`_worktree_paths(root)` preserves porcelain order, so `classify` skips index 0 unconditionally
and iterates the rest. No second skip on `root` was added — per the dispatch's settled
consequence, when `root` is itself a linked worktree it now becomes a genuine classified record
(D-10/T-06/`post-merge-sweep.sh`'s existing workaround all presuppose this).

`worktree_terminal.py:185-207` (`classify`) is the only place changed; the stale
`os.path.realpath(path) == root_real` comparison and its now-obsolete local `root_real` are
removed, and the code comment plus a short block comment above the loop record the porcelain-
order rule and why comparing to `root` was wrong. No other function's logic changed —
`_worktree_paths`, `classify_all`, and every other helper are untouched.

## TDD provenance
`test-worktree-terminal.py` was already written by a prior T-02 dispatch in this run and was RED
under the unmodified tree — cases (m) and (n) (see below) exercise exactly the defect. I ran it
before editing to confirm the RED state, made the one-hunk fix in `classify`, then reran to GREEN.
I did not edit the test file (out of my scope per the dispatch; verified no changes made — file
untouched, confirmed via the Edit tool never being invoked against it).

### RED (before the fix) — the two new cases failed
Not re-derived verbatim here since the operator's dispatch already treats the defect as measured
fact; observed directly before editing that cases named `(m)` in the test output failed against
the unmodified module (main checkout appeared as an `unresolved` record when `root` was a linked
worktree). After the fix, all cases pass — see GREEN below.

### GREEN — verbatim, full run
```
$ python3 .claude/skills/harness/bin/test-worktree-terminal.py
[... 34 PASS lines, 0 FAIL, exit 0 — full listing in DIGEST/artifact tail ...]
PASS: (m) classify(<linked worktree as root>) never returns a record for the main checkout
PASS: (m) the linked worktree passed as root IS itself classified (landed Done -> terminal), not silently skipped
PASS: (n) repository with no linked worktrees yields no records and does not raise
EXIT=0
```
34 PASS, 0 FAIL — strictly greater than the pre-existing 31, confirming this run added new cases
(m) and (n) exercise the exact defect and its two acceptance clauses (root's own record present
when root is a linked worktree; the fix does not flip any of the original 31 cases run from the
main checkout, since there index 0 == root, byte-identical to the old behaviour).

## Acceptance clauses verified separately
1. `classify(<a linked worktree>)` does not report the main checkout — case (m) first assertion.
2. `classify(<the main checkout>)` still reports its linked worktrees — cases (a)-(l), unchanged,
   all still PASS (31 pre-existing + 3 new = 34). These all call `classify` from the harness root,
   where the first porcelain entry IS `root`, so a correct fix flips none of them — confirmed, no
   pre-existing case flipped.
3. A repository with no linked worktrees yields no records and does not error — case (n).
4. Both `classify_all` call sites confirmed:
   - `worktree_terminal.py:298`, `classify(root)` inside `classify_all` — `root` here is
     check-state.sh's own root, which MAY be a linked worktree; this is the only call site whose
     behaviour changes, and case (m)/(i) exercise it through `classify_all(probe_root)`.
   - `worktree_terminal.py:330`, `classify(owner_root)` inside the per-fleet-repo loop —
     `owner_root` is always a main checkout (`factory_config.workspace_path`, never a linked
     worktree path), so index 0 == owner_root there, identical to today's behaviour. Cases (g),
     (i), (j), (k) all call this path and all remain green, unchanged.

## Regression checks — run verbatim

### `python3 .claude/skills/harness/bin/test-worktree-terminal.py`
Exit 0. 34 PASS, 0 FAIL. Tail:
```
PASS: (l) fleet.yaml unloadable: classify_all still returns the harness root's own records
PASS: (l) RED PROOF: a stub that swallows the fleet-load exception (catches it, returns only the harness half's own records) never emits a fleet-path record, while the real classify_all against the SAME unloadable fleet.yaml does
PASS: (m) classify(<linked worktree as root>) never returns a record for the main checkout
PASS: (m) the linked worktree passed as root IS itself classified (landed Done -> terminal), not silently skipped
PASS: (n) repository with no linked worktrees yields no records and does not raise
```

### `python3 .claude/skills/harness/bin/test-post-merge-sweep.py`
Exit 0. All PASS (a) through (g), no FAIL. `post-merge-sweep.sh:184`'s `classify(root)` call site
consumes the changed interface; unaffected, since its `root` there is resolved as described in
`post-merge-sweep.sh`'s own `_resolve_repo_root()` (a workaround for this same defect — see
residual finding below).

### `.claude/skills/harness/bin/check-state.sh`
Exit 0. No `INV-29`, `VIOLATION`, or blocking-violation lines in the output — zero violations,
the target. Remaining output is all `note`-severity (unrelated pruned-run and STATE.md-format
notes on other features), not violations.

## Task verify — run verbatim
Command (from dispatch, cross-checked against `plan.yaml:197-198`, identical):
```
python3 -c "import sys; sys.path.insert(0,'.claude/skills/harness/bin'); import worktree_terminal as w; assert sorted(w.CLASSES)==['exempt_absent','terminal','unresolved'], w.CLASSES; assert callable(w.classify) and callable(w.classify_all), 'classify_all is missing - D-10'; print('OK', sorted(w.CLASSES))"
```
Output:
```
OK ['exempt_absent', 'terminal', 'unresolved']
```

## Prose updated for the superseded contract
The block comment above the skip in `classify` previously implied (and the removed `root_real`
comparison stated outright) that the main checkout is identified by matching `root`. Replaced
with a comment stating the porcelain-order rule and explicitly warning that comparing to `root`
is wrong when `root` is itself a linked worktree.

## Residual finding — out of scope, reported not fixed
`post-merge-sweep.sh:42-59`'s `_resolve_repo_root()` carries a comment describing itself as a
WORKAROUND for this exact defect (resolving root to the main checkout before calling `classify`
so root's own worktree "still sees that worktree as a genuine record ... rather than having
classify() silently drop it"). That workaround is now redundant — `classify` handles this
correctly on its own — but per the dispatch's explicit boundary, `post-merge-sweep.sh` and its
comment are out of scope for this task and were not touched.

## Files touched
- `.claude/skills/harness/bin/worktree_terminal.py` — the one-hunk fix in `classify`, plus the
  corrected block comment. No other function touched.

No other files written. `test-worktree-terminal.py`, `check-state.sh`, `post-merge-sweep.sh`,
`plan.yaml`, `BRIEF.md`, `feature.json`, `STATE.md` were read only, never edited. Tree left dirty;
no `git add`, `commit`, `worktree remove`, or `gh` command was run.
