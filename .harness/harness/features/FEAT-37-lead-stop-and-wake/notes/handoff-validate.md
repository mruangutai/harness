# Handoff — FEAT-37, validate (closed) — written at 68cc8e9

## Next

**One thing is still owed: SC-08.** It is the only criterion that measures conduct rather than
text on disk, and it cannot be graded from inside a worktree. Dispatch ONE domain lead from a main
checkout whose working tree carries merge commit `68cc8e9`, then read that lead's sidecar and
confirm it ended its turn on dispatch rather than polling. The main checkout is currently on
`fix/868-analysis-digest-and-lead-notes`, which does NOT carry the merge, so a dispatch from it
today reads the OLD playbook and proves nothing.

Nothing else is owed. The feature is merged, all eight cards are at Done, milestone #29 is closed,
and the residual findings are filed as issues, not left in the briefing.

## Trust

- Merged as PR #912, merge commit `68cc8e9`; `gh-sync.py ship` exit 0, eight cards to Done,
  milestone #29 closed, `feature.json` status `Done` — verified-at 68cc8e9
- **CI was red first, and the qa gate had reported it green.** T-09 pushed DEC-70's index row to 45
  words against a 30-word cap, so `test-gen-decisions-index.py` failed at the graded `4e652f9`.
  `git show 4e652f9:...DECISIONS-INDEX.md` gives 45 words for that ruling — verified-at 4e652f9
- Fixed at `6430320`, ruling shortened to 28 words. Word-cap test PASS, regeneration diff exit 0,
  `--group coverage` 3/3 PASS — verified-at 6430320
- Seven SCs met by their declared methods at `4e652f9`; the diff from there to the merge touches
  feature records plus that one index row, so the panel verdict still covers the code — verified-at 68cc8e9

## Dead ends

- **Do not re-derive the cause of the false dispatch refusal (#917) from the briefing.** It says a
  single registry file at the outer root is shared by every worktree. That is FALSE — each root has
  its own `.harness/.inflight-claims.json`, and both files exist on disk. `inflight_registry.py:64`
  joins the relative path onto whatever root it is given. The suspect is `dispatch-guard.sh:123
  _root_for(flow)` choosing the root, and that is a hypothesis nobody has tested.
- **Do not run SIMPLIFY on this feature.** It must precede the `review_sha` pin, and the panel has
  already graded at `4e652f9`, so it now costs the panel run as well. It is no longer a one-run
  decision and was deliberately left undone.
- **Do not add a success criterion for the DEC-70 preload gap (#913).** pm and validator-lead
  independently ruled it a NEW criterion, and adding one to a signed BRIEF after grading changes
  what was signed. It is a backlog row on purpose.

## Working set

- `.harness/harness/features/FEAT-37-lead-stop-and-wake/notes/ship-review-2026-08-27-02.md` — the briefing
- `.claude/skills/harness-team/SKILL.md` — the playbook the rule lives in
- `.claude/skills/harness/bin/test-lead-stop-and-wake.py` — the guard, groups `playbook`, `coverage`, `bound`
- Open issues: #913 #914 #915 #916 #917 #918 #919 #920
