# Handoff — FEAT-13, build → validate — written at 56abf27, seq-2

Written at the seam by the orchestrator that crossed it in one session, not by a successor. Recorded
because the seam is real even when the session is continuous.

## Next

Sequence the validate phase against a pin that CONTAINS the work. Both tasks are committed —
`56abf27` `[harness:t-01]` carries all nine source and test files, and T-02's live read follows. The
blocking `test_matrix` qa gate is the first validate segment, then the reviewer panel, then pm's
goal-check over all ten SCs. T-01 is `change_type: cross_module`, so the matrix requires exactly
`unit` and `integration` and nothing else.

## Trust

- Everything runs in a git worktree at
  `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/FEAT-13-single-issue-board-lookup`; the
  main checkout is on `chore/203-end-copy-distribution`, FEAT-12 mid-build — verified-at 56abf27
- The main checkout's nine in-scope files are byte-identical to `origin/main`, so no work leaked to
  the wrong root — `git diff --quiet origin/main` over each — verified-at 56abf27
- Unit 10/10 scripts exit 0 and integration 97/97 exit 0, re-run by me rather than relayed —
  verified-at 56abf27
- `factory_gh.project_items` occurs 0 in decompose, 0 in land, exactly 1 in claim, which is the
  structure T-01's `verify:` demands — verified-at 56abf27
- `_find_existing_item_id` is a bare delegation carrying no `query=` and no state scoping, and
  `_item_repo` has zero remaining references in `bin/` — read at source — verified-at 56abf27
- `plan.yaml:368`'s `argv[:2] == ["project", "item-list"]` can NEVER match — `run_gh`
  (`factory_gh.py:88`) builds `[gh] + list(args)` — verified-at 56abf27
- `.harness/notes/grilling-board-read-lookups-2026-08-10.md` is NOT reachable from this branch; it
  is on `chore/203` only — `git cat-file -e` on all three refs — verified-at 56abf27

## Dead ends

- Do not introduce any open-only filter into decompose's lookup — `BRIEF.md ## Constraints` —
  source: operator
- Do not touch the claim poll at `factory_claim.py:238`, or `project_items` and its `totalCount`
  guard — same artifact — source: operator
- Do not fix `land`'s closed-issue failure: filed as **#238**, out of scope — same artifact —
  source: operator
- Do not treat `claim --issue` exiting 2 rather than 1 as a defect: ratified at signature —
  `plan.yaml approval.rulings` Q1 — source: operator
- Do not route test authoring to `harness-qa`: defect **#218** — source: operator dispatch
- Do not check out the feature branch in the main checkout — it would pull FEAT-12's tree out from
  under a live flow — verified-at 56abf27

## Working set

- `.harness/features/FEAT-13-single-issue-board-lookup/plan.yaml`
- `.harness/features/FEAT-13-single-issue-board-lookup/BRIEF.md`
- `.harness/features/FEAT-13-single-issue-board-lookup/feature.yaml`
- `.harness/features/FEAT-13-single-issue-board-lookup/runs/t01-eng/digest.md`
- `.harness/features/FEAT-13-single-issue-board-lookup/notes/receipt-harness-backend-dev-lookup-swap.md`
