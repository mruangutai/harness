# STATE

## Current

- feature: BUG-1507-ready-station-signature
- run: VALIDATE PASSED at `ac5e24e5` — panel `must_fix: []`, `severity_max: med`, all four readers
  ran. Returned to the main session, which owns PR open, CI watch, merge and `gh-sync.py ship`
- squad: none — the orchestrator's build+validate mission is complete
- status: in_review (panel clean; awaiting the main session's PR and merge)
- station: `review` (plan.yaml line 3), written by `gh-sync.py status <feature-dir> review`
- review_sha: `ac5e24e51f2520e273580f66c372b5bd143001f1`

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
- 2026-09-08: OPERATOR SIGNED (plan.yaml `approval.status: approved`, BRIEF `## Approval`
  approved, at acc8bf63). Both open questions ruled by the operator: Q1 — accept the disclosed
  limit that task-card Ready exclusivity (`gh_board.py` code work) stays out of scope; Q2 — keep
  both T-05 and D-06, strike neither, retype nothing. The main session then ran the post-signature
  `gh-sync.py status <feature-dir> ready` and recorded SC-01's transcript at
  `notes/sc01-ready-write-transcript.md` (partial: (a) and (b) met, (c) not applicable — zero
  sub-issues recorded).
- 2026-09-09: BUILD PHASE OPENED, station `ready` -> `building`. The orchestrator ran
  `plan-merge.py set-feature-station --station building` on this feature's own `plan.yaml` at the
  moment the eng segment began, BY HAND from the worktree copy of T-03's instruction (the
  control-plane checkout does not carry it until this branch merges). Observed `status: building`
  at plan.yaml line 3; SC-05's record written to `notes/sc05-building-write-transcript.md`.
- 2026-09-09: T-01, T-02, T-03 landed main-session-direct by the orchestrator (the DEC-174
  carve-out `plan.yaml` `lanes:` records — `check-domain.sh --resolve` returns NOBODY for all three
  `.claude/` doc surfaces). Commits `e5223f10` (T-01), `d9caec31` (T-02), `3063b1dc` (T-03). Each
  task's own `verify:` re-run by the orchestrator after the edit: all three exit 0, each having
  been RED on the same tree before the edit. T-02 additionally names `plan.yaml` explicitly in the
  Building row so SC-06's "which writes the card and which writes the plan" is answerable from the
  row alone.
- 2026-09-09: run `2026-09-08-t04-t05-eng` PASS, 0 send-backs — `harness-eng-lead` hosted the
  `build` team and routed both tasks to `harness-backend-dev`. T-04's Building bullet plus D-02's
  decision paragraph added to `cmd_status`'s docstring (16 insertions, zero deletions, every line
  inside the docstring — SC-08 holds); T-05's witness created with the accepted sets DERIVED from
  `factory_config` and an in-process negative control, no subprocess self-reinvocation and no
  conditionally skipped row (the disposition of PF-4d48a751). Orchestrator re-ran both `verify:`
  blocks itself: T-04 exit 0, T-05 exit 0 with 8 PASS rows and 0 FAIL. Committed `64bc9351`.
  `cycles_used` unchanged at 2 — a clean first-pass run adds none (DEC-157).
- 2026-09-09: run `2026-09-08-qa-validator` PASS, 0 send-backs — the blocking `qa_gate`.
  `integration` is the only kind the matrix demands, for the three `bugfix` tasks (T-01, T-02,
  T-05); the two `docs` tasks require none. All three discharge to
  `tests/integration/test-station-argument-spelling.py`, which the lead verified can report RED
  rather than only green. SC-02, SC-03 and SC-09 all PASS; `must_fix: []`. The orchestrator re-ran
  the two SC-09 suites itself: both exit 0. Note at `notes/qa-BUG-1507-build.md`.
- 2026-09-09: run `2026-09-08-01-simplify-eng` PASS — SIMPLIFY, the last build step, run BEFORE
  the pin. All four angles read the five-path diff; the pass is EMPTY BY RULE, not by omission.
  Two findings, neither appliable: a redundant conjunct at the witness's line 139 (dropping it
  would weaken an assertion after the qa gate) and a residual that D-05's `because:` does not name
  every directory the sweep glob excludes (its only remedy edits a signed `plan.yaml`, which pm
  alone may write). Both carried as non-blocking backlog rows. Working tree clean at `287aafb5`.
