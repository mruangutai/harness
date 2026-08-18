# STATE

## Current

- feature: FEAT-23-ship-flow-fixes
- run: none — the briefing is written and the feature awaits the operator's ship acceptance
- squad: none
- status: awaiting-user

**The feature is complete.** Branch `feat/FEAT-23-ship-flow-fixes`, tip `9885670`. Six tasks landed,
all 13 success criteria met or deliberately deferred, the blocking qa gate and the review panel both
PASSED, the four-angle simplify pass ran as the last build step, and Expertise is distilled across
all three squads. Three tickets close with it: #417, #430, #453.

**The briefing is `notes/ship-review-2026-08-17-13.md`** (rendered sibling `.html`). It carries 23
proposed backlog rows, B-1 to B-23; anything the operator does not strike becomes an issue on
acceptance, and anything not listed dies silently.

Verified by me at `9885670`, not relayed: `--kind unit` 16/16 scripts exit 0; `--kind integration`
12/12 exit 0; SC-05 measured **per section** — the only method that can see it — with all four angles
at `plan surface` 1 / `code surface` 1; `check-expertise.sh` exit 0 over all 15 files;
`check-state.sh` exit 0; parent `#454` at `Review`.

**The panel's PASS was taken at `490c37c` and the tip has moved five times since.** It transfers on
measurement, re-taken at the FINAL tip: **zero** `.py`/`.sh`/`.ts` files changed between `490c37c`
and `18a2e05`, the only non-markdown file in the whole delta being my own `feature.json`. Everything
since the pin is prose, Expertise, notes and one generated HTML. Re-measure if the tip moves again.

Two criteria are **deferred by `BRIEF.md:149-152`**, not missed: SC-04 (the next feature to ship needs
no follow-up commit to clear INV-26) and SC-13 (the next feature planned from a named ticket lands it
in `Plan`). They are the real test of this feature and they are answered on the *next* one.

Budget: `cycles_used` **4 of 10** — one cycle, spent on the unmet SC-05. `len(runs)` **19 of 20**, an
informational bound that never stops a feature. My read: the runs earned their place with two
exceptions, both mine — the duplicate T-05 dispatch and the reviewer-ops correction round.

Next: the main session presents the briefing. On acceptance it runs `gh-sync.py ship` and
`gh-sync.py backlog` for the unstruck rows. Merge stays user-gated; nothing has merged. See
`notes/handoff-build.md`.

## Open Questions

- **The largest cost of this feature was a harness defect, not the work.** `validate-digest.py --hook`
  fires on a lead's turn-end while its dispatched member is still in flight; a lead has no wait
  primitive, so its only exits are a premature verdict or a fabrication. **Eight recurrences.** It does
  not merely produce false returns — it manufactures a disk state that reads exactly like an abandoned
  run, and I misread one and dispatched T-05 twice (~146k tokens, zero code). **A mitigation now holds:
  leads that keep the turn open with read-only calls until members return have defeated it seven
  consecutive times.** DEC-174 surface — operator-only. Briefing row B-1.
- **THIS ORCHESTRATOR'S TWO ERRORS, recorded as failures.** (1) The duplicate T-05 dispatch above: the
  file that would have stopped me is the run's own `state.yaml`, which records `dispatched_at` and
  `completed_at` per step, and I never opened it. (2) I dispatched the three panel reviewers as
  "write-less", following the playbook's close-out wording, when `check-domain --resolve` grants each
  its own Expertise file — costing a correction round. The playbook wording is briefing row B-16.
- **`check-expertise.sh` cannot detect a wipe** — it validates sections, caps, word counts and the line
  budget, all of which a file reduced to one entry would pass. The no-wipe evidence for this feature is
  before/after count pairs taken independently by each lead and member, not the checker.
  `harness-security-reviewer.md` sits at 134 of its 150-line budget and the spawn hook truncates
  silently rather than erroring.
- **The digest-skim's value split by squad and the split is the finding.** Engineering accepted 11
  entries, all 11 from the skim; validation 9, 8 from the skim — because no member of either squad kept
  an observation log. Product accepted 10 and **zero** came from another agent's digest. The skim earns
  its cycle exactly where members write no log. Rows B-18, B-19.
- All remaining residuals — the untested fail-open branches, `_atomic_write`'s third copy, the D-05
  `argv1` prose error, the index tag-row regression, the `§4.4` naming defect, the scratchpad guard,
  the missing `Agent` tool, the missing `SendMessage` — are enumerated as B-2 to B-23 in the briefing
  with their evidence. They are not repeated here; the briefing is the artifact addressed to a human.
- Arch finding G remains deliberately unapplied by the operator's signature.
