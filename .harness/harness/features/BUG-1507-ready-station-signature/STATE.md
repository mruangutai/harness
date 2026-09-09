# STATE

## Current

- feature: BUG-1507-ready-station-signature
- run: none — plan phase closed at the operator signature gate
- squad: none
- status: awaiting-user

Log:

- 2026-09-08: station `plan` — feature instantiated from templates; mission PLAN opened against
  issue #1507. Premises re-verified on disk in the worktree before any dispatch: `harness-plan.md:24`
  carries `status <feature-dir> Ready`; `github-mirror.md:94,96` carry `status <dir> Ready` /
  `status <dir> Review`; `SKILL.md`'s build phase (136-153) names no feature-level `building` write;
  `gh-sync.py` `cmd_status` docstring (1305-1317) enumerates Ready/Review/Plan/Done/Abandoned and
  omits Building. `.agents/skills` is a symlink to `../.claude/skills`, so `.claude/...` is the one
  canonical, git-tracked path for all four surfaces.
- 2026-09-08: run `plan-product` PASS — pm drafted BRIEF.md (6 REQ, 10 SC) and plan.yaml (5 tasks,
  6 decisions, `status: plan`, `approval.status: pending`). It found a FIFTH live instance of the
  same defect at `harness-plan.md:11` (`board-station.py <n> Plan`) and folded it in as D-06 under
  disclosure. Orchestrator independently confirmed that instance: `board-station.py` validates its
  station argument against `factory_config.station_names(board)`, which returns the six lowercase
  MANDATED_STATIONS, so `board-station.py <n> Plan` refuses at exit 2 exactly as
  `gh-sync.py status <dir> Ready` does. The `/harness-plan` kickoff board write has been dead too.
- 2026-09-08: run `2026-09-08-01-product` FAIL — plan-phase panel segment 1, pm's goal-check of the
  drafted plan against the operator's stated intent. 3 of 5 Definition-of-Done bullets discharged;
  9 findings (0 high/critical, 5 med after lead re-rank, 2 low, 2 info). All repairs BRIEF-only.
  Note at `notes/research-BUG-1507-goalcheck-plan-c0.md`. `cycles_used` 0 -> 1.
- 2026-09-08: RECORD CORRECTION, disclosed rather than silently rewritten. The orchestrator had
  appended the draft run as id `2026-09-08-01-product` with `code_grade: n_a`. Two errors: the
  goal-check lead then named its own run DIRECTORY `2026-09-08-01-product`, so one id labelled two
  different runs and `check-state.sh`'s `run_verdicts` would have collapsed a PASS and a FAIL onto
  it; and `code_grade` belongs only to a validator run (`check-state.sh` reads it only when
  `squad == "validator"`). Corrected: the draft run now carries the id of its own run directory,
  `plan-product`, and no `code_grade`; the goal-check run keeps `2026-09-08-01-product` and carries
  its true verdict, FAIL. No verdict or outcome was altered by this correction.
- 2026-09-08: run `2026-09-08-1-product` PASS — fix cycle. R-1..R-7 landed against F-01..F-07;
  F-08 accepted, F-09 declined with reason. Orchestrator ruled Q1 to the disclosure route (the
  issue's own scope line excludes the code work) and Q2 to yes.
- 2026-09-08: run `2026-09-08-01-validator` PASS — plan-panel, `cycle: 0`, `severity_max: med`,
  `must_fix: []`. BOTH readers ran; neither was skipped. 4 findings: two `scope` findings that the
  T-02 and T-03 `verify:` commands prove phrase-presence rather than the binding their REQ needs;
  one `should-not-exist` finding against T-05's self-reinvocation machinery; one low against D-03's
  circular justification.
- 2026-09-08: run `2026-09-08-02-product` PASS (1 send-back inside the run) — the panel record.
  All four findings resolved and transcribed into `plan.yaml`'s `panel:` key with computed `PF-`
  ids. `cycles_used` 1 -> 2.
- 2026-09-08: orchestrator verification at its own tier, none of it delegated: all four `PF-` ids
  recomputed with `panel_findings.py` (4/4 matched); all five `verify:` commands run from the
  worktree root, each RED (T-01..T-04 exit 1, T-05 exit 2 file-absent); `check-plan-routes.py`
  0 violations exit 0; zero backticks in any plan value; `handoff_done_when.py` exit 0. Additionally
  probed that T-02's and T-03's REPAIRED gates can report GREEN — mutated text in memory, no file
  touched: each returns 0 on the correct fix and 1 on the exact near-miss its finding named. A gate
  that cannot go green blocks the build as surely as one that cannot go red ships a defect.
- 2026-09-08: PLAN PHASE CLOSED at the operator signature gate. `notes/handoff-plan.md` written.
  `approval.status` stays `pending` in both plan.yaml and BRIEF.md — only the main session signs.

## Open Questions

- Q1 (operator, decides at signature): the operator's DoD bullet 2 asks that a card at Ready ALWAYS
  mean "signed, not started". Measured false today for TASK cards — `gh_board._task_statuses` reads
  an absent task status as `ready` (`gh_board.py:192-202`), so a reconcile can place a task card at
  Ready with no signature. The PARENT is protected (`derive_station` never returns `ready`, D-18).
  Closing the task-card half is `gh_board.py` code work the issue's own scope line excludes. The
  limit is disclosed in BRIEF.md `## Constraints`; the operator accepts it or widens scope.
- Q2 (operator, decides at signature): T-05 (the regression witness test) and D-06 (repairing
  `harness-plan.md:11`) are COUPLED — `:11` sits inside T-05's sweep scope, so striking T-05 makes
  D-06 optional while keeping T-05 forces it. Striking T-05 also requires retyping T-01/T-02 from
  `bugfix` to `docs`, or three tasks are left with no `test_matrix` evidence and the qa gate fails.
  Both strike notes in BRIEF.md now name every casualty.
- Q3 (harness owner, not a work item): a subagent return delivered as task status
  `failed (exit 1)` with "Subagent called yield with null data" while the transcript carried a
  complete, well-formed VERDICT/DIGEST/artifact block and every claimed artifact was present and
  correct on disk. Observed twice this run, by two different tiers. A tier routing on the tool
  status alone discards a passing run.
- Q4 (harness owner, not a work item): the orchestrator playbook and the plan.yaml template both
  say `plan-merge.py apply` "unions by id", which reads as though re-emitting a same-id item with a
  corrected body changes it. It does not — `apply` refuses at exit 7 CONFLICT
  (`plan-merge.py:738-742`); the verb that changes a value is `amend`. A pm reading the current
  wording takes exit 7 as a gate failure.
