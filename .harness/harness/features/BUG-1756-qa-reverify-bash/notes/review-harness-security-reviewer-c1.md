# Security review — BUG-1756-qa-reverify-bash — c1

## Verdict

PASS. I reviewed the immutable pin `c1f9601fe87660b732aac0bf5e5f72dd17fac0d7` against signed base `af1c1d88a7e81010fd4902b2144b5cd5eb67f9ef`. The delta is security-relevant because agent-authored digest data selects subprocess arguments and test output is relayed to stderr, but it creates no exploitable OWASP/STRIDE regression. The c0 security conclusion remains valid, and c0 Q1/Q2/Q3 introduce no new security concern at c1.

## Measured audit

- `.claude/skills/harness/bin/validate-digest.py` — `_claimed_kinds` reads agent-authored evidence kinds. `_reverify_suite` passes each kind through list-form argv `[sys.executable, run_bin, "--kind", kind]`, never through a shell. The executable and runner path are not derived from the digest. The runner accepts only `unit`, `integration`, or `all`; an unsupported value exits non-zero and the gate refuses the claimed PASS. Metacharacters and leading dashes remain a single value after `--kind`, so they cannot become commands or flags. Duplicate values are deduplicated, and the accepted vocabulary bounds successful repetitions to three. No command-injection, flag-confusion, elevation, or unbounded successful fan-out finding.
- `.claude/skills/harness/bin/validate-digest.py` — the first failing rerun still exposes only the final 20 lines of its captured stdout/stderr. The pre-change check already emitted that same tail from the default run. Selecting a subset of the same fixed runner's kinds does not widen the source, amount, audience, or privilege needed to produce that output. No credential, digest body, environment dump, cross-user record, or export was added.
- `tests/integration/test-validate-digest.py` — the Python stub records test-controlled argv in a temporary fixture. The c1 in-process OSError and `TimeoutExpired` arms monkeypatch only the locally loaded validator module and add no production input or secret-bearing sink. They close c0 Q1 by reaching the exception seam and do not change production reachability.
- `notes/receipt-main-session-T-01-fail-first.md` records the final SC-01/02/03 cases against the pre-fix validator, closing c0 Q2 without adding executable input. `notes/receipt-main-session-fix-c1.md` explains that rebasing removed the unrelated failing local commit, closing c0 Q3 without a security posture change.
- Agent/doctrine marker edits replace a regex-matching concrete feature example with non-matching placeholders, and `.claude/commands/harness.md` / `.omp/commands/harness.md` require the actual marker on dispatch. This prevents accidental feature identity confusion by documentation examples; it does not grant a caller a new identity or authorization capability.
- Full 37-path census: the remaining changes are mirrored agent/doctrine text, feature planning/review records, cycle-accounting code/schema/tests inherited in the signed range, decision indexes, and one Vitest result cache containing only a test path/failure boolean. They add no auth route, credential material, network/SSRF request, database/template/export sink, dependency, deserialization boundary, cross-tenant access, or sensitive log payload.

## Threat model

- **Tampering / elevation:** a QA agent can choose evidence `kind` values, but cannot choose the interpreter or production runner through the digest; invalid kinds fail closed. Mitigated.
- **Information disclosure:** a failing fixed runner can emit its normal 20-line output tail to the same hook stderr audience as before; no new source or volume is exposed. Mitigated/no delta.
- **Denial of service:** each invocation retains the 1800-second timeout; deduplication plus the runner's closed vocabulary bounds successful kind reruns, while the first invalid kind stops immediately. An agent able to submit the QA return gains no new compute capability beyond its existing test-running role. Mitigated.
- **Spoofing:** concrete marker examples no longer satisfy the feature-marker regex, while actual dispatches must carry the real feature id. Mitigated.

No findings and no open questions.

```yaml
VERDICT: PASS
DIGEST:
  headline: "PASS at review_sha c1f9601fe87660b732aac0bf5e5f72dd17fac0d7: the security-relevant argv, output-tail, exception-test, and marker deltas add no exploitable security regression."
  in_scope: true
  scope_reason: "Agent-authored evidence kinds cross into Python subprocess argv, runner output crosses into hook stderr, and feature markers affect identity resolution; the full pinned diff was therefore audited for OWASP and STRIDE rather than scoped out."
  severity_max: none
  findings: []
  must_fix: []
  threat_model:
    - { boundary: "QA digest kinds -> fixed Python runner argv", stride: "T|E|D", mitigated: true }
    - { boundary: "runner stdout/stderr -> hook stderr tail", stride: "I", mitigated: true }
    - { boundary: "spawn exception/timeout -> fail-open diagnostic", stride: "D", mitigated: true }
    - { boundary: "dispatch marker -> feature identity resolution", stride: "S|T", mitigated: true }
  open_questions: []
  files_touched:
    - /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-security-reviewer-c1.md
  expertise_update: []
artifact: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1756-qa-reverify-bash/.harness/harness/features/BUG-1756-qa-reverify-bash/notes/review-harness-security-reviewer-c1.md
```