- 2026-09-09: BUILD -> VALIDATE seam. `gh-sync.py status <feature-dir> review` run (lowercase),
  plan station `building` -> `review`; no parent issue is recorded for this feature, so no card
  was written and the mirror reported that in one line, exit 0. `review_sha` pinned at the seam
  commit, which contains every deliverable and no later code change.
- 2026-09-09: run `2026-09-08-panel-validator` PASS — the validate panel, `cycle: 0`, at the pinned
  `ac5e24e5`. ALL FOUR readers ran; none skipped. `severity_max: med`, `must_fix: []`,
  `code_grade: grade_2` (one accepted grade-2 function with its reason on file). Five findings, none
  gating: VL-01 (med, the lead's own — the witness cannot see the `plan-merge.py
  set-feature-station --station <token>` shape that T-02 and T-03 add to the swept corpus), F-01
  (low, the `verify:` chain's BrokenPipeError under `pipefail`, not exploited because
  `run-unit-tests.sh` executes the file directly), F-02 (med, accepted code-risk grade 2), and two
  assessed-and-dismissed info rows. Reviewer notes at `notes/review-harness-{code-reviewer,qa,
  security-reviewer,ui-reviewer}-c0.md`.
- 2026-09-09: VL-01 measured by the orchestrator rather than relayed, at
  `notes/vl-01-plan-merge-shape-measurement.md`: the unguarded shape occurs TWICE in the swept
  scope, both `building`, both accepted — the gap is latent, nothing ships broken, and the
  placeholder `--station <name>` is already excluded correctly by the witness's character class.
  NOT routed as a fix cycle: T-05's signed `intent:` spells the pattern character for character, so
  widening it would amend an approved plan without approval. Carried up as a non-blocking backlog
  row with its cost measured (one alternation, one accepted-set entry, `MIN_OCCURRENCES` 6 -> 8).
- 2026-09-09: RECORD CORRECTION, disclosed rather than silently repaired. Two things.
  (1) The qa segment was first appended to `feature.json` under the id `2026-09-08-qa-validator`
  while its run DIRECTORY is `2026-09-08-03-qa-validator`; the id now matches the directory, the
  same class of error this feature already corrected once in the plan phase.
  (2) While probing whether `feature-json-merge.py set-key` accepts a non-scalar, the orchestrator
  ran it against `runs` and it ACCEPTED an array, overwriting the whole runs list with the single
  probe entry. It was restored in the next call from this STATE.md log and the run directories on
  disk: nine runs, verdicts unchanged, `2026-09-08-01-validator` keeping its `code_grade: n_a` and
  every code-grading run correctly omitting the key. No verdict was altered. The probe was
  careless — `set-key`'s own help says "scalar", and it does not enforce that; raised as Q5.

## Open Questions

- Q1 RESOLVED by the operator at signature: accept the disclosed limit. Task-card Ready
  exclusivity is `gh_board.py` code work the issue's own scope line excludes; the limit stays
  disclosed in BRIEF.md `## Constraints`.
- Q2 RESOLVED by the operator at signature: keep both T-05 and D-06; strike neither, retype
  neither T-01 nor T-02 to `docs`.
- Q3 (harness owner, not a work item): a subagent return delivered as task status
  `failed (exit 1)` with "Subagent called yield with null data" while the transcript carried a
  complete, well-formed VERDICT/DIGEST/artifact block and every claimed artifact was present and
  correct on disk. Observed twice in the plan phase, by two different tiers. A tier routing on the
  tool status alone discards a passing run.
- Q4 (harness owner, not a work item): the orchestrator playbook and the plan.yaml template both
  say `plan-merge.py apply` "unions by id", which reads as though re-emitting a same-id item with a
  corrected body changes it. It does not — `apply` refuses at exit 7 CONFLICT
  (`plan-merge.py:738-742`); the verb that changes a value is `amend`. A pm reading the current
  wording takes exit 7 as a gate failure.
- Q5 (harness owner, not a work item): `feature-json-merge.py set-key` is documented as setting a
  top-level key to a JSON SCALAR value, and it accepts a JSON array without complaint — so a single
  mistaken call silently replaces the whole `runs` history, which is the one part of `feature.json`
  no other verb can reconstruct. Either the verb should refuse a non-scalar, or `runs` should be
  named as a protected key.
