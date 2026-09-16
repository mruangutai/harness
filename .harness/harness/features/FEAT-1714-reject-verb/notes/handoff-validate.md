# Handoff — FEAT-1714-reject-verb, validate → ship — written at 130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57, seq-6

## Next

Ship: PR #1761 squash-merged; records land on the ship branch (station done, pr recorded, milestone #75 closed). Nothing further runs; SC-05 (worktree cleanup classification) is verified by the landed record.

## Trust

- Validate c2 PASS at 130d5b5f1dd60a95d71e3e99bc245c49d3b0cd57: qa matrix (unit, integration) at the exact pin, code/security/ui readers, goal-check SC-01..SC-05 met — .harness/harness/features/FEAT-1714-reject-verb/notes/review-harness-qa-c2.md — VERIFIED
- Two validate FAILs (c0 VAL-01..06, c1 QA-C1-01/02) fixed main-session-direct (DEC-174); each fix has a receipt — .harness/harness/features/FEAT-1714-reject-verb/notes/receipt-main-session-fix-c2.md — VERIFIED
- Rebased onto origin/main after BUG-1716: seven judgement kinds, DEC-230 merged by hand, ledger.md reject row — .harness/harness/docs/DECISIONS.md#DEC-230 — VERIFIED

## Dead ends

- validate-digest.py's #919 re-verification runs the Python runner under bash and refuses every honest qa PASS; out of scope here, filed as #1756 — .claude/skills/harness/bin/validate-digest.py — VERIFIED
- The first-sync record has no parent (open creates it at build entry); the original reject design assumed one and was corrected in fix c1 — .claude/skills/harness/bin/gh-sync.py — VERIFIED

## Working set

- .harness/harness/features/FEAT-1714-reject-verb/feature.json
- .harness/harness/features/FEAT-1714-reject-verb/plan.yaml
- .harness/harness/features/FEAT-1714-reject-verb/STATE.md

## Done when

Scope: ship segment
Authority: brief-perspective:.harness/harness/features/FEAT-1714-reject-verb/BRIEF.md#operator
Authority: brief-sc:SC-02
Authority: brief-sc:SC-03
