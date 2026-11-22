# Red-first — T-04 merge slice (merge-gate.py merge-distill + distill-candidate hook)

Owned files: `.claude/skills/harness/bin/merge-gate.py`, `tests/integration/test-merge-gate.py`.

Command (only this file was run): `python3 tests/integration/test-merge-gate.py`

## RED — new tests against the pre-change merge-gate.py (5305edbd)

Exit 1, `23 FAILED` (42 pre-existing checks ok). Log: `/tmp/f2225-t04/red.txt`. Failing checks:

- FEAT-2225 unreadable git merge ref denies rather than guessing non-distill
- FEAT-2225 gh outage with no matching feature denies: changed paths unreadable
- FEAT-2225 valid distill merges once, holding the owner lock, at the exact head
- FEAT-2225 valid distill emits head, main and committed hash evidence
- FEAT-2225 raw git merge of a distill candidate is refused with the merge-distill command
- FEAT-2225 raw gh pr merge of a distill candidate is refused with the merge-distill command
- FEAT-2225 nested raw gh distill merge is refused
- FEAT-2225 repository-tier Expertise change is a distill candidate whatever the branch name
- FEAT-2225 unreadable gh changed-path evidence refuses
- FEAT-2225 distill waits on the one owner-checkout lock and refuses LOCKED
- FEAT-2225 lock refusal exits with the merge core's LOCKED code
- FEAT-2225 distill refuses a head that does not contain current main
- FEAT-2225 distill refuses a worktree that is not at the PR head
- FEAT-2225 distill rechecks main immediately before merging
- FEAT-2225 distill rechecks the PR head immediately before merging
- FEAT-2225 distill refuses committed Expertise that differs from the replay
- FEAT-2225 distill refuses when replay --check refuses (unreceipted change)
- FEAT-2225 replay-valid distill with missing build-entry evidence refuses with recovery guidance before gh merge
- FEAT-2225 replay-valid distill with wrong-repository build-entry evidence refuses with recovery guidance before gh merge
- FEAT-2225 replay-valid distill with recovery-required build-entry evidence refuses with recovery guidance before gh merge
- FEAT-2225 distill refuses a feature id that does not own the PR
- FEAT-2225 merge-distill refuses a PR that changes no Expertise
- FEAT-2225 a shipped feature's distill candidate is not exempt

During implementation one more red appeared and was fixed: "distill rechecks main immediately
before merging" still failed while `_recheck` read main BEFORE re-viewing the PR head (the fake gh
advanced main on that second view and the merge ran). The recheck now re-views the head first and
reads main last, immediately before `gh pr merge`.

## GREEN

Same command: exit 0, `ALL PASSED`, 65 ok / 0 FAIL, ~34 s wall. Log: `/tmp/f2225-t04/green.txt`.

## Deliberate changes to existing expectations

- `T-05 gh outage with no matching feature allows` became
  `FEAT-2225 gh outage with no matching feature denies: changed paths unreadable`: the gh outage now
  leaves the candidate's changed paths unreadable, which refuses rather than guessing non-distill.
  The DEC-138 "could not verify … allowing it" path is kept and covered by the new
  `T-05 gh head outage with readable ordinary diff and no matching feature allows`.
- `T-05 branch matching no feature allows` now creates the `other` branch first, because a merge of
  a ref that does not exist has unreadable changed paths and is now refused (new check above).
