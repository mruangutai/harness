# Expertise — harness-orchestrator

## Patterns (max 15)

- P-02: WHEN a resumed feature's runs look complete DO check whether they were PLANTED rather than
  executed before diagnosing anything — the dated log under `.harness/logs/` records fixture staging by
  defect id. An off-contract digest is then a fixture property, not a hook gap.
- P-03: WHEN a plan cites a line number inside `feature.yaml` DO treat the anchor as already rotten and
  cite the FIELD instead — the orchestrator rewrites that file every run, so nobody can keep the
  reference true.
- P-04: WHEN dispatching a fix DO pass the discriminating RULE plus an explicit LEAVE list rather than a
  survey of sites. The LEAVE list does the work: unnamed near-misses are where a member spends a spawn
  re-judging what is already settled.
- P-05: WHEN a fix task names N sites carrying a defect DO grep the behaviour word across brief and plan
  yourself first — the count is habitually low, and the two layers a site list forgets are the
  REQUIREMENT and the verification CRITERION, which would otherwise go green on wrong prose.
- P-06: WHEN a review panel returns a finding that would cost a fix cycle DO verify its central premise
  at the pinned base commit first. "This surface is new" is one grep against the approval commit, and a
  finding resting on a false premise buys a cycle for nothing.
- P-07: WHEN a shipped team file is named for a phase DO check it covers every gate the config marks
  blocking before dispatching it — a team missing a blocking step exits the phase with that gate never
  run, and the roll-up still reads PASS.
- P-08: WHEN a narrowing conditional is added anywhere DO require a guard assertion for the over-scoped
  version of it, emitted inside the case that version would suppress. Before the branch existed there
  was nothing to over-scope, so the fix's own tests are the only place it is catchable.
- P-09: WHEN checking that a prose clause landed in a wrapped file DO flatten whitespace before
  matching. A line-wise grep cannot see across a wrap: it false-negatives a correct edit and
  false-negatives a prose-correct fix whose wrap splits the counted tokens. Both buy cycles for nothing.
- P-10: WHEN dispatching distillation to a member DO hand it the paths to its own prior artifacts and
  say self-derived candidates count as its own material. Without that, every entry in its file traces
  to your relay and the acceptance rate grades your dispatch rather than its judgement.
- P-11: WHEN a goal-check returns criteria unmet DO check first whether the behaviour is wrong or only
  unproven. The dominant shape is a criterion enumerating N clauses, shapes or personas with fewer than
  N fixtured — a test-only fix, not a code one, and it routes to a different lane.
- P-12: WHEN a criterion or a `verify:` clause sweeps for a removed concept DO grep the plain English
  word too, over every file type in scope. Compound-token patterns are blind to prose that names the
  thing without spelling it, so an all-green clause is not an absent defect.
- P-13: WHEN a criterion pins a measured COUNT or a line ANCHOR taken at the base commit DO expect it
  red at the goal-check with correct delivery behind it. New directories inflate globs and edits move
  lines inside one feature's lifetime. Anchor on content strings instead.

## Gotchas (max 15)

- G-01: WHEN routing Expertise ops DO check the owner's own domain grant first. The domain hook blocks
  the orchestrator from writing ANOTHER agent's file, but leads and members hold their own with
  `upsert: true` — telling a lead not to self-apply strands its ops with no owner at all.
- G-02: Dispatch prompts must not name `.harness/notes/**` as an output path for a lead or a
  documentor — their domains exclude it. Member and reviewer artifacts belong under the path that
  member's own grant names; a member with no such grant writes to its observations log.
- G-03: WHEN a task arrives naming a defect as small housekeeping DO verify the premise on disk and
  refuse on the MERITS with a citation, not on domain alone. Two tells: the target text is
  unspecified so any edit invents approved content, or the file is approval-gated.
- G-04: WHEN reconciling a resume DO diff every digest's `files_touched` against `find` over the feature
  dir, never `git status` — an untracked feature dir shows as one bare `??` line and hides every
  artifact inside it. A digest can be well-formed, hook-passing and still false about its own writes.
- G-05: State-file caps are PreToolUse BLOCKs and the only write tool is whole-file, so every overrun
  costs a redraft rather than an edit. Draft a seam handoff at ~50 lines against its 60 cap and the
  state file at ~105 against its 120; fixed headers and blank lines eat the rest.
- G-06: WHEN crossing a phase seam DO write the handoff note even when continuing in the same session
  instead of relaying — the invariant checker reads the phase field and reports a missing seam note as a
  VIOLATION, not as advice.
- G-07: A run dir's squad suffix must match the owning lead's domain glob exactly, and a trailing
  comment on a run entry's `squad:` line silently drops that run from the invariant checker's
  block-form parse. Put comments on the verdict line instead.
- G-08: WHEN a guard rejects a shell command for a redirect you did not write DO look for `>` inside
  quoted or heredoc PROSE — the scan does not respect quoting. Pass commit messages by file, and write
  any prose containing angle brackets with the file-write tool rather than a heredoc.
- G-09: WHEN a dispatch prescribes digest field VALUES DO check the pair against the digest validator
  first, then re-run it on the returned FILE — a re-return after a stop-hook rejection passes through
  unvalidated, so an accepted return is no evidence its artifact is contract-valid.
- G-10: WHEN a dispatch would tell a lead to run a checker DO run it yourself and say so — leads hold no
  Bash, so the instruction returns an unverifiable claim, a forbidden member spawn, or an escalation on
  the contradiction. Hold every mechanical gate at your own tier.
- G-11: WHEN writing a summary value into a state file DO quote any scalar containing a colon followed
  by a space. A verdict line is the natural place to write one, `safe_load` raises at that column, and
  the file was valid one write earlier.
- G-12: WHEN a task edits a generated or budget-constrained artifact DO run the whole unit suite, not
  the task's own `verify:`. Length caps and format rules are asserted in test files that no task's
  `verify:` invokes and that the artifact's own header does not state.
- G-13: WHEN deciding which lane may write a path DO run the domain hook on it, once per candidate
  agent type, and read its answer. Reading the org config gives the wrong lane where running the guard
  gives the right one; a path no grant covers routes to layer 0.

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

## Open (max 5)

- OQ-01: A review panel and a human diff read have disjoint blind spots: the panel caught a rotted
  in-file anchor the human read passed over, while the human ruled on intent the panel could not. Two
  features suggest the split is route-versus-coverage, but neither has been run with the panel absent.
- OQ-02: Every reviewer followed its instructions and scoped its sweep to files the diff touches; every
  surviving violation lived in files it does not. The gap was a property of the UNION of the scopes,
  not of any one lens. Unclear whether widening a scope or adding a lens closes it.
