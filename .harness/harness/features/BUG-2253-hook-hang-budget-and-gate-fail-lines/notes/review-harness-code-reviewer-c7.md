# BUG-2253 cycle 4 code review — PASS

**T-01's seven behavioral unit tests close the unit-coverage omission without production changes. Both SCs remain satisfied; no new findings or must-fix.** Reviewed exactly `3dd8bb677bb2936361e3952030fc24f15bf9afc6..3ba8dd4bf65392a1dd4fe99dddfebb14fe68d01d`, not later HEAD.

## Stage 1 — specification compliance

- Read BRIEF, signed plan (no decisions), feature pin and previous validation digest before judging changes. T-01 explicitly includes the unit file and literal verify: `python3 tests/integration/test-validate-digest.py --only run_bug2253_cases && python3 tests/unit/test-validate-digest-run-pool-lines.py`. The files/verify amendment supports SC-01 and the matrix floor; it does not weaken either SC. The original intake digest has no implementation amendments to reconcile.
- SC-01: `validate-digest.py:2489-2549` prints ordered, duplicate-preserving file diagnoses before the unchanged 20-line tail only after a nonzero independent execution; refusal remains 2. Unit tests `tests/unit/test-validate-digest-run-pool-lines.py:30-71` execute loaded production parsing and printing, not source-string checks. They bind literal outputs for duplicate failures, passing-file exclusion, spaced names, case echoes, same-name PASS/header echoes, mutation adjacency, exact buried-tail rendering and tail-only fallback.
- SC-02: integration test `:1025-1031`, `:3033`, `:3066`, `:3286-3288`, `:3316-3318` replaces exactly six budgets; `:6505-6676` executes all six enclosing-function call sites with default/rebound budgets, real blocking subprocess calls and readiness-independent watchdog controls. No other timeout changes appear in the pinned diff. Neither SC is marked inspection-only.
- Walked the full commit list and diff: all 92 changed paths are the three Python paths or feature records; no foreign feature work, human-tagged commits, dirty tracked files or canonical-reader inventory change. PRODUCT `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` remain absent in the pinned tree; no invented guidance or documentation expansion.

## Stage 2 — quality and evidence

- The unit tests use `harness_boundary.load_repo_module` and exact output equality. Returning None/empty output cannot satisfy them. Concrete discriminators include dropping a duplicate, retaining a passing/case line, splitting spaced names, popping a header on PASS, accepting a nonadjacent mutation, omitting the heading, or altering one tail line. These are inspected failure implications, not executed mutants.
- Supplied `receipts/unit-red.txt` honestly reports exact-base **7 errors because helpers are absent**, not seven behavioral defect failures. `unit-red-b228c3a2.stderr` independently shows the echo test producing `[]` instead of both real FAIL lines on the older parser. `green-c5-unit.stderr` reports seven passing tests. Existing `red-c4.*` supplies genuine base diagnostic loss and six observed `[3,3,3]` budget failures; later fixture exceptions after watchdog kills are not extra independent defect evidence.
- Derived equivalence with git diff: production gate is unchanged from `3c6fb908` to pin; all Python files are unchanged from executed fix `d9026b74` to pin. Supplied `green-c5.txt` and streams record the literal chained verify passing (17 integration cases, seven unit tests). These are supplied receipts, not reviewer execution. QA owns final exact-pin execution.
- Python risk grading: Main supplied base `3dd8bb67` / head `d9026b74`, exit 0, **38 PASSING, no FAIL**. Python equivalence to the pin supports `code_grade: pass`; no reviewer grader/tests/build/lint/formatter ran. Independent inspection finds no newly broken error path or unjustified module layer.
- Settled rulings are not reopened: monotone header membership deliberately accepts occasional over-listing; unchanged runner-launch/timeout fail-open is outside this patch. No new silent-loss/refusal defect identified within SC scope.

## Principles applied

- **Model the Domain**: the monotone set of headed filenames expresses the accepted never-un-name invariant without synchronized block-close state (`validate-digest.py:2500-2523`).
- **harness-code-review**: checked literal subjects and concrete reddening changes; kept missing-helper errors distinct from behavioral red evidence.

Open questions: none. Source edits: none. Required final check is QA's one exact-pin execution of the literal T-01 verify above.
