# QA matrix gate — FEAT-29-graphql-budget

review_sha: 4b98191 (verified: `git rev-parse --short HEAD` = 4b98191)
diff graded: bee6234..4b98191 (union)

## Phase 1 (pre-code) expected coverage, derived from BRIEF.md + plan.yaml only

- unit: project_item_stations — stationed/null-station/pagination/truncation/no-totalCount/null-user
- unit: board_stations — repo exclusion, stationed present, unstationed None present, content-null safe
- unit: gh_cost_log — success line, failing line w/ rc, counter-read failure -> null cost no raise,
  80-char truncation, ON writes, OFF (unset) writes nothing (file AND line, success AND failure),
  coverage-notice first line, no duplicate coverage line
- unit: factory_gh rate-limit message — positive (budget message w/ used/limit/reset) + negative
  discriminator (unrelated failure does NOT produce it)
- integration: gh-sync.py's gh wrapper — same cost-log wiring, since T-03's intent explicitly
  names gh-sync.py:114 as a second wrap site
- integration/inspection: check-state.sh INV-26 identical violation set + positive control

All but one of these materialized in the diff. The gap: **no test anywhere exercises gh-sync.py's
cost-log wiring.**

## Commands verified verbatim against plan.yaml / harness.json

- unit: `.claude/skills/harness/bin/run-unit-tests.sh --kind unit` — matches T-01..T-04's `verify:`
  and `test_kinds.unit.cmd`. Match.
- integration: `.claude/skills/harness/bin/run-unit-tests.sh --kind integration` — matches
  `test_kinds.integration.cmd`. Match. No BLOCKED.

## Measured results (my own run, not the caller's)

- `--kind unit`: exit 0, 164 PASS / 0 FAIL (18 scripts, drift detector clean — test-gh-cost-log.py
  registered)
- `--kind integration`: exit 0, 90 PASS / 0 FAIL (12 scripts)
- Both counts reproduce the caller's baseline exactly.

## Matrix by task

| Task | change_type | required | state |
|---|---|---|---|
| T-01 | logic | unit | **satisfied** — all 6 assertion classes named in intent present in test-factory-gh.py:713-862, plus a query-shape guard (no widened fieldValues connection) |
| T-02 | logic | unit | **satisfied** — 4 required assertions present, isolated per fixture (test-gh-board.py:210-251) |
| T-03 | feature | unit AND integration | **PARTIAL — missing.** factory_gh.py half of the wiring (run_gh) is thoroughly unit-tested (test-gh-cost-log.py, 24 checks). The gh-sync.py half (gh-sync.py:114-116, `with gh_cost_log.measured(args) as _cost:`) has **zero test coverage in either kind**. `test-gh-sync.py` (the integration file that would exercise it, per B-6 sitting in INTEGRATION_SCRIPTS) is untouched in this diff — no mention of `gh_cost_log`, `HARNESS_GH_COST_LOG`, or cost recording anywhere in it. SC-05 names "gh-sync.py's wrapper" explicitly as in scope; this half of that scope is unverified. |
| T-04 | bugfix | unit + bug-class | **satisfied** — positive test (rate-limit text -> budget message w/ used/limit/reset, test-factory-gh.py:1366-1404) and discriminator (unrelated "could not resolve to a Repository" failure -> message absent, asserted on content not just a token, :1420-1438) |
| T-05, T-08 | docs | none | n/a |
| T-06, T-09 | scaffolding | none | n/a |

**matrix_ok: false** — T-03's integration/gh-sync.py gap. Route back to T-03's owner
(harness-backend-dev) to add a test-gh-sync.py case that drives gh-sync.py's `gh()` wrapper
through a failing and a successful call with `HARNESS_GH_COST_LOG=1`, asserting a line lands in
the cost log the same way test-gh-cost-log.py already proves for `factory_gh.run_gh`.

## Known findings — confirmed against the diff (not rediscovered)

- B-1 (test-factory-gh.py abort shape): not re-litigated; treated as no mutation evidence where
  cited. All coverage claims above rest on assertion review, not mutation, for exactly this reason.
