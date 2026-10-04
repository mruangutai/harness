# QA c5 pinned gate — BUG-1898

**BLUF: PASS.** The sole c5 probe delta at `7893fe7a23e493dcd1554e439f28e3c9832b4de4` correctly distinguishes the S3 nested lead row from top-level/dotless ids; retained c4 product proof remains sufficient, including SC-02 wake reclaim (99/99), and the authorized operator receipt ends PASS 29/29.

## Scope, Phase 1, and matrix

- Reviewed immutable pin `7893fe7a23e493dcd1554e439f28e3c9832b4de4`, full range `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..7893fe7a23e493dcd1554e439f28e3c9832b4de4`, focused range `f73c999482fd931021a3eb50d30aa8ab2a885283..7893fe7a23e493dcd1554e439f28e3c9832b4de4`. The focused range changes only `tests/manual/probe-inflight-claim-lifecycle.py` (+22/-6).
- Phase 1, before source: T-01/T-02 require unit+integration; T-03 adds unit; T-04's config-shape declaration requires integration. c5 itself changes the locally-run SC-07 probe oracle, so the warranted new evidence is an offline oracle plus the retained live receipt.
- Required kinds were rerun in a fresh immutable archive: `bun test tests/unit/omp-hooks.test.ts` exited 0, 99 pass/0 fail (273 assertions), including wake reclaim at `tests/unit/omp-hooks.test.ts:1875-2002`; `python3 tests/integration/test-run-unit-tests-kinds.py` exited 0, 8/8 PASS. The recorded c4 dry-run exited 0 and started no OMP session.
- `inflight_claim_lifecycle_live` is `locally_run`, not an automated matrix kind; its required recorded run is the final receipt below. Component/UI do not match the lifecycle surface. The BRIEF's unresolved typecheck runner remains a declared non-gating coverage gap.

## c5 offline oracle

- In an archive created exactly with `git archive 7893fe7a23e493dcd1554e439f28e3c9832b4de4 | tar -x -C /tmp/BUG-1898-qa-c5.W4OOSk`, `python3 -m py_compile tests/manual/probe-inflight-claim-lifecycle.py` exited 0.
- A temporary import-and-call oracle invoked `nested_ids` and `crossed_rows` from that pinned file, then `python3 oracle.py` exited 0: `PASS nested-only=Nest.Probe dotless-excluded top-level-green wrong-persona-red wrong-parent-red`.
- This proves: sampled lineage selection accepts only ids beneath a governed orchestrator; dotless ids do not enter the nested set; exactly one nested id (`Nest.Probe`) is required; a real `harness-eng-lead` child with `parent_agent_id=Nest` is green; top-level orchestrator rows are green; wrong persona and wrong parent each produce a crossed row. The no-row check passes `governed + nested` to `governed_rows` (`tests/manual/probe-inflight-claim-lifecycle.py:465-466`), so its selector includes the nested id.

## SC evidence and fail-first

- SC-01 — `tests/integration/test-suite-claim-preservation.py:107-121`; red-first: `notes/review-harness-qa-c0.md:23`.
- SC-02 — `tests/unit/omp-hooks.test.ts:1875-2002`; red-first baseline 85 pass/13 fail, including wake reclaim: `notes/review-harness-qa-c0.md:24`.
- SC-03 — `tests/integration/test-inflight-registry.py:1238-1410`; red-first: `notes/review-harness-qa-c0.md:25`.
- SC-04 — `tests/unit/omp-hooks.test.ts:2020-2130`; red-first: `notes/review-harness-qa-c0.md:26`.
- SC-05 — `tests/integration/test-check-omp-port.py:194-214`; wrong-bus red-first: `notes/review-harness-qa-c0.md:27`.
- SC-06 — `tests/integration/test-validate-digest.py:5815-5844`; red-first: `notes/review-harness-qa-c0.md:28`.
- SC-07 is UAT and stated only from the retained operator receipt. Its immediately prior entry is FAIL 28/29 because dotless `Plain` was misclassified as nested (`notes/live-omp-probe.md:717-751`). The last entry is the authorized PASS 29/29 (`:911-950`): S3 reports the nested `Nest.Probe` lead row cleanly, and the snapshots show empty registry `before` and `after` (`:1055-1102`). No live mode was run here.

## Findings, cleanup, and residuals

No finding. `handoff-validate.md` sequence-3 late succession (INV-43) and the operator-owned dirty overlay remain residuals, not c5 failures. The first archive scratch, temporary oracle, and generated cache were removed; the rerun archive is removed before return. No source/tests were modified and no formatter, linter, project-wide suite, or credentialled probe was run.
