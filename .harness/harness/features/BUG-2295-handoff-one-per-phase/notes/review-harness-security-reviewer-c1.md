# Security review — BUG-2295 — c1

PASS with one low advisory; no blocking security defect identified in T-01.

Reviewed dd04e52a898109fdbe09cf5fa14e1148161734d0..253cdf2aedf8f1b40fe712aa4e9301cdb764bf34 through pinned git objects. Task binding: T-01, owner main-session-direct (DEC-174).

## Scope and evidence

- In scope: check-domain.py accepts agent-controlled Write/Edit paths and content, then decides whether a handoff mutation is permitted. STRIDE: Tampering at the hook-payload → handoff-policy boundary.
- Lowercase cycle names remain routed by RE_HANDOFF (:1486), including Edit reconstruction (:2631–2659), and the added rule (:2296–2318) returns a filename problem independent of valid content. Aggregate problems produce exit 2 (:2867–2873). Unreconstructable Edit candidates also explicitly refuse. Existing content checks remain additive.
- SC-03/SC-04 inspection: gh-sync.py :2586–2593 changes comments only; the pinned diff preserves the executable ship predicate and exemption. No historical shipped handoff paths change.
- Tests (:909–939) add Write/Edit refusal and canonical acceptance cases; no new dependency, subprocess input interpolation, credential handling or external request surface. Feature records and notes are governance prose/metadata; the full diff contains no apparent credential additions.
- Existing bootstrap exception fail-open behavior and alias-resolution limitations are not introduced or widened by this patch. This review does not certify the entire existing hook.

## Finding

SEC-01 — kind: substance; scope: none; severity: low; task: T-01; owner: main-session-direct.

`check-domain.py:2296` adds a case-sensitive `_RE_HANDOFF_CYCLE`, while the routing `RE_HANDOFF` at :1486–1487 is case-insensitive. An agent already permitted to write handoff notes can submit valid content to `notes/handoff-BUILD-c1.md`: routing and Edit reconstruction recognize the file, but the new `[a-z0-9-]+?` phase match does not, so no cycle-name problem is emitted. This defeats naming hygiene, not authorization or the ship prerequisite; the actor gains no underlying write privilege. Align the new detector's case handling with its existing routing predicate. Static source evidence only; no runtime exploit claimed.

## Verification and questions

No source changes, suite runs, code-grade runs, or pin operations. QA/main owns the assigned integration gate: `set -eu; python3 tests/integration/test-check-domain-post.py` (dispatch requires `env -u HARNESS_AGENT_TYPE`). Open questions: none. Missing product docs are explicitly recorded by the approved BRIEF; no substitute authority was invented.
