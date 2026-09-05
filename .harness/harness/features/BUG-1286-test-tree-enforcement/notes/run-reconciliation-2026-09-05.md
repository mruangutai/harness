# Pre-merge run reconciliation — BUG-1286-test-tree-enforcement

**Two orphan run directories were discarded and one checker blind spot is recorded here, so the
deletion is a documented act rather than a silent one.**

`runs/` is gitignored (`.gitignore:7`), so neither directory was ever in the tree under review and
neither deletion appears in any diff. That is precisely why the removal is written down.

## What was discarded, and why each carried no canonical evidence

**`runs/2026-09-05-02-validator`** — the T-04 tree-audit run's first lead digest. `validate-digest.py
lead` returns `BLOCKED (contract violation) — no artifact: path`, which is the violation
`check-state.sh` reported. The validator lead's own digest for the successor run records what
happened: the first write omitted `artifact:`, `check-domain.sh` correctly refused to overwrite a
recorded digest, and the corrected record took its own directory. The canonical record is
`runs/2026-09-05-03-validator`, which validates clean and IS recorded in `feature.json`. The run's
evidence is the committed `notes/qa-tree-audit.md`. Nothing unique was lost.

**`runs/2026-09-05-07-validator`** — the B-2 SHA-correction run's first lead digest. Its digest
validates clean, but its own `artifact:` line names
`runs/2026-09-05-08-validator/digest.md` — it declares another directory to be the record, so it is
a pointer rather than a record. `-08` validates clean and IS recorded in `feature.json`. The run's
evidence is the committed `notes/qa-audit-sha-correction.md` and `notes/qa-tree-audit.md`.
Recording `-07` as well would have counted one step of one member's work as two runs.

Both were superseded duplicates of runs that are recorded, valid, and whose artifacts are
committed. Neither was a failure being hidden: the underlying work PASSED, is recorded, and its
evidence is in the tree.

## The checker blind spot this exposed, which matters more than the orphans

Through this feature the orchestrator ran `check-state.sh` from the **main checkout** and read
exit 0 as clean — four times, including immediately before declaring the ship gate green. That
reading was **vacuous**. This feature's directory exists only inside the worktree, so the checker
run from the main checkout never discovered it and had nothing to report. The gate passed because
its discovery found nothing, which is indistinguishable from passing on the merits by exit status
alone.

Run from inside the worktree, the same checker exits 1 and names the violation above. The main
session's canonical run found it; the orchestrator's did not. **A `check-state.sh` result is only
evidence about a feature whose directory the invocation can actually see** — for a feature living
in a worktree that means running it from the worktree.

## Not done here

The operator's ship acceptance (`notes/answers-2026-09-05-ship.md`) names a pruned backlog: file
B-13, B-9, B-10, B-11 and B-6, with B-4, B-5, B-8 and B-14 consolidated into B-6, and B-7, B-12 and
B-15 struck. Filing those is `gh-sync.py backlog`, a main-session subcommand, and is not the
orchestrator's to run. The merge and the worktree removal are likewise not the orchestrator's acts.
