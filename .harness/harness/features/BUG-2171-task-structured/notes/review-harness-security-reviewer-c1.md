# Security review — BUG-2171 — c1

PASS. Scope IN: agent-authored yield data crosses a structured-input boundary and can trigger a privileged append to a lead run record. Independent review of immutable range `b7af829c0207522b43f978b5275a2ebdc96b3210..d3792019e74ff266c2414708124512544d1fc9f6` found no exploitable security regression and no must-fix.

## Boundary assessment

- **Structured input / injection:** the hook performs one `JSON.parse` only when yield `data` is a string, then accepts only a non-null, non-array object (`.omp/extensions/harness-hooks.ts:1298-1308`). It does not evaluate input or interpolate it into shell, SQL, templates, paths or URLs. Malformed JSON and JSON null, arrays and primitives retain the refusal path. Parsed and native objects converge on the same fixed-script policy call and `digest_object` payload (`:1309-1323`).
- **Held-run integrity:** the held-run decision reads `VERDICT` from the parsed object before validation; string PASS is refused and string BLOCKED alone reaches the unchanged validator path (`harness-hooks.ts:1309-1315`; `tests/unit/omp-hooks.test.ts:2827-2845`). There is no representation mismatch for duplicate JSON keys because both checks consume the same parsed object.
- **Schema and authorization:** dispatcher schema controls remain refused before hook-owned strict injection (`harness-hooks.ts:375-405,1216-1228`). Canonical schema and semantic validation remain downstream; accepting an equivalent serialized object grants no capability unavailable to the same agent through native object data.
- **Append integrity:** `validate-digest.py`, `digest_destination.py`, `digest_record.py` and the persona schemas are byte-identical at base and pin. The unchanged writer binds hook-owned child, parent, feature, checkout and run identity to exactly one open registered lead run and exact granted artifact (`digest_destination.py:99-150`). Descriptor-relative traversal uses `O_NOFOLLOW`; the leaf is regular and writable and opened with `O_APPEND` (`:153-194`). The validator reads and appends through that descriptor and proves the exact safe-dumped object is selectable before writing (`validate-digest.py:1917-1965`).
- **Secrets, disclosure and dependencies:** the complete 22-path pinned delta adds no dependency, request target, credential handling or export. An added-line credential-pattern sweep found no credential-shaped material. Existing debug rendering is bounded and the new representation does not expose data to a new actor or sink.
- **Configuration gate:** `task.structured` is enabled, and the port gate uses boolean identity (`is not True`), so false, strings and integer `1` cannot enable the contract (`.omp/config.yml:12-18`; `check-omp-port.py:83-102`).

## Threat model

- Agent/model → YieldTool hook: Tampering / information disclosure / denial of service; mitigated by single parse, object narrowing, closed schema and semantic validator.
- Dispatcher → child schema contract: Tampering / elevation of privilege; mitigated by refusal of caller schema controls and hook-owned strict injection.
- Validator → durable run digest: Tampering / repudiation / elevation of privilege; mitigated by runtime/run binding, exact destination authorization, no-follow descriptor traversal, append-only write and canonical post-append selection.

Findings: none. Open questions: none. No tests, builds, linters, formatters or smoke runs were executed; QA owns the required gates. No source or run-state files were edited.
