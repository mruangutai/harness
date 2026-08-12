# Expertise — harness-pm

## Patterns (max 15)
- P-01: WHEN a `verify:` grep would already have passed before the change DO label it
  non-discriminating and name a substitute command whose result only the change can produce.
  An absence-grep that was already empty proves nothing. Exemplar: the `## Verify receipts`
  section of a shipped plan under `.harness/features/`.
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
- P-06: WHEN judging whether an unmet criterion is undischargeable DO read the signed proof
  standard. If it forbids the only technique that could instantiate the condition, it cannot also
  demand it: the strongest proof permitted inside the standard is the proof, and the route is a
  fix cycle.
- P-07: WHEN drafting a criterion DO read it for presupposition against the criteria already
  written. A clause asserting something about surviving occurrences presupposes they survive,
  which negates any absence check over the same files. Each reads sound alone.
- P-08: WHEN a task's `verify:` counts or forbids a token DO grep that same task's own intent prose
  for the token before shipping the task. You author both halves, and the conflict is invisible on
  reading — it appears only when someone runs the clause.
- P-09: WHEN handed a claim that a test already covers a property DO mutate the tool to violate the
  property and see which cases redden. Cited lines are often comments, not assertions. A mutant
  that reddens every case is broken, not evidence of strong coverage.
- P-10: WHEN a criterion, task step, or carried-forward evidence pointer cites a location DO anchor
  it on content text, never a line number or an ordinal such as a test-case number. Both rot within
  one cycle as files shift, leaving verdicts standing while every pointer under them lands wrong.
- P-11: WHEN a criterion names the mechanism behind a behaviour DO confirm the code uses that
  mechanism before signature, or state the observable outcome instead. A criterion false only in
  its mechanism routes as a fix cycle against working code, never as a re-signature.
- P-12: WHEN tasks partition a token sweep DO run the widest verify pattern tree-wide at plan time,
  assign every hit to an owning task, and order the sweeping task after them. A narrower pathspec
  upstream is a blind pass; the widest grep is the real survey.
- P-13: WHEN a criterion's clauses are verified DO count techniques, not clauses. Several source
  greps share one blind spot, and a single idiom change defeats them together. Balanced clause and
  fixture counts hide this. Give at least one clause a behavioural check.
- P-14: WHEN a brief names a hazard DO probe the opposite input condition as well before planning
  against it. The named half is the half someone already noticed; the unnamed half often fails
  open, exiting clean where the named one fails loudly.
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
- G-04: WHEN re-deriving counts, lists or partitions in a revision pass DO include the items you
  added earlier in that same pass. Your own additions are the likeliest staleness source, and a
  self-describing list that under-counts itself still reads as authoritative.
- G-05: WHEN an amendment widens the scope of an already-executed task DO carry the re-dispatch
  signal in your DIGEST. A filed receipt proves only what it ran against, and no plan file can
  re-open a task that already passed.
- G-06: A sibling worktree under `.claude/worktrees/` is a full second copy inside the search path:
  `.gitignore` hides it from `git grep` but not `grep -r`, and the same path resolves to different
  content there with no error. Confirm which checkout resolved any file:line you cite.
- G-07: WHEN confirming a criterion built from several tokens DO enumerate every hit with the full
  pattern and confirm each sits inside text the change removes. Greping one token of five verifies
  one fifth of the claim; file-level arithmetic is not evidence.
- G-08: WHEN a task adds a file to a suite that keeps an explicit registration list DO register it
  in that same task. A drift detector fails the WHOLE run on an unregistered file, reddening every
  other task's verify. Exemplar: the SCRIPTS array in this repo's unit-test runner.
- G-09: WHEN a step you write will mutate live state DO trace the tool's resolution of its target
  from its entry point first. A CLI can take the target from a config file while the flags name
  something else, sending your one live measurement at the wrong system.
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

## Open (max 5)
