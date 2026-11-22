# Security review — FEAT-2229 — c4

**PASS: SEC-C2-01/F3-I is closed against the operator's four-rule ruling by source reasoning; execution remains QA-owned.** A separate DEC identifier-boundary advisory below is NEW CLASS, not an F3-I residual or an authorization to expand this fix round.

Reviewed reachable pin `46d0c4bce7cec18e0aabec56a490981496970cc0`, range `dfa52536..46d0c4bce7cec18e0aabec56a490981496970cc0`; inspected c3-to-c4 scanner/test delta without executing c3. Read BRIEF, plan, PRODUCT/AGENTS.md, ruling, c3 security evidence and relevant SPEC/DEC-188/254/index changes. Product docs/spec.md, docs/decisions.md and docs/architecture.md are absent as recorded by the brief; none invented.

## Scope

All 50 changed paths assessed: four production Python files and two configurations are in scope for schema/provenance/authority integrity; six instructions/templates/roles for interpreted governance and pinned evidence; three authority documents for enforcement claims; four test/classification files for regression wiring. The remaining 31 feature records/receipts/reviews are in scope for credential and authority-claim inspection, not executable enforcement. Full-diff added-line credential/URL sweep found quoted documentation, not credential-shaped additions. This surface already received c1–c3 review. No new network, shell execution, SQL, spreadsheet export, dependency or cross-user data surface.

## Four-rule closure — T-01 / SC-02

- **Indentation:** `check.py:203-210,277-283` limits both fence and ATX heading starts to 0–3 ASCII spaces. In the exact c3 input (`review-harness-security-reviewer-c3.md`), the four-space closer no longer matches, so the intervening spoof DEC-10 remains fenced; only the genuine DEC-10 is selected. CLI regression `test-plan-decision-dispositions.py:345-373` supplies that input plus genuine-section control, over-indented opener and heading-boundary cases.
- **Backtick opener info:** `_opener` (`check.py:286-288`) refuses an opener whose suffix contains a backtick. CLI spoof/control case `:376-380` discriminates this rule.
- **Closer:** `_fence_after` (`check.py:291-301`) requires the opener's character, at least its run length, and whitespace-only suffix. Info-string fake closers remain content; existing CLI case `:315-322` and nested-run fixture remain connected.
- **Fenced headings:** `_real_headings` (`check.py:304-313`) records headings only while outside a fence. Existing ordinary/nested examples and new unclosed-fence case (`:383-387`) remain CLI inputs, not fixture-only assertions.

**Assurance boundary:** these are static, discriminating input-to-branch arguments, not observed CLI results or proof of arbitrary CommonMark conformance. No builds, tests, grading tools, formatters, mutants or equivalence checks were run. QA must supply c4 execution/test-first evidence and ef269da2/pin equivalence; c3 results were not reused as c4 execution evidence.

## NEW CLASS — SEC-C4-01 / substance / med / scope none / T-01 / SC-02

`check.py:277-283,329-336` rejects only a following digit after the requested DEC id. Concrete document lines `## DEC-10x — not DEC-10`, `Spoof clause.`, then genuine `## DEC-10 — Ten`, `Genuine clause.` cause `section("DEC-10")` to select the first section: `(?!\d)` accepts `x`. With DEC-10 indexed, an eligible row quoting `Spoof clause.` passes this clause check by reasoning. An actor needs decision-document write access plus draft submission; gain is bypassing declared clause integrity, not additional document-write privilege. This identifier-token class is outside the ruling's four fence/heading rules and the predicate already exists at c3. Recommendation: adjudicate independently, then require an exact identifier delimiter and actual-CLI negative/positive controls; do not silently fold it into F3-I. No c4 must-fix requested for this new class.

SC-04/05/06 security inspection: canonical scope challenges omissions (`teams/plan.yaml:103-108`); pm requires per-row pinned landing evidence and failed-landing routing (`harness-pm.md:64-82`, validator `:104-105`); DEC-188/254 and SPEC retain bounded draft checking, not general freshness inference. Writer provenance refusals and segment-specific authority remain structurally intact. No additional T-02/T-03 finding.

Must-fix: none. Open questions: none. Remaining execution: QA's assigned pinned checks; independent identifier-boundary adjudication is recommended, not a continuation of the accepted F3-I ruling.
