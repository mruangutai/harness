# Simplify pass — BUG-2420 build diff — 2026-11-22

Scope: `git diff d5be5392 2f2b21aa -- .claude/skills/harness/bin/plan_merge/stations.py tests/integration/test-plan-merge.py tests/unit/test-plan-merge-first-station.py`.
Four parallel read-only `scout` dispatches, one angle each (harness-simplify, code surface); main-session-direct (DEC-174), so no eng-lead route.

| Angle | Reader | Result |
|---|---|---|
| reuse | S2420Reuse | no findings: the text.py field/indent helpers accept any deeper indent, so none is a drop-in for the exact-field-indent contract; the integration case reuses fixture_root/run_apply/run_verb/check |
| simplification | S2420Simplify | no findings: `_splice_station` carries real insert/rewrite behaviour; exact field indent and the tasks-range bound are required anchoring |
| efficiency | S2420Efficiency | no findings: linear scans over the already-loaded lines inside the existing locked update; the unit file avoids CLI start-up |
| altitude | S2420Altitude | no findings: station discovery and mutation stay in the station writer; apply is untouched, as signed |

Nothing to apply. No deviation from the signed T-01 intent.

Pre-pin CI parity (main, at 2f2b21aa): every `run:` step of `.github/workflows/tests.yml` job `checks` run locally — typecheck (after `bun install --frozen-lockfile`), precompile, unit suite (66 files), feature state, plan routes, canonical-reader audit, instruction paths, layout, repository state — all exit 0.
