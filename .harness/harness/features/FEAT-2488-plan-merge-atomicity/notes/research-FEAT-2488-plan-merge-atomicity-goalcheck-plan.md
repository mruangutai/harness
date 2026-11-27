# Goal-check (plan) — FEAT-2488 plan_merge two-file amendment atomicity

**BLUF: yes, the plan as it stands after the cycle-2 apply still delivers the operator's stated intent.** All three declared perspectives pass. Every binding ruling (Q1–Q6), every named non-goal and all five SC seeds are still carried. The c2 repairs (PF-cc9533d1, PF-484f97f2, PF-ebc96c4b) tighten how recovery behaves and how it is reported. They add no mechanism the grilling did not ask for, and one of them removes a step. One gap carries over from the earlier grade unchanged: Q6's rework ruling (2 rounds / 90 min) is a DEC-226 signature-time ruling and is not yet recorded. Nothing blocks the plan.

This note replaces the pre-c2 grade, which is now stale.

**What was graded against what:**
- Graded against: `/Users/molchairuangutai/GitHub/harness/.harness/notes/grilling-plan-merge-atomicity-e-2026-11-23.md`.
- Read alongside: the applied BRIEF.md and plan.yaml. The plan's approval status is `pending`. `panel:` is at cycle 2 with 12 findings, all 12 `resolved` and 0 `open`.
- Checks I ran:
  - `plan-merge.py check --root <feature worktree>` with HARNESS_AGENT_TYPE unset: 2 tasks, 13 anchors resolved, 0 failures.
  - The SC-05 base count, re-measured at 2491336e: 1 + 4 + 3 = 8 `check(` calls across the three ledger-failure cases.

## Perspectives (`## Done when — by perspective`)

| Perspective | Grade | Carried by |
|---|---|---|
| operator | **pass** | **SCs:** SC-01, SC-04, SC-07.<br>**T-01:** `locked_pair_update` and `recover_journals`; the unit cases for convergence, double recovery, LOCKED code 6 and DIVERGED code 5; the c2 replay-failure unit case and interleaving cases (i)–(iv).<br>**T-02:** torn-state cases (a)–(f); (g), the exact-stdout regression lock; (h), feedback failure after commit; (i), a ledger failure after the journal is published reported as committed-pending; (j), new in c2, a replay failure reported as pending, never "nothing was written", with no Traceback; and an 11-suite no-journal regression verify (SC-07). |
| code maintainer | **pass** | **SCs:** SC-02, SC-03, SC-06.<br>**T-01:** puts `replace_bytes`, `JournalPending`, `locked_pair_update` and `recover_journals` in `harness_merge`. Item 10's docstring states the protocol, that only the journal and its directory are fsync'd, the JournalPending boundary and the lock order plan.yaml.lock → feature.json.lock.<br>**T-02:** deletes `_replace_bytes` and `_restore_plan`, moves approval's BRIEF rename onto `replace_bytes`, corrects the `feature_json_write` fsync claim and removes the reset bookkeeping. Its verify asserts that no `plan_merge/*.py` contains mkstemp, os.replace or journal handling. |
| reader (qa / reviewer) | **pass** | **SCs:** SC-05, SC-01.<br>**T-02:** migrates the three ledger-failure cases rather than deleting them, keeping every check, so they carry at least 8 `check()` calls. I re-measured the base count at 2491336e: 8. Torn states are built on disk.<br>**Red receipts:** `red-t01-journal-unit.txt` and `red-t02-plan-merge-base.txt` are captured before production edits. After c2, (i) must reach the feature.json replace seam at the base before its outcome is graded, so its red is the old diagnostic differing, not a setup failure (PF-484f97f2). |

Every perspective has at least one task serving it.

## Binding rulings after c2

