# QA test-matrix gate — FEAT-18-board-truth

## Verdict: PASS

Diff under review: `git diff main...6d2d61b` (all six tasks). Confirmed
`6d2d61b..89ecc11` touches only `.harness/features/FEAT-18-board-truth/{STATE.md,feature.json,
notes/handoff-build.md}` — source-clean as claimed (`git diff 6d2d61b..89ecc11 --stat`).

**Working tree verified against the pin, not just the commit range.** `git rev-parse HEAD` = `89ecc11`
(matches), `git status --porcelain -- .claude/skills/harness .harness/harness.json` returned nothing —
no uncommitted source edits. The suite runs below executed against exactly the tree the pin claims,
not a stale or dirty checkout.

## Phase 1 (BRIEF + plan only, no source) — expected coverage

- SC-01/02/03: integration coverage of `gh-sync.py start-task`/`close-task` against a fake `gh`,
  asserting field-set calls (item id + column), the derived-parent function, and the loud/quiet
  failure split.
- SC-04: inspection — no retry anywhere on the `gh-sync.py` path.
- SC-05: integration coverage of `check-state.sh` INV-26, with a non-vacuous mis-columned +
  corrected-twin pair.
- SC-06: unit/integration coverage of `check-plan-routes.py`'s new status enum, including the
  capital-`Building` typo case, plus a clean run over the live plan corpus.
- SC-07: inspection — absence of the four board keys/item-edit call from
  `branch-create-gate.sh`, paired with a live run proving the gate still denies.
- SC-09: inspection — `SKILL.md`'s sync-point table names an owner for all six subcommands.
- T-06 (docs) is matrix-exempt, not a gap.

This matches what actually shipped — no Phase-1/Phase-2 delta to report.

## Per-kind result

| kind | state | cmd | result |
|---|---|---|---|
| unit | satisfied | `run-unit-tests.sh --kind unit` | exit 0, all scripts PASS including `test-gh-board.py` (17 cases), `test-branch-create-gate.py` (8/8), `test-check-plan-routes.py` (case_25a–e) |
| integration | satisfied | `run-unit-tests.sh --kind integration` | exit 0, all scripts PASS including `test-gh-sync.py`, `test-check-state.py`, `test-check-plan-routes.py` (drift detector clean, both `test-gh-sync.py` and `test-check-plan-routes.py` present in `INTEGRATION_SCRIPTS`, not moved between arrays) |
| functional | not applicable (case a — matrix does not require it) | `cmd: null`, `status: excluded` (DEC-187) | soft skip, signed |
| component | not applicable (case b — no `change_type` in this diff requires it) | `cmd: null`, `unresolved` | soft skip |
| ui | not applicable (case b) | `cmd: null`, `unresolved` | soft skip |
| eval | not applicable (case b — no `ai_behavior` task) | `cmd: null`, `unresolved` | soft skip |
| typecheck | not applicable (case b — not in matrix at all) | `cmd: null`, `unresolved` | soft skip |
`docs` is not a `test_kinds` entry — T-06's `change_type: docs` maps to `[]` in the matrix (exempt).
Its verify command is reported under task-level evidence below, not in this table.

Both skip reasons are distinguished as instructed: `functional` is case (a) — the matrix names it
excluded under a signed decision (DEC-187). `component`, `ui`, `eval`, `typecheck` are case (b) — no
`change_type` in this diff (`logic`, `cross_module`, `api`, `docs`) ever requires them; none is
`frontend`, `feature`, or `ai_behavior`.

## Task-level verify commands, run verbatim

- T-01: `python3 test-check-plan-routes.py && python3 check-plan-routes.py` → all cases PASS,
  live-corpus scan exits 0, `0 violation(s)`.
- T-02: `python3 test-gh-board.py && run-unit-tests.sh --kind unit` → both exit 0 (T-02's files are
  a DEC-174 leave-list item — I ran the standing task verify, wrote and edited nothing there).
