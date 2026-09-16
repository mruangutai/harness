# Handoff — BUG-1756-qa-reverify-bash, build → validate — written at d267bf559e917bbe358cefac395e5a85ef8b24bf, seq-1

## Next

Validate over review_sha (pinned after this commit): one validate dispatch to harness-validator-lead (qa, code, security, ui, goalcheck); any fix is main-session-direct (DEC-174). This validate is the first run through the REPAIRED #919 hook — a qa PASS with a green matrix should now clear it.

## Trust

- T-01 built direct by Main: `_reverify_suite` spawns `[sys.executable, run_bin, --kind k]` per claimed kind, first failure stops, bare when none named; fail-open posture unchanged — .claude/skills/harness/bin/validate-digest.py — VERIFIED
- Fail-first: the Python stub is refused with exit 2 on the parent commit — notes/receipt-main-session-T-01-fail-first.md — VERIFIED
- 10/10 bug919 cases incl. SC-01..SC-04; both matrices green; code-grade 0 FAIL — tests/integration/test-validate-digest.py — VERIFIED

## Dead ends

- none

## Working set

- .harness/harness/features/BUG-1756-qa-reverify-bash/plan.yaml
- .harness/harness/features/BUG-1756-qa-reverify-bash/feature.json
- .harness/harness/features/BUG-1756-qa-reverify-bash/notes/receipt-main-session-T-01-fail-first.md

## Done when

Scope: validate segment
Authority: brief-perspective:.harness/harness/features/BUG-1756-qa-reverify-bash/BRIEF.md#operator
Authority: brief-sc:SC-01
Authority: brief-sc:SC-04
