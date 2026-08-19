# Handoff — FEAT-29-graphql-budget, build → build (blocked) — written at bee6234, seq-2

## Next

Do not dispatch qa, SIMPLIFY or the panel yet — the build phase has not exited, because T-03 has no
PASS run and cannot get one until the operator answers Q1/Q2 in
`notes/layer0-batch-b-FEAT-29.md` §6. When T-03's `files:` is amended, re-dispatch
`harness-eng-lead` with **T-03 alone** (the `build` team, same team file), then in order: the qa
segment to `harness-qa` — T-03 is `change_type: feature`, so the matrix requires **unit AND
integration**, not unit alone — then SIMPLIFY via eng-lead, re-run the suites, pin `review_sha` at
the branch tip, then the panel via `harness-validator-lead`.

## Trust

- T-01, T-02, T-04 landed PASS; suite exit 0 with zero `^FAIL` lines, 139 `PASS` lines — re-run by me,
  not relayed — verified-at bee6234+worktree
- The DEC-174 carve-out held: `check-state.sh` and `gh-sync.py` are byte-unchanged — `git diff --stat`
  empty on both — verified-at bee6234
- The cheap read works against the REAL API: 486 items for 5 GraphQL points via
  `factory_gh.project_item_stations` — live call, this session — verified-at bee6234
- T-03 is unlandable as written: `run-unit-tests.sh:40-55` exits 2 for any `test-*.py` in neither
  script array, over the UNION regardless of `--kind`, and `run-unit-tests.sh` is not in T-03's
  `files:` — read the source — verified-at bee6234
- Board stations: T-01/02/03/04/07/09 read `Backlog`, T-05/06/08 read `Done`, parent reads
  `Building` — live read — verified-at bee6234
- The lead's 198/198 case total — its digest — **UNVERIFIED**; the runner prints `N/N cases passed`
  for only some scripts and my own count summed 27 by that pattern
- Every assertion was proven able to go red — the lead's receipts under `notes/receipt-*` —
  **UNVERIFIED by me**; I hold no write grant on `gh_board.py` or `factory_gh.py`, so I cannot run a
  mutation probe myself. This is the one substantive claim I could not check.

## Dead ends

- Do NOT run `gh-sync start-task` or `close-task` for any FEAT-29 task until T-07's after-measurement
  is captured — seven positive-control lines quote cards reading `Backlog`, and closing #586 already
  destroyed the eighth — `notes/layer0-batch-b-FEAT-29.md` §1, §3 — verified-at bee6234
- Do not edit `CLAUDE.md`, `check-state.sh`, or `.harness/notes/**` — `NOBODY` or DEC-174 carve-out —
  `check-domain.sh --resolve` — verified-at 3920513
- Do not widen T-03's `files:` yourself — it amends a signed artifact and is the operator's —
  playbook authority boundary — verified-at bee6234
- Do not re-run the qa segment on the current three-task diff; T-03 will change it and the matrix
  grades the diff — `harness.json` `test_matrix` — verified-at bee6234

## Working set

- `.harness/harness/features/FEAT-29-graphql-budget/notes/layer0-batch-b-FEAT-29.md`
- `.harness/harness/features/FEAT-29-graphql-budget/runs/2026-08-19-01-eng/digest.md`
- `.harness/harness/features/FEAT-29-graphql-budget/plan.yaml`
- `.harness/harness/features/FEAT-29-graphql-budget/notes/measurement-before-positive.md`
- `.claude/skills/harness/bin/run-unit-tests.sh` (the drift detector, lines 40-55)
