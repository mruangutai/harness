# Code review — BUG-1898 — c6

**PASS.** Both stages pass at immutable pin `47b345fe65e992e07386de717f43b9f8dd495dc8`; F-SEC-C5-01 is closed and no singleton/crossed-row fail-open remains.

## Stage 1 — spec compliance

- Reviewed canonical `a4d72e7fc91d0cf7a568d9e2a5225465a422170e..47b345fe65e992e07386de717f43b9f8dd495dc8` against `BRIEF.md` and `plan.yaml`; the focused c6 range `7893fe7a23e493dcd1554e439f28e3c9832b4de4..47b345fe65e992e07386de717f43b9f8dd495dc8` measures **one executable path only**, `tests/manual/probe-inflight-claim-lifecycle.py` (`21` lines changed: `15` additions, `6` deletions). It serves T-04 / SC-07's S3 oracle and introduces no scope change.
- At the pin, `_governing_root` recognizes lineage below a governed orchestrator at any depth; `nested_ids` gathers every such sampled id (`tests/manual/probe-inflight-claim-lifecycle.py:433-441`). `crossed_rows` accepts only a one-segment-deeper `harness-eng-lead` whose `parent_agent_id` exactly equals that root; deeper lineage, wrong persona, and wrong parent are crossed (`:444-458`). S3 separately requires exactly one nested id and its final selector checks `governed + nested` (`:461-475`).
- The final operator-authorized SC-07 entry in `notes/live-omp-probe.md` is PASS `29/29`, registry `before: []` and `after: []`. Its observed `Nest.Probe` row is `harness-eng-lead` parented by `Nest`, matching the pinned oracle.
- No spec violation, omission, mismatch, or scope creep found.

## Stage 2 — code quality and fail-open hunt

- Exact-pin scratch execution bound the search to F-SEC-C5-01 and the named discriminators. `Nest.Probe` and a top-level governed orchestrator produced no crossed row. Each of `Nest.Probe.Deep` with the c5 QA/`Nest.Probe` shape, an otherwise-well-formed deeper lead, wrong persona, wrong parent, and a mixed valid `Nest.Probe` plus invalid deeper row produced a crossed row; the mixed sample also yielded two nested ids, independently failing the singleton check.
- An exhaustive 27-combination probe over depths 1–3 × three personas × three parents had zero mismatches: only direct `Nest.Probe` + `harness-eng-lead` + parent `Nest` was accepted. Thus no remaining lineage shape can enter singleton `nested_ids` while escaping `crossed_rows`.
- Canonical pinned `code-grade.py` reports `PASSING: 130`, with no severity or reason-required record; `code_grade: pass`. No fail-open, silent-failure, relevant regression, or substantive quality finding found.

## Review record

- Exact-pin commit walk completed; no `[harness:human]` commits are in scope. Working-tree dirt is limited to Harness-owned `feature.json`, so pinned source bytes were used.
- Retained named non-blocking residual: `notes/handoff-validate.md` seq-3 remains the historical late succession under INV-43.
- No live mode, formatter, linter, project-wide build, or project-wide suite was run.
- Immutable archive scratch was removed by Main after the reviewer write guard refused `rm`; Main confirmed the path no longer exists. The operator-owned `bug1898-overlay.mIdqOR` was never touched.

## Principles applied

No craft principle citation was needed for this focused oracle correction.
