# Observations — harness-eng-lead — FEAT-27-expertise-repository-tier

- 2026-08-19: dispatch-guard.sh blocked my first T-02 spawn because I passed `model: sonnet`.
  The block was correct (DEC-152/155) and cost one spawn attempt with zero member work. Worth
  noting the failure mode is silent in my own reasoning — I reached for the parameter without
  registering it as a decision. The guard, not my judgement, is what caught it.

- 2026-08-19: T-02's twelve test cases assert the absence of "authoritative on conflict" and
  "most specific" in the hook's EMITTED OUTPUT only. A comment inside inject-expertise.sh
  retaining either phrase passes all twelve. I grepped the script directly on return: 0 hits
  for "authoritative on conflict" and 0 for "carries more weight"; one hit at :106 for "most
  specific", inside a comment, using the rationale intent 1b explicitly PERMITS ("the most
  specific tier, so they ride last") rather than the one it forbids. The distinction only
  exists if you read 1b closely — a coarser grep-for-"most specific" gate would have failed
  correct work.

- 2026-08-19: the precedence line's "emit exactly once" property is not pinned by the shape of
  the test alone. Case 1 asserts two substrings; case 2 counts one of them once. Both stay true
  if the line is split across two printf calls. I read inject-expertise.sh:110 to confirm it is
  a single printf outside the per-segment loop. Substring assertions cannot see line structure.

- 2026-08-19: spent both in-flight waits on reads rather than polling, and both paid. The
  qa-gate detect-glob gap (harness.json:119 does not name test-check-expertise.py while
  harness-qa-gate/SKILL.md:74 resolves an unmatched detect glob to FAIL) and the
  plan-vs-digest change_type vocabulary mismatch (validate-digest.py:158 has no `logic` member)
  were both found in dead time, not during assessment.

- 2026-08-19: the SubagentStop digest hook fires on every turn I end, including turns where a
  member is still in flight and no verdict exists yet. Ending a turn to wait for a completion
  notification is therefore not free — it returns a contract-violation rejection each time.
  Filling the wait with real reads is the only shape that both satisfies the hook and avoids
  the polling my own G-13 warns against.

- 2026-08-19: I hit my own P-14 while checking T-03's intent premise. Grepping
  harness-distill/SKILL.md for "advisory|scan|token" returned one irrelevant line and I nearly
  reported the premise falsified. The skill spells it "advisorily" (:61-62: "check-expertise.sh
  flags such entries advisorily, for a human to rule on, and a flag is not a violation"), so
  the premise holds and T-03 closes a real doc-ahead-of-code gap. The near-miss is the point:
  I authored P-14 and still ran the one-spelling grep first.
