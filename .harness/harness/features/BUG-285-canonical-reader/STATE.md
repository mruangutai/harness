# STATE

## Current

- feature: BUG-285-canonical-reader
- run: none — ship review assembled from the completed validation run; no new squad dispatched
- squad: none
- status: awaiting_user — all signed criteria are met and the operator ship decision is the only remaining gate
- station: review, unchanged in `plan.yaml`; the feature is not marked done because it has not been merged and `gh-sync.py ship` has not run
- briefing: `notes/ship-review-2026-09-15-fix-c1-validator.md`
- review SHA: `5be21a432b87ed648c0bed50fbf9a2642c84e0a9`
- validation: PASS after fix round c1; all four first-panel findings resolved, matrix complete, no must-fix findings
- cycles: 10 of 10; no further fix cycle is available without an operator-approved raise
- operator gate: review the briefing and decide whether to accept the feature and which proposed backlog rows, if any, to file. This run will not create, merge, or close a PR.

## Open Questions

- none blocking
- the briefing proposes backlog rows B-1 through B-5; anything not selected dies silently
