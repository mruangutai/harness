# Security review — BUG-1724-run-end-tokens — c1

BLUF: PASS. The pinned T-01 delta has a real security surface—host-supplied result data crosses into subprocess argv and mutates the feature ledger—but no exploitable security defect was found.

## Pin and surface

Reviewed exactly `1a1c1925..3eb4c27525a17640c4b60a9b735d02eb911dc074`, not the worktree HEAD. The approved six-file census is:

- `.omp/extensions/harness-hooks.ts` — changed; security-relevant executable boundary.
- `.claude/skills/harness/bin/feature-record.py` — changed; security-relevant parser and ledger writer.
- `.claude/skills/harness/SKILL.md` — changed; operator command contract, no new executable interpolation.
- `tests/unit/omp-hooks.test.ts` — changed; security evidence only, no credentials in added fixtures.
- `tests/unit/test-omp-hooks.py` — unchanged in the pinned range; no delta to audit.
- `tests/unit/test-feature-record.py` — changed; security evidence only, no credentials in added fixtures.

The broader clean range contains feature bookkeeping and review records as well, but no additional executable surface. The prior `_quoted_scalar_closed` high finding is absent: `check-state.py` is not changed by this clean range and is not carried forward.

## Threat review

- **Tampering / input validation (T-01):** `event.details.results[*].tokens` is host-reported input. The hook accepts only JavaScript numbers that are integers and non-negative, ignores malformed rows and values, aggregates once per task call, and passes only the derived number. The CLI independently requires an integer at least zero. Zero remains measured; absence remains unstamped/null.
- **Injection / subprocess boundary (T-01):** the hook supplies fixed list-form argv to `policyRunner`; there is no shell interpolation. `--file` and `--tokens` each have a fixed following value, and the token string is derived only after numeric validation, preventing option re-parsing and command injection.
- **Path traversal / authorization (T-01):** the delta does not derive a path from the event. It reuses the existing registry-backed feature-root resolution and `featureJsonPath` result. The new CLI verb has no new privilege boundary: a caller able to execute it with an arbitrary file already has equivalent ledger mutation capability through existing feature-record verbs.
- **Ledger integrity / repudiation (T-01):** mutation occurs only when exactly one entry is started and unended. No-open and multiple-open states refuse before mutation; conflicting run ids are named. Writes continue through the existing locked, schema-checked feature writer. Bare `run-end` preserves a stamped value, while an explicit non-negative override remains deliberate behavior.
- **Information disclosure / secrets (T-01):** raw task results are neither persisted nor printed. Output is limited to aggregate token counts, the target path already supplied to the CLI, and conflicting run ids. The added diff contains no credential material, dependency, network request, SSRF surface, authentication decision, or unsafe deserialization.
- **Availability / advisory behavior (T-01):** stamp refusal or execution failure stays inside the existing non-blocking advisory `try` path, so it cannot block the hook gate. That fail-open choice affects accounting/advisory freshness only; an actor controlling the host result already controls whether a measured token value is present and gains no additional system privilege.

No finding is bindable to T-01, and no unbindable-class finding is present. In particular, large but valid host numbers can at worst cause an accounting stamp refusal or host-number precision loss; the actor would already control the measurement source, so this creates no privilege or cross-user capability delta.

```yaml
VERDICT: PASS
DIGEST:
  headline: "The pinned T-01 host-input and ledger-mutation boundary is validated, argv-safe, path-contained by existing resolution, and exposes no exploitable security defect."
  in_scope: true
  scope_reason: "Host-reported token data crosses into subprocess argv and a persistent feature ledger, so Tampering, Injection, Information Disclosure, Repudiation, and availability behavior required review."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "host task-result details -> validated token aggregation", stride: T, mitigated: true }
    - { boundary: "validated aggregate -> fixed list-form feature-record argv", stride: T, mitigated: true }
    - { boundary: "registry-resolved feature path -> locked/schema-checked ledger mutation", stride: "T|R", mitigated: true }
    - { boundary: "ledger diagnostics/advisory -> orchestrator-visible output", stride: I, mitigated: true }
    - { boundary: "stamp failure -> non-blocking advisory continuation", stride: D, mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-security-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1724-run-end-tokens/.harness/harness/features/BUG-1724-run-end-tokens/notes/review-harness-security-reviewer-c1.md
```
