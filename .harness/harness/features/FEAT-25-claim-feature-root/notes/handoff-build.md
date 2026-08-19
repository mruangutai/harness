# Handoff — FEAT-25-claim-feature-root, build → validate — written at 8d7b273, seq-2

## Next

Dispatch the four-angle simplify pass to harness-eng-lead as its own squad segment over the six
files in `git diff --name-only d1ffd7f...HEAD` — the LAST build step, before `review_sha` is
pinned. Then re-run both gate kinds at the new tip, re-pin `review_sha` there, and only then
dispatch the `review` team to harness-validator-lead. All three PLAN tasks are `status: done`.

## Trust

- The qa gate is GREEN at the graded commit: `run-unit-tests.sh --kind unit` exit 0 and
  `--kind integration` exit 0, all 12 scripts PASS, measured by me in a throwaway worktree checked
  out at 8d7b273 with no working-tree drift — notes/gate-measurement-2026-08-19.md — verified-at 8d7b273
- The exit 1 seen in the working tree is entirely held dirt: uncommitted `.harness/harness/docs/DECISIONS.md`
  disagrees with a fresh decisions-index regeneration. Absent from the graded diff; no FEAT-25 file
  participates — same note — verified-at 8d7b273
- The graded diff is exactly the six declared files, and SC-08 clause (b) is clean on six separate
  verdicts (five forbidden files individually absent, `load_board` absent from every added line) —
  my own run of both checks — verified-at 8d7b273
- Counts at the tip are 120 / 106 / 41 against the d1ffd7f baselines 114 / 106 / 40, re-derived by
  qa independently rather than quoted — notes/qa-c1.md §2 — verified-at 8d7b273
- F-1 is PRE-EXISTING, measured not inferred: `git diff d1ffd7f...HEAD -- test-layout-migration.py`
  is one hunk `@@ -399,6 +399,16 @@` adding case 22; the fail-open report block at :412-419 appears
  only as unchanged context — verified-at 8d7b273
- `bash-write-guard.sh` does refuse worktrees outside `.claude/worktrees/`; it blocked two of my
  attempts, including one through a shell variable it cannot resolve. No carve-out defect there —
  runs/2026-08-19-2-qa-validator/digest.md Q1 answered — verified-at 8d7b273
- cycles_used stays 2: both leads reported ZERO send-backs and I dispatched no rework. The
  validator run is recorded FAIL because that is what it returned — my measurement is the
  resolution, not a rewrite of its verdict — feature.json — verified-at 8d7b273

## Dead ends

- Do NOT fix F-1 or F-2 in this feature. No SC is unmet and no gate is red, so there is no rework to
  do; T-03's intent says "Add nothing else", making a case-22 assertion a plan change that is pm's
  under the operator's approval. Both go to the panel named, and only a `high` ruling reopens them —
  runs/2026-08-19-2-qa-validator/digest.md F-1/F-2 — verified-at 8d7b273
- Do NOT rename `test-factory-claim.py:997` or `:1003`. SC-07 authorises exactly one rename and it
  is spent; both assertions carry full power at eight (derived inputs, `range(901, 909)`) — the
  labels alone are stale — notes/qa-c1.md F-3 — verified-at 8d7b273
- Do NOT re-adjudicate the integration gate from a working-tree run. Any agent that runs it in this
  checkout gets exit 1 for a reason that has nothing to do with this feature — same gate note —
  verified-at 8d7b273
- Never stage the held dirt: `.claude/agents/harness-{eng,product,validator}-lead.md`,
  `.harness/harness/docs/DECISIONS.md`, `.harness/harness/docs/SPEC.md`, and the untracked FEAT-26
  and FEAT-27 directories — `git status --porcelain` — verified-at 8d7b273

## Working set

- .harness/harness/features/FEAT-25-claim-feature-root/notes/gate-measurement-2026-08-19.md
- .harness/harness/features/FEAT-25-claim-feature-root/notes/qa-c1.md
- .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-19-2-qa-validator/digest.md
- .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-19-1-eng/digest.md
- .harness/harness/features/FEAT-25-claim-feature-root/plan.yaml
