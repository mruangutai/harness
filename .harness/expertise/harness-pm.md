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
- P-03: WHEN a criterion declares automated verification DO NOT admit a source-code reading as its
  evidence — that converts it to inspection, and the method is fixed at approval. Name the passing
  test, or return the criterion not met.
- P-04: WHEN a criterion enumerates N distinctions or shapes DO map each to an assertion of its own
  and read that assertion, never matching counts. Equal counts hide a miscredited neighbour, and
  inequality is not transitive — the enumeration can be half-covered while every count agrees.
- P-05: WHEN grading a criterion DO grade its own full text: a leading claim broader than its
  enumerated list still binds, and an enumeration delivered in part is not met, never partial.
  Met on a method that cannot detect the failure it exists to detect is worse than unmet.
- P-06: WHEN a criterion cannot be met DO decide whether the defect is in the code or in the
  sentence. If a retry could make it true, route a fix cycle. Otherwise escalate — never adopt a
  narrower reading yourself, even one a downstream gate upheld.
- P-07: WHEN a criterion admits two readings DO test each against the remedies already sanctioned
  for it. A reading that makes every sanctioned remedy non-compliant on arrival is the wrong one.
  That is external evidence for narrowing, which your own preference never is.
- P-08: WHEN a task's `verify:` counts or forbids a token DO run that verify's exact command — same
  flags, same case — against the task's own intent prose before shipping. You author both halves,
  and a friendlier-flagged trial hides a collision the shipped clause will redden correct work on.
- P-09: WHEN handed a claim that a test already covers a property DO mutate the tool to violate the
  property and see which cases redden. Cited lines are often comments, not assertions. A mutant
  that reddens every case is broken, not evidence of strong coverage.
- P-10: WHEN a criterion, task step, or carried-forward pointer cites a location DO anchor it on
  content text, unless an ordinal is pinned by a recorded no-renumber constraint the graders share.
  An unpinned line number or ordinal rots within one cycle, leaving verdicts standing over pointers
  that land wrong.
- P-11: WHEN a criterion requires a test to detect drift between two renderings DO require one
  side to execute the real artifact, or both call sites to import one owner. A mirror inside the
  test cannot detect drift in the thing it copies, and grades met while blind one way.
- P-12: WHEN specifying a detector or sweep pattern DO derive it from the weakest fragment every
  target site necessarily contains, greped against the real file — never from the shape of the
  commonest site. An optional trailing fragment makes variant sites invisible, and the sweep then
  reports clean over them.
- P-13: WHEN a criterion's clauses are verified DO count techniques, not clauses. Several source
  greps share one blind spot, and a single idiom change defeats them together. Balanced clause and
  fixture counts hide this. Give at least one clause a behavioural check.
- P-14: WHEN a dispatch hands you a count that a plan step must assert DO recompute it against the
  tree that step will run in. A handed-down count can describe the unremedied state, and earlier
  steps of the same remedy often remove one — a stale count manufactures a mid-sequence halt.
- P-15: WHEN a task's intent directs the doer to write a factual claim about the codebase DO verify
  that claim at source before shipping the task. You author both halves, no sweep catches a false
  claim that is correctly spelled, and the doer either refuses or propagates it.

## Gotchas (max 15)
- G-01: WHEN citing or counting anything in a file another agent may be editing DO pin the figure
  with `git grep <SHA>` and re-read the anchor at final state. Working-tree numbers mix pre- and
  post-edit positions, and equal counts across a concurrent edit are not confirmation.
- G-02: WHEN resolving which lane may write a path DO run the domain guard on the path and read its
  exit code. Reading the team config gave the wrong lane where the live hook gave the right one,
  and a dispatch naming a path is not evidence the path is granted.
- G-03: WHEN collecting command evidence for an automated criterion DO redirect the run to a file
  and grep it. Piping a multi-script runner to `tail`/`head` truncates the earlier output away and
  reports the pipe's exit status, not the runner's — the evidence disappears silently.
- G-04: WHEN a verify slices a region anchored on a label's FIRST occurrence DO bound the region
  on both sides, or assert the label occurs once. A stray earlier mention relocates the region onto
  unrelated code that already satisfies the count, and the clause greens on work never done.
- G-05: WHEN an amendment widens the scope of an already-executed task DO carry the re-dispatch
  signal in your DIGEST. A filed receipt proves only what it ran against, and no plan file can
  re-open a task that already passed.
- G-06: WHEN your count contradicts a recorded one DO reproduce the recorded invocation before
  calling it drift. Two totals under one label are often two different measurements, and the
  invocation the plan or criterion mandates is the one that defines the quantity being graded.
- G-07: WHEN citing gate or panel evidence produced before the commit you are grading DO diff the
  range for source changes and re-run the suites at that commit. An earlier green proves the earlier
  tree, and the provenance rots silently because the verdict text stays true-looking.
- G-08: WHEN a task adds a file to a suite that keeps an explicit registration list DO register it
  in that same task. A drift detector fails the WHOLE run on an unregistered file, reddening every
  other task's verify. Exemplar: the SCRIPTS array in this repo's unit-test runner.
- G-09: WHEN routing a fix cycle DO name which met verdicts the remedy commit itself will falsify.
  A criterion quantifying over the whole change set goes stale underneath a later commit, the grade
  was correct when taken, and nothing can unland the commit that broke it.
- G-10: WHEN a check compares a field looked up by a name discovered at runtime DO add an explicit
  key-absent branch reporting CANNOT VERIFY. A wrong key makes both sides None, the comparison
  reports clean for every record, and its silence reads as proof.
- G-11: WHEN a later signed ruling falsifies prose inside an approved brief DO report the
  contradiction and leave the prose standing. Editing a signed artifact is a re-signature, not a
  record correction, but the brief is what the next reader opens.
- G-12: A plain YAML scalar containing a space then a hash starts a comment: `safe_load` truncates
  the value there, so an inline issue reference silently deletes the rest of the sentence. Write
  prose scalars folded or quoted, then reload the file and confirm each value's tail survives.
- G-13: WHEN you narrow or correct a claim in one section of an artifact you are revising DO grep
  the whole artifact for the claim's tokens and fix every occurrence in the same edit. Fixing only
  the cited section leaves two contradictory statements inside one document.
- G-14: WHEN a verify asserts absence by counting DO NOT wrap the search in
  `test "$(cmd | wc -l)" = 0`: a search that errors prints nothing, the count is zero and the test
  passes. Assert the search's exit status, or pair it with a positive control that must match.
- G-15: WHEN a criterion will be graded against working-tree state rather than a commit DO make the
  task name its before and after capture commands and their output artifacts. Untracked files leave
  no commit evidence, so a missing capture is unrecoverable and stays invisible until goal-check.

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

## Open (max 5)
