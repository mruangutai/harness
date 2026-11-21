# QA c6: form-only correction of the c5 return, pin 91f1d0c64fc4ce94d3fcb8110933c2171a0424d6

**PASS, unchanged from c5.** This note records no new execution. All executed evidence (T-01 verify, board lifecycle, unit 61 files, integration 87 files, T-02, natural red at `9d4f1cb9`, M-STRING A/C/D/E kill, valid B and foreign controls) is c5's: `notes/review-harness-qa-c5.md`. It is preserved and still usable. No tests, builds or linters were rerun.

## What changed
- The prior return began with the prose "Evidence collected; returning." before the JSON object. This return is exactly one JSON object with no prefix, suffix or fence.
- `named_tests` is an integer in every `kinds` entry, never null. The prior values (unit 3, integration 4) were not reconciled with the 61/87 discovery counts. I could not re-derive them, so I replaced them with a count I can show: **distinct test files cited in `sc_evidence`** for that kind. Unit = 1 (`tests/unit/test-feature-record.py`). Integration = 3 (`test-board-lifecycle.py`, `test-gh-sync-open.py`, `test-check-state-records.py`). These are file counts, not test-case counts. They are not the discovery totals: the runner executed 61 unit files and 87 integration files in c5, and those are also file counts.
- The unit and integration commands each run the whole kind bucket. `named_tests` only says how many of the bucket's files carry SC evidence.

## fail_first, current versus inherited
- SC-01: **current**, executed in c5. Natural red at `9d4f1cb9`: `test-board-lifecycle.py` rc 1, A/C/D/E FAIL, foreign and valid B PASS. Mutation tier on top: M-STRING on a temp pin copy, rc 1, same four FAIL.
- SC-02, SC-03, SC-05: **inherited**, not re-run. Natural-red receipts in `notes/review-harness-qa-c1.md`.
- SC-04, SC-06: **inherited**, not re-run. Mutation-tier M-INV7 and M-LIVE in `notes/review-harness-qa-c3.md`.
- The c5 reasoning stands: the only source change in `a80b9ef3..91f1d0c6` is `board_lifecycle.py` (plus its test and feature records), and the suites ran green at the pin.

## Independence qualification (replaces c5's exclusive claim)
c5 said only QA's evidence had examined the c2 fix besides the author's. That was unsupported and is dropped. The code and security reviewers independently inspected the c2 fix. Only QA ran the behavioral proofs (natural red, M-STRING) on the LABEL binding at this pin.

## Schema validation
Return object validated against `.agents/skills/harness/bin/digest-schemas/harness-qa.json` with `common.json` references, using python `jsonschema` Draft 2020-12 with a referencing registry. The candidate was `/tmp/qa-c6-return.json`. Result: **0 errors**. Required DIGEST fields present and no extras: headline, open_questions, files_touched, expertise_update, suite, failures, coverage_gaps, matrix_ok, fail_first, kinds, sc_evidence. This checks the schema only. `validate-digest.py` acceptance is the orchestrator's check.

## Not done
Same as c5: no live or remote Kaya recovery; SC-08 UAT stays an operator action; product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent.
