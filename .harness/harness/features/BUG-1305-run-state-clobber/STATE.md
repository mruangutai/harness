# STATE

## Current

- feature: BUG-1305-run-state-clobber
- run: none
- squad: none
- status: blocked
- station: ready (signed 2026-09-05 at 75cdd200; no task started)
- blocker: all eight live tasks are execution_mode main-session-direct under DEC-174, so no squad may build them; segments for the main session are in notes/build-segments-BUG-1305.md
- cycles: 9/9 — a first-pass run costs none, the first send-back exhausts the budget and stops

## Open Questions

- Main session: execute segments S1-S5 (notes/build-segments-BUG-1305.md) yourself, or rule that DEC-174's carve-out does not cover these surfaces and re-route them to the eng squad. The orchestrator cannot dispatch a squad against a main-session-direct task.
