# Security review — BUG-2190 — c0

**PASS: no actionable security issue in T-01.** In scope: the change relaxes a repository-binding verification boundary and consumes feature records, fleet declarations and an operator-selected executable.

Reviewed `c6bd42d20fa9bf58e4c1dd3ede417caefc23a853..33c0c181e62c5e75692c8320fc01aaaaf06fa40b`; excluded the unrelated FEAT-71 merge contribution at `907225c1` by comparing its first-parent contribution separately. Feature census: board/table runtime changes, focused unit/integration tests, canonical-reader row, DEC-221/index, feature receipt/plan/amendment/build records. Documentation and fixtures add no credential-bearing surface; full feature-delta secret-pattern sweep found only explanatory token/auth references.

## Boundary assessment

- **T-01 / SC-01, SC-03:** `board.py:306-323` rejects non-mapping factory values, validates the raw repository with the existing fullmatch predicate, validates fleet data through the canonical loader and requires exact `repo_entry` membership. `feature_schema.py:494-508` classifies malformed non-null factory shapes as bound, preventing owner fallback. Null/absent bindings retain existing owner semantics.
- **T-01 / SC-02, SC-05, SC-06:** `board.py:330-353` carries the selected exact factory repository into the unchanged evidence, provenance, receipt and recovery-command logic. `feature_schema.py:549-590` denies bound legacy owner inference, absent active provenance, explicit repository mismatch and incomplete replacement recovery. Offline selection is not early success.
- **T-01 / SC-04:** Only a false cached auth probe selects local validation. Authenticated selection delegates directly to the full resolver; its FleetError becomes an invalid-binding finding, not an offline retry (`board.py:320-343`). The narrowed remote verification is explicitly authorized by DEC-221 and `notes/operator-signature-2026-11-08.md`, not a finding.
- **Command/environment boundary:** `ctx.py:248-263` executes `[gh_bin, "auth", "status"]` without shell interpolation, caches per executable, and maps probe failures to the approved offline mode. FACTORY_GH control already grants executable selection; this diff adds no shell evaluation or new privilege. Repository names never become executable paths.
- **Scheduling/output:** `table.py:181-185` declares auth as a read; `runner.py:112-126` treats non-path reads as selecting all features, not skipping checks offline. Findings retain existing output/recovery formatting. Inventory and decision changes do not add executable policy or dependencies.

Read BRIEF SC-01..SC-06, plan, research/build evidence, operator signature, product AGENTS/SPEC §13, DEC-220/221 and decision index. Test assertions inspected, including distinct owner/product identities and online-read failure controls; builder-reported red/green evidence was not independently executed. No tests, builds, linters, formatters or grading commands run; execution belongs to QA.

**Findings:** none. **Must-fix:** none. **Open questions:** none. Source/tests/fixtures unchanged.
