# Rework ruling by delegated authority — BUG-2420 — 2026-11-22

Authority: the operator's delegation (`notes/answers-2026-11-22-signoff.md`). Ruled by
`fable-advisor` (`AdvisorC5PatchMerge`).

**Question.** Validate c0 returned PASS at c0c3f1b9 with no must-fix. One finding was raised: the
code reviewer's med/substance, advisory under `advisory_unless_high`. `changed_lines` in
`tests/unit/test-plan-merge-first-station.py` compared lines by membership and read with newline
translation, so SC-01's "every other byte unchanged" was not proven. QA's CRLF mutant M8 stayed
green. Merge on c0, or fix first?

**Ruling: A.** Fix now as rework round 1, then run validate c1, then merge. A `substance` finding
is fixed inside the rework ruling. The test is SC-01's own evidence artifact. Merging it on CI
alone would break the pinned-review chain.

**Constraints.**
1. Timebox to the ruling window. If it expires before c1 completes, stop. Never fall back to the
   stale c0 pin.
2. Re-run red against the pinned pre-fix `stations.py` (sha256 `ceef2a6b…`): the insertion row
   must still fail. The refusal row asserts bytes identical to the original.
3. Read bytes, with expected bytes built from `PLAN` by the exact splice. Keep the needle checks
   and the 4-checks-per-row loop. Test grades stay ≥ 3.
4. c1 scope: QA and code only, over the test-only diff at the new pin.
5. This spends the one rework round. If c1 fails, return with the findings named; there is no
   round 2.
6. QA-OBS-2: no action.
7. Main-session-direct (DEC-174).

**Done.**
- Fix: f08cc8f7. Receipts: `notes/rework-c1-oracle.md`. Red against the pinned module: still red.
  M8: now caught. Green at the fix. The literal verify exits 0 with grades passing.
