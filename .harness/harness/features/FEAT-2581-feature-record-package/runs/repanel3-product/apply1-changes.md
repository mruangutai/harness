# repanel3-product — apply1 (pm, one pass): changed fields

Transcribed by the lead from pm's return (agent Feat2581Resume.AlliedChameleon.IcyLynx); pm's goal-check addendum is notes/research-FEAT-2581-feature-record-package-goalcheck-plan.md:315-348. approval.status pending; panel: unchanged; record-panel/set-panel/check NOT run yet.

## plan.yaml
- **T-03.verify (:396+)** rewritten on four invariants:
  1. Strict decode (`cz`): canonical RFC 4648 base64, b64decode(validate=True), re-encode equality → PF-96cdf9f1.
  2. Derived fields: every non-verdict receipt line (baseline_failing, case_set, d02_item, d02_item_record, gate_captures, audit_scanned_files, divergence) recomputed; every build-divergences.md body recomputed, incl. d02# file/symbol/old+new source from fixed table TB via `git show` at base and pin (`sg`, `SO`, `bd==BODY`); pin audit's zero unresolved sites → PF-3882d444.
  3. SC-08 records: exactly one `divergence: <id>` … `end_divergence` record per divergence of every kind (measured, baseline#, cases#, d02#) plus `test_change:` records equal to base..pin git diff of each changed tests/ path → PF-cf9cf710.
  4. Readable account: each record ends `account:` + injective decoded line rendering (`vl`/`ac`/`U`), ≥1 `| ` line required → PF-a37e5b40.
  NEW: record kind `suite` (one per test file per side), used to derive case_set/baseline_failing/FAIL lines; not compared whole (timings).
- **T-03.intent (:428+)**: PL-10 acceptance in opener; four-guarantee paragraph; Measurement files (suite kind, strict decode); Suites/Case identity derived from suite records, PL-04 keep stated; Gate capture (item table, test_change); Audit M=0 from record; Compare (single `divergence:` format, account rendering, PL-05 personal ruling at ship review, widened normative clause); Receipt (every non-verdict line recomputed).
- **D-01.because (:220)**: 24 rows = 23 caller rows + moved loader's own row; Settled "rows change only file and id" does not hold for them; PL-03 accepted 2026-11-27, canonical_reader_audit keys and two test expectations change with them.
- Unchanged: T-01, T-02, D-02, D-03, execution modes/agents, approval:, panel:.

## BRIEF.md
- SC-08 (:47): `divergence:` record with exact old/new bytes + readable rendering, recomputed from committed records; unreached item carries file/symbol/old+new source read from both refs; operator's own ruling; test expectations as base→pin diff.
- Verification gaps bullet 3 (:68-71): symbol source at baseline and pin via `git show`.
- Constraints disclosure (:99-122): PL-01, PL-05, PL-03; PL-10 and PL-09 accepted ("Q3 (a) is not amended"); discloses cycle-4 suite-record growth beyond PL-09.

## Notes
- research-feature-record-package.md §2 item 3 (:36-47): count corrected, PL-03 recorded.

## pm open questions (non-blocking)
- OQ-C4-1: T-01.intent (:333+) still says the nine moved rows change "only file and id", contradicting its next clause for the loader row; T-01 was a non-goal.
- OQ-C4-2: new `suite` kind grows notes/measurements/*.jsonl.gz beyond what PL-09 accepted; size unmeasured; re-confirm PL-09 or set a ceiling (BRIEF.md:119-122).
- OQ-C4-3: TB pins 11 (file, symbol) pairs; a T-01 rename fails T-03 closed; should T-01 say symbols stay put?
