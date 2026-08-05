# STATE

## Current

- feature: FEAT-09-plan-time-route-check
- phase: ship (validate → ship at 3a5a245; seam note `notes/handoff-ship.md`)
- worktree: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-09 (branch feat/FEAT-09-plan-time-route-check)
- head: 3a5a245 · base: 47ed11f · `review_sha` 7354ad0
- run: none open
- status: **awaiting_user** — one decision left, SC-08. Everything else is done.

**The feature is finished and ready to ship.** All four tasks DONE, the panel's only HIGH fixed and
re-reviewed, distillation complete across ten agents, and the CEO briefing written to
`notes/ship-review-close.md`. The build phase should never discover routing again: the checker run
live on this feature's own PLAN gives **0 violations and exactly one DEVIATION naming T-01** — the
DEC-174 carve-out disclosed rather than blocked.

**Goal-check ran at HEAD on all 12 SCs: 11 MET, SC-08 UNMET-AS-UNPROVEN.** This is the only open
item. `check-plan-routes.py` implements no path matcher at all, so clause 4's property holds by
construction — but the fixture written to catch a future contributor re-introducing a prefix
comparison **cannot fail**. I measured it rather than relaying it: the case-17 path resolves to
**two** agents live, and a prefix-only implementation would grant it to **six**, while the test
asserts only "no VIOLATION for T-01, some OK for T-01" and the `OK` line names no agent. Three
remedies are on the table and the choice is the user's — (a) change shipped checker output, (b)
amend SC-08 (approval-gated), (c) accept and file. Not routed to a lead: it is a decision, not a
fix, which is why `cycles_used` stays at 2.

**Nothing unreviewed sits in the tree.** `git diff --name-only 7354ad0 HEAD` returns `feature.yaml`
only — re-verified this leg, because a goal-check citing an unreviewed source commit would rest on
an unpinned diff.

**Gates re-run BY ME at HEAD, not relayed:** unit exit 0 (32 PASS, 0 FAIL, 13 scripts) · docs 0 ·
state 0 · index drift 0 · all 12 Expertise files pass `check-expertise.sh`. The leads hold no Bash
and two flagged their own Expertise files unverified, so I held every mechanical gate at my tier.

**Squad returns:** eng PASS, validator PASS, product **ESCALATE** — product escalated for SC-08
alone and was right to: a decision only the user can make must not ride quietly inside a PASS, and
that was product's last scheduled run on this feature.

**The headline finding, carried into the briefing.** VF-1, VF-2 and now SC-08 are one class: the
logic was correct and the thing meant to notice could not. VF-1/VF-2 are wrong reachability; SC-08
is an assertion that cannot discriminate. None was visible to someone reading the gate's own code
and every gate was green throughout. An all-green verify is not an absent defect.

## Open Questions

- **Q-SC08 BLOCKING** — the only blocker. Which remedy for SC-08's non-failing fixture: (a) name the
  resolving agent in the checker's `OK` line, (b) amend the criterion, or (c) accept as unproven and
  file? (c) is principled; none is free. Detail in `notes/ship-review-close.md`.
- Q-B1 NON-BLOCKING, NEEDS A RULING — a `shared:` file (package.json, pyproject.toml) is falsely
  REJECTED by the checker. It fails **closed**, not open. Answering it amends DEC-179.
- Q-B2 NON-BLOCKING — three of SC-08's four clauses are respellable source greps. Issue #74 mode 3,
  live in this feature; same root as the blocker above.
- Q-DOC NON-BLOCKING, HARNESS DEFECT — the team rule text names the state-file violation as
  top-level keys holding *prose lists*, but the guard rejects any unrecognised top-level key
  including a bare integer counter. The doc is narrower than the enforcement.
- Q-INV17 NON-BLOCKING, HARNESS DEFECT — a handoff note's shape is re-checked only once `phase:`
  moves past the seam, so an over-cap note sits unflagged for the whole phase it describes.
- ~~Q-RESCOPE~~ **RESOLVED** — delta review ran, PASSED, findings applied at 7354ad0.
- ~~Q-VF1~~ **RESOLVED at 7218d63.** ~~Q-VF2~~ **FILED as issue #132** by ruling, out of scope here.
