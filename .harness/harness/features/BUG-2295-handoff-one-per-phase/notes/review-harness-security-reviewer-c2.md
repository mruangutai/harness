# Security review — BUG-2295 — c2

PASS: c1 SEC-01 is closed at 7d76c1cea576822760e8bc42432f8c01fc3c8031. No remaining security findings; T-01 remains main-session-direct.

Reviewed base dd04e52a898109fdbe09cf5fa14e1148161734d0 to the dispatch pin, plus the c1-pin-to-c2-pin source delta. Evidence is static pinned diff and consumer inspection, not runtime verification. Source/test consumer reads match the pin (pin-to-working-tree diff empty).

## Changed-surface census

18 paths; 557 insertions, 4 deletions. Security scope is IN:
- `check-domain.py` (16 additions, 1 deletion): agent-controlled Write/Edit paths cross handoff-policy enforcement; STRIDE Tampering.
- `gh-sync.py` (5 additions, 3 deletions): security-adjacent ship prerequisite, but comments only; no executable policy change.
- `tests/integration/test-check-domain-post.py` (46 additions): regression evidence, not a new production boundary; fixed subprocess argv, no new dependency/request/credential handling.
- Fifteen feature records: `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`; notes `answers-2026-11-22-signoff.md`, `handoff-build.md`, `red-first-T-01.md`, `research-BUG-2295-handoff-one-per-phase-goalcheck-validate-c1.md`, `research-patch-intake.md`, `review-harness-{code,security,ui}-reviewer-c1.md`, `review-harness-qa-c1.md`, `simplify-pass.md`; and `observations/harness-orchestrator.md`. Governance/evidence metadata and prose, no new executable boundary. Full-diff credential-pattern sweep found only token-count metadata and review prose, no apparent secrets.

## Closure and refusal paths

- SEC-01 previously let an already-authorized note writer evade naming hygiene, without gaining write privilege. At `check-domain.py:2296`, `_RE_HANDOFF_CYCLE` now uses the same `_I` as routing `RE_HANDOFF:1486–1487`; phase and suffix case no longer disagree. `:2315` lowercases the canonical diagnostic. The c1-to-c2 diff directly contains both corrections.
- `:2299–2308` accumulates the filename refusal alongside existing cap, section and Done when checks, independent of valid content. `:2407–2426` routes it into shape problems; `:2863–2873` emits stderr and exits 2.
- Edit routing still recognizes suffixed names (`:2631–2635`); malformed, unreadable or unreconstructable candidates explicitly exit 2 (`:2640–2659`), while reconstructed candidates enter the same shape rule. No newly introduced exception/fail-open branch identified.
- Tests `:909–951` bind `Build-c1`, `build-C1`, `VALIDATE-C12` to both Write and existing-target Edit refusals, require exit 2 and supersede guidance, and separately compare the lowercase canonical path case-sensitively. Canonical acceptance and lowercase multi-digit cases remain. Unchanged-file assertions alone are not refusal evidence.
- SC-03/SC-04 inspection: pinned `gh-sync.py:2586–2593` changes only the prerequisite comment; executable predicate/exemption and shipped FEAT-2225/FEAT-2229 history are unchanged in the full diff. Existing DEC-252 commentary discrepancy is explicitly outside T-01, not a finding.

No tests, builds, linters, formatters, probes or code-grade execution. QA owns the assigned existing gate: `set -eu` followed by `python3 tests/integration/test-check-domain-post.py`. Main's red/green claims remain attributed to `notes/red-first-T-01.md`; this report does not independently certify those executions. Missing PRODUCT docs/spec.md, docs/decisions.md and docs/architecture.md are acknowledged by the approved BRIEF; no substitute guidance used. Open questions: none. c1 artifacts preserved.
