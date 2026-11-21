# QA c5: LABEL authoritative binding at 91f1d0c64fc4ce94d3fcb8110933c2171a0424d6

**PASS.** The high T-01/SC-01 LABEL finding is **CLOSED** (no longer open, no regression). Every command below was executed by this reader in a managed pinned checkout (`pinned-checkout.py`, HEAD == `91f1d0c6…`, `git status --porcelain` empty before and after, `HARNESS_AGENT_TYPE` and `HARNESS_PROJECT_DIR` unset). Prior receipts were not reused as execution. Only my own evidence has examined the c2 fix besides the author's (O-07).

Phase 1 (source-blind, BRIEF/plan only) expected: SC-01 bound commands, board reconciliation and every refused or unproven binding with no Harness fallback, plus a valid-binding control; SC-02 replacement/refusal; SC-03 attribution; SC-04 INV-7 no-floor; SC-05 refusal provenance; SC-06 live validation negatives. All have named tests. No gap.

## Executed (serial, pin tree)
|Command|Exit|Result|
|---|---|---|
|T-01 verify, 5 scripts verbatim|all 0|feature-record `OK`; digest-record `OK`; gh-sync-build-entry PASS lines; gh-sync-open `ALL PASSED`; check-state-records ok lines|
|`tests/integration/test-board-lifecycle.py`|0|192 PASS lines, `all checks passed.`; six `LABEL ownership` cases PASS|
|`run-unit-tests.py --kind unit`|0|61 files, 8 workers, 74.5 s|
|`run-unit-tests.py --kind integration`|0|87 files, 8 workers, 254.4 s|
|T-02 `check-decision-anchors.py --file …DECISIONS.md`|0|28 anchors, 0 failed|
|T-02 `gen-decisions-index.py --stdout \| diff - DECISIONS-INDEX.md`|0|empty diff (0 lines)|

Counts are files, not cases. T-01 is `cross_module` (unit + integration floor); both kinds ran non-empty and are satisfied. Whole-feature diff includes runtime code. Logs: `/tmp/qa-c5-*.log`.

## Red-first, natural (SC-01)
Managed pin at `9d4f1cb9` (the red-first commit: new tests over pre-fix `board_lifecycle.py`), `test-board-lifecycle.py` rc **1**:
- PASS: bound to acme/other (foreign collision, no finding, no write).
- FAIL: acme/widget undeclared in the fleet (A).
- FAIL: served config sync off (C).
- FAIL: served config unavailable (D).
- FAIL: served config naming acme/other (E).
- PASS: declared and validly configured (B control).

This is semantic red, not signature-absent: the valid control and foreign case pass on the same base, so the red is exactly the refused-binding write. It matches the QA c4 table row for row. The regression commit precedes the fix `587e591b` (test-first ordering confirmed by log).

## M-STRING (independent, temporary `git archive` copy of the pin; script `/tmp/qa_c5_mstring.py`; pin and assigned tree untouched)
Mutation: `board_lifecycle.py` `_label_record_owner` line `bound_repo = feature_schema.resolve_binding(doc, root)[0]` replaced by `bound_repo = repo_name` (trust the `factory.repo` string). Asserted byte-changed (`count == 1`).
- Clean copy: rc 0, six LABEL cases PASS.
- Mutant copy: rc **1**. A, C, D, E FAIL. Foreign collision and valid B stay PASS. KILLED, and the surviving controls keep meaning: foreign shows ownership filtering still holds, B shows the valid binding still writes once.

## fail_first audit
- SC-01: current natural red above (`9d4f1cb9`), plus M-STRING mutation tier.
- SC-02, SC-03, SC-05: **inherited** natural-red receipts, `notes/review-harness-qa-c1.md`. Not re-reproduced; the only source change in `a80b9ef3..91f1d0c6` is `board_lifecycle.py` (plus its test and feature records, per `git diff --stat`). Suites above re-ran green.
- SC-04, SC-06: **inherited** mutation-tier evidence M-INV7 and M-LIVE, `notes/review-harness-qa-c3.md`. Not re-run; unchanged code, suites green here.

## Prior must_fix disposition
- High LABEL (code-reviewer, T-01/SC-01, kind substance): **closed**, independently re-measured natural red and mutant kill above.
- QA return contract (form, low): this return is the schema-conformant object. Whether the validator accepts it is the orchestrator's check.
- Foreign collision, SC-04 no-floor, SC-06 live provenance closures: retained, suites green, no regression.

## Not done
No live or remote Kaya recovery. SC-08 UAT stays an operator action. Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent; BRIEF, plan and Harness DECISIONS were the authority.

## Principles applied
- Build the Lever: one `/tmp` script runs the clean and mutant copies from the same pin.
- Attack the Premise: I ran base and mutant to check the positive control is a real declared binding, not undeclared variant A.

Scratch removed on return: three managed pins (`harness-qa`, `-base`, `-mstr`) and the `/tmp` mutant copies.
