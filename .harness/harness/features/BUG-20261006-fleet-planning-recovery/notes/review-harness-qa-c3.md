# QA c3 — fix c1 revalidation at a80b9ef3b2a30b1fa73101385a15b71b873cf09b

**PASS.** Every suite and every mutant below was executed by this reader in a clean pinned checkout (`pinned-checkout.py`, HEAD verified == `a80b9ef3…`, clean status, `HARNESS_AGENT_TYPE` unset, no project-root env inherited). The high LABEL defect is closed and SC-01/04/06 each now have discriminating integration evidence. Only my own evidence has examined the fix. The prior reviewers' independence did not cover it (O-07).

Phase 1 (source-blind, BRIEF/plan only) expected: LABEL foreign-number collision plus same-repo control; every bound command and config-refusal outcome (SC-01); real-reader no-floor/unknown-legacy notes (SC-04); refusal provenance rejected live and missing complete digest still a violation (SC-06); unchanged SC-02/03/05 coverage. All have a test (no gaps).

## Executed here (serial, pin tree)
|Command|Exit|Result|
|---|---|---|
|T-01 verify, 5 scripts verbatim (feature-record, digest-record, gh-sync-build-entry, gh-sync-open, check-state-records)|all 0|`OK`, `OK`, PASS lines, `ALL PASSED`, 41-line ok report|
|`test-board-lifecycle.py` (added regression)|0|`all checks passed.`|
|`run-unit-tests.py --kind unit`|0|61 files, 8 workers, 71 s|
|`run-unit-tests.py --kind integration`|0|87 files, 8 workers, 254 s|
|T-02: `check-decision-anchors.py`|0|28 anchors, 0 failed|
|T-02: `gen-decisions-index.py --stdout \| diff`|0|empty diff|

Counts are files, not cases. Both kinds ran non-empty. T-01 = cross_module, so unit and integration are the floor. Both are satisfied by named tests exercising this change. Logs: `/tmp/qa-c3-*.log`.

## Independent mutation / pre-fix proofs (temporary `git archive` copies under `$TMPDIR/qa-c3-*`; assigned tree untouched; each copy asserted byte-changed; clean pin copy = green baseline above). Harness `/tmp/qa_c3_mutants.py` was rewritten by me; the lead's `/tmp/b06_mutants.py` was inspected, not used.
|Mutant|Live in fixture?|Result (mutated copy, real test file)|
|---|---|---|
|M-OWNER: `feature_schema.py` drops the `bound is not None` branch (owner fallback), 2 lines|yes|`test-gh-sync-open.py` exit 1. All 8 `fleet_bound_command_cases` FAIL, all 4 `fleet_config_failure_cases` FAIL (12 new). 15 other tests, incl. replacement cases, FAIL too|
|M-INV7: pre-fix `inv_7` (FAIL-count floor) from `4a05030d^`, 42 lines|yes|`test-check-state-records.py` exit 1: 3 INV-7 (SC-04) assertions FAIL (no-floor, evidenced-L note, unknown-U note)|
|M-LIVE: `validate-digest.py` accepts a hash recorded as refusal, 7 lines|yes|exit 1: "live validator still rejects R's refused prose" FAILS|
|Extra X-LABEL-OWNER: `_label_record_owner` returns owned for any record|yes|`test-board-lifecycle.py` exit 1: collision case FAILS|
|Pre-fix `board_lifecycle.py` @6451153 (reproduces high)|yes|exit 1, 7 FAIL: collision (`acme/other` #17 yields finding/write) plus all 6 malformed-record cases. The same-repo `acme/widget` control passes pre-fix, so the red is semantic, not signature-absent|

Test-first order confirmed from history: `8d5fbaf2` (tests only, red) precedes `843a16dc` (source fix); `35d46417` adds the SC-01/04/06 cases after the fix existed, so their fail-first tier is **mutation**, not natural red.

## Findings (advisory only)
- low / coverage: M-LIVE reddens only the standalone live-validator assertion (1 FAIL). The `close-run` assertion in the same case is not discriminated by a validate-digest acceptance mutant. I also mutated validate-digest to accept the hash for any argv shape (extra probe). `close-run` still refused at stage run-end ("no fenced YAML block"), a separate gate, and feature.json stayed unchanged. So fail-closed holds via independent layers; the assertion is a retained control, not provenance-specific.
- `check-state` records the stale "note" lines for R/Q/S as designed. No violation line for FAILs.

## Retained SC-02/03/05 coverage
Executed green here: `test-gh-sync-open.py` (replacement/refusal cases, `:315-599` range of prior notes), `test-feature-record.py` (SC-03/05 unit cases). I did not recreate their natural fail-first reds. Cite `notes/review-harness-qa-c1.md` (c4e8bbc8 pre-fix reds) as receipt evidence.

## Missing guidance
Product `docs/spec.md`, `docs/decisions.md`, `docs/architecture.md` are absent in the checkout. I used BRIEF, plan and `.harness/harness/docs/DECISIONS.md` (T-02 anchors/index verified) as authority and did not invent contents.

## Principles applied
- Build the Lever: one script (`/tmp/qa_c3_mutants.py`) runs all mutants on fresh copies, so the proofs were repeatable and never touched source.
- Attack the Premise (not applied as a formal rule): I probed the second close-run call site of the live-validation path instead of trusting a single combined PASS (P-06/O-06).

Pin removed on return.