- B-2 (gh_board.py's "unreachable `or {}` guard"): **CONTRADICTED.** It is the only `or {}` in
  gh_board.py (line 142, `content = item.get("content") or {}`). It IS reachable — a null-content
  item is a live case per T-01's own intent ("An item whose content is null gets an empty dict"),
  and test-gh-board.py's isolated null-content fixture (line ~236-251) exercises it directly and
  passes (`board_stations: item with content null does not crash and is not in output`). Whatever
  made B-2 record it as unreachable does not hold against this diff.
- B-3 (T-04 fixtures tolerate an extra gh call): confirmed — test-factory-gh.py:215-224 comments
  explicitly queue two Results "not one" to accommodate the rate-limit budget path's extra
  subprocess call.
- B-5 (stale line anchor in T-03's intent): not independently re-checked; not load-bearing for
  matrix_ok.
- B-6 (test-gh-sync.py sits in INTEGRATION_SCRIPTS, `--kind unit` never runs it): confirmed at
  run-unit-tests.sh:18. This is the direct cause of the T-03 gap above — the file that would
  exercise gh-sync.py's change was never touched.

## SC evidence (verify: automated only)

- SC-02: test-gh-board.py:231-236 (repo exclusion, stationed present, unstationed None-present)
- SC-05: test-gh-cost-log.py — ON-half lines ~101-235 (success/failing/counter-fail/truncation/
  coverage-notice), OFF-half lines 243-257 (unset -> no file AND no line, success AND failing —
  graded hardest per instruction). Satisfied for factory_gh.run_gh's path; gh-sync.py's path is
  the T-03 gap above and is NOT separately evidenced.
- SC-07: test-factory-gh.py:1380-1438, positive + discriminator, content-asserted
- SC-10: `--kind unit` + `--kind integration`, both exit 0, matches the caller's baseline counts
  exactly (164/0, 90/0)

## SCs not mine (verify: inspection) — pending, not failing

- SC-01, SC-03, SC-04, SC-06, SC-08, SC-09: not automated by design (DEC-187/D-02). T-06 has
  landed (`notes/measurement-before.md` exists, dated 2026-08-19 10:53). **T-07 and T-09 are
  genuinely still `status: pending`** — confirmed live: `notes/measurement-after.md` and
  `notes/measurement-board6.md` do not exist in the feature's notes/ directory. SC-01, SC-03,
  SC-04 (which grade against T-07/T-09's output) are pending evidence, not failures.

## Changed-file set vs plan.yaml's declared files — divergence found

Actual diff (bee6234..4b98191), code files only:
factory_gh.py, gh-sync.py, gh_board.py, gh_cost_log.py, run-unit-tests.sh, test-check-state.py,
test-factory-gh.py, test-gh-board.py, test-gh-cost-log.py.

Union of tasks' declared `files:` (code portion): factory_gh.py, test-factory-gh.py, gh_board.py,
test-gh-board.py, gh_cost_log.py, test-gh-cost-log.py, gh-sync.py, run-unit-tests.sh,
check-state.sh.

**Divergence: `test-check-state.py` is changed in the diff (21 lines — the INV-26 fixture now
answers both `gh project item-list` and `gh api graphql` shapes, commit `00bc623`) but is not
listed under ANY task's `files:`.** It is a DEC-174 carve-out file (main-session-direct only,
which the diff's commit messages are consistent with — not team-dispatched), so I did not and
will not edit it. But the plan's traceability is incomplete: this file's change plainly belongs to
T-07's territory (it is what makes INV-26's fixture answer the new query shape) yet T-07 itself is
still `status: pending` and carries no note of this file. Flagging as an open question for
plan/traceability, not a code defect.

**Also observed, not caused by me:** `.harness/logs/gh-cost-2026-08-19.jsonl` exists untracked (168
lines, dated today, contains FEAT-05-fixture records from a fake-gh test run) — pre-existing
pollution of a NOBODY-writable path from a run that had `HARNESS_GH_COST_LOG=1` set outside a temp
root, before amendment 5 flipped the default. I did not touch this file (verified line count
unchanged across both my test runs, both run with the variable unset). Not mine to clean; flagged
as an open question.