- **Q1 scope:** carried.
  - Atomicity: D-01, T-01 and T-02.
  - DEC-199 letter compliance: T-02 item 3.
  - fsync docstring: T-02 item 1.
  - The 5 dead lines and the unread `base_doc` parameter: T-02 item 5.
  - No DEC amended: every `decisions_affected` row is `keep`.
  - `check-plan-routes.py` and `test-check-plan-routes.py` are not edited: the do-not-edit lists in T-01 and T-02.
  - Approval hashing untouched: DEC-230 is `keep`.
  - T-01's single `canonical-reader-classification.json` row goes in the audit's data file, not in either file Q1 forbids.
- **Q2 design:** carried.
  - Plan-first order (D-01).
  - Recovery in the core (D-02; c2 adds "acted on only as re-read, membership included, under its primary's lock").
  - Every plan-lock acquirer recovers first (T-01 item 9).
  - The lock order is documented.
  - No production injection hooks: c2's (i), (j) and the interleaving cases monkeypatch in tests only.
  - `locked_update` has no fsync.
  - Two departures remain, both within the latitude Q2 gave: the journal's directory is also fsync'd, and idempotence uses byte images rather than judgement equality (research note; D-02 `because:`).
  - c2 moved *toward* the grilling's "fsync applies to the journal only" posture: the post-unlink directory fsync on replay is dropped, and the reason is stated in item 6.
- **Q3 simplification:** carried. Byte splicing is kept, there is no LOC target and no SC is phrased as a line count. `_task_search` and `_item_range_within` are not consolidated, and `PRESERVE_BASE_BYTES` and `UNION_MERGE` are untouched (T-02's do-not-edit list).
- **Q4 execution:** carried. Both tasks and all three lane rows are main-session-direct, with red tests first.
- **Q5 SC seeds:** carried.
  - SC-01 → BRIEF SC-01. c2's replay-failure reporting falls under its existing "never 'nothing was written'" clause.
  - SC-02 → SC-02 and T-02's verify.
  - SC-03 → SC-03, by code anchor, which the seed allowed.
  - SC-04 → SC-04, SC-06 and SC-07. The advisory narrowing in OQ-2 below still applies.
  - SC-05 → SC-05, base count 8.
- **Non-goals:** all six are still in the BRIEF's `## Out of scope`, and no c2 edit touches them.
- **Q6:** E2 is deferred (#2489), and the `test-check-plan-routes.py` defect correctly has no E task. **The rework ruling (2 rounds / 90 min) is not recorded:** `approval:` carries only `status: pending`.

## Did c2 push scope beyond the grilling?

**No.** Each repair specifies behaviour the grilling already required: deterministic recovery, completed under the lock, re-runs idempotent, never lying about what was written.

- **PF-cc9533d1:**
  - **What it adds:** `JournalPending.replay`, two replay diagnostic lines, and `_resolve_plan` exiting 2 with no Traceback.
  - **Why it stays in scope:** without it, a failed roll-forward would print "nothing was written" while a member had already been replaced. That is the dishonest-ledger direction Q2 was built to prevent.
  - **Net effect:** it also *removes* the post-unlink directory fsync (Delete First).
- **PF-484f97f2:** retargets test (i) onto a seam present at both base and pin. It changes the test only and adds no mechanism.
- **PF-ebc96c4b:**
  - **What it adds:** a membership re-check under the primary's lock, and a refusal of duplicate members as JOURNAL UNREADABLE.
  - **Why it stays in scope:** it is the DEC-199 lock discipline applied to recovery, and it adds no surface.
- **The `_resolve_plan` preflight recovery hook:** it is kept, not new in c2. c1's should-not-exist finding was dispositioned against it, and T-02 case (a) is now named as the evidence that the hook is required. That is a defensible reason for keeping it inside the grilling's "every acquirer ... checks first".

The net new operator-visible surface is one message class (the replay lines). It follows from SC-01 rather than extending it.

## Open
- OQ-1 (non-blocking): main records the Q6 rework ruling (2 rounds / 90 min) at signature (DEC-226).
- OQ-2 (non-blocking, advisory):
  - SC-04 locks full stdout for two amend shapes. Every other existing amend case is protected only by its own assertions (SC-07).
  - The removed lines could only ever print APPROVAL-RESET, which (g) asserts is absent.
  - Accept the narrowing, or widen it at signature.
