# Expertise — harness-eng-lead

## Patterns (max 15)
- P-01: WHEN a member reports a receipt in prose instead of the observed value DO send it back
  for the verbatim output and the invocation form — a lead-tier send-back costs one member
  spawn; the same gap found later by the review panel costs a feature cycle.
- P-02: WHEN dispatching a task that inverts or retires an existing assertion DO put the
  adjacent labels, docstrings and usage strings explicitly in scope — prose asserting the
  superseded contract is the same defect class, and a stale test label propagates upward as
  though it were a measurement.
- P-03: WHEN a task's verify list is greps plus a test suite DO ask which changed module the
  suite actually executes — a module the runner never imports is left unproven by a green gate,
  not proven by it.
- P-04: WHEN a member kept no observations log DO hand it the paths to its own prior artifacts
  and say self-derived candidates count as its own material — otherwise every entry in its file
  traces to your relay, and the acceptance rate grades your dispatch, not its judgement.
- P-05: WHEN a member reports entry or finding counts in its headline DO count its own ops list
  and open the file before repeating the number — self-reported totals have disagreed with the
  file in successive runs, and yours is the tier where a count becomes a measurement.
- P-06: WHEN approving a replacement for an assertion DO ask what the old one PINNED and check
  the new SET still pins it — "no assertion may be weakened" passes when each is individually as
  strong and the set has lost a property, so nothing reddens when the defect returns.
- P-07: WHEN a dispatch requires you to run a check you hold no shell for DO route it to an
  in-squad non-doer that re-extracts the command from the approved plan and byte-diffs it
  against your dispatch string, and state in your digest which form of evidence was delivered.
- P-08: WHEN a clause count is offered as evidence a design rule is guarded DO count only the
  behavioural clauses — grep clauses die to a rename, and an assertion coarser than the property
  it names is green under the bug.
- P-09: WHEN a dispatch states what a file contains — an anchor, a justification, a relayed
  finding's premise — DO open the file before relaying it: an unchecked claim is copied verbatim
  into source, tests and records, and survives every gate green.
- P-10: WHEN a gap's remedy is an obligation recorded in prose DO propose the instrument that
  reddens instead — and where none can exist, say at review that no code gate verifies it:
  inspecting a rule proves it exists, never that it fires.
- P-11: WHEN a member's finding would be remedied only by contradicting a signed decision DO
  route it up as a decision question and keep the verdict PASS — dispatching the fix would make
  the squad amend an approved plan without approval.
- P-12: WHEN a member is barred from running the checker that validates its own output DO read
  the checker and apply its rule yourself before accepting — the carve-out moves the check to
  you, it does not remove it.
- P-13: WHEN a verify rests on a generator diff or a glob-driven scan DO ask what its empty
  case returns — `generate && git diff --exit-code` passes when nothing was written, a
  zero-match glob exits 0; pair each with an assertion on content
- P-14: WHEN a sweep or detector keys on one spelling of the thing it hunts DO enumerate the
  other spellings — joined tuples, depth arithmetic, wildcards — before trusting its file list
  or its clean report; sites it cannot spell are absent from both
- P-15: WHEN an optional edit's only proof would be authored by the same agent making it, over
  text no standing assertion pins, DO decline it and backlog the alternative verbatim — a fixer
  certifying its own fix is the shape of the defect these passes exist to catch.

## Gotchas (max 15)
- G-01: `.claude/skills/harness/bin/**` sits in both backend-dev's and dev-ops's domain in
  team-config.yaml, so the domain hook cannot keep their writes disjoint there — serialize any
  two tasks touching one file under it and attribute each write.
- G-02: WHEN two specialists' domains both grant a task's path DO route by the plan's own
  `execution_agent` when it names one, and record it — re-routing on `consult-when` purity would
  amend an approved plan, and the grant itself cannot discriminate.
- G-03: A path in no agent's `domain:` and absent from `shared:` is writable by no agent —
  `manifest_domains` does no widening or inheritance. Re-dispatching to another specialist
  reproduces the denial; the fix is a manifest grant or main-session-direct, neither a lead's call.
- G-04: WHEN a receipt path is named both by the team file's `outputs:` template and by the
  approved plan's `files:` list DO write the plan's literal path — a `verify:` clause greps the
  plan's string, so the rendered template leaves the gate red on correct work.
- G-05: WHEN distilling into a shared Expertise file from a worktree DO compare entry text
  against the main checkout's current copy before writing, never IDs — a worktree branched
  before the last distillation carries a stale base whose write reverts the prior feature's
  entries, every format check green.
- G-06: WHEN two agents disagree about HEAD and you hold no shell DO read `.git/HEAD`,
  `.git/refs/heads/<branch>` and `.git/logs/HEAD` directly — a mid-run fast-forward means
  measurements taken earlier were taken against a different tree, so re-measure what the
  decision turns on.
- G-07: WHEN a task's intent presents an enumeration of sites as exact and its verify counts the
  remainder DO re-derive the set yourself — one missed site reds a correct execution, and the
  executor's cheapest way green is deleting the literal the gate exists to protect.
- G-08: WHEN a verify clause scans from a heading anchor to EOF for text the task must write DO
  measure that string's pre-existing occurrences in the target file — nonzero, or an anchor one
  heading level higher, greens the clause on text nobody wrote.
- G-09: WHEN a success criterion grades a commit range but every task's verify only greps and
  runs suites DO enumerate the working tree's modified files outside every task's files list
  before the commit — a sweep-all commit fails that criterion on paths the squad never touched.
- G-10: WHEN dispatching a distillation into an existing Expertise file DO capture one
  distinctive token per current entry before the spawn and compare by text on return — the
  format checker has no notion of prior state, and a drop plus a renumber leaves the id set
  identical.
- G-11: WHEN relaying a closed run's finding into permanent memory DO re-measure its premise at
  the current tree first — a finding is dated at its pin, the tree moves past it, and a remedied
  one distilled as fact teaches something false that no gate can catch.
- G-12: WHEN a dispatch must prove one error message discriminating from another DO require a
  runtime assertion — trigger both, assert the substring present in one and absent from the
  other. `grep -c` counts source LINES, so a phrase straddling an f-string's line break returns
  zero, which reads as unique.
- G-13: WHEN a member is still in flight DO spend the open turn on reads that could change your
  assessment, never on filesystem polling — completions arrive by notification, and a receipt
  already on disk may still be mid-revision, so reading it early buys a false finding.
- G-14: WHEN rating a finding that a function fails silently DO enumerate its call sites first —
  if every caller pre-filters the case, it is a falsified docstring, not a live hole, and
  severity decided by who calls it is the difference between a fix cycle and a routed question.
- G-15: WHEN dispatching against a suite with known failures DO decide the expected FAIL set and
  its evidence before the member reports — deciding after is how a new defect gets filed under
  "expected", and a known FINDING is not a known FAILURE.

## Outcomes (max 10)

## Open (max 5)
