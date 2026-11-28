# Send-back criteria — FEAT-2622 plan run 2026-11-28-01 (written before any member return, P-05)

## draft (pm) is sent back if any of:
- `plan-merge.py check` not reported exit 0.
- Any task not `execution_mode: main-session-direct`.
- No SC covering each operator constraint: (1) structured `exposure` on every reader finding, plan-panel and validate-time; (2) validate-digest.py refusal of contrived+no_worse+non-adversary in must_fix or high+; (3) validator-lead collation triage amending "never revise a reader's severity"; (4) adversarial/malformed tests limited to trust boundaries in harness-tdd-enforcement + QA guidance; (5) forward-only, no re-grade.
- `decisions_affected:` silent on DEC-31/206/228/230 without a stated reason, or no task owns DECISIONS.md.
- The three "Not yet specified" items neither resolved in the BRIEF/plan nor raised as open questions.
- Scope includes re-grading shipped digests, changing DEC-31 gate, or #2627.
- Generated agent frontmatter hand-edited instead of regenerated via gen-agent-output.py.

## readers: a return without a findings list each carrying kind + own severity → re-prompt once, then BLOCKED (contract violation).

## Practicality triage at fan-in: transcribe severity unchanged (shape only); triage is pm's at apply and the operator's at signature. A finding whose own text shows contrived + no_worse + non-adversary is noted as such in the digest assessment, not re-rated.
