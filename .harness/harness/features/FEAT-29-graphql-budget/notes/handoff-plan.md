# Handoff — FEAT-29-graphql-budget, plan → build — written at 3920513, seq-1

## Next

Do **not** dispatch until `notes/measurement-before.md` exists and passes T-06's `verify:` — that
file is the whole reason the build was held. Then dispatch the `build` team to `harness-eng-lead`
with **T-01, T-02, T-03, T-04** (all `execution_mode: team`, `execution_agent: harness-backend-dev`);
the lead routes each by `consult-when`. Then, in order: the qa segment (`test_matrix`, the only
blocking gate), SIMPLIFY via eng-lead, re-run the suites, pin `review_sha` at the branch tip, panel
via `harness-validator-lead`. Then write `notes/layer0-segments-FEAT-29.md`'s batch B handover
(T-09, T-07, T-08) and return.

## Trust

- Both approval gates pass; `plan.yaml approval.status: approved`, `BRIEF.md ## Approval` approved —
  `.harness/harness/features/FEAT-29-graphql-budget/plan.yaml:5`, `BRIEF.md:148` — verified-at 3920513
- Q1 (board pruning) is RULED code-fix-only; nine tasks, none added — `BRIEF.md:141` — verified-at 3920513
- Lanes unchanged at the branch point; `gh_board.py`/`factory_gh.py`/`gh_cost_log.py`/`gh-sync.py` →
  `harness-backend-dev, harness-dev-ops`, `CLAUDE.md` → `NOBODY` — `check-domain.sh --resolve` output —
  verified-at 3920513
- `check-plan-routes.py` = `0 violation(s)`, exit 0; `DEVIATION` on T-06/T-07/T-09 is correct output —
  run at 3920513 — verified-at 3920513
- Mirror opened without an orphan; parent #571 skipped as already recorded, milestone #18,
  sub-issues #579–#587 — `feature.json` `github` block — verified-at 3920513
- GraphQL budget 3673/5000 used at 09:59 local, window resets 10:45:06 — `gh api rate_limit` —
  verified-at 3920513
- `check-state.sh` was clean for FEAT-29 with two violations on FEAT-26/FEAT-28 unapproved BRIEFs —
  operator's run on this tree, minutes before spawn — **UNVERIFIED by me** (a re-run costs ~507 of
  1,327 remaining points)
- Issues #579–#587 may or may not be on board 3; `gh-sync.py open` printed no station line —
  `notes/layer0-segments-FEAT-29.md` re-check 5 — **UNVERIFIED** (a board read is the expensive call)

## Dead ends

- Do not build the eng segment in a git worktree — the feature dir is untracked on `main`, so a
  worktree from the branch point carries no `plan.yaml` — `git status --porcelain` at spawn —
  verified-at 3920513
- Do not land T-01/T-04 early to parallelise — both perturb the tree SC-04 compares
  (`factory_gh.py` is imported by `check-state.sh`; T-03 writes `.harness/logs/gh-cost-<date>.jsonl`
  during the gate run) — `notes/layer0-segments-FEAT-29.md` — verified-at 3920513
- Do not re-open Q1 or add a pruning task — operator ruling — `BRIEF.md:141` — verified-at 3920513
- Do not "upgrade" SC-01/SC-03 from `verify: inspection` to automated — that is a plan change —
  `BRIEF.md ## Verification gaps` — verified-at 3920513

## Working set

- `.harness/harness/features/FEAT-29-graphql-budget/plan.yaml` (tasks, `verify:`, `intent:`)
- `.harness/harness/features/FEAT-29-graphql-budget/notes/layer0-segments-FEAT-29.md`
- `.harness/harness/features/FEAT-29-graphql-budget/BRIEF.md` (SC-01..SC-10, constraints)
- `.harness/harness/features/FEAT-29-graphql-budget/feature.json`
- `.claude/skills/harness/bin/check-state.sh` (INV-26 at 1120-1240)
