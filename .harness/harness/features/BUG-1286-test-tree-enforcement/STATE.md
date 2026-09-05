# STATE

## Current

- feature: BUG-1286-test-tree-enforcement
- run: pre-merge reconciliation complete
- squad: none
- status: awaiting_user

Ship ACCEPTED by the operator (`notes/answers-2026-09-05-ship.md`, mruangutai, 2026-09-05: "Ship
now", advisor-pruned backlog). The pre-merge record is committed and the branch is ready. Not
merged, no PR, the worktree stands — the merge, the backlog filing and the worktree removal are the
main session's acts, not the orchestrator's.

`review_sha` is pinned at `bb3a31edc1971447b998fda1f9a736944bc8e612`; feature station `review`, all
five task stations `done`. `cycles_used` 11 of 11 — exactly the one cycle the operator authorised.

All gates green at the pinned revision, each re-measured by the orchestrator rather than relayed:
reviewer panel PASS with `must_fix` empty and `severity_max: med`; pm goal-check **19 of 19 SC MET**;
`code-grade.py` exit 0 with zero high-severity records; unit 342 PASS / 0 FAIL / 27 files;
integration 14/0; `--check-layout` exit 0; tree-audit `TOTAL 85 OUTSIDE 9 VIOLATIONS 0` with the
note round-trip at exit 0; decision anchors 30/0.

**`check-state.sh` run FROM THE WORKTREE exits 0** with no violation for this feature and only the
informational INV-22 run-count note. That qualification is load-bearing and is why the pre-merge
reconciliation happened: see below.

Two orphan run directories were discarded, documented in
`notes/run-reconciliation-2026-09-05.md`: `runs/2026-09-05-02-validator`, whose digest failed the
lead contract and is superseded by the recorded, valid `-03`; and `runs/2026-09-05-07-validator`,
whose own `artifact:` line names `-08` as its record. Both were superseded duplicates of recorded
runs whose evidence is committed under `notes/`. `runs/` is gitignored, so neither deletion appears
in any diff — which is exactly why it is written down.

## Open Questions

- For the main session: merge, then file the operator's pruned backlog with `gh-sync.py backlog` —
  B-13, B-9, B-10, B-11 and B-6, with B-4, B-5, B-8 and B-14 consolidated into B-6 and B-7, B-12 and
  B-15 struck. Then remove the worktree from outside it.
- **Correction to this feature's own earlier record.** The orchestrator ran `check-state.sh` from
  the MAIN checkout four times and read exit 0 as clean, including immediately before declaring the
  ship gate green. Those readings were VACUOUS: this feature's directory exists only in the
  worktree, so a checker run from the main checkout never discovered it. The main session's
  canonical run found the violation; the orchestrator's did not. A `check-state.sh` result is
  evidence only about features the invocation can actually see.
- Harness defect, backlog B-13, found independently by two readers: the integration suite is not
  hermetic against `HARNESS_AGENT_TYPE` — 15 FAIL lines under an agent's own env, green for a human,
  reproduced unchanged at the merge-base. Agents have been grading a red suite as evidence.
- Carried harness defects filed as B-9, B-10 and B-11: `validate-digest.py`'s `code_grade` deadlock
  for plan-phase readers; members editing the MAIN checkout through bare relative paths under a
  worktree dispatch, twice, both caught and reverted; and run-artifact hygiene — two digests written
  without their contract block and two `state.yaml` files clobbered by a later run and repaired.
