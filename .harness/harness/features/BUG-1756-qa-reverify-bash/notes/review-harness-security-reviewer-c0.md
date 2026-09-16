# Security review — BUG-1756-qa-reverify-bash — c0

## Verdict

PASS. Reviewed the pinned change at `01dd2ed8eb6802048cf21ef3508e2e9310096695` against the signed base `af1c1d88a7e81010fd4902b2144b5cd5eb67f9ef`. The delta is security-relevant because an agent-authored digest now selects subprocess arguments and the subprocess output is relayed to stderr, but it introduces no exploitable OWASP/STRIDE regression.

## Security analysis

- `.claude/skills/harness/bin/validate-digest.py:1955-1995` (T-01) — untrusted `kinds:` values cross into subprocess construction. The command uses list-form argv `[sys.executable, run_bin, "--kind", k]` with no shell, so metacharacters cannot become commands. The fixed runner path is resolved independently of the digest. `.claude/skills/harness/bin/run-unit-tests.py:72-91,129-138` accepts only `unit`, `integration`, or `all`; every other value returns non-zero, causing the existing gate to refuse the QA PASS. This mitigates command/flag injection and arbitrary test selection. No finding.
- `.claude/skills/harness/bin/validate-digest.py:2000-2015` (T-01) — the first failing runner's final 20 stdout/stderr lines remain exposed to the agent/operator. This exposure existed before the patch; the delta only selects claimed suite kinds and does not add credentials, environment values, paths, or digest contents to that output. No new information-disclosure finding.
- `tests/integration/test-validate-digest.py:2145-2395` (T-01) — fixture scripts consume only test-controlled argv, use list-form subprocess execution, and write into isolated temporary directories. They contain no production credential or authorization path. No finding.
- `.harness/harness/features/BUG-1756-qa-reverify-bash/{BRIEF.md,STATE.md,feature.json,plan.yaml,notes/answers-2026-09-16-sign.md,notes/handoff-build.md,notes/handoff-plan.md,notes/receipt-main-session-T-01-fail-first.md}` and `.harness/notes/grilling-qa-reverify-bash-2026-09-16.md` — planning/state records only; inspected for credential-shaped content and security claims. They contain no secret, auth change, executable interpolation, export, or cross-user data surface.

No auth/authz route, credential handling, network request/SSRF, database/template/export sink, deserialization boundary, dependency, or cross-tenant data access changed. This assesses this delta only; it is not a claim that the broader validator/hook surface has never needed or received security review.

## Threat model

- **Tampering / elevation:** an agent controlling its QA digest can choose `kinds:` values, but cannot change the executable or create shell syntax; unsupported kinds fail closed as a disagreement. Mitigated.
- **Information disclosure:** a failing selected test can place its normal output tail in hook stderr, but the patch does not widen the output source or amount relative to the pre-change behavior. Mitigated/no delta.
- **Denial of service:** duplicate kinds are deduplicated and the vocabulary is runner-limited; each invocation retains the existing 1800-second timeout. An agent already able to submit the gated QA result gains no new system privilege. Mitigated.

## Findings

None.

## Open questions

None.
