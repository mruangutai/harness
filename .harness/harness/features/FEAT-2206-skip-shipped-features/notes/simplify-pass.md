# Simplify pass — FEAT-2206 (code surface, before review_sha)

Four read-only readers (scout), one angle each, over `git diff b7af829c 4e8415dc -- .claude tests`
(17 files). Settled decisions (DEC-252: shipped = one plan.yaml status line, filter at feature-list
build, INV-24/29/52 comparison-only, INV-28/30 retired) were declared not flaggable. Main session
applies (DEC-174 main-session-direct; no eng-lead).

| Angle | Finding | Disposition |
|---|---|---|
| REUSE | `test-check-state-shipped.py` duplicated the audit-hook wrapper of `test-check-state-corpus.py` verbatim | **Applied**: one `OPEN_TRACE_WRAPPER` in `tests/integration/f58_sparse_fixture.py`, which both suites already import; both `check()` helpers use it. Assertions unchanged. |
| SIMPLIFICATION | `SEAM_NOTES` comment still called "no handoff" the terminal stations' "whole difference from done", contradicting the emptied `done` row | **Applied**: comparison removed; the no-seam-crossed reason kept. |
| EFFICIENCY | scoped `population()` re-opened and re-decoded every shipped landed `feature.json` the census had already parsed | **Applied**: `_landed_entry` reuses the census document when it is a mapping and re-reads leniently only when the strict parse produced none. |
| ALTITUDE | none — one shipped authority in `ctx.py`, filtered at subject construction, reused by the runner's early exit | — |

Re-run after the apply: test-check-state-shipped (unit + integration), `--real-corpus`,
test-check-state-corpus, test-check-state-handoff, test-feature-corpus-census,
test-checker-structure-locks — all exit 0.
