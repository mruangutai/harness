# STATE

## Current

- feature: FEAT-58-corpus-outside-worktree
- run: **PLAN PHASE COMPLETE AND SIGNED**, 2026-09-10. `plan.yaml` `approval.status: approved` with seven recorded rulings, `BRIEF.md ## Approval` approved-by mruangutai — both verified on disk, not taken from a digest. Station `ready`. On disk: 13 tasks (N-01..N-10, N-12, N-13, N-14; N-11 a deliberate gap), 17 decisions, 10 REQ, 15 live criteria (SC-15 a deliberate gap), ledger 45. Handoff: notes/handoff-plan.md
- squad: none — the next phase is build, and it is a fresh dispatch
- status: ready
- post-signature acts completed: N-14 added, converting panel finding H-01 to build-phase work with M-01's remedy folded into the same name-set assertion, per the operator's Q1 ruling; N-13's intent conformed to that ruling by excising the withdrawn cycle-8 red-proof staging, which could not redden and would have invited a FALSE red; `gh-sync.py open` run as Build entry, recording `github.build_entry: opened`.
- budget: cycles_used 9 of 10 — the unspent cycle is build's margin by the operator's instruction, not a resource for plan text. runs 51.

## Open Questions

- **BLOCKING FOR THE MIRROR, AND IT IS A HARNESS DEFECT, NOT THIS PLAN'S: `gh-sync.py` cannot record this feature's issue ids.** Its receipt loader filters recorded keys through `re.fullmatch(r"T-\d+", key)` at `gh-sync.py:613`, and this plan's task ids are `N-NN`. `open` created and attached all thirteen sub-issues and wrote the map at `:1159`, but the next load dropped every key and `save_recorded` (`:929`) wrote the emptied map back. The proof it is a defect and not a contract is inside the same receipt: `attached` (`:604-608`) carries the identical `N-NN` ids with no filter and survived intact. Live consequences: `status ready` moves nothing (`:1594-1597`), `start-task` refuses every task with "has no recorded issue — was `open` run?" (`:1482-1483`), `status review` moves nothing, `ship` lands no card. The mirror is never a gate, so nothing is blocked from proceeding — but nothing on the board will move, and **a card at `Ready` is therefore not available as proof of the signature.**
- **DO NOT RE-RUN `gh-sync.py open` FOR THIS FEATURE.** Its skip check reads the same empty map, so a re-run creates thirteen DUPLICATE sub-issues. The full id mapping is recorded by hand at `notes/mirror-ids-FEAT-58.md` (milestone #66, parent #1641, source #1559, N-01..N-14 → #1642..#1654). The fix is one regex in `bin/gh-sync.py` and is main-session-direct work outside FEAT-58.
- Accepted as known residue in `approval.rulings`, to be met in build rather than re-litigated: M-02 and L-03 (build catches both the moment the test is written), L-01 and NF-01 (no runner exposure).
- Carried, non-blocking: N-14's intent still refers conditionally to N-13's now-removed red-proof paragraph and cites N-13 as a staging precedent. Neither misleads — the first is a conditional prohibition that stays correct, the second is provenance and N-14 spells its own staging in full. Fix only if N-14 is amended for another reason.
- Filed and not fixed here: #1595, #1596, #1597, #1598, #1630, #1631, #1635, #1636, #1637, #1638, #1640.
