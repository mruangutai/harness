# Security review — BUG-2171 — c0

PASS. T-01 introduces no identified exploitable security regression. Scope IN: agent-controlled yield data crosses a validation boundary and can cause a privileged durable append.

Reviewed immutable range `b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6`. Product AGENTS.md, mapped SPEC §8.3, DEC-174/237, BRIEF and approved plan govern; the operator-approved JSON-object-string exception is intentional, not a finding against the older object-only wording.

## Boundary assessment

- **SC-01 / T-01:** pinned hook delta is exactly one added refusal-text line plus JSON parsing inside yield; config enables boolean `task.structured: true`. Dispatch, schema projection/injection, lifecycle and append are unchanged (`.omp/extensions/harness-hooks.ts:384,1295`; `.omp/config.yml:18`). Gate uses identity `is not True`, excluding integer 1 (`check-omp-port.py:96`).
- **SC-04 / T-01:** one `JSON.parse`, no evaluation or recursive decoding. Invalid JSON, null, arrays and primitives reach unchanged RETURN_THE_OBJECT refusal. Parsed objects and object inputs converge before held-run BLOCKED-only enforcement and the identical validator call. Digest fields cannot replace hook-owned binding, runtime lineage, feature or review-pin payload fields (`harness-hooks.ts:1295-1323`). Regression source covers malformed values, one parsed-object validator invocation and held string PASS/BLOCKED cases (`tests/unit/omp-hooks.test.ts:1719-1742,2827-2846`).
- **Tampering / elevation:** validator applies schema/semantic checks before append. Destination authorization compares hook-owned child/parent/feature/checkout/run identity, requires the sole open registered lead run and exact manifest-granted artifact, and rejects traversal (`validate-digest.py:2258-2278`; `digest_destination.py:63-155`).
- **Tampering / repudiation:** descriptor-relative directory traversal and leaf opening use O_NOFOLLOW; leaf must be writable and regular, with O_APPEND. Same descriptor reads/appends; safe YAML rendering must remain selectable as the exact object before any write (`digest_destination.py:158-195`; `validate-digest.py:1941-1964`). String input cannot select another append route.
- **Injection / disclosure / denial of service:** input remains JSON stdin to a fixed-script, argv-form subprocess, not shell/template/SQL text. No dependency, network target or credential surface added. Full pinned delta and feature receipts were swept for credential-shaped material; none identified. Parsing accepts another representation of already-authorized input, not a new actor or capability; no new unbounded external ingress identified.

## Live evidence and limits

Independently inspected the actual main, SmokeProductLead and SmokeProductLead.SexualRoundworm JSONL files under session `2026-11-21T15-51-23-264Z_01a1fece-1d80-71ed-bc1b-55ec6796029b`. Both session_init records expose yield and closed persona-shaped output schemas; task results report strict valid returns. Actual PM yield `call_2c282581…` and lead yield `call_8a582d7c…` succeeded. Lead writes contain only the same human prose as before.md; its transcript contains no validator/shell call or authored fence, whereas durable digest.md includes the appended record.

Persisted task arguments contain schema fields: their presence alone cannot establish who supplied them. Hook injection is consistent with successful dispatch through the reviewed refusal/injection handler, not independently proven by schema equality alone; the smoke agent's prose confession is likewise not raw caller-input evidence. This security PASS does not independently certify that host-provenance claim. The exercised `d1e203d4` and pin have identical .omp and validator/gate sources; their sole difference within .omp/bin/tests is the added integer-1 integration row.

No checks executed; saved red/green receipts inspected only. No source edits. Findings/must-fix: none. Open questions: none for this security assessment. QA/validator retains ownership of complete SC-03 acceptance and required gates.
