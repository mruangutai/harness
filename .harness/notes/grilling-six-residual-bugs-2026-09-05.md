# Grilling — six residual Harness bugs — 2026-09-05

## Destination

Fix issues #1302, #1303, #1304, #1305, #1306, and #1308 end to end and move each through every Harness station through ship.

## Settled

- Success for each issue is an approved BRIEF and plan, completed build and validation, merged pull request, ship closeout, closed source issue, passing issue-specific verification and PR checks, and `python3 .claude/skills/harness/bin/check-state.py` exiting 0.
- Each flow starts with an eight-cycle build/review cap. The Advisor may approve additional cycles, but twenty is the hard maximum.
- Material questions are decided by the Advisor; the operator delegates those answers so the flows can continue.
- Allowed changes are only the implementation, focused tests, governing decisions/docs, and Harness lifecycle artifacts required by the six issues.
- Existing unrelated user changes remain untouched.
- Follow the worktree rule and DEC-174 enforcement-layer carve-out.

## Issue-specific source

- #1302: B-6 plus B-4, B-5, B-8, and B-14 from `.harness/harness/features/BUG-1286-test-tree-enforcement/notes/ship-review-2026-09-05-ship-final.md`.
- #1303: B-9 from that ship briefing.
- #1304: B-10 from that ship briefing.
- #1305: B-11 from that ship briefing.
- #1306: B-13 from that ship briefing.
- #1308: its GitHub issue body is the authoritative problem and requirement statement.

## Out of scope

- Unrelated cleanup, redesigns, compatibility shims, or work outside the six issue requirements.
- Risk acceptance, scope reduction, or failed-gate waivers.

## Stop conditions

Stop and escalate if a flow reaches twenty cycles, the Advisor cannot resolve a material ambiguity, required credentials are unavailable, or completion requires destructive or unrelated changes.
