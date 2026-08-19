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

- 2026-08-19: I passed `model: sonnet` AGAIN on the FIX-01 dispatch, a second time in the same
  feature, after already recording the first block in this very log. The guard caught it again.
  A lesson written in a log I do not re-read mid-run does not change my behaviour; only the
  hook does. This is the argument for enforcement over doctrine in my own conduct, not just in
  the code I review.

- 2026-08-19: the FIX-01 dispatch reached me carrying "it reached me as exit 0" for a red
  integration suite. I read run-unit-tests.sh:57-71 during the in-flight wait: it counts
  failures and `exit 1` when any script fails. So the runner is correct and the false green was
  pure narration — someone reported a status they never observed. Worth separating: a tool that
  lies needs a fix, a narrator that lies needs evidence discipline, and the remedy differs.

- 2026-08-19: I hand-derived all six expected fixture lists from team-config.yaml myself during
  the wait, then compared positions against the member's output on return (lines 40, 57, 76,
  94, 112, 126). This is the cheapest form of P-12-style independent check I have found: derive
  the answer while blocked anyway, so verification on return costs one grep instead of trust.
  It also caught that the manifest has 16 repository-tier grants while the fixture pins only 6.

- 2026-08-19: harness_yaml.py:362's docstring carries the SAME stale "equivalent to
  check-domain.sh's pre-change collect()" claim as the test docstring the dispatch flagged. The
  advisory finding was framed as a test-file issue and is actually a two-site issue. A finding
  scoped to the file where it was noticed under-reports its own blast radius.

- 2026-08-19: the member's DIGEST reported `task: T-05` while my dispatch said FIX-01 and its
  own receipt says FIX-01. The durable artifact was right and the routing field was wrong —
  which is the more dangerous direction, since the orchestrator reads the DIGEST field and
  never opens the receipt.
