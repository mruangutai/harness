# PASS — LABEL foreign-number ownership bypass is closed

Exact fix delta: `6451153169f469f5bd9d5f3f01bf89b82787b720..a80b9ef3b2a30b1fa73101385a15b71b873cf09b`. T-01, main-session-direct. No actionable security findings or must-fix items. This explicitly supersedes c1's incomplete LABEL assessment; c1's STATUS reasoning alone did not close the prior high.

## Ownership traced to writes

- **Foreign mirror collision:** `board_lifecycle.py:961–989` loads each record and excludes a nonmatching `factory.repo` before contributing any numbers. A valid Kaya task #17 therefore contributes nothing to Harness's recorded-number set. A matching repository must additionally pass immutable mirror-evidence and active-provenance checks. Conflicting/missing bound provenance and incomplete recovery cannot authorize LABEL.
- **Malformed/unreadable inputs:** `:929–948,961–972,992–1008` returns no owned numbers for an unreadable corpus/record or malformed mapping. Residual findings contain no `issue_number`; `_fixable` at `:1130–1135` excludes them. `_apply_reconcile_findings` at `:1199–1211` cannot dispatch their label writes. Valid independent records may still authorize their own issues; an invalid record does not broaden scope.
- **Actual effect:** `_label_findings` at `:1019–1036` requires membership in the proven set for the owner repository. Only actionable LABEL findings reach `_apply_fix` at `:1171–1176`, which passes the audited repository explicitly to `gh issue edit`. The deliberately broad non-owner-repository policy remains unchanged; foreign records no longer authorize writes in the owner repository.
- **Identity-level controls inspected, not executed:** `tests/integration/test-board-lifecycle.py:1017–1077` asserts malformed-record residuals with no `issue edit`, and pairs identical #17 fixtures differing only in repository: foreign means no finding/no label write; same-repository means a finding/exactly one label write. Author-reported pre-fix red/fixed green receipts are in `notes/fix-evidence-c1-2026-11-21.md`; independent execution belongs to QA.

## Additional trust boundaries and scope

`feature_schema.py:369–408,545–577,604–650` confines evidence to regular feature-local resolved paths, rejects traversal/escaping symlinks and changed hashes, checks exact feature/effect identity, and binds recovery generations and adopted receipts. LABEL now consumes these checks rather than trusting replacement provenance alone. Hash-bound local notes are not authentication against an actor already authorized to rewrite both the governed record and its evidence. No newly introduced privilege was identified for that actor.

All 16 delta paths were scoped: one production ownership consumer and three integration fixtures are in scope; the remaining 12 feature/run/review records are audit/provenance material, not new executable endpoints. Full raw-delta credential-pattern search found no matches. No new dependencies, shell execution, export interpretation or credential stores were introduced. SC-06's new integration assertions separately bind historical refusal, live rejection and unchanged state (`test-check-state-records.py:1121–1164`); they do not change live acceptance code.

SC-07 security-relevant inspection: adopted `DECISIONS.md:2993–2999,7231–7274,7928–7942`, its index, BRIEF SC-01/04/06 and plan D-01/D-04 remain consistent with fail-closed routing and historical-versus-live evidence. Product `docs/spec.md`, `docs/decisions.md`, and `docs/architecture.md` are absent (docs census contains only `PRINCIPLES.md` and `invalid-states-audit.html`); the dispatch-designated adopted decisions and feature authorities supply the applicable guidance. No unresolved guidance question.

Reasoned source assurance only: no tests, builds, linters, formatters, mutation probes, live network calls or operational recovery ran. Inspected source/tests/decision files have no working-tree delta from the exact pin. Open questions: none.
