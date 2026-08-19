# Expertise — harness-orchestrator

## Patterns (max 15)

- P-02: WHEN dispatching any validator run DO re-pin `review_sha` at a commit that CONTAINS the work
  under review, and move the pin again after every commit. An inherited pin from an earlier phase
  reviews a tree the work is absent from and returns PASS on nothing.
- P-03: WHEN you restate another agent's claim in your own voice DO attribute it or check it
  first — restating launders a report into a fact, and every dispatch you write afterwards carries
  it as established.
- P-04: WHEN dispatching a fix DO pass the discriminating RULE plus an explicit LEAVE list rather than a
  survey of sites. The LEAVE list does the work: unnamed near-misses are where a member spends a spawn
  re-judging what is already settled.
- P-05: WHEN a criterion quantifies over N items DO verify each item separately — a file-global grep is
  satisfied by N-1 conforming ones and cannot see the Nth, and a second reader using the same method
  corroborates nothing, it only repeats the measurement.
- P-06: WHEN a review panel returns a finding that would cost a fix cycle DO verify its central premise
  at the pinned base commit first. "This surface is new" is one grep against the approval commit, and a
  finding resting on a false premise buys a cycle for nothing.
- P-07: WHEN a shipped team file is named for a phase DO check it covers every gate the config marks
  blocking before dispatching it — a team missing a blocking step exits the phase with that gate never
  run, and the roll-up still reads PASS.
- P-08: WHEN a plan edits the enforcement layer that governs you DO work out when your own write access
  changes before choosing the turn cadence. Front-load every status write into the last writable
  moment; mid-cluster the plan-before-subcommand rule is unsatisfiable and your digest is the only
  record.
- P-09: WHEN a change moves what a gate DISCOVERS DO compare its output volume against a baseline
  captured before the change. The exit code stops being evidence: a gate whose discovery finds nothing
  passes every check it has, silently.
- P-10: WHEN dispatching distillation to a member DO hand it the paths to its own prior artifacts and
  say self-derived candidates count as its own material. Without that, every entry in its file traces
  to your relay and the acceptance rate grades your dispatch rather than its judgement.
- P-11: WHEN a goal-check returns criteria unmet DO check first whether the behaviour is wrong or only
  unproven. The dominant shape is a criterion enumerating N clauses, shapes or personas with fewer than
  N fixtured — a test-only fix, not a code one, and it routes to a different lane.
- P-12: WHEN a blocking gate's configured command exits non-zero DO re-run it unmodified in a
  clean checkout at the commit under grade before routing the failure. The gate grades a commit, not
  a tree; uncommitted drift outside the graded diff reddens it identically, and measuring at the pin
  excludes nothing.
- P-13: WHEN a criterion pins a measured COUNT or a line ANCHOR taken at the base commit DO expect it
  red at the goal-check with correct delivery behind it. New directories inflate globs and edits move
  lines inside one feature's lifetime. Anchor on content strings instead.
- P-14: WHEN a decision records a two-sided TRADE DO verify both sides landed before accepting the task
  as done. The deferral gets delivered and the delivery dropped, and each task's verify binds only its
  own mechanical form, so every gate stays green.
- P-15: WHEN a gate, a gate's test or a fixture reports green DO check that it CAN report red.
  Reachability and assertion strength are separate from logic and neither is visible in the code you
  are reading, so an all-green verify is not an absent defect.
- P-16: WHEN dispatching a review panel DO name the exact file set to every reviewer and refuse every
  pre-emptive skip — the gating defect lives in the UNION of two lenses' scopes, where each reviewer is
  individually correct and no single one of them can see it.

## Gotchas (max 15)

- G-01: WHEN routing Expertise ops DO check the owner's own domain grant first. The domain hook blocks
  the orchestrator from writing ANOTHER agent's file, but leads and members hold their own with
  `upsert: true` — telling a lead not to self-apply strands its ops with no owner at all.
- G-02: WHEN checking that prose carries a required phrase DO normalise whitespace before counting, and
  mind case. A fixed-string grep returns zero when the phrase spans a wrapped line, which reads exactly
  like missing work and reverses a correct verdict.
- G-03: WHEN a task arrives naming a defect as small housekeeping DO verify the premise on disk and
  refuse on the MERITS with a citation, not on domain alone. Two tells: the target text is
  unspecified so any edit invents approved content, or the file is approval-gated.
- G-04: WHEN reconciling a resume DO diff every digest's `files_touched` against `find` over the feature
  dir, never `git status` — an untracked feature dir shows as one bare `??` line and hides every
  artifact inside it. A digest can be well-formed, hook-passing and still false about its own writes.
- G-05: WHEN a probe returns a plausible value DO confirm the CALL SHAPE matches the function's
  contract before treating it as evidence — a probe that exercises the wrong branch returns a real
  value and is indistinguishable from a measurement.
- G-06: WHEN crossing a phase seam DO write the handoff note even when continuing in the same session
  instead of relaying — the invariant checker reads the phase field and reports a missing seam note as a
  VIOLATION, not as advice.
- G-07: WHEN a lead's digest reports its run finished DO open that run's own state file and treat any
  step with an unset completion time as still live. A digest can be fenced, verdict-bearing and
  premature; re-dispatching over a live run duplicates the work.
