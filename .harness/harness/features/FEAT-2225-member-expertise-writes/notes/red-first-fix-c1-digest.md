# Red first — validate c1 fix, DigestContract slice (F1 authority CLI + guard, F2 regression)

The tests were written first. RED runs used a copy of the bin directory with `validate-digest.py`
and `dispatch-guard.py` taken from HEAD 8cddd8cd (`git show HEAD:<path>`), at
`/tmp/t04fix/headbin`, selected through the suites' existing override variables. Raw output:
`/tmp/t04fix/red-vd.txt`, `/tmp/t04fix/red-dg.txt`. GREEN output: `/tmp/t04fix/green-dg.txt`,
`/tmp/t04fix/full-vd.txt`.

## F1 — registered distill authority CLI (`validate-digest.py --distill-authority`)

RED: `VALIDATE_DIGEST_BIN=/tmp/t04fix/headbin/validate-digest.py python3 tests/integration/test-validate-digest.py --only run_member_expertise_authority_cases`
→ exit 1, 0/10 passed. Every case failed because HEAD has no such CLI:
- authority: a member of a lead's registered distill run
- authority: a lead on its own registered distill run
- authority: the orchestrator of a feature with a registered distill run
- authority: a parent the live claim does not record is refused
- authority: a runtime holding no live claim is refused
- authority: an ungoverned agent is refused
- authority: an unreadable request fails closed
- authority: a member of an ordinary registered run is refused (the F1 counterexample)
- authority: a lead on an ordinary registered run is refused
- authority: the orchestrator of a feature with no distill run is refused

GREEN: 10/10.

## F1 — dispatch-guard refuses a distill marker with no bound `distill-*` run

RED: `DISPATCH_GUARD_BIN=/tmp/t04fix/headbin/dispatch-guard.py python3 tests/integration/test-dispatch-guard.py`
→ exit 1, 158 of 161 passed:
- FAIL case 35: an ordinary build lead's member carrying the distill marker is refused before any claim
- FAIL case 36: a lead start on an ordinary registered run carrying the distill marker is refused before any claim
- FAIL case 37: the orchestrator of a feature with no distill-* run is refused the marker

The positive control (case 37: the orchestrator of a feature with a registered `distill-*` run
starts with the marker) passed before and after.

GREEN: `python3 tests/integration/test-dispatch-guard.py` → exit 0, 161 of 161.

## F2 — complete-content verification, pinned at the validate-digest level

Fixture: qa's craft file holds G-01, committed at HEAD. qa applies a receipted add of P-01;
qa's yield and the lead's consolidation both verify, and the lead's durable record is written.
G-01 is then deleted with no receipt.

RED (HEAD validator plus the core `expertise-merge.py` as it stood before MergeGate's change;
`git diff HEAD -- expertise-merge.py` was empty at that point):
`--only run_member_expertise_f2_cases` → exit 1, 2/6 passed (the two controls):
- FAIL F2 durable: an unreceipted deletion of a pre-existing entry fails the durable check (CLI printed `digest ok`)
- FAIL F2 durable: feature-record.py close-run refuses the run at its digest stage (it passed digest and stopped at run-end)
- FAIL F2 live: the member's yield is refused after the unreceipted deletion (exit 0)
- FAIL F2 live: the lead's yield is refused after the unreceipted deletion (exit 0)

The same four also stayed red with this slice's validate-digest.py and the unchanged core. The
fix belongs to T-01's `verify-receipt` (MergeGate). validate-digest still trusts its exit code.

GREEN with MergeGate's core change in the worktree: `python3 tests/integration/test-validate-digest.py`
→ exit 0, `ALL PASSED.` (member-expertise: leaf 13/13, lead 13/13, supersession 8/8,
authority 10/10, F2 6/6).

## Grades (path mode, every touched function)

validate-digest.py: `_run_identity` 5, `_registered_distill_context` 4, `_live_context` 5,
`_authority_refusal` 5, `_authority_request` 5, `distill_authority_mode` 4.
dispatch-guard.py: `_is_distill_run_id` 5, `_distill_run_feature` 5, `_declares_distill` 5,
`_orchestrator_distill_authority` 4, `_refuse_unbound_distill_marker` 5, `_distill_preflight` 5.
Tests: every new function scores 4 or 5 (bar 3).
