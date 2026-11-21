# Operator ruling — FEAT-2225 F2 after validate c3 (2026-11-21)

Asked by the main session after `r-20261121-8-validate-c3-validator` FAIL, with the rework ruling
(2 rounds / 90 min) exhausted. Open question Q-F2-RULING, `notes/handoff-validate-c3.md` seq-8.

**Ruling: accept F2 as a documented boundary and ship.** Not extended by a round; not abandoned.

## What the operator approved

Amend SC-03 and T-04's intent (pm, re-signature) so close-time verification is promised relative to
the default branch **as the local repository records it**. Unreceipted content committed on the
feature branch and then hidden by deliberately moving default-branch refs (`git update-ref`,
`git branch -f`, `git symbolic-ref`) is a stated boundary at close. It is contained at merge:
`merge-gate.py merge-distill` fetches the live remote main, replays every receipt onto it, and refuses
when a committed Expertise blob differs from the replay. Every other SC-03 clause is unchanged.

## Reasoning presented to the operator

The merge gate is the integrity boundary that protects shared Expertise, and it reads the live
remote. Closing the close-time gap means defending an agent's own close check against that agent
forging git refs. That is adversarial self-sabotage, better closed by the guard and anchor hardening
tracked separately.

## Follow-up

Hardening filed as #2251: anchor close-time verification on an unmovable authority, and refuse
default-branch ref moves for governed agents.
