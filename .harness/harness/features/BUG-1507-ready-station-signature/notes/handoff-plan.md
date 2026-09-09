# Handoff — BUG-1507-ready-station-signature, plan → build — written at 4b5dbb23, seq-1

## Next

Do not dispatch anything until the operator's signature lands: this note is written AT the
gate, not after it. Once `approval.status` reads `approved`, build in two waves, because
T-05 `depends_on` T-01 and T-02 and those two are NOT the eng squad's to write. Wave 1 is
main-session-direct — T-01, T-02, T-03 (`check-domain.sh --resolve` returns NOBODY for all
three surfaces, a DEC-174 carve-out recorded in `plan.yaml` `lanes:`). Wave 2 dispatches
`harness-eng-lead` for T-04 then T-05, per plan-task:T-05.verify. Record the feature station
as `building` when wave 1 opens — that instruction is what T-03 adds, and this feature is its
first user.

## Trust

- The plan is panel-PASS at severity_max med, both readers ran, none skipped; all four
  findings `disposition: resolved` — `plan.yaml` `panel:`, verified-at 4b5dbb23 (all four
  `PF-` ids recomputed with `panel_findings.py` by the orchestrator, 4/4 matched).
- Every one of the five `verify:` commands is RED on the unfixed tree (T-01..T-04 exit 1,
  T-05 exit 2, file absent) — orchestrator ran all five from the worktree root,
  verified-at 4b5dbb23.
- T-02's and T-03's repaired gates also go GREEN on a correct fix and RED on the exact
  near-miss each finding named — orchestrator probe over mutated text in memory, no file
  touched, verified-at 4b5dbb23.
- `harness-plan.md:11`'s `board-station.py <n> Plan` is a live FIFTH instance of the same
  defect: `board-station.py` validates against `factory_config.station_names(board)`, the
  six lowercase MANDATED_STATIONS — `board-station.py:169-172`, verified-at 4b5dbb23.
- `approval.status` is `pending` and `## Approval` in BRIEF.md is `pending` — UNVERIFIED as
  a build precondition; the successor confirms both read `approved` before wave 1.

## Dead ends

- Do not add `building` to `cmd_status`'s early-return tuple. `load_recorded` raises
  `SystemExit` on an unparseable `feature.json`, so short-circuiting is NOT
  behaviour-preserving — source: `plan.yaml` D-02, `gh-sync.py:515-540`, verified-at 4b5dbb23.
- Do not lowercase a station word that names a board COLUMN. Only the token after a tool
  name and that tool's first argument is a command argument — source: `plan.yaml` D-04 and
  each task's LEAVE list, verified-at 4b5dbb23.
- Do not use `plan-merge.py apply` to change an existing item's value: it refuses at exit 7
  CONFLICT. `amend --key ... --field ... --expect-sha256 --value-file` is the verb —
  source: `plan-merge.py:738-742`, verified-at 4b5dbb23.

## Working set

- .harness/harness/features/BUG-1507-ready-station-signature/plan.yaml
- .harness/harness/features/BUG-1507-ready-station-signature/BRIEF.md
- .harness/harness/features/BUG-1507-ready-station-signature/notes/intent-BUG-1507.md
- .claude/skills/harness/references/github-mirror.md
- .claude/skills/harness/SKILL.md

## Done when

Scope: build BUG-1507's five tasks once the operator has signed
Authority: approval:.harness/harness/features/BUG-1507-ready-station-signature/BRIEF.md#Approval
Authority: plan-task:T-01.verify
Authority: plan-task:T-05.verify
