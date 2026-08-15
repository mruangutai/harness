# QA gate — FEAT-09, cycle 0

base `47ed11f` · review_sha `4918d06` (HEAD). Scope: `git diff 47ed11f..4918d06`.

## Verdict: PASS, with coverage findings

Suite is green, matrix is satisfied, and the 17+8 fixtures are mostly real discriminating tests —
but two of them (SC-08 clause 4, the SHARED line) claim more assurance than they deliver, and four
branches in `check-plan-routes.py` have zero coverage. None of these fail the floor (the matrix only
requires `unit`, and `unit` is present and passing), so this is `PASS` with findings for a dev to pick
up, not a `FAIL`.

## Gate run

`.claude/skills/harness/bin/run-unit-tests.sh` — exit 0, **13/13 scripts PASS** (matches the corrected
count; `PLAN.md:312`'s "14 PASS" is stale per the task brief, confirmed by reading `SCRIPTS` array —
13 entries at `run-unit-tests.sh:6`). Full run: `grep -c "^PASS "` on the runner's own output = **32**
(13 script-level `PASS` lines + 19 case-level lines from `test-check-plan-routes.py`, which itself
prints `PASS test-check-plan-routes.py` as its 13th script-level line — 19 of those 32 are new named
cases: 16 of the 17 numbered cases emit one named check each, case 17 splits into 3, so 16+3=19).
`test-check-domain.py`'s new `run_resolve()` block adds 8 more named `ok`/`FAIL` lines (not counted in
the `^PASS ` grep — that suite prints its own `ok`/`FAIL` format, then one `PASS test-check-domain.py`
line from the runner). `check-docs.sh` — exit 0, no stale statements.

Also ran `check-plan-routes.py` against the feature's own PLAN, since T-02's `verify:` predicts an
exact receipt (`PLAN.md:226-228`) I had not otherwise exercised (my case-17-style probing above used
only `tempfile` fixtures): **matches exactly** — `0 violation(s) across 1 plan(s)`, exit 0, and exactly
one `DEVIATION T-01 ... but declared main-session-direct` line, naming T-01 as predicted.

**Required kinds** (`.harness/harness.json` `test_matrix`): T-01, T-02 are `change_type: logic` →
requires `unit`, present (`test-check-domain.py`, `test-check-plan-routes.py`, both in-diff, both
registered in `run-unit-tests.sh:6`, both passing). T-03, T-04 are `change_type: docs` → matrix
requires nothing; their own `verify:` (greps + `run-unit-tests.sh` + `check-docs.sh`) passed directly.

```
matrix_ok: true
suite: pass
failures: 0
kinds: [{ kind: unit, state: satisfied, cmd: ".claude/skills/harness/bin/run-unit-tests.sh", named_tests: 32 }]
```

## SC evidence

- SC-01/02/03/04 → `test-check-domain.py` cases (a)-(h), all individually named, all exercise the
  real `--resolve` CLI or the real hook path (`test-check-domain.py:417-469`).
- SC-05/06 → `test-check-plan-routes.py` cases 1-5 (`:59-83`).
- SC-07 → cases 6-7 (`:85-99`) — case 7 diffs exit status against the same plan with the wildcard task
  removed, a real discriminator, not a fixed-value assertion.
- SC-08 → cases 8,9,16 (source greps) + case 17 (behavioural) — see finding F1 below.
- SC-09 → cases 10-12 (`:111-118`), plus my own `wc -l` confirms template is 68 lines (<80 budget).
- SC-10 → case 13 + the whole-suite run above.
- SC-11 → confirmed directly: `git diff 47ed11f..4918d06 -- .claude/agents/harness-pm.md` is **empty**
  (0 lines); rule lives once, at `harness-spec-driven/SKILL.md:28-40`.
- SC-12 → cases 14-15 (`:129-136`).

## Coverage findings

