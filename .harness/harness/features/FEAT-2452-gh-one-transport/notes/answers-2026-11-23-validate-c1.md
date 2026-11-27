# Rulings after validate c1 — FEAT-2452 — 2026-11-23

Ruled by fable-advisor (AdvisorD5OQ), which holds the operator's delegated approval ("defer to fable-advisor"). Full text: agent://AdvisorD5OQ.

## OQ-GC2-1: SC-05 #13 failing-first
- **Authority:** operator delegation; c0's must_fix named H1's abandon regression as sufficient; the rework ruling makes c2 the last round.
- **Gap:** the three per-item close-failure assertions have never been observed red.
- **Ruling (a):** accept the literal discharge; no mutant run.
  - `_apply_abandon_plan` (gh-sync.py:2194-2206) is a flat loop with no break, return or raise path.
  - The assertions at test-gh-sync-abandon.py:534-548 require the later tickets' close calls and the milestone close in the recorded call log, so a break-after-first-failure mutant would fail them deterministically.
  - The label-create red at 15a240bc is real and QA reproduced it.
- **Constraint:** the ship record states the narrowed reading and must not claim the per-item red was observed.

## Dispositions, all confirmed
| Item | Disposition | Constraint |
|---|---|---|
| A2 opt-in cost log persists inline --body | backlog at ship | name the disclosure class (non-public body text when opted in) |
| OQ-QA-2 check-domain vs DEC-153 in-pin perturbation | backlog | — |
| OQ-QA-3 pinned checkout lacks node_modules | backlog | — |
| B2 abandon silent on the label 403 when every close fails | backlog | — |
| B4 unit seam never asserts the labels event | backlog | — |
| B1/B3 URL owner/repo and host/port bounds | fold into fix c2 | failing-first; priority strictly M1 → M2 → B1/B3; B1/B3 drop to backlog before M1 narrows |
