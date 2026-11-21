# F2 boundary amendment — pm

Completed only the operator-authorized SC-03 sentence and T-04 intent sentence amendment. No implementation or goalcheck performed. Authority: notes/answers-2026-11-21-f2-ruling.md; supporting history: notes/handoff-validate-c3.md and notes/review-harness-security-reviewer-c3.md §F2. Existing failures remain historical failures, not retroactive passes.

## Exact changes

BRIEF.md line 21 replaces only: “Unreceipted or file-inconsistent changes cannot pass close-run or replay/merge integrity checks.”

Replacement: “Unreceipted or file-inconsistent changes cannot pass close-run verification against the default branch as the local repository records it; content hidden by deliberately moving default-branch refs (`git update-ref`, `git branch -f`, `git symbolic-ref`) is a stated close-time boundary refused at replay/merge integrity (`merge-gate.py merge-distill` against the live remote); hardening is tracked in #2251.”

plan.yaml T-04.intent, source line 256, replaces only: “unreceipted/file-inconsistent changes instead fail existing close verification and replay/merge integrity gates.”

Replacement: “unreceipted/file-inconsistent changes cannot pass close-run verification against the default branch as the local repository records it; content hidden by deliberately moving default-branch refs (git update-ref, git branch -f, git symbolic-ref) is a stated close-time boundary refused at replay/merge integrity (merge-gate.py merge-distill against the live remote); hardening is tracked in #2251.”

Full raw intent proposal: notes/research-FEAT-2225-member-expertise-writes-t04-intent-amend.md (plain text, no heading). Captured current block sha256 from amend --show: e6714dd6e231b4905829768d8cee2e9096bb0a46bf4a2967cd5e1722417d71f7. Used amend --expect-sha256 with that hash, --value-file pointing at the proposal and exact reason: operator ruling 2026-11-21 (answers-2026-11-21-f2-ruling.md): F2 accepted as a documented boundary; close verification relative to local default branch; hardening #2251.

## Preservation evidence

Requested before/after measurements, no git: each following SHA256 is identical before and after.

- BRIEF bytes with only the target sentence removed: 42b5964355473f2fdf37ed214c62d3219f77a6ed7846c9b50bdb083362597789. This preserves all other SC-03 clauses, all other SCs and all non-target text byte-for-byte.
- BRIEF bytes from ## Approval through EOF: 80ac38068682967247e4f00f3afb9ce25b45bfd0ade2c3d3a7bc6237565c2332.
- Entire parsed plan with only T-04.intent replaced by the same sentinel, serialized as sorted JSON: 784a28789379759a490fb16d5271f28e1ccb48cc70141fd478f8785d2e0d2eb9. Every non-target field, task, decision and approval value preserved.
- Plan approval sorted JSON: 72dab7350ba5f2210521c5999c590c189440c0650b923779eb00f082dd442d46; remains approved, Mike Ruangutai, 2026-11-21. No approval was authored or re-signed by pm.
- Loaded amended intent equals the full proposal file: True. Proposal generation asserted exactly one old-sentence occurrence and replaced only it.

## Amendment stdout (verbatim)

```text
AMENDED tasks:T-04.intent judgement=amendment
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/plan.yaml
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2225-member-expertise-writes/.harness/harness/features/FEAT-2225-member-expertise-writes/feature.json
```

The tool also automatically emitted check-state --changed diagnostics (not separately invoked by pm): INV-33 reports review_sha 6d9e6053a6367c78f1e5848a6801e7ca09d82dd1 stale after this amendment; existing panel resolved/skipped notes, unknown historical cycle attribution for r-20261121-9-amend-f2-product, and LAYOUT dirty (8), three paths not to repair. No APPROVAL-RESET receipt. No remote sync, tests, builds, lint, formatters, separate check-state, verify commands, goalcheck, git, commit, push or gh commands executed.

## Touched files and next authority

All paths below are relative to this feature directory:
- BRIEF.md
- plan.yaml
- feature.json (automatic amendment ledger)
- notes/research-FEAT-2225-member-expertise-writes-t04-intent-amend.md
- notes/research-FEAT-2225-member-expertise-writes-amend-f2-pm.md (this receipt)

Open questions: none. Main owns re-signature and fresh review pin handling; no new SC verdicts claimed.