**F1 — MED — SC-08 clause 4 is individually satisfied; the clause SET does not discriminate the
over-permissive matcher class.** Clause 4's literal text — "no `startswith`/prefix comparison... a
path granted only through a mid-pattern wildcard still resolves to its granting agent" — IS proven:
case 17 (`test-check-plan-routes.py:139-159`) shells all the way through `check-plan-routes.py` →
`check-domain.sh --resolve` → the real `matches()`, so a hand-rolled prefix comparison inside
`check-plan-routes.py` would fail it. What the four SC-08 fixtures together (8, 9, 16 source greps +
17 positive-behavioural) do NOT catch: `.harness/features/*/runs/*-eng/**` matched against
`.harness/features/FEAT-09-plan-time-route-check/runs/1-eng/notes.md` never requires the mid-pattern
`*` to span a `/` — the wildcard consumes only `1` before `-eng`, all within one segment. A
reimplementation whose `*` incorrectly matches `/` (fnmatch's own defect, which `glob_to_re`'s
docstring at `check-domain.sh:61-69` explicitly calls out as a **different**, over-permissive failure
mode) would ALSO report this path OK — over-matching produces the same "OK" case 17 checks for, and
clauses 9/16 only grep for absent strings, which an over-permissive matcher can still satisfy under a
different name. Confirmed: no fixture anywhere in the diff asserts a path that a `/`-crossing `*`
would wrongly grant and the real matcher denies — grepped both test files for `1-eng`/`runs/.*eng`,
one hit only, the positive case. Held at MED rather than higher because `matches()`/`glob_to_re()` are
explicitly *not modified* by this diff (T-01 intent) — nothing regresses today — but a future
reimplementation of the over-permissive shape ships green against this exact suite.

**F2 — MED — the `SHARED <pattern>` line (D-02, `check-domain.sh:200-201`) is untested end-to-end
through `check-plan-routes.py`, and I ran the scenario rather than inferring it.**
`resolve_agents()` (`check-plan-routes.py:64`) explicitly strips `SHARED ...` lines before deciding
grant status. No fixture in the 17 cases uses a `files:` entry that is a shared-only surface
(`package.json`, `pyproject.toml`, etc. — `team-config.yaml:59-64`). Measured directly: a fixture task
`files: package.json`, `execution_mode: team` → `check-plan-routes.py` prints
`VIOLATION T-01: package.json ungranted (NOBODY); execution_mode is team — legal tokens: team,
main-session-direct` and **exits 1**; separately, `check-domain.sh --resolve package.json </dev/null`
itself prints `NOBODY` then `SHARED package.json`, exit 0 — the SHARED signal reaches
`check-plan-routes.py` and is thrown away. So today a planner naming a genuinely shared file (any of
the 5 in `team-config.yaml:59-64`) as a task's sole `files:` entry with `execution_mode: team` gets a
`VIOLATION` telling them to pick `team` or `main-session-direct` — neither of which is actually true;
the file is co-owned by convention, not by domain grant. No test pins this behaviour and no doc names
it, so it is either an intentional simplification nobody wrote down, or a live UX gap on the
authorization boundary the SHARED line exists to communicate.

**F3 — LOW/MED — four branches in `check-plan-routes.py` have zero test coverage:**
missing `files:` line → `VIOLATION` (`:79`); an ungranted path with an unrecognized/unknown
`execution_mode` token, e.g. the retired `squad-dispatched` (D-07 names this as the "safe direction"
case) → no fixture; a PLAN path argument that does not exist → `exit 2` (`:135-137`); `check-domain.sh`
itself exiting 2 (unparseable/duplicate-key manifest) propagating to `check-plan-routes.py`'s own
`exit 2` (`:58-60`). All four are real code paths I read directly, none is exercised by any of the 17
named cases or elsewhere in the diff.

**F4 — INFO — SC-08 clauses 8, 9, 16 are source greps**, as flagged in the dispatch — respellable, so
their assurance rests entirely on case 17, which F1 says is narrower than SC-08 clause 4 claims.

## Coverage gaps against Phase-1 (BRIEF-only) expectations

None beyond F1-F3 above — my Phase-1 list (derived from BRIEF SC-01..SC-12 before reading source)
matches what T-01/T-02's fixtures actually implement one-for-one; the delta found is depth-of-proof
(F1, F2) and untested error/edge branches (F3), not missing SCs.

## Test-first check

`test-check-domain.py`'s new `run_resolve()` block and `test-check-plan-routes.py` both ship in the
same diff as the code they test (T-01, T-02 each list test file + source file in one `files:`), per
FEAT-07 D-02's "diff only vouches for itself if it contains the test" convention. Cannot verify commit
ordering (no intermediate commits in this worktree's history for this feature branch) — not a finding,
just unverifiable from where I sit.

## Not applicable

`functional`, `integration`, `component`, `ui`, `eval`, `typecheck` — all `cmd: null` in
`harness.json`, and the matrix does not require them for `logic`/`docs` change types here. Soft skip,
consistent with the BRIEF's own `## Verification gaps` section.
