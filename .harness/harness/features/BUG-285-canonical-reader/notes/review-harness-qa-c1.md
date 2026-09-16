# QA c1 targeted matrix reverify

## BLUF
**PASS.** At `5be21a432b87ed648c0bed50fbf9a2642c84e0a9` (parent implementation `26b1ad93e678de31a508b10069ecc8f8e874c540`), all signed targeted gates pass, every original finding is resolved with genuine fail-first evidence, and the repository-policy matrix is satisfied.

## Pin and matrix
- Reviewed range: `8c3143bd5668ce11186a2a1f8dbe784ff9639d88..5be21a432b87ed648c0bed50fbf9a2642c84e0a9`; `HEAD` exactly equals the required final tip.
- T-02/T-03/T-04 are `cross_module`, requiring unit and integration; T-01/T-05/T-06/T-07 are runtime-touching `bugfix` tasks, requiring unit. The signed T-01, T-02, T-03, T-04, and T-07 commands all exited 0. T-07 reported `0 unresolved reader site(s) across 69 Python file(s)` and confirmed the retired baseline/mode are absent.
- `unit`: satisfied (T-02/T-03/T-04/T-07 named unit scripts green). `integration`: satisfied (T-01/T-02/T-03/T-04/T-07 named integration scripts green). No locally-run kind's detect surface changed. `matrix_ok: true`; coverage gaps: none.

## Finding dispositions
- **F-01 — resolved** (`high`, `substance`, T-01): `case_canonical_reader_unclassified_accessor_module_call` binds a synthetic raw `json.load` under `artifact_accessors.py` and requires a category-specific remedy plus `PLAN AMENDMENT REQUIRED` (`tests/integration/test-check-plan-routes.py:2174-2201`). The receipt records its genuine pre-fix exit 1 and current T-01 self-test is green (`notes/receipt-main-session-fix-c1.md:6-42`).
- **F-02 — resolved** (`high`, `substance`, T-02): the central test asserts the exact comment-bearing issue-285 YAML document parses through the historical permissive route and raises from the public strict accessor (`tests/unit/test-feature-json-reader.py:126-152`). Replayed at historical `97b39c504151f3c7c011d9d479b8d8a53abc6bf0`, the isolated promised inverse exited 1 after returning the complete expected YAML mapping; current T-02 is green (`notes/receipt-harness-backend-dev-fix-c1.md:9-43`).
- **F-03 — resolved** (`high`, `substance`, T-03/T-04): the live baseline binds the checker result's unresolved count and exit code (`tests/integration/test-check-plan-routes.py:2082-2106`). Replayed against compatible historical `5369a9ba8326fb95a74ee32b3468cb1268b960f4`, its audit assertion observed 116 unresolved readers and exited 1; current T-01 self-test is green (`notes/receipt-harness-backend-dev-fix-c1.md:45-78`).
- **F-04 — resolved** (`high`, `substance`, T-05/T-06/T-07): durable comparison evidence is genuine: the historical comparator and 29-case baseline at `0259fce02d6196be92c94edb2cb4ec8c60cd0997` hash to the receipt's `e655…28fd33a5` and `6a48…eebce`; the receipt records exact comparison pass at strict-accounting `0ad0d0b8490bcfa84f5bf3a6c9aec0f213460800` and an isolated one-case stdout divergence that exits 1 (`notes/receipt-main-session-fix-c1.md:44-98`). Current T-07 independently proves retirement absence and terminal canonical state.
- **SEC-01 — assessed and dismissed** (`med`, `substance`, T-02): unchanged. Signed scope requires refusal for wrong-typed nested parent/issues fields, not a new top-level github/factory block-shape contract; T-02 current consumer tests remain green.

## Fail-first and SC evidence
- SC-01: `tests/integration/test-check-plan-routes.py:2174-2201`; red receipt `notes/receipt-main-session-fix-c1.md:15-39`.
- SC-02: `tests/unit/test-artifact-accessors.py`; red receipt `notes/receipt-harness-backend-dev-T-02-c0.md:7-10`.
- SC-03: `tests/unit/test-feature-json-reader.py:98-204`, `tests/integration/test-gh-sync-open.py`, `tests/integration/test-factory-decompose.py`; red receipt `notes/receipt-harness-backend-dev-T-02-c0.md:9-11`.
- SC-04: `tests/integration/test-check-plan-routes.py:2082-2117`; replayed red evidence above and `notes/receipt-harness-backend-dev-fix-c1.md:51-77`.
- SC-05: historical exact comparator receipt `notes/receipt-main-session-fix-c1.md:44-95`; T-07 retirement/current contract gate green.
- SC-07: `tests/unit/test-feature-json-reader.py:126-152`; replayed red evidence above and `notes/receipt-harness-backend-dev-fix-c1.md:16-39`.
