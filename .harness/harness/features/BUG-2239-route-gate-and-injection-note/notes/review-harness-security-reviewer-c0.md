# Security review — cycle 0

PASS — no exploitable security issue identified in T-01.

Reviewed exactly `926383aef86ee505d2909c291ef4ab672b8ea09b..0646be2354b49c46e7a7b0acc5f15eff84cf5d19`; no tests, builds, linters, formatters or grading commands executed. QA owns execution.

## Scope and trust boundaries

- **In scope:** agent-authored plan content crossing the intake gate, manifest authority, schema-injection provenance and human/interpreter-facing diagnostics. The existing route processor is unchanged; this delta invokes it rather than weakening it.
- **Tampering / failure semantics:** `plan_merge/check.py:195-231` passes the resolved target plan, planning root and already-resolved manifest root to the shared processor before `_check_all`. Each VIOLATION becomes a counted failure without deduplication; `None` exits 5. Propagated processor exceptions cannot reach the exit-0 success path. Unlike hook exit semantics, this is a CLI gate.
- **Paths / input:** the new call does not interpolate plan paths into shell commands or load executable YAML. Existing processor `check-plan-routes.py:381-418` uses validated loading and explicit fleet resolution; resolver invocation at `:93-107` uses argv without a shell. Existing anchor/agent checks remain additive. No new write capability or attacker-controlled executable location is introduced.
- **Spoofing / provenance:** `.omp/extensions/harness-hooks.ts:1221-1233,1329-1335` derives the disclosure flag from `withDigestSchemas` returning a revision, not from caller fields. The note is a fixed literal (`:373-374`), emitted only with an accepted schema revision; refusals still return first. Bash revisions cannot set this flag. Existing schema-control refusals and strict bundle loading (`:377-409`) remain intact.
- **Information disclosure:** full pinned diff credential-pattern sweep found no credential material. New diagnostics expose local plan paths and rule findings to the existing CLI operator, not a new audience. JSON import restores an existing report mode without broadening collected data. No dependency, network, tenant, spreadsheet-export or authentication surface was added.
- **Remaining changed-surface census:** three regression files are test-only. Feature BRIEF/plan/state, research, receipts, run identities and digests are local governance/evidence records; BUG-2171 metadata removals/status rollback do not change executable authorization or grant a lower-trust actor new capability. No concrete security exploit identified in those changes.

## Acceptance traceability (static assessment)

- SC-01 / SC-03: shared delegation and failure counting inspected at `plan_merge/check.py:195-231`; no budget/status/routing predicates copied.
- SC-04: `tests/integration/test-plan-merge.py:3110-3234` covers budget, both statuses, valid acceptance, target isolation, cannot-load refusal and sentinel/root delegation; `:3043-3048` retains the distinct NOBODY finding. Red receipt `notes/receipts/red-plan-merge.txt:374-423` shows missing rule failures with successful baseline checks, not merely fixture-loading crashes.
- SC-02 / SC-05: exact conditional note and preserved refusal path inspected above; flat/batch/no-injection assertions at `tests/unit/omp-hooks.test.ts:1647-1682` bind returned input and context.
- SC-06: `check-skill-weight.py:21` restores json import; real JSON/plain subprocess assertions at `tests/integration/test-check-skill-weight.py:127-149`. Runtime evidence validation belongs to QA.

Product `docs/spec.md`, `docs/decisions.md` and `docs/architecture.md` are absent (docs listing contains only PRINCIPLES.md and invalid-states-audit.html); no control-plane product guidance substituted.

Findings: none. Must fix: none. Open questions: none.
