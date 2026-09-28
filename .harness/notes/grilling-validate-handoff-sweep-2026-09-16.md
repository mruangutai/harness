# Grilling — post-merge sweep can ship before the validate handoff exists (#1129) — 2026-09-16

## Destination
`gh-sync.py ship` refuses, before its first irreversible GitHub write, any feature that has not
reached the validate seam — `notes/handoff-validate.md` absent and the DEC-174 all-direct
exemption not holding — so a `git pull`-fired sweep can no longer land cards at Done and close a
milestone for work still being validated. The same predicate INV-17 applies decides the exemption.

## Mission
mission: patch
reason: cause known (#1129, closed 2026-09-01 without a landing; the fix on `feat/FEAT-51` targeted the `.sh` sweep and was never merged; #1674's Python rewrite carried no guard), diff bounded to one refusal in the writer, one extracted predicate and the fixtures that model validated features.
confirmed-by: operator ("do your recommendation for issue://1129", 2026-09-16; old branch deleted on their word)

## Settled
- Where the guard lives → in `cmd_ship` (the writer), not only in `post-merge-sweep.py` (one caller). Main's manual ship is the other caller and today's BUG-1723 records show the note being added after the ship.
- Refusal, not skip → `die()` exit 1; the sweep's positive-signal gate already keeps the worktree on non-zero and never reads a refusal as permission to delete.
- Exemption → `handoff_policy.exempt_reason(feat_dir)` extracted from check-state's `_handoff_exempt` (INV-17) unchanged; both call it. Fail-closed on an unreadable plan.
- Fixtures → every builder that models a validated feature writes the note (`write_validate_handoff`); `stage_ship(validated=False)` is the refusal's own case.
- DEC-174 → gate surface: build main-session-direct; the orchestrator runs intake and validate only.

## Fog
- none

## Out of scope
- Whether the sweep should run on `git pull` at all (its trigger); INV-17's own wording.
