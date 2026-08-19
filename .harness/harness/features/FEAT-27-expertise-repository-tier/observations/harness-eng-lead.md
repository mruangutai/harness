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

- 2026-08-19: dispatch-guard.sh has now blocked a `model:` parameter twice in FEAT-27, from two
  DIFFERENT leads. Two of my own blocks are recorded above, so the org-level shape is not "one
  lead has a bad habit" — it is a rule the org keeps rediscovering at runtime rather than at
  authoring time. The parameter is available in the tool schema and forbidden only by a hook, so
  every lead meets the prohibition for the first time by tripping it. That is a design
  observation about where the rule lives, not a complaint about the guard, which worked both times.

- 2026-08-19: on T-07 I verified the mutant's discriminating power from source BEFORE the member
  returned, and it changed what I would accept. `kaya` is a plain lowercase token, so the segment
  filter at inject-expertise.sh:75-77 does NOT reject it — which is precisely why a dangling
  symlink reddens where an unexpanded glob word cannot. Two independent assertions fail under the
  mutant: the "kaya" header printed at :114, and stderr, which takes three writes (head, wc, and
  the empty `$( )` making `[ "" -gt 40 ]` a bash integer error at :57-58). Deriving WHY a case can
  fail, not just that it did, is what separates assessing from re-running.

- 2026-08-19: THIRD `model:` block in one feature, on the simplify pass — I passed `model: opus`
  to all four angle dispatches in a single message, so one habit cost four blocked spawns at once.
  The two earlier entries in this very log did not prevent it. What is now clear is that the
  batching multiplies the error: a per-dispatch mistake in a fan-out wave is not one mistake, it
  is N. The guard is the only thing standing between the habit and the org.

- 2026-08-19: the simplify pass's most valuable finding came from neither the four angles nor the
  assessment — it came from a read I did while all four were in flight. No case in
  test-inject-expertise.py writes anything under the neutralized `home`, so the global tier is
  never exercised, and four PROJECT-tier fixtures are literally named "GLOBAL BODY…" which makes
  the untested path read as tested. Four independent readers each carrying one angle all missed
  it because it is not any single angle's question. The in-flight wait is not dead time; it is the
  only slot where the lead reads the same surface without an angle constraining it.

- 2026-08-19: two of four readers reported case counts that did not survive my own count
  ("14 base + 20 extra" vs my 9 `case()` registrations and 22 `record()` calls; "16 scripts" vs
  run-unit-tests.sh:17's 17). Neither error changed a finding, which is exactly why it is
  dangerous — a wrong number attached to a correct conclusion is the form that propagates, because
  nothing about the conclusion invites re-checking the number.

- 2026-08-19: a read-only dispatch is not self-enforcing for an agent holding Bash. The efficiency
  reader planted three files in the live tree to count N empirically, then removed them and proved
  the tree clean — good evidence, obtained by the one method the round's premise forbade, while a
  qa gate graded the same commit. "Read-only" stated in prose is a request; the domain hook cannot
  see Bash writes. When a measurement genuinely needs a populated tree, the dispatch should name
  the temp-CLAUDE_PROJECT_DIR technique the suite already uses, rather than leaving the reader to
  invent one.
