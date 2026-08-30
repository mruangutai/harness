# Expertise — harness-pm

## Patterns (max 15)
- P-01: WHEN a `verify:` grep would already have passed before the change DO label it
  non-discriminating and name a substitute command whose result only the change can produce.
  An absence-grep that was already empty proves nothing. Exemplar: the `## Verify receipts`
  section of a shipped plan under `.harness/harness/features/`.
- P-02: WHEN a criterion will cite automated evidence from a test kind DO check that kind's detect
  globs match files on the surface being changed: a non-null runner matching zero files here is a
  gate that proves nothing. Widen the runner as a task rather than downgrading the criterion to
  inspection.
- P-03: WHEN a criterion's grading set is derived from the artifact under grading — the plan's own
  file lists — DO re-base it on a source that artifact cannot define, then name the concrete case
  that now fails it. Otherwise it is true by construction and can never fail.
- P-04: WHEN a criterion quantifies over N items DO give each item its own assertion, in the verify
  you author and again when grading. A file-global search or a matching count is satisfied by the
  conformers alone, blind to the one item that conforms to nothing.
- P-05: WHEN grading a criterion DO grade every clause against its own subject: a leading claim
  broader than the enumeration binds; a trailing gloss whose subject excludes the case does not.
  Part of an enumeration is not met. A method blind to the failure grades worse than unmet.
- P-06: WHEN a criterion cannot be met DO decide whether the defect is in the code or in the
  sentence. If a retry could make it true, route a fix cycle. Otherwise escalate — never adopt a
  narrower reading yourself, even one a downstream gate upheld.
- P-07: WHEN a task or criterion sanctions alternative implementations DO read it as committing
  only to the weakest one: a fully conforming build may pick the alternative that delivers none of
  the property. Name the property in the instruction, or drop the alternative that cannot deliver it.
- P-08: WHEN a task's verify counts a token, or its intent directs the doer to write a factual
  claim, DO run the verify's exact command against the intent prose and verify the claim at source.
  You author both halves; no sweep catches a correctly-spelled false claim.
- P-09: WHEN handed a claim that a test already covers a property DO mutate the tool to violate the
  property and see which cases redden. Cited lines are often comments, not assertions. A mutant
  that reddens every case is broken, not evidence of strong coverage.
- P-10: WHEN a pointer cites a location DO anchor it on content text AND assert the target's own
  identifier separately. Body anchoring survives line drift but is blind to renumbering: entries
  renumber in the destination while every content anchor still matches, and the verdict stands.
- P-11: WHEN a criterion quantifies over a scope DO check, before dispatch, that the tasks tracing
  to it carry file lists covering that scope. A task naming one file cannot satisfy a clause over
  every document, so the criterion fails at goal-check for a planning reason no retry can fix.
- P-12: WHEN specifying a detector or sweep pattern DO derive it from the weakest fragment every
  target site necessarily contains, greped against the real file — never from the shape of the
  commonest site. An optional trailing fragment makes variant sites invisible, and the sweep then
  reports clean over them.
- P-13: WHEN judging whether a criterion is covered DO count independent methods, not clauses or
  concurring readers. Checks sharing one method share one blind spot, and a second reader who
  repeats that method is one measurement counted twice. Give at least one clause a behavioural check.
- P-14: WHEN a dispatch hands you a figure or a premise that sizes the work DO re-derive it against
  the tree the work will run in, and read the ticket's own later comments. A wrong premise changes
  the unit of work, not just a number, and re-deriving costs minutes.
- P-15: WHEN citing a named test case as an automated criterion's evidence DO grep the plan for
  that case's own passing line. An assertion no verify block pins is deletable with the whole
  suite green, and evidence that can vanish silently does not meet an automated bar.

## Gotchas (max 15)
- G-01: WHEN citing or counting anything in a file another agent may be editing DO pin the figure
  with `git grep <SHA>` and re-read the anchor at final state. Working-tree numbers mix pre- and
  post-edit positions, and equal counts across a concurrent edit are not confirmation.
- G-02: WHEN resolving which lane may write a path DO run the domain guard on the path and read its
  exit code. Reading the team config gave the wrong lane where the live hook gave the right one,
  and a dispatch naming a path is not evidence the path is granted.
- G-03: WHEN collecting command evidence for an automated criterion DO capture output by command
  substitution and grep the variable. Piping to `tail`/`head` truncates earlier output and reports
  the pipe's exit status, not the runner's; a redirect captures whole but is a write, refusable
  where the path is not granted.
- G-04: WHEN a verify slices a region anchored on a label's FIRST occurrence DO bound the region
  on both sides, or assert the label occurs once. A stray earlier mention relocates the region onto
  unrelated code that already satisfies the count, and the clause greens on work never done.
- G-05: WHEN a fixture test calls a loader whose default path binds at import DO require the task's
  intent to pass the fixture path explicitly. Omitted, the loader reads live state, the test passes
  for the wrong reason, and it proves nothing about the fixture it appears to exercise.
