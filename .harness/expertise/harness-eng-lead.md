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
- P-06: WHEN a review of an unapproved artifact finds a blocking design gap DO check the
  artifact's own status field before grading — a draft still pending signature routes the
  finding to the planner and returns PASS; halting it breaks the revision flow it was written for.
- P-07: WHEN a task's write path is unowned by your own manifest reading DO split it so the
  bankable phase dispatches first — the guard's denial names the permitted set and routes,
  where halting on your reading alone banks nothing.
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
- P-13: WHEN a verify command asserts a generator's output matches the tree DO ask what makes it
  red — `generate && git diff --exit-code` passes when the author wrote nothing; pair it with a
  stdout diff and a grep for a mandated literal.
- P-14: WHEN a plan declares a pattern that detects a stale form DO audit it against every real
  occurrence in the target file — a pattern generalised from the commonest site misses the
  variants, and the file then reports clean while carrying dead sites.

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

## Outcomes (max 10)

## Open (max 5)
