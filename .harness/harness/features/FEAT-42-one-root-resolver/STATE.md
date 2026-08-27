# STATE

## Current

- feature: FEAT-42-one-root-resolver
- run: t01-t02-eng (harness-eng-lead) returned PASS. No run in flight.
- squad: engineering
- status: Building. Plan and BRIEF approved 2026-08-27, committed at ea71a1c.
- T-01 and T-02 are `done` in plan.yaml. 18 tasks remain: 3 team (T-04..T-06, all gated on T-03),
  15 main-session-direct.
- cycles_used: 4 of 10 (one send-back inside t01-t02-eng, for evidence not for the work).
  runs: 6 of 20. Both within budget.
- ORCHESTRATOR SCOPE: the 5 `team` tasks only. The 15 `main-session-direct` tasks are the main
  session's under DEC-174. T-03 gates T-04..T-06, so the next squad segment cannot start until the
  main session has run it.
- Verified BY ME at disk this run, not relayed: both verify blocks extracted from plan.yaml and run
  under my own hand, exit 0, ending `T-01-OK` and `T-02-OK`; `harness_boundary.py`'s TOP-LEVEL
  imports are exactly os/re/sys in both the base version and the edit (the `io`/`contextlib`/
  `factory_config` imports at :297-300 are pre-existing, lazy, and inside `resolve_fleet`);
  `worktree_owner` is AST-identical to 3952814; `wayfind.py` now holds zero `HARNESS_PROJECT_DIR`
  occurrences and no `def root(`.
- Enforcement layer re-checked green with T-01 in the tree: test-check-domain, test-bash-write-guard,
  test-feature-worktree, test-check-plan-routes, test-check-state, test-dispatch-guard all PASS.
- SC-01 re-derived independently over the corrected scan set: still 21 occurrences across 17 files,
  `.omp/extensions/harness-hooks.ts` in scope. `wayfind.py`'s occurrence is now gone, so the next
  measurement should read 20 across 16.
- GitHub mirror: no sub-issues and no parent were ever recorded for this feature (`gh-sync.py open`
  never ran). The mirror is never a gate; noted, not fixed.

## Open Questions

- Q8 (from eng-lead, non-blocking, bears on T-03): `resolve_root` returns the raw
  `HARNESS_PROJECT_DIR` string un-normalized at `harness_boundary.py:68` while every other return
  path is absolute. MEASURED: a relative override returns `'.'` and a trailing-slash override
  returns the slash verbatim. T-03 cds to that value. Impact TODAY is zero — the variable is unset
  in this environment and OMP injects an absolute cwd (`harness-hooks.ts:144`) — so the hazard is
  latent, not live. Recommendation: fold a one-line `os.path.abspath` plus one test case into T-04's
  dispatch rather than spending a fix cycle now.
- Q9 (from eng-lead, non-blocking): T-13's stated rationale for deleting `KNOWN_DIRECTORY_PROBE`
  will be false after T-02 — `wayfind.py` contributes zero probes and is skipped at
  `test-check-plan-routes.py:1183`, so case (20)'s manifest rule will not apply to it, it will
  simply stop seeing it. The deletion is still right; only the reason changes.
- Q10 (from eng-lead, non-blocking): `resolve_root` probes with `os.path.isfile`; the model at
  `check-plan-routes.py:498` uses `os.access(..., os.R_OK)`. At T-13's cutover an
  unreadable-but-present `team-config.yaml` flips from "not a root" to "is a root".
- Q11 (from eng-lead, non-blocking, bears on T-03): T-03's own verify can pass on a suite that ran
  nothing — `grep -c` writes `0` on no match and neither suite run's exit status is checked, so a
  suite exiting 2 from both cwds gives `0` vs `0`, `diff` succeeds and `T-03-OK` prints. Asserting a
  nonzero count is a plan change, which is pm's.
- Q12 (harness defect, non-blocking): `test-validate-digest.py` is not hermetic. Its 6 `[hook]`
  cases read the LIVE `.harness/.inflight-claims.json`. DISCRIMINATING CHECK: with a claim in flight
  it exits 1 with exactly those 6 failures; with the registry at `{}`, same tree, it exits 0 ALL
  PASSED. FEAT-42 T-17 should close it. Until then the qa gate's result depends on whether an agent
  happens to be running.
- Q13 (BLOCKING, harness defect, operator's call): **INV-26 has no green branch for a mid-build
  feature with a finished task, and I hit both sides of it this run.** With no mirror it refuses
  ("tasks are in flight or finished but feature.json records no mirrored issues — run
  `gh-sync.py open`"); after `open` it refuses per task ("plan says done, so the card should read
  Done — the board reads Backlog"). `_EXPECT` at `check-state.sh:1404` maps `done` to the DONE
  station, and the widening at `:1499-1501` applies ONLY while feature.json status is `Review`, so
  the whole Building phase is red from the first done task. Only `cmd_ship` (`gh-sync.py:1231`)
  writes the done station, and that is the main session's act at ship acceptance. So the gate is
  red at 98bd4b3 and will stay red for every actor until ship, including the main session's 15
  direct tasks. Marking the tasks anything but `done` would falsify the record; running `ship`
  would close a feature that is 2/20 built. This needs a ruling.

- Q3 (OPEN, non-blocking — DEC-179 gap): the route check resolves from each task's literal `files:`
  paths and is structurally blind to what a `verify:` block touches. Widen it to verify blocks?
- Q4 (OPEN, non-blocking): D-05 records 20/16, D-12 supersedes with 21/17. Whether D-05 is corrected
  in place is the operator's call.
- Q7 (OPEN, non-blocking, harness defect): `bash-write-guard.sh` blocked a heredoc artifact write
  because the prose body contained an ASCII arrow, parsed as a redirect to a literal target.