- T-03: `python3 test-gh-sync.py` → PASS, part of the integration run above.
- T-04: `python3 test-check-state.py` → PASS, part of the integration run above (T-04 is also
  leave-list — same treatment as T-02).
- T-05: `! grep -qE '...' branch-create-gate.sh && python3 -c ... | ... deny` → both halves ran, grep
  absence confirmed and the positive-control deny fired with the exact reason text.
- T-06: verbatim `for c in open start-task close-task ...` loop + two greps → exit 0.

## SC evidence

| SC | Test |
|---|---|
| SC-01 | `test-gh-sync.py:1086-1099` — start-task sets the sub-issue's item-edit then the parent's, distinct item ids asserted from the fake's call log |
| SC-02 | `test-gh-board.py` `derive_station` cases (building→Building, all-done→Review, mixed→None, empty→None, no-status-key→None) + `test-gh-sync.py:1092-1117` (parent tracks task-status changes; Done-exempt feature makes no item-edit call, `:1144`) |
| SC-03 | `test-gh-sync.py:1150-1184` — the loud pair, one fixture: item-edit fails → exit 0, stderr `gh-sync: ERROR` naming issue 40, the following issue call still happens; gh absent → one SKIP line, exit 0, no item-edit attempted |
| SC-04 | inspection — no retry-shaped keyword in `gh-sync.py`, **and** both `set_station` call sites read directly (`gh-sync.py:196`, `:574`): each is a single `try`/`except gh_board.BoardError` with no loop or re-invocation on failure |
| SC-05 | `test-check-state.py:1371-1386` — mis-columned fixture (T-01 done, card in Backlog) is a violation naming feature/task/status/column; the byte-corrected twin (v.2) reports nothing |
| SC-06 | `test-check-plan-routes.py` `case_25a`–`case_25e`, plus the live-corpus run (`check-plan-routes.py` unargumented, exit 0) |
| SC-07 | inspection — grep-absence of the four keys/`item-edit`, paired with running the gate live against a bad-flow branch; both halves executed verbatim, deny fired |
| SC-08 | struck, `verify: none` — no evidence required |
| SC-09 | inspection — T-06's verbatim verify loop, exit 0 |

## matrix_ok: true

All four in-diff `change_type`s (`logic` ×3, `cross_module` ×1, `api` ×1, `docs` ×1) have their
required kinds present and green. `cross_module`'s `integration` requirement is satisfied indirectly
— `test-gh-sync.py` and `test-check-state.py` (both integration) exercise `gh_board.py`'s five public
functions through `gh-sync.py`'s and `check-state.sh`'s real call paths, not just `test-gh-board.py`
(unit) in isolation.

## Mutation evidence

I did **not** re-run mutation proof for T-02 (`gh_board.py`/`test-gh-board.py`) or T-04
(`check-state.sh` INV-26) — both are on the explicit leave list (DEC-174 carve-outs), and running a
live mutate/restore cycle on them is not mine to do even in a worktree, since the dispatch reserves
edits and proofs on those paths to the main session. I looked for a written receipt substantiating
the "6 of 6" / "5 of 5" figures relayed to me in the dispatch and **found none** in
`.harness/features/FEAT-18-board-truth/notes/` or `STATE.md` — grepped for "mutat", "6 of 6", "5 of
5", "6/6", "5/5" across every note file, zero hits. I am relaying the dispatch's report as an
unverified claim, not a measurement I hold evidence for. It was not load-bearing for this PASS: my
verdict rests on the unit/integration suite runs and the individual verify commands I executed
directly above, all green.

## Findings

- The T-02/T-04 mutation-proof figures cited in the dispatch have no corresponding artifact in this
  feature's notes. Not a coverage gap (both kinds are independently satisfied by the suite runs
  above) — flagged so the claim isn't propagated as measured when it wasn't found.

## Coverage gaps

None against any live SC (SC-01 through SC-07, SC-09). SC-08 struck, no evidence required.
