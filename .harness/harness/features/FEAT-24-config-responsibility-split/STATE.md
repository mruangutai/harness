# STATE

## Current

- feature: FEAT-24-config-responsibility-split
- run: .harness/harness/features/FEAT-24-config-responsibility-split/runs/2026-08-19-2-product/
- squad: product
- status: in-progress

Phase: **ship, building. Nine of ten tasks are done, committed and verified; T-10 is in flight.**
The record was reconciled first — `plan.yaml` said `pending` for five committed tasks and their
cards sat in `Backlog`; all five are now `done` and #504-#508 are closed. `check-state.sh` is back
to its seven pre-existing violations with none added.

**The feature's central path now works, and it did not before.** `board_for` against the live API
returns kaya's board with all five stations. Two defects in `factory_gh.file_at_ref` had shipped
past 208 passing checks: `gh api -f` forced a POST (404), and `validate=True` rejected GitHub's
line-wrapped base64 (285 newlines in kaya's payload). Both were invisible because every case drives
a fake `gh` that models argv but not the real response. Fixed at `574f73c`, with a case that feeds
wrapped base64 through the fake — I proved it reddens by restoring the pre-fix decoder at runtime,
one FAIL, the named case, no file edited. **SC-06 is met and was checked live, not from the suite.**

Commits: `000934b` T-01 · `22814c7` T-08 · `692672d` T-09 (kaya PR #335) · `962417a` T-02 ·
`d177bab` T-07 part A item 1 · `0ee0124` T-03/T-04/T-05/T-06 · `b88cbfd` T-07 · `574f73c` the
base64 fix · `d80f1c4` the record reconciliation.

**Next, in order:** T-10 returns → commit → the qa `test_matrix` segment (validator squad, the
project's only blocking gate) → the four-angle simplify pass (eng-lead, read-only, before the pin)
→ pin `review_sha` → the review panel → pm's goal-check on all 13 SCs → close-out (ship-refresh and
distillation in ONE turn, two dispatches) → the CEO briefing.

**Simplify hazard, carried:** before applying any finding to a file a verify clause reads, check
whether the clause greps words the edit changes. A pass did exactly that today and gates stayed
green.

Cycles: **3 of 10** — the plan-phase architecture fix, and two live-defect fix cycles.
Runs: 11 recorded of 20.

## Open Questions

- Q1 (harness defect, backlog): a lead returned BLOCKED with no digest while its member was still
  in flight and the fix was landing — issue #461, now the ninth instance. Do not re-file.
- Q2 (harness defect, backlog B-12): `factory_land.py` does not commit; T-09 failed with
  `No commits between master and factory/issue-334` until the operator committed by hand.
- Q3 (harness defect, backlog B-4): `feature.json`'s schema declares no `phase` property under
  `additionalProperties: false`, so the playbook's "record your phase there" is unsatisfiable.
- Q4 (harness defect, backlog B-11): `gh-sync.py` has no un-start subcommand.
- Q5 (new, for the briefing): the fake `gh` recorder models argv but not the HTTP method or the
  real response shape, and shipped two defects past a green suite. A live smoke check for
  `file_at_ref` is the candidate fix; qa should rule on it at the matrix gate.
- Q6 (main session): four paused feature dirs carry six of `check-state.sh`'s seven violations.

Briefing: `notes/ship-review-2026-08-18-ship-01.md` — stale, rewritten at the ship decision.
