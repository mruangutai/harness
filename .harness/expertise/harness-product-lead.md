# Expertise — harness-product-lead

## Patterns (max 15)
- P-01: WHEN a dispatch hands you a finding as near-certain DO verify its central premise at source
  before relaying it — pre-argued framing is the least trustworthy input a lead receives, and one
  grep can overturn what two tiers already accepted.
- P-02: WHEN assessing a member's cited evidence DO open at least one cited line rather than
  counting them — a pointer can be sound while the prose gloss of it is wrong, and a pointer's
  whole value is that it survives being opened.
- P-03: WHEN the member who owns a gate decision was skipped DO make that call yourself and report
  it as overridable in either direction — a gate nobody fired is indistinguishable in the record
  from a gate that passed.
- P-04: WHEN relaying a distillation candidate DO grep the member's OWN prior artifacts for it, not
  only what it carries at spawn. A candidate restating a member's own note is graded as its
  material, and its acceptance rate then measures your relay rather than the lesson.
- P-05: WHEN a dispatch hands you an enumerated set of sites DO re-run the enumeration yourself with
  a wider pattern before dispatching — until it is re-run wide the set is a sample, and a
  pre-measured baseline makes the post-edit check sound by construction rather than by report.
- P-06: WHEN a task offers the member a choice between two remedies DO check at your own tier
  whether one is already foreclosed and encode the survivor as a hard constraint — a member spawn
  spent discovering the option was never available buys nothing.
- P-07: WHEN a member reaches your own verdict by a different route DO adopt the more durable route
  as the record and say the two differed — agreement on the verdict hides that one footing is
  disputable and the other is structural.
- P-08: WHEN a dispatch hands you an exclusion list or a disjoint-file-set claim DO re-derive it
  from the other artifact it describes, not from the list itself — it is a claim about a document
  only this tier opens, and a member honouring it exactly still collides.
- P-09: WHEN a member reports N clauses balanced against N fixtures DO recount the clauses against
  the task's own intent prose, not against the fixture map — a count taken from the criterion's own
  wording is self-consistent and still short of what the task forbids.
- P-10: WHEN your dispatch names an output path for a member DO check it against that member's own
  domain grant first — a role owning a named per-feature artifact is exactly the one the receipt
  convention does not cover, and the guard denies the dispatched path correctly.
- P-11: WHEN a member re-anchors a stale citation set DO count the clauses each pointer covers
  before and after, not merely their currency — a thinner-but-current pointer that folds two
  clauses onto one head silently deletes evidence, and it rides in on the fix for staleness.
- P-12: WHEN a handed-down constraint carries its own justification DO check what that justification
  is ABOUT against what the constraint claims — a reason naming one tool's reading scope says
  nothing about what breaks at runtime, and a rationale contradicting its own constraint settles
  the question with no new evidence.
- P-13: WHEN you are about to credit your own tier with seeing something first DO grep the member's
  artifact for it before the claim is filed. A finding the member raised and declined to act on
  reads like one it missed, and the digest is what the record keeps.
- P-14: WHEN checking whether a member folded your instructions in DO grep for the fact each names —
  the cited line, the identifier — never your own wording. A member writes its own prose but carries
  the anchor verbatim, so a phrasing-grep reports absent what is there.
- P-15: WHEN two constraints you read separately could contradict DO compose them against each
  other before dispatch — reading both halves of a contradiction is not checking them, and the
  composition is where an unsatisfiable gate hides from every reader who saw only one half.

## Gotchas (max 15)
- G-01: WHEN a test name or label is offered as evidence DO read the invocation it wraps — labels
  are consumed downstream as measurements, so a label that misdescribes its own test propagates as
  if it were one.
- G-02: WHEN two agents contradict each other about repo state and settling it needs a clock or git
  history DO name both possibilities and route it to the tier holding the commit pen — without a
  shell this tier cannot tell stale from wrong.
- G-03: WHEN writing your run state.yaml DO put every value inside a step entry and add nothing new
  at top level — the guard rejects any unrecognised top-level key, including a bare counter, not
  merely the prose the rule text names.
- G-04: WHEN a member reports a harness defect DO read the governing rule file at HEAD before
  relaying it up — a rule amended since the member's habit formed turns the report into a stale
  escalation the tier above cannot close.
- G-05: WHEN spot-checking a member's `file:line` evidence on a worktree feature DO confirm the path
  you read resolved inside the worktree — your cwd is the main checkout root by construction, so the
  same relative path returns a pre-feature copy with unrelated content at the same line numbers.
- G-06: WHEN a member reports a cycle count DO recount it as send-backs you yourself issued and
  check what the tier above already charged — a member cannot see another squad's rework, so an
  inherited cycle gets double-counted against the feature budget.
- G-07: WHEN a fix cycle lands a commit after a goal-check DO re-check the criteria graded met at
  the earlier commit, not just the one the cycle targeted — those grades are stale, not wrong, and
  a criterion constraining commit shape is falsified by the very commit that closed another.
- G-08: WHEN a member's output appears to be missing a standard artifact DO check which role's
  domain owns that path before flagging it — a file another tier creates at a later stage is
  indistinguishable on disk from an omission, and the member cannot create it at all.
- G-09: WHEN two records report different numbers under one label DO compare the invocations that
  produced them before calling either drift — differing commands make agreement and disagreement
  equally uninformative, and a spelling or exclusion gap is settleable without a shell.
- G-10: WHEN a fix you are about to route will move the commit a gate is currently running against
  DO sequence the fix and re-pin before accepting that gate's verdict — a concurrent panel's PASS
  covers the tree it started on, and neither party sees the collision.
- G-11: WHEN grepping for an anchor phrase inside a YAML block scalar or hard-wrapped prose DO
  search one distinctive token rather than the multi-word phrase — a line wrap splits the phrase
  across two physical lines, and grep then reports ABSENT what is present and correctly written.
- G-12: WHEN a grep over your own run directories returns zero DO confirm the tool honours ignore
  rules before calling it absent — run state is commonly gitignored as ephemeral, and a
  ripgrep-backed search silently reports nothing over exactly the artifacts your tier verifies.
- G-13: WHEN a dispatch names one digest by path DO enumerate the run dir before quoting from it —
  concurrent passes write sibling filenames rather than overwriting, so a run dir is not guaranteed
  to hold exactly one, and findings in the sibling reach nobody.

## Outcomes (max 10)
- O-01: WHEN a cosmetic defect sits in a file a human is already about to open DO fold it into that
  pass rather than spending a member spawn — rework at this tier costs one spawn, the same rework
  after routing costs a cycle.
- O-02: WHEN a member's receipt disagrees with the artifact it wrote and the artifact is correct DO
  rebuild the receipt from the file and state in your digest that you did — a re-spawn over a
  report-only defect is waste, and normalising it silently is the worse error.
- O-03: WHEN a member's displacement choice during distillation looks arguable DO record the
  reservation and let it stand — the judgment is the member's by rule, and a send-back over one
  entry costs a spawn to overturn a call you were not given.
- O-04: WHEN dispatching a member on a remedy you have already endorsed DO require it to say why
  with evidence rather than adopt deferentially — an overturn arriving with primary-source evidence
  costs one return, and a deferential pass costs the cycle that discovers the remedy was wrong.

## Open (max 5)
