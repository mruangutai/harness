# Handoff — FEAT-29-graphql-budget, build → validate — written at 8c89f57, seq-3

## Next

Do not dispatch anything until the operator answers Q1 and Q3 in
`notes/ship-review-2026-08-19-02.md`. Q1 decides whether the blocking matrix is satisfied as signed;
Q3 grants T-03 a fourth cycle for the `rc` clause. On Q3 granted, dispatch `harness-eng-lead` with
**T-03 alone**: drive `_counting_fake(rc=1)` through `run_gh`, catch `GhError`
(`factory_gh.py:163-168` raises rather than exits), assert the logged `rc == 1`. Both files are inside
T-03's `files:`. Then re-gate qa, then SIMPLIFY via eng-lead, re-run both suites, re-pin
`review_sha` at the new tip, then the panel via `harness-validator-lead`. Batch B (T-07 then T-09) is
the operator's and gates the goal-check, since SC-01/SC-03/SC-04 grade against it.

## Trust

- Both suites green at the pin: unit exit 0 / 0 FAIL / 18 scripts, integration exit 0 / 90 PASS /
  0 FAIL — re-run by me — verified-at 3fbfd0a
- The cheap read works against the REAL API: 486 board-3 items for 5 GraphQL points — live call —
  verified-at bee6234, code unchanged since
- `harness-qa` is NOT granted `factory_gh.py`; `harness-backend-dev` and `harness-dev-ops` are —
  `check-domain.sh --resolve` — verified-at 3fbfd0a. This is why run 06's mutation proofs are
  admissible and qa's admissibility doubt does not reach them
- `_cost.returncode` at `factory_gh.py:162` is pinned by nothing; deleting it leaves `--kind unit`
  green — qa's worktree mutation, `runs/2026-08-19-07-validator/probe-rc-line-162.md` — **UNVERIFIED
  by me** (no write grant on that file), but the four wrap-site cases provably use default `rc=0`
- `review_sha` = `3fbfd0a` = branch tip at pin time — `git rev-parse` — verified-at 3fbfd0a. **Re-pin
  after every commit**; it was stale on FEAT-25 and FEAT-27
- The "172 PASS" style figures are per-check line counts, not suite size; the runner emits one line
  per script, 18 for unit — `run-unit-tests.sh:58-67` — verified-at 3fbfd0a. Only deltas are sound

## Dead ends

- Do NOT run `gh-sync start-task` or `close-task` for any task until T-07's after-measurement lands —
  seven positive-control lines quote cards reading `Backlog`, and closing #586 already destroyed the
  eighth — `notes/layer0-batch-b-FEAT-29.md` §1, §3 — verified-at bee6234
- Do NOT re-dispatch over a run whose `state.yaml` shows `in_flight` with no `completed_at`, however
  clean the tree measures — an orphaned member wrote a mutation probe after my measurement —
  `runs/2026-08-19-06-eng/digest.md` Q1 — verified-at 3fbfd0a
- Do not edit `check-state.sh`, `test-check-state.py` (DEC-174 am.4 carve-out, repaired and green),
  `CLAUDE.md`, `.harness/notes/**`, `.harness/logs/**` — `check-domain.sh --resolve` — verified-at 3fbfd0a
- Do not upgrade SC-01/SC-03 to automated, and do not route the matrix question as a `FAIL` — the
  remedy edits a signed artifact — `BRIEF.md ## Verification gaps` — verified-at 3fbfd0a

## Working set

- `.harness/harness/features/FEAT-29-graphql-budget/notes/ship-review-2026-08-19-02.md`
- `.harness/harness/features/FEAT-29-graphql-budget/runs/2026-08-19-07-validator/digest.md`
- `.harness/harness/features/FEAT-29-graphql-budget/notes/layer0-batch-b-FEAT-29.md`
- `.harness/harness/features/FEAT-29-graphql-budget/plan.yaml`
- `.harness/harness/features/FEAT-29-graphql-budget/feature.json`
