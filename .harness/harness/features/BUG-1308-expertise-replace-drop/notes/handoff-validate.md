# Handoff — BUG-1308, validate → ship — administrative recovery

## Next

Ship against the pinned `review_sha` recorded in `feature.json`. The final c4 panel and final
goal-check both pass, no must-fix remains, and the operator's delegated Advisor approved ship.
The GitHub ship transition has completed through feature PR #1379; persist this terminal state in
ship-state PR #1386.

## Trust

- Final c4 panel: PASS, severity_max med, no must_fix; VL-01 through VL-06 independently re-executed closed — verified-at b70d57b4
- Final goal-check: SC-01 through SC-12 MET — verified-at b70d57b4
- Operator-adopted SC-13 is MET by case21, case22, u17 and u18; SC-14 is MET by case23, case25, case26 and u19 through u22 — verified-at b70d57b4
- Unit suite: exit 0, zero FAIL, 29 files; integration suite: exit 0, zero FAIL, 46 files on the merged tree — verified-at 433df520
- Feature PR #1379 merged after integration CI passed in 1m52s; issue #1308, parent #1325 and tasks #1326 through #1329 moved to done; milestone #48 closed — verified by the ship transition

## Dead ends

- Do not reopen the implementation or rerun the panel; no production or test byte changed after the reviewed pin.
- Do not re-type `ENTRY_RE` or the `str.splitlines()` boundary alphabet.
- Do not treat advisory follow-ups #1380 through #1385 as ship blockers.

## Working set

- .harness/harness/features/BUG-1308-expertise-replace-drop/feature.json
- .harness/harness/features/BUG-1308-expertise-replace-drop/plan.yaml
- .harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md
- .harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-c4-validator/digest.md
- .harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-goalcheck-sc-c4.md

## Done when

Scope: feature PR 1379 is merged, the recorded GitHub cards and issues are done, milestone 48 is closed, and terminal state is durable on main
Authority: brief-sc:SC-13
Authority: brief-sc:SC-14
Authority: approval:.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md#Approval
