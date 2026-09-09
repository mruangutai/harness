# QA gate — cycle 2, review_sha 358ac56188a04f63f83dbbc3f9bfd4a6fc1c28f2

## BLUF

`matrix_ok: true`. Both re-derived measurements match the dispatch's claims exactly, verified by
direct execution, not inspection. No production code changed since the certified tip d80a7b12; the
only diff (`d80a7b12..358ac561`) is a 4-line `GRADE-2 REASON` comment in
`tests/integration/test-hooks-install.py` plus the `review_sha` bump in `feature.json`
(`git diff --stat 358ac561..HEAD` confirms only `feature.json` + `notes/` files changed after the
pin — zero executable lines). GATE-ONLY: authored nothing.

## Change-type inference (full feature diff, merge-base `6ad7233f`..`358ac561`, per P-13)

Task `change_type`s present in `plan.yaml`: `config`×1, `bugfix`×5, `feature`×2, `docs`×2,
`scaffolding`×2. `feature`'s `always: [unit, integration]` alone sets the floor to **unit +
integration**, independent of any `bugfix`/`config` `when` predicate. (`bugfix`'s
`__bug_class__`/`match_bug_class` leg is a standing unresolvable placeholder per repo Expertise
G-08 — contributes nothing, does not shrink the floor set by `feature`.)

## Per-kind state

| kind | state | command | observed |
|---|---|---|---|
| unit | **satisfied** | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind unit` | exit 0, 33 files, pool summary "33 files, 2.23s wall" — all named PASS |
| integration | **satisfied** | `env -u HARNESS_AGENT_TYPE .agents/skills/harness/bin/run-unit-tests.sh --kind integration` | exit 0 (job bg_23, 70.44s wall); 3949-line log, no FAIL lines |

`ai_behavior`, `ui`, `component`, `functional`, `typecheck` are not implicated by this diff (no
production surface of those kinds touched) — not applicable, consistent with the standing
`test_kinds` config (`functional`/`eval` excluded by signed decisions; `ui`/`component` unresolved
and untouched here).

## Re-derived measurement 1 — `test-hooks-install.py`

Ran directly: `env -u HARNESS_AGENT_TYPE python3 tests/integration/test-hooks-install.py`.

- **Exit code: 0** (both the internal `EXIT=0` self-report and the process return code).
- **Cases discovered and executed: 5** (`case_commands_verbatim_in_skill`,
  `case_sc08_before_and_after`, `case_sc13_idempotence`, `case_sc13_reporting_and_red_proof`,
  `case_sc14_end_to_end_and_red_proof`) — `main()` (line 506-513) calls all five unconditionally, no
  filter/skip logic, confirmed by reading the dispatcher.
- **30 named `PASS:` assertions, 0 `FAIL:`** — counted from the raw run output
  (`grep -c '^PASS:'` / `'^FAIL:'`), not the internal tally alone.
- This is not a narrowed/empty sweep: `case_sc14_end_to_end_and_red_proof` performs real git
  merges against bootstrapped origins (`(e-green) real merge succeeds`,
  `(e-green) SC-14: the terminal feature's worktree is gone after a real merge`), and both
  `case_sc13_*` and `case_sc14_*` carry live RED-PROOF arms that assert the *opposite* fixture
  variant actually reddens (e.g. `(d) RED PROOF: unconditional variant FAILS clause 2`,
  `(e-red) RED PROOF: ... the worktree SURVIVES the merge`) — evidence the suite discriminates,
  not merely that it runs.

## Re-derived measurement 2 — code-grade gate

Ran directly (not the wrapping unit test): `.agents/skills/harness/bin/code-grade.py --base
6ad7233f5014c9488228154335fb16295b6f65bc --head 358ac56188a04f63f83dbbc3f9bfd4a6fc1c28f2 --json`
over the full feature diff.

- `passing: 50` — matches the claimed count exactly.
- `records`: 54 total. Grade histogram: `{5: 29, 4: 20, 2: 4, 3: 1}`. **Zero grade-1.**
- The single grade-3 record is `tests/integration/test-merge-gate.py::fixture` — a **test** file,
  not production code, so **zero production grade-3**, matching the claim.
- The four grade-2 (`result: FAIL`, `severity: med`) records are all in files carrying a written
  `GRADE-2 REASON` comment, confirmed by direct grep, not inference:
  - `.claude/skills/harness/bin/merge-gate.py:main` — `merge-gate.py:29,118`
  - `tests/integration/test-check-state.py:case_t06_build_entry_invariant` — `:4619`
  - `tests/integration/test-hooks-install.py:_run_merge_and_check` — `:392` (this is the comment
    this cycle added)
  - `tests/integration/test-post-merge-sweep.py:case_t07_build_entry_receipt` — `:883`

Both figures (`50 PASSING`, `no grade-1 / no production grade-3`) are confirmed by my own
measurement at this pin, not accepted from the dispatch.

## Adequacy (separate from `matrix_ok`)

No production behavior changed this cycle (comment-only diff), so there is nothing new for the
suite to newly bind against — this section speaks to the standing suite the floor is resting on,
measured live, not inherited from cycle 1's prose.

- **unit** binds real decision tables, not passthrough plumbing: `test-gh-sync-build-entry.py`'s
  `BE-*` cases exercise `record_build_entry`/`load_recorded`/recover-terminal helpers across
  distinct recorded-state combinations (era-exempt, conflicting `--parent`, absent record,
  recovered-terminal), and `test-feature-schema-build-entry.py` covers
  `BUILD_ENTRY_ERA_EXEMPT` membership as a pure function. These are table-driven with both
  positive and negative rows, not single happy-path smoke checks.
- **integration** is the stronger of the two for this feature: `test-hooks-install.py`,
  `test-post-merge-sweep.py` and `test-check-state.py` each carry explicit mutation/RED-PROOF arms
  (install a broken shim, flip a recorded value, drop a config key) that assert the wrong-code
  variant actually reddens, per DEC-217's Over clause and this repo's own precedent — not a case
  where "green" could not have distinguished correct from broken code.
- I did **not** find a case where a green assertion's subject was decoupled from its target (P-01/
  G-11 class of defect) in the two kinds I re-ran directly; I looked specifically at the four files
  carrying `GRADE-2 REASON` comments (the highest-complexity, most failure-classes-per-function
  code) since that is where a vacuous assertion is most likely to hide, and each carries live
  mutation coverage as noted above.
- I did not re-run `locally_run` kinds (`omp_session_accessor`, `handoff_comprehension`,
  `issue_types_live`) — none of this feature's touched surface (`merge-gate.py`, `gh-sync.py`
  build-entry path, `feature_schema.py`, `post-merge-sweep.sh`) matches those kinds' `detect`
  globs, so they are not implicated and no recorded run is owed for this change.

No new finding. This is a clean, independently re-derived confirmation at 358ac561, not a restatement
of cycle-0's settled findings and not a manufactured finding to justify the spawn.

## Files authored

None beyond this note. Zero test/fixture/source/helper files created or modified.
