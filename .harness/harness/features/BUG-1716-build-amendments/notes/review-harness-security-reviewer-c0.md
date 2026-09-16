# Security review — BUG-1716-build-amendments — c0

## BLUF

PASS with two medium-severity tamper-detection gaps. The changed surface is security-relevant: it accepts an engineering-lead YAML digest, mutates signed plan text and a JSON audit ledger under separate locks, and changes when approval survives. No command interpolation, path traversal, secret, authorization, or data-exposure defect was found in the pinned delta.

## Findings

1. **med · substance · task T-05 — one amendment permanently exempts every signed field on that task from INV-40.** `check-state.py:2912-2918` reduces each `T-NN.field` amendment identity to `T-NN`, then skips hash comparison for that task forever. A repository writer who can make or exploit one legitimate amendment to `T-01.intent` can later alter `T-01.files` or `T-01.verify` through another plan-writing route without adding an amendment; approval remains signed and INV-40 is silent. The actor needs plan-write capability, so this is audit-evasion/tampering rather than privilege escalation. The focused tests prove another-task separation but do not exercise another field or a later edit on the same task (`tests/integration/test-check-state-feat59.py:430-453`). Owner: T-05. Bind coverage to the complete recorded departure chain (field and resulting value/hash), not task presence.

2. **med · substance · task T-04 — legacy signed plans lose their former approval-reset protection while having no replacement hash check.** The delta stops treating replacement of an existing task field as a signature-resetting change (`plan-merge.py:1024-1027`), but INV-40 explicitly returns without checking any approved record lacking `signed_task_hashes` (`check-state.py:2907-2911`). Therefore an approved plan signed before BUG-1716 can have `intent`, `files`, or `verify` replaced by generic `apply`/`amend`; approval remains approved and no ledger violation is emitted. The actor needs access to a governed plan writer, so impact is undetected signed-plan tampering under unusual access, not elevation. Owner: T-04. Preserve reset semantics for hashless approved records, or backfill hashes before permitting replacement.

## Threat model

- **Tampering — lead digest → plan.yaml / feature.json:** partially mitigated. Closed keys/types, anchored file entries, stale-`was` comparison under the plan lock, destination resolution, schema reload, and ledger-before-plan ordering reject common malformed/stale input; findings 1–2 leave detection gaps after mutation.
- **Information disclosure — digest/reason → ledger/briefing:** mitigated. The delta records supplied task text/reasons only in feature-local artifacts and adds no credential/log/network surface.
- **Elevation / spoofing — CLI caller → approval and ledger:** mitigated by existing governed write routes and the main-session signing boundary; this delta grants no new OS/network authority. `record-amendments` attributes entries to the orchestrator, so its safety still depends on the existing command/write guard rather than digest authorship.
- **Denial of service / race — two-file mutation:** mitigated for concurrent plan changes by compare-under-plan-lock and locked feature writes. A feature-ledger write can precede a later plan replace failure, but that produces a harmless extra audit entry rather than unauthorized plan text.
- **Injection / traversal / secrets:** mitigated or absent. YAML is loaded through the strict existing loader; no shell/SQL/template execution or user-controlled path join was introduced; the full pinned diff contains no credential material.

## Inspected surface census

- **Executable input/mutation surface:** `.claude/skills/harness/bin/{check-state.py,feature-record.py,feature-schema.json,plan-merge.py,validate-digest.py}` — reviewed digest/YAML/JSON shape, destination selection, hashes, approval semantics, locks, compare-and-splice, ledger selection, and failure behavior.
- **Tests:** `tests/integration/{test-check-state-feat59.py,test-plan-merge.py,test-validate-digest.py,test-validate-feature-json.py}` and `tests/unit/test-feature-record.py` — reviewed security-relevant assertions and the same-task/different-field gap.
- **Authority and operating prose:** `.claude/agents/harness-eng-lead.md`, `.omp/agents/harness-eng-lead.md`, `.claude/skills/harness-code-review/SKILL.md`, `.claude/skills/harness/SKILL.md`, `.claude/skills/harness/references/{briefing.md,ledger.md}`, `.harness/harness/docs/{DECISIONS.md,DECISIONS-INDEX.md}` — reviewed authorization boundaries, attribution, overrule, and disclosure claims.
- **Feature records:** `BRIEF.md`, `STATE.md`, `feature.json`, `plan.yaml`, the two answers notes, four T-02..T-05 fail-first receipts, plan research/review notes, orchestrator observation — reviewed for signed decisions D-01..D-08, ownership, stated safety case, secrets, and evidence. No additional security finding.

## Open questions

None.
