# Receipt — harness-dev-ops — T-13 — c1

## BLUF

`gh-sync.py status <feature-dir> <Status>` is implemented and GREEN. It couples recording
`feature.json`'s `status` (via the existing `_record_status`) to the board writes that phase
event implies, exactly per the plan's step 2/D-16. Full `run-unit-tests.sh --kind all` passes
(all scripts PASS, zero FAIL lines). Note on `plan.yaml`'s `status: building` for this task —
per T-13's own intent (step 2's "Plan" branch), `status <dir> Plan` is a no-op for stations by
design; the task-level `plan.yaml` status the orchestrator records is a different field
entirely (per-task `status: done/building`, not the feature-level phase), so nothing here
touches or contradicts it.

## Subcommand: `status <feature-dir> <Status>`

argv, exactly:
```
gh-sync.py status <feature-dir> <Status>
```
dispatched from `main()`:
```python
elif cmd == "status":
    if len(argv) < 3:
        die("status needs a Status value")
    cmd_status(feat_dir, argv[2], repo, board)
```

## Authority: feature.json vs the parent card

**`feature.json`'s `status` is the authority; the board station is its mirror.** `cmd_status`
writes `feature.json` first via the existing `_record_status` (unconditional, never gated on
any board write), then performs *only* the station writes that phase event implies. On
disagreement — e.g. a board write raises `gh_board.BoardError` — the code prints one stderr
line per failed card and moves on; `feature.json`'s recorded status is never rolled back and
never re-derived from the board. This matches D-15/D-16/D-21 (station derivation reads
plan.yaml task statuses through `derive_station`, never `feature.json`; `feature.json`'s
status is never resolved to a column for the parent by this subcommand — see T-15, a separate
task, for the audit-side reconciliation of a disagreement).

## Station-write behavior implemented (step 2)

- **Ready**: every recorded `T-NN` sub-issue → `board["stations"]["ready"]`, one
  `gh_board.set_station` call each. The parent is never touched (D-18). Zero recorded
  sub-issues → prints one line, writes nothing, no fallback to the parent.
- **Review**: the parent AND every recorded sub-issue → `board["stations"]["review"]`
  (operator ruling, D-23). A parent not recorded prints one stderr line; sub-issue writes
  still proceed.
- **Plan / Done / Abandoned**: no station write at all.
- Refusals (exit 2, before anything is recorded): unknown `Status` value; `Ready` when
  `plan.yaml`'s `approval.status != "approved"`; `Review` when not every task in
  `plan.yaml` carries `status: done`.
- A `BoardError` on one card prints one stderr line and the remaining cards are still
  written (unchanged failure posture from every other station write in this file).

## Cases added, each with its RED proof

All added to `test-gh-sync.py`, in a new "T-13: gh-sync.py status" section:

1. Unknown Status value refused exit 2, names the value, writes no station, leaves
   `feature.json` unrecorded.
2. `status Ready` on 3 recorded sub-issues: exact set `{ITEM_41,ITEM_42,ITEM_43}` written,
   never the parent; every write selects `OPT_READY`; `feature.json` recorded `Ready`.
3. `status Review`: exact set `{parent, sub-issues}` written, all select `OPT_REVIEW`.
4. `status Plan|Done|Abandoned`: no station write at all; each records its own status.
5. `status Ready` with zero recorded sub-issues: no `item-edit` call, prints the
   "nothing to move" line — proves no parent fallback (SC-14).
6. Refusal: `status Ready` with no `approval.status: approved` in `plan.yaml` → exit 2,
   names `Ready`, zero station writes, `feature.json` status untouched.
7. Refusal: `status Review` with a task not `done` → exit 2, names `Review`, zero station
   writes, `feature.json` status untouched.
8. One sub-issue's `set_station` raising (custom fake gh that fails only for `ITEM_41`):
   exit 0, remaining sub-issues (`ITEM_42`, `ITEM_43`) still written, one stderr `ERROR`
   line naming `41`, `feature.json` status still recorded as `Ready`.

**RED proof, without touching the stash (per the session's #780 rule):**
```bash
cp .claude/skills/harness/bin/gh-sync.py <scratch>/gh-sync.py.mine
git show b8f7279:.claude/skills/harness/bin/gh-sync.py > .claude/skills/harness/bin/gh-sync.py
python3 .claude/skills/harness/bin/test-gh-sync.py   # 24 FAILED
```
Result: **exactly 24 FAILED**, all and only the new T-13 assertions (verified by name —
every `FAIL` line matched a case listed above; every pre-existing check stayed green:
160 `ok` + 24 `FAIL` = 184, the same 184 total the green run produces). Restore:
```bash
cp <scratch>/gh-sync.py.mine .claude/skills/harness/bin/gh-sync.py
diff -q <scratch>/gh-sync.py.mine .claude/skills/harness/bin/gh-sync.py   # identical, exit 0
```
`git diff --numstat` after restore showed only the two intended files changed
(`gh-sync.py` +124/-3, `test-gh-sync.py` +208/-5); no third file touched.

Two test-suite fixture helpers gained optional, backward-compatible parameters to support
these cases (no existing caller's behavior changed): `write_plan_yaml(..., approval=None)`
and `stage_station(..., approval=None, source_issues=None)`.

## Verify: `run-unit-tests.sh --kind all`

Ran after the restore. Every script in the suite printed `PASS`, including
`PASS test-gh-sync.py` and `PASS test-factory-integration.py` (integration kind, unaffected
by this task since T-13's files are `gh-sync.py`/`test-gh-sync.py` only). Zero `FAIL` lines
anywhere in the full log (2735 lines). `git status --short` after the run showed only the
two intended files modified.

## Digest note (issue #778)

Planned `change_type: logic`; `validate-digest.py:158` restricts `dev-ops`'s `change_type`
enum to `{config, scaffolding, infra, ci}`, which rejects `logic`. Substituted
`change_type: infra` for the DIGEST below — closest available value for a bin-script change
with no better fit in the enum — and reporting the rejection per the dispatch's instruction
rather than silently picking one.

## Open question

`feature.json`'s per-feature top-level `status` versus `plan.yaml`'s per-task `status`
field are two different, unrelated fields with the same name. This task only ever touches
the former (`feature.json`, via `_record_status`) and only ever *reads* the latter
(`plan.yaml` task statuses, for the Review-refusal check and, unchanged, via
`derive_station`). Nothing in T-13 writes `plan.yaml`. Not filed as an open_question since
it is not a defect — flagged here only because the dispatch specifically asked which record
is authoritative and this is where the two vocabularies could be confused.