- G-08: WHEN a guard rejects a shell command for a redirect DO note that it masks quoted spans
  wholesale, so ANY quoted target blocks — literal or variable, including an approved plan's own
  `verify:`. Re-express it as a script file, and pass commit messages by file.
- G-09: WHEN a dispatch prescribes digest field VALUES DO check the pair against the digest validator
  first, then re-run it on the returned FILE — a re-return after a stop-hook rejection passes through
  unvalidated, so an accepted return is no evidence its artifact is contract-valid.
- G-10: WHEN a dispatch would tell a lead to run a checker DO run it yourself and say so — leads hold no
  Bash, so the instruction returns an unverifiable claim, a forbidden member spawn, or an escalation on
  the contradiction. Hold every mechanical gate at your own tier.
- G-11: WHEN a feature needs a worktree DO create it under `.claude/worktrees/<one-segment>/` inside the
  project root. `check-domain.sh` strips exactly that prefix and matches identical globs; a worktree
  anywhere else escapes the root and the hook RETURNS WITHOUT ENFORCING — a silent fail-open, not a
  block.
- G-12: WHEN a task edits a generated or budget-constrained artifact DO run the whole unit suite, not
  the task's own `verify:`. Length caps and format rules are asserted in test files that no task's
  `verify:` invokes and that the artifact's own header does not state.
- G-13: WHEN deciding which lane may write a path DO run the domain hook on it, once per candidate
  agent type, and read its answer. Reading the org config gives the wrong lane where running the guard
  gives the right one; a path no grant covers routes to layer 0.
- G-14: WHEN a member reports restoring a file it mutated to prove a test fails DO run `git diff` on
  that file yourself before committing. A failed restore is invisible in the diffstat you are reading
  for the file the task was supposed to change, and it commits silently.
- G-15: WHEN a ruling or a handed-down claim quotes a shared file DO re-run the check in the tree you
  are standing in. A worktree sits on the far side of an unmerged seam, so one path gives two answers
  and only one of them governs you.

## Outcomes (max 10)

- O-01: WHEN you believe a reviewer step has nothing to find DO dispatch it anyway and record the
  reviewer's OWN verdict. Both self-scoping reviewers are built to look and decline, and a decline from
  one that looked is a reviewed finding; your prediction of one is not.
- O-02: WHEN an interrupted dispatch left member artifacts on disk while every step still reads
  `pending` DO verify the artifacts' key claims yourself, then re-dispatch the SAME lead with explicit
  assess-not-redo instructions. Never redo the work, never mark another agent's steps complete.
- O-03: WHEN a mission lands on a feature with a brief and plan but no state or feature file DO create
  both — that is the real deliverable when the named asks turn out to be refusals. Budgets come from
  project config, never inherited from another feature.
- O-04: WHEN a plan carries a criterion whose subject no agent domain covers DO carve it out of the
  agent goal-check citing the plan's own precondition, and return it as a named pre-ship step. Handing
  it to a checker returns it unmet and demands a fix cycle routable to no lead.
- O-05: WHEN re-dispatching an agent to apply ops it already recorded DO name the source path and say
  application-not-re-adjudication, and pre-measure anything a cap would force it to condense. Verbatim
  application then costs one spawn, and a drop becomes a reported judgement rather than silent drift.
- O-06: WHEN most of a plan's tasks fall in the layer-0 lane DO return them as dependency-ordered
  SEGMENTS, each task carrying its `verify:` verbatim, and put the tasks independent of the riskiest
  one in the same segment as it — a failure there then wastes none of them.
- O-07: WHEN a panel finds a surface violating an ALREADY-APPROVED requirement DO route it as a fix
  cycle, not as a plan amendment. Approved-but-unmet needs no re-signature; only a criterion that
  cannot be met as written does. Naming which it is settles the routing in one step.
- O-08: WHEN a finding's only remedy would contradict a SIGNED decision DO route it up as a decision
  question with a recommendation and keep the verdict PASS. Dispatching the fix makes a squad amend an
  approved plan without approval, and no fix cycle can legitimately close it.
- O-09: WHEN a task's product is an integration DO invoke the real dependency once yourself before
  accepting a green suite — a fake that cannot model the dimension a defect lives in produces green
  that means nothing.
- O-10: WHEN two read-only segments share no files DO dispatch them in one message, since concurrency is
  free and nothing surfaces the wait — but settle first what happens to one segment's verdict if the
  other's outcome moves the tip, because neither can see that collision.

## Open (max 5)

- OQ-01: A review panel and an orchestrator's own checking have disjoint blind spots. The panel caught
  a signed clause shipped half-built that behavioural checking missed; the same checking caught two
  gates passing while discovering nothing. Three features suggest intent-versus-mechanism, and none has
  run with the panel absent.
- OQ-02: Shared `.harness/expertise/` has no lineage protection. Nothing reconciles a landed diff
  against the plan's declared files, so an undeclared edit to a per-spawn-injected file rides any
  cluster commit and only a human notices. Whether the fix is diff-vs-plan reconciliation, write-guard
  scoping, or keeping Expertise off feature branches is undecided.
