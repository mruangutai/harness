# PASS — FEAT-64 QA clean-pin re-gate

Review SHA: `721b690e3578fbaba2b88d93774667d94ac4d8a3` (detached execution checkout `feat64-pin`). All named executable, matrix, signed-chain, and retained fail-first gates pass. SC-01 is supported: the current ledger and current byte evidence agree; c1's `103/.harness=99` is the historical failed finding, not current ledger evidence.

## Matrix

- `.claude/skills/harness/bin/run-unit-tests.py --kind unit` — exit 0; 42 named files; pool summary: `42 files, 10.34s wall`.
- `.claude/skills/harness/bin/run-unit-tests.py --kind integration` — exit 0; 69 named files; pool summary: `69 files, 94.84s wall`.

The signed plan marks T-01, T-02, and T-03 `cross_module`; both required kinds ran and passed.

## Signed verification chains

- **T-01** — `python3 tests/unit/test-factory-gh.py && python3 tests/unit/test-feature-schema-build-entry.py && python3 tests/unit/test-gh-cost-log.py && python3 tests/unit/test-handoff-done-when.py && python3 tests/unit/test-handoff-policy.py && python3 tests/unit/test-harness-boundary.py && python3 tests/unit/test-harness-yaml-corpus.py && python3 tests/unit/test-run-identity.py && python3 tests/integration/test-factory-decompose.py && python3 tests/integration/test-harness-yaml.py && python3 tests/integration/test-inflight-registry.py && python3 tests/integration/test-worktree-terminal.py` — exit 0; all 12 commands passed.
- **T-02** — `python3 tests/unit/test-gh-sync-build-entry.py && python3 tests/integration/test-board-station.py && python3 tests/integration/test-check-omp-port.py && python3 tests/integration/test-check-skill-weight.py && python3 tests/integration/test-gh-sync-abandon.py && python3 tests/integration/test-gh-sync-open.py && python3 tests/integration/test-gh-sync-record.py && python3 tests/integration/test-gh-sync-ship.py && python3 tests/integration/test-gh-sync-start-task.py && python3 tests/integration/test-post-merge-sweep.py && python3 tests/integration/test-run-unit-tests-kinds.py && python3 tests/integration/test-run-unit-tests-layout.py && python3 tests/integration/test-upgrade-config.py` — exit 0; all 13 commands passed.
- **T-03** — `python3 tests/unit/test-broad-catch-census.py && python3 tests/integration/test-check-plan-routes.py && python3 .claude/skills/harness/bin/check-plan-routes.py --consolidation-audit` — exit 0; the two suites printed `ALL PASS`; audit reported `0 consolidation finding(s) under bin/`.

## C1 fail-first binding recheck

- **SC-01 — supported.** `notes/red-first-receipts.md` §2 retains T-01/T-02/T-03 REDs. Current `notes/build-divergences.md` §A4 records `101/.harness=97` to clean `220feabb` `104/.harness=100` and names exactly three added YAML files; current `notes/byte-evidence.md:340-350` records the same `104/.harness=100`. The c1 `103/.harness=99` statement records the prior inconsistency that this correction closed.
- **SC-02 — supported.** Red-first receipt §2 T-03 records ceiling and four mutant REDs (`:117-132`); changed byte evidence records the census FEAT-64 ceiling rows at `byte-evidence.md:213-239`.
- **SC-03 — supported.** Red-first receipt §2 T-01 records library and hook REDs (`:57-91`); changed byte evidence lists new boundary cases at `byte-evidence.md:317-338` and handoff cases at `:290-302`.
- **SC-06 — supported.** Red-first receipt §2 T-03 records the live and shipped double-route-load REDs (`:117-120`); changed byte evidence lists route-load cases at `byte-evidence.md:42-70`.
- **SC-07 — supported.** Red-first receipt §2 T-02 records tool-family REDs (`:93-112`); changed byte evidence exists for board-station, check-omp-port, and other tool suites (`byte-evidence.md:10-34`, `99-192`). The byte-identical suites in `byte-evidence.md:99-115` and `128-132` are retained unchanged evidence, not missing proof, because their red-first bindings remain recorded.
- **SC-08 — supported.** Red-first receipt §2 T-01 records the handoff single-parse RED (`:70-73`); changed byte evidence lists the single-parse case at `byte-evidence.md:290-302`.

No must-fix remains: GC-64-04 is closed by the current consistent A4 and byte-evidence records. No command failed.
