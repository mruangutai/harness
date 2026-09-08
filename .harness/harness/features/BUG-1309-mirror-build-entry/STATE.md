# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-c13-product/state.yaml
- squad: product
- station: **building** (unchanged; `plan.yaml:24` reads `status: building`). T-04 and T-05 are at
  `building`, the other eleven tasks stay `done`. `review_sha` reads d8f4dc49 and is STALE by
  construction — re-pin it at the tip of the direct implementation before any validator run (INV-6).
- status: blocked on **main-session-direct implementation** (DEC-174) plus two operator acts, not on
  a decision. Every question this feature raised for the operator is now answered.
- **SC-04 is WIDENED, and the last open decision is closed.** The operator ruled the standing Q1 —
  of widen SC-04 / add an SC / disclose in `## Verification gaps`, the ruling is **widen**, and the
  other two are refused. pm amended `BRIEF.md` SC-04 in place, one hunk, 16 insertions and 7
  deletions confined to that bullet: `BRIEF.md:108-125`, evidence and clause map in
  `notes/research-BUG-1309-sc04-amend-c13.md`. SC-04 now grades three things instead of one —
  (a) everything it graded before, with the reason-shape clause scoped to the single-owner deny;
  (b) the deterministic duplicate-owner DENY, every claiming feature directory id named in stable
  sorted order, no re-run or receipt command offered, decided BEFORE the era gate; (c) the
  attribution bound as a graded REQUIREMENT — one owner plus any amount of noise is not ambiguity,
  and a branch no valid record claims is ALLOWED while an unreadable, malformed, non-object or
  differently-branched record sits elsewhere in the scan. (c) is what makes cycle 11's `473d82cb`
  scan-wide sentinel falsifiable at criterion level: it denied exactly the merge (c) requires
  allowed. `## Approval` was NOT touched — byte-identical, verified by diff.
- the four operator rulings behind the amendment: `notes/rulings-2026-09-08-panel-c7.md` (R-0 BRIEF
  re-signed at `ea0bdd6b`; R-1 refuse ambiguity; R-2 flag-aware parser; R-3 derive the recovery
  command). The plan text was amended for them in cycle 13, two PASS passes,
  `notes/research-BUG-1309-planamend-c13.md` and `-c13b.md`, with `approval:` byte-identical
  throughout; decisions D-13/D-14/D-15 record the rulings.
- **The plan signature must move, and the operator has said they will re-sign it.** `amend` holds
  the approval bytes by design, so `plan.yaml:3-6` still reads `approved` / `date: '2026-09-04'`
  over text amended 2026-09-08. The exact command and its preconditions are in the Open Questions
  below. A bare re-sign PRESERVES the four existing `approval.rulings` entries (`plan.yaml:7-25`) —
  verified in source, not assumed: `_approval_fields` (plan-merge.py:1081-1094) attaches `rulings`
  only when `--overrule` is passed, and `_replace_signature_fields` (plan-merge.py:1116-1127)
  rewrites the FIRST `status`, `approved_by` and `date` lines only, so each ruling's own nested
  `date:` passes through untouched.
- **The BRIEF signature needs no byte change.** `BRIEF.md ## Approval` already reads
  `date: 2026-09-08`, and the SC-04 amendment was made on 2026-09-08 under the operator's own
  ruling, so the recorded signature date already covers the amended text. There is no verb for the
  BRIEF block; if the operator wants an explicit re-affirmation it is a hand edit of those three
  lines by the main session, which alone holds that grant.
- the implementation is fully specified for the main session in
  `notes/direct-packet-2026-09-08-panel-c7.md` — three code edits (merge-gate.py `git_merge`,
  merge-gate.py `feature_for` + caller, gh-sync.py `_build_entry_recovery_notice`), six test cases,
  the exact verification commands, and the regression fence that must not move. No squad may execute
  any of it.
- cycles 13/14 — UNCHANGED by this round: the product lead reported zero send-backs, and an
  operator ruling answered rather than reworked (DEC-157). One cycle remains. runs 42 against a
  20-run budget (INV-22, informational, surfaced in the briefing).
- the briefing at `notes/ship-review-2026-09-08-resume.md` is STALE on the three findings and now
  also on SC-04; it is rewritten after the implementation lands, before the ship decision.
- next, in order: main-session-direct implementation → re-pin `review_sha` → qa matrix → panel c8 →
  goal-check including the widened SC-04 → SC-10 UAT → rewritten briefing → ship.

## Open Questions

- Q1 — **CLOSED 2026-09-08.** SC-04 under-coverage of the ambiguity DENY. Operator ruled WIDEN;
  applied at `BRIEF.md:108-125`, evidence `notes/research-BUG-1309-sc04-amend-c13.md`.
- Q2 (blocking, operator — **the one actionable step**) — the amended plan must be re-signed. The
  operator has stated the intent to re-sign. The main session runs, from the worktree
  `/Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/BUG-1309-mirror-build-entry`:

      python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py \
        sign-approval \
        --file .harness/harness/features/BUG-1309-mirror-build-entry/plan.yaml \
        --by 'Mike Ruangutai' --date 2026-09-08

  Preconditions: no `--overrule` (the three panel-c7 highs were ruled FIX, not risk-accepted, so
  nothing is being accepted); `HARNESS_AGENT_TYPE` must be ABSENT from the environment — the verb
  refuses any governed agent at exit 10 from inside `cmd_sign_approval` itself, so the main session
  runs it directly and never delegates it. Expected output: `SIGNED … by Mike Ruangutai on
  2026-09-08` then `APPLIED …`. Afterwards `plan.yaml:3-6` reads `date: '2026-09-08'` with the four
  2026-09-06 rulings intact at `plan.yaml:7-25`.
- Q3 (blocking, operator) — SC-10 UAT: `notes/uat-BUG-1309-mirror-build-entry.md`, 8 steps.
  Independent of R-1..R-3, but it must run BEFORE the worktree is released, because the script
  points at that checkout.
- Q4 (non-blocking, harness defect) — the `open` horn of the non-era recovery-required notice is
  specified by an UNNAMED intent bullet and is asserted by no test today: `grep -rn "MERGE is
  refused" tests/` returns nothing. Backlog row, or a later amendment.
- Q5 (non-blocking, harness defect) — a harness-product-lead run returned a complete, well-formed
  VERDICT/DIGEST/artifact and the host reported it `failed (exit 1)` with "Subagent called yield
  with null data". A correct return read as a failed run; every claim in it was verified at source.
- B-12 and the B-1..B-13 ship backlog in the stale briefing still await operator disposition.
