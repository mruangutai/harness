# BUG-2180 goalcheck — validate-c0

Implementation and regression assertions satisfy the bounded goals by inspection at `556a23ffea8dafcf5110e80fe25a42ee2542ff2b`; automated discharge remains partial until independent QA publishes its pinned receipt. No product defect or scope expansion found. This read-only assessment ran no tests.

## Perspectives

- **operator — partial:** SC-01, SC-03, SC-04 trace through T-01 to `board.py#_inv26_binding`, `_inv26_groups`, `_inv26_group`, `_inv26_check`; `test-check-state-inv26.py#case_x` x.1–x.6 discriminate own-repository routing, overlapping issue numbers, owner-sync-off independence, visible original errors, no fallback, and continued healthy-feature comparison. Build evidence reports red then green; independent QA discharge is outstanding.
- **code maintainer — partial:** SC-02 traces through T-01 to retained `case_v`/`case_w` controls and added `case_x` x.4; only the two owned files changed against `4a05030d401593003209f525fd06e00802eccd36`. Existing selection, projection and owner-declaration helpers are retained; independent QA discharge is outstanding.

## Success criteria

All code/test pointers below refer to the review pin; production path is `.claude/skills/harness/bin/check_state/board.py`, test path is `tests/integration/test-check-state-inv26.py`.

| SC | Status | Discriminating evidence |
|---|---|---|
| SC-01 | partial | `case_x` x.1 asserts parent/task/source query numbers [14,16,17] exclusively in org/prod; x.2 is its misplaced-task twin; x.3 checks owner-sync-off; x.4 separates overlapping #41 and unique numbers across repositories and boards. `_inv26_groups` keys by repository, board owner and number; `_inv26_group` passes only that group's map to comparison. |
| SC-02 | partial | Pinned diff preserves existing case_v/case_w assertions; v.1/v.2 and phase twins retain negative/positive controls, v.3/v.4/v.11/v.12 retain exemptions, v.7/v.14 retain absent-gh/null-board controls. `_inv26_declared_board`, `_inv26_feature_numbers` and projection/read helpers remain unchanged; `_inv26_check` retains auth gating. x.4 proves independent owner comparison. |
| SC-03 | partial | `_inv26_group` catches BoardError and actual factory_gh.GhError, emits feature/repository/board/original-error CANNOT VERIFY and returns without inventing an empty map; outer group iteration continues. x.5 asserts unresolved-issue text, no traceback, exit 1 and a healthy owner's misplaced-card finding. |
| SC-04 | partial | `_inv26_binding` catches FleetError without owner fallback; `_inv26_groups` records it and continues. x.6 asserts broken feature/error, a healthy owner's comparison and owner query numbers exactly {40,41}. |

`notes/build-evidence-2026-11-07.md:5–14` reports test-first commit f1032619 against unchanged baseline production: existing 31 assertions pass and x.1–x.6 fail for routing/error behavior. Lines 18–21 report final exit 0, 37 ok, zero FAIL. These are main's build receipts, not independent QA results or evidence that I executed a gate. QA must bind those receipts to this pin and supply its specific per-SC automated evidence; its digest was not yet published when collected.

## Findings and open questions

- No actionable product findings; no substance/form/proportionality defect established for T-01. Outstanding evidence is a validation dependency, not an implementation finding: lead should collect QA's final per-SC fail-first and passing receipts before marking these automated SCs met or shipping.
- Missing product guidance remains the three declared checkout paths `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md`; no specific bounded routing question remains unresolved because approved BRIEF/plan settle it. No substitute guidance was invented.
- Required verify is exactly `python3 tests/integration/test-check-state-inv26.py` followed by a newline. QA alone runs final gates, including the configured unit floor. No live GitHub availability, #2181, INV-30, gh-sync or Kaya-corpus outcome is claimed.