- G-06: WHEN your count contradicts a recorded one DO reproduce the recorded invocation before
  calling it drift. Two totals under one label are often two different measurements, and the
  invocation the plan or criterion mandates is the one that defines the quantity being graded.
- G-07: WHEN citing gate or panel evidence produced before the commit you are grading DO diff the
  range for source changes and re-run the suites at that commit. An earlier green proves the earlier
  tree, and the provenance rots silently because the verdict text stays true-looking.
- G-08: WHEN citing a suite's exit code or ok-line count as proof it passed DO read the runner's
  failure accounting first. One counting a failure only when a detail string is non-empty exits 0
  while printing FAIL lines, which no ok-count sees. Grep the failure prefix.
- G-09: WHEN routing a fix cycle DO name which met verdicts the remedy commit itself will falsify.
  A criterion quantifying over the whole change set goes stale underneath a later commit, the grade
  was correct when taken, and nothing can unland the commit that broke it.
- G-10: WHEN a check compares a field looked up by a name discovered at runtime DO add an explicit
  key-absent branch reporting CANNOT VERIFY. A wrong key makes both sides None, the comparison
  reports clean for every record, and its silence reads as proof.
- G-11: WHEN checking that a move preserved content verbatim DO build the anchors from the move
  commit's own removed lines, never from the baseline the brief quotes. The source drifts between
  that baseline and the move, and the mismatch then reads as content rewritten by the move.
- G-12: A plain YAML scalar containing a space then a hash starts a comment: `safe_load` truncates
  the value there, so an inline issue reference silently deletes the rest of the sentence. Write
  prose scalars folded or quoted, then reload the file and confirm each value's tail survives.
- G-13: WHEN you narrow, correct or supersede a claim DO fix every occurrence of it in the same
  edit — grep the whole artifact, and rewrite the artifact itself whenever your handoff summary
  supersedes it. The summary reaches one tier; the file is what the next context opens.
- G-14: WHEN a verify asserts absence by counting DO NOT wrap the search in
  `test "$(cmd | wc -l)" = 0`: a search that errors prints nothing, the count is zero and the test
  passes. Assert the search's exit status, or pair it with a positive control that must match.
- G-15: WHEN you author a verify, or grade a criterion, over a file the task produces DO read it at
  the ref under review, never the working tree. A tree-reading check passes for any deliverable that
  was never committed, and untracked output leaves no evidence at the ref at all.

## Outcomes (max 10)
- O-01: WHEN proving a test reddens if either side changes alone DO mutate one branch at a time,
  never one per side. Separate branches behind the same rendering redden different assertion sets,
  so a per-side proof reports the side covered while a whole branch stays unprobed.
- O-02: WHEN designing a mutation DO first read which side consumes which function, then aim it at
  the fixture the case itself builds. A mutant that reddens other cases but not the one under test
  missed its target, and that reads as coverage.
- O-03: WHEN proving a multi-grep verify block against a mutated file DO give every grep its own
  process substitution. One shared `<(...)` is a one-shot stream: the first grep drains it, so later
  absence checks pass and presence checks fail, inverting the whole ladder.
- O-04: WHEN proving a NEW conjunct of an and-chained verify can turn green DO build a temp tree
  where every earlier conjunct passes, then mutate only the new one. On the pre-change tree an
  earlier conjunct exits first, so the new one never runs and its green is assumed, never observed.
- O-05: WHEN mutating a resolved lookup back to a hardcoded literal DO first check that the
  fixture's value differs from that literal. Equal values make the mutation a no-op, the suite
  stays green, and the green reads as coverage of an assertion that cannot fail.
- O-06: WHEN a probe or mutation harness reports a uniform verdict across cases DO assert it ran
  the real artifact and reached the branch under test. A mis-invoked harness, or a call with the
  wrong argument shape, returns one early guard's answer for every case and reads as clean.
- O-07: WHEN a criterion claims a check fails against the pre-change code DO run the current suite
  against the earlier commit's copy of the changed file. Where the change is one script, a prior
  commit is a free mutant and proves the clause independently of the gate that asserted it.
- O-08: WHEN a criterion demands that a mutant redden DO first check whether the test harness
  already honours a binary-override environment variable. A seam pointing the suite at a temp copy
  turns an unprovable claim into a two-command proof, with no edit to the shipped script.
- O-09: WHEN a criterion needs an unreadable path DO create a dangling symlink inside the test's
  own temp directory. It fails a readability test for every uid and is never checked in, whereas a
  zeroed file mode is a no-op as root and is not preserved by version control.
- O-10: WHEN a read-only dispatch needs mutation evidence DO copy the tool and its test module
  into a temp directory outside the tracked tree and import it there — a test building its own
  fixtures needs no repo layout, so mutation proof survives a no-write grant.

## Open (max 5)
