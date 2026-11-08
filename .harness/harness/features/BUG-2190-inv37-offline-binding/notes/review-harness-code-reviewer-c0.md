# BUG-2190 · code review · c0

FAIL — T-01 leaves two explicit acceptance assertions unimplemented. The inspected production selection matches the authorized offline exception; the omissions are in regression coverage, not an observed runtime failure.

## Stage 1 — spec compliance

Reviewed c6bd42d20fa9bf58e4c1dd3ede417caefc23a853..33c0c181e62c5e75692c8320fc01aaaaf06fa40b, excluding unrelated changes merged at 907225c1. Repository-derived grading base: 924c548690a8a7c0e51baf5ad2485a97d7219b98. No in-scope human commits or tracked dirty source files. The excluded FEAT-71 range contains human commit d8942104.

- **med · substance · T-01 · SC-03 omission:** `tests/integration/test-check-state-inv37-offline.py:157` and `tests/unit/test-check-state-inv37-local-binding.py:123` vary only `factory.repo`; their builders always create a factory mapping. Neither supplies malformed factory shapes. Concrete missing scenario: offline `factory: []` must produce invalid-authoritative-binding without remote reads or owner fallback. [INFERENCE] Replacing the new mapping guard with an unchecked `.get` would crash on that input while these new cases would not exercise it. Add a real malformed-factory case through INV-37 and its integration entrypoint, asserting the binding finding, no traceback and zero remote reads.
- **med · substance · T-01 · SC-02 omission:** integration `:126-154` and unit `:110-120` assert receipt/provenance classification but never assert the recovery instruction. Concrete scenario: bound `org/prod`, recorded `org/repo`, opened receipt requires `recover-mirror`, not compatible `open`/`recover-terminal`. [INFERENCE] Passing owner repo only to `recovery_command_line` at `board.py:330` would preserve the asserted conflict detail yet select the wrong command; current assertions would not notice. Assert recovery-command selection for the missing/mismatched/unproven cases against the selected factory repository.

Inspected SC-01/03/04/06 selection: `board.py:306-323` checks mapping, raw `_REPOSITORY.fullmatch`, canonical fleet load and exact membership; authenticated and unbound cases delegate without remote-error fallback. SC-02 downstream receipt/provenance/recovery calls preserve the selected repo (`board.py:350-357`). SC-05 eligibility and owner/sync-off flow remain unchanged (`board.py:332-352`). Table declares `gh:auth` (`table.py:184`); the canonical-reader row and operator-approved DEC-221 exception are present. All four amendment notes were compared against BRIEF criteria and operator signature; no feature scope expansion found. No SC uses `verify: inspection`.

## Stage 2 — code quality

Deferred because Stage 1 fails. Mandatory mechanical grading only: pinned `code-grade.py` completed successfully, 36 passing records, grades 4–5, no grade-2 reasons or high records. No tests, builds, linters, formatters or mutants executed by this reviewer. Build evidence is author-reported; QA owns behavioral verification.

## Principles applied

- Model the Domain — inspected the existing binding predicate and local fleet membership as the authoritative selection model; no additional state model is requested.

## Open questions

None. Fix both coverage omissions within existing T-01/SC scope, then re-review and let QA execute its assigned checks.
