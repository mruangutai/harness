# Goalcheck — BUG-2169 — validate c0

FAIL: operator evidence remains incomplete; CI and code-maintainer perspectives pass their SCs. Fresh QA establishes natural pre-fix failures and green signed verify at the review pin. QA separately finds a concrete grant-test regression outside that verify.

Review: c4e8bbc87e858bb2a0320efd766c7036cbcebb8b..6c896d981ed17d2bae528818ecffa56400ae2666; all product-content citations below refer to the latter pin. T-01 traces all five SCs; both added file surfaces are ledgered in feature.json. No tests executed by this reader.

## Perspective outcomes

- **operator — fail (SC-01 partial, SC-02 partial; T-01).** Pinned dispatch-guard.py:77–111 retains trusted yaml as a whole package and normalizes/rejects unsafe origins. tests/unit/test-lead-start-preflight.py:443–530 covers startup, four unsafe-origin plants, and platform advice. Fresh notes/review-harness-qa-c0.md:10–18,33–52 identifies the same image-owned single-install C-loader environment at base and pin, records semantic single-install red -> green, and measures all four plants red under the keep-every-yaml mutant. This discharges the C-loader/isolation clauses, not the required non-C-loader case: no qualifying single-install non-C-loader execution is documented. Advice branches pass at pin, but the base run returns early at missing install_command, so none of the actual advice/warning assertions has semantic fail-first evidence.
- **CI — pass (SC-03; T-01).** Pinned .github/workflows/tests.yml diff removes both --ignore-installed installations and the misleading distro-build comment, reverting both jobs to python3 -m pip install --upgrade pyyaml jsonschema. This satisfies the specified content inspection; it does not claim that a CI run or its mutable image population was measured here.
- **code maintainer — pass (SC-04, SC-05; T-01).** Fresh QA note:33–52 records base dispatch/start-return semantic tag-None failures, fixed-pin exits 0 (135/135 and 57/57), preflight 62/62, zero FAIL lines and 13 seconds together; the named unsafe-origin mutant also discriminates. The note preserves named key failure excerpts and source identities; these external review receipts need not be committed into the reviewed source. SC-05 remains met by pinned worktree_terminal.py::_read_landed_plan_yaml: MissingDependency still calls _scan_top_level_status and the new explanation preserves its purpose. QA's separate D-14a regression remains a validation failure, not a reason to falsify these specific SC outcomes.

## Criterion grading and finding

SC-01 partial (automated); SC-02 partial (automated); SC-03 met (inspection); SC-04 met (automated); SC-05 met (inspection).

**GC-01 — kind: substance; task: T-01; unrated (narrowed, not withdrawn).** Withdraw the earlier assertion that qualifying base/pin C-loader measurements and discriminating integration evidence are unavailable: fresh QA note:10–18,33–52 now supplies them. Remaining remedies are (1) demonstrate a successful single-install non-C-loader start in the signed Ubuntu/CI source, without changing the production loader policy, and (2) capture behavioral pre-fix failures for each advice branch/warning against pinned old advice, rather than merely absence of the new helper. QA owns these evidence gaps. Historical build-note raw stdout/stderr captures remain unlinked; fresh QA logs are explicitly ephemeral /tmp/qa2169/*.log, with key excerpts preserved in its durable note. Do not portray fresh reproduction as proof that pre-edit captures were preserved.

**Separate QA finding F-1 — kind: substance; task: T-01; unrated (QA-owned).** QA note:67–74 measures test-check-domain-grant.py D-14a green at base and red at pin because it still requires pip wording on Debian. This contradicts the historical build summary's identical-before/after claim. Remedy: migrate that assertion to platform-selected advice and have QA verify; no fix performed here.

GC-01's remaining obligations are required by the signed text, not extra coverage preferences: the operator perspective and SC-01 explicitly require C-loader and non-C-loader starts, and SC-02 explicitly requires all advice-branch/warning assertions to fail against pinned pre-fix advice. A missing-function assertion does not measure obsolete advice behavior. Retain those portions regardless of QA's adequacy-only classification; withdraw the superseded general lack-of-base/pin-measurements portion. Fresh QA reproduction supplies present evidence but makes no claim about preserved pre-edit history. No scope change or operator question is needed.

## Open questions

None requiring an operator decision. Evidence completion belongs to QA/main, not UAT. No source, tests, plan, brief, or GitHub changes made.
