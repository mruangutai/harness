# Expertise — harness-orchestrator

## Patterns (max 15)

- P-01: WHEN metering a run DO diff per-agent `by_agent` cumulatives against the previous run's block,
  never the top-line total, and record the post-run cumulative beside the delta as the next baseline.
  The reporter is project-cumulative and exits 1 on unpriceable models while still emitting.
- P-02: WHEN a resumed feature's runs look complete DO check whether they were PLANTED rather than
  executed before diagnosing anything — the dated log under `.harness/logs/` records fixture staging by
  defect id. Staged runs owe no cost append, and an off-contract digest is then a fixture property,
  not a hook gap.
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

## Gotchas (max 15)

- G-01: WHEN routing Expertise ops DO check the owner's own domain grant first. The domain hook blocks
  the orchestrator from writing ANOTHER agent's file, but leads and members hold their own with
  `upsert: true` — telling a lead not to self-apply strands its ops with no owner at all.
- G-02: Dispatch prompts must not name `.harness/notes/**` as an output path for eng-lead — its domain
  excludes it. Member and reviewer artifacts belong under the path that member's own grant names.
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
  block-form parse. Put comments on the verdict or cost line instead.
- G-08: WHEN a guard rejects a shell command for a redirect you did not write DO look for `>` inside
  quoted or heredoc PROSE — the scan does not respect quoting. Pass commit messages by file, and write
  any prose containing angle brackets with the file-write tool rather than a heredoc.

## Outcomes (max 10)

- O-01: WHEN the design pass rules no end-user interaction and no design contract exists DO skip the
  ui-reviewer step and record the skip with its rationale — there is nothing to review and the reviewer
  self-scopes out at the cost of a spawn. The same rationale retires the post-build ui audit.
- O-02: WHEN an interrupted dispatch left member artifacts on disk while every step still reads
  `pending` DO verify the artifacts' key claims yourself, then re-dispatch the SAME lead with explicit
  assess-not-redo instructions. Never redo the work, never mark another agent's steps complete.
- O-03: WHEN a mission lands on a feature with a brief and plan but no state or feature file DO create
  both — that is the real deliverable when the named asks turn out to be refusals. Budgets come from
  project config, never inherited from another feature.
- O-04: WHEN a plan carries a criterion whose subject no agent domain covers DO carve it out of the
  agent goal-check citing the plan's own precondition, and return it as a named pre-ship step. Handing
  it to a checker returns it unmet and demands a fix cycle routable to no lead.

## Open (max 5)

- OQ-01: Relayed distillation candidates were accepted at near 100% across six members in one feature.
  Good sourcing and a member treating relay as instruction look identical in one sample; a second
  feature with zero rejections means the relay has become dictation.
