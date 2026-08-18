# Receipt — T-05 — harness-backend-dev — c2 (duplicate-dispatch finding, no new work done)

**BLUF: T-05's deliverables already exist on disk and are already verified GREEN, receipted at
`receipt-harness-backend-dev-T-05-c1.md` (mtime 10:26, same runid `c1`). This dispatch (`c2`) hit
the dispatch's own tripwire on the pre-edit red run and STOPPED before touching anything. Do not
merge this receipt's forensics into `c1`'s — `c1` is left untouched as the authoritative record of
the real RED→GREEN work.**

## 1. Pre-edit verify — verbatim invocation, output, exit code (the mandated red run)

Invocation:
```
python3 -c "
import yaml
p=yaml.safe_load(open('.harness/harness/features/FEAT-23-ship-flow-fixes/plan.yaml'))
print([t for t in p['tasks'] if t['id']=='T-05'][0]['verify'])" | bash
```
Output:
```
T-05 GREEN
```
Exit code: **0**.

The dispatch instructed explicitly: *"If it prints `T-05 GREEN` on this untouched tree, STOP and
return `BLOCKED` with the output — that is a finding about the gate, not permission to proceed."*
It printed `T-05 GREEN`, exit 0, on a tree I had not touched. Per instruction I stopped here and
did not run step (ii) (standalone `test-board-station.py`), did not edit any file, and did not
adopt/correct/rewrite anything.

**Correction to the dispatch's own framing, based on what the forensics below show:** this is not
a gate defect. `run-unit-tests.sh` and the drift detector are fine. The tree the dispatch describes
("board-station.py does not exist") was true at dispatch-authoring time and is no longer true at
execution time — the deliverables were written by another run between then and now.

## 2. Provenance forensics — the two requested read-only git commands, raw output

`git status --porcelain -- .claude/skills/harness/bin/`:
```
 M .claude/skills/harness/bin/run-unit-tests.sh
?? .claude/skills/harness/bin/board-station.py
?? .claude/skills/harness/bin/test-board-station.py
```
Both new files are **untracked**; `run-unit-tests.sh` is **modified, unstaged**. None are inside any
commit.

`git show --stat d96ab5e -- .claude/skills/harness/bin/`:
```
 .claude/skills/harness/bin/gh-sync.py      | 89 +++++++++++++++++++++------
 .claude/skills/harness/bin/test-gh-sync.py | 98 +++++++++++++++++++++++++++++-
 2 files changed, 167 insertions(+), 20 deletions(-)
```
`d96ab5e` (T-01's commit, 2026-08-17 10:15:54) carries only `gh-sync.py` and `test-gh-sync.py` — it
does **not** carry `board-station.py`, `test-board-station.py`, or the `run-unit-tests.sh` edit.
Confirms the dispatch's own claim about `d96ab5e`.

## 3. The actual provenance: an already-complete, already-receipted `c1` run

`ls -lat .harness/harness/features/FEAT-23-ship-flow-fixes/notes/` (top of listing) showed:
```
-rw-r--r--  1 molchairuangutai  staff  6520 Aug 17 10:26 receipt-harness-backend-dev-T-05-c1.md
```
— i.e. a receipt at the **exact path this dispatch names for me**, timestamped after `d96ab5e`
(10:15:54) and after the on-disk files' mtimes (`board-station.py` 10:20, `test-board-station.py`
10:18). I read it in full. It documents:

- A genuine pre-edit RED run of the plan's `verify:` clause (`T-05: ...does not exist`, exit 1).
- A disclosed Iron Law lapse (production code written before the test file existed), self-caught
  and corrected: file hashed, moved out of tree, test suite written, RED watched (8/8 FAIL for the
  right reason — `can't open file`), file restored, hash re-verified before GREEN.
- All seven required PASS labels plus an eighth (stronger) assertion on the field-set case.
- `run-unit-tests.sh --kind unit` and `--kind all` both green with the file registered.
- The full `T-05 GREEN` verify output.
- `case_20` on `test-check-plan-routes.py` checked directly and shown PASS (item 4a's
  variable-first form confirmed, without editing `INTEGRATION_SCRIPTS`).

I independently confirmed the two load-bearing facts without re-running the suite: the
`UNIT_SCRIPTS` diff (`git diff -- run-unit-tests.sh`, shown above minus the one-line addition of
`"test-board-station.py"`) and my own pre-edit verify reproducing `T-05 GREEN` exit 0. Both match
`c1`'s claims.

`STATE.md` for FEAT-23 does not yet mention T-05 as landed (grep for `T-05` returns only sequencing
prose, no completion marker) — so the `c1` work is real and verified but not yet reconciled into
feature state.

## 4. Verdict on the inherited `test-board-station.py` (item 4 of the dispatch checklist)

Not mine to render — `c1` already rendered it (self-authored, not "inherited" from an unexplained
source as the dispatch's briefing assumed). The dispatch's premise that the file was a pre-existing
mystery artifact with "no receipt... on disk" accounting for it is now stale: `c1`'s receipt is that
accounting, and it postdates the dispatch's own measurement.

## 5. What I did NOT do

- Did not edit `board-station.py`, `test-board-station.py`, or `run-unit-tests.sh`.
- Did not run step (ii) (standalone pre-edit test run) — moot once the verify itself greened
  pre-edit; running it risked a destructive race against a possibly-still-in-flight duplicate
  writer.
- Did not overwrite `receipt-harness-backend-dev-T-05-c1.md`. Falsifying or replacing a receipt
  documenting real, verified RED→GREEN work with a BLOCKED report would destroy the record rule 15
  protects.

## Files touched

`[]` — none. (Confirmed: `git status --porcelain` shows the same two untracked files and one
modified file as `c1` left behind; nothing added by this run.)

## Open question for the lead/orchestrator

Two runs (`c1`, this `c2`) were dispatched for the same T-05 under the same runid label. `c1`
completed real work and holds a verified receipt; `c2` (this run) arrived after and found the work
already done. Please reconcile: (a) confirm `c1`'s receipt as canonical, (b) update `STATE.md` /
`plan.yaml` execution-state to mark T-05 done from `c1`'s work, and (c) determine whether this was a
genuine concurrent duplicate dispatch or a stale/replayed one, so it doesn't recur for later tasks
in this feature.
