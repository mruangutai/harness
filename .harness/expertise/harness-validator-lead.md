# Expertise — harness-validator-lead

## Patterns (max 15)
- P-01: WHEN a member's cited anchors drift from source DO republish the lines you measured and
  keep its mechanism — drift of several lines coexists with exactly-correct reasoning, so
  re-measure rather than discount, and never promote an unverified anchor into your digest.
- P-02: WHEN ranking advisory findings for a backlog DO order by irreversibility before
  severity — a low-severity defect whose failure cannot be undone outranks a medium that is
  cheaply reversible, and no member can see that axis from inside its own lens.
- P-03: WHEN a coverage gate returns green DO establish how many of the changed units it actually
  bound before reporting it as assurance — a gate can be correct and near-vacuous at once, and
  "the gate is satisfied" is not the claim "the change is tested".
- P-04: WHEN a defect class is named anywhere in a feature — by a member or by you — DO sweep the
  surface for further instances before closing the next gate on it; your own earlier finding is
  the one nobody thinks to re-sweep.
- P-05: WHEN relaying candidates into a member's distillation DO carry only cross-member and
  lead-tier findings — a member independently derives everything its own note already holds
  before it reads the relay, so recalling that back contributes nothing and wastes half the
  relay.
- P-06: WHEN two reviewers each return PASS on adjacent mechanisms DO check each one's mechanism
  against the criteria the other verified — the gating defect lives in the union of the scopes,
  and no member is positioned to call it from inside its own lens.
- P-07: WHEN dispatching a review panel DO hand the file set down explicitly rather than let each
  reviewer self-scope — self-chosen scopes leave the seams between them uncovered, and the seam
  is where the gating defect sits.
- P-08: WHEN you have verified at source that the code does X DO treat that as a different claim
  from "something holds it to X" and require a mutation before calling the seam closed — correct
  today and pinned against regression are separate findings, and only the second survives an edit.
- P-09: WHEN a panel returns few or no findings DO record in your adequacy notes that this cannot
  distinguish a clean diff from a shallow pass, and name which reviewers produced falsification
  evidence — a mutation or equivalent probe is the only discriminator available to you.
- P-10: WHEN carrying a task's verify clause verbatim DO also establish which command the coverage
  gate itself rests on — the configured per-kind command can be strictly broader than the task's
  own clause, so a faithful carry can satisfy the task and still not be what makes the gate true.
- P-11: WHEN a dispatch hands down an equivalence, count or SHA relation you cannot check
  without a shell DO fold the measuring command into a member's step rather than relay it — a
  lead with no shell either routes the measurement or publishes an assumption.
- P-12: WHEN a review panel is pinned before the work is committed DO name which criteria assert a
  landed shape and mark them unclearable by any reviewer — reading the working tree still buys
  real findings, but no pre-commit verdict is complete.
- P-13: WHEN a change moves what a gate DISCOVERS DO require a reported non-zero discovery count
  before accepting its exit code — a sweep over an empty set exits 0 exactly like a clean sweep,
  and no fixture binds the real tree.
- P-14: WHEN a sweep for a defect class returns zero or a small count DO first confirm the pattern
  matches a known positive instance — a pattern anchored on a detail the real instances lack
  reports an absence indistinguishable from cleanliness, and your own sweep is the one nobody
  re-runs.

## Gotchas (max 15)
- G-01: WHEN the blocking gate passes and an advisory gate carries the only defect DO headline
  both — which gate blocks says nothing about which gate finds things, and a digest headed by the
  passing gate reads one tier up as clearance.
- G-02: WHEN recording a run metric or a verified fact DO put it in the digest and a one-line step
  note — the run state's top-level allowlist is closed and rejects an invented key even when its
  value is a bare integer, not prose.
- G-03: WHEN every gate returns green DO establish which routes actually reach each gate and
  whether each fixture can fail — logic can be correct while reachability is wrong, and neither
  is visible to anyone reading the gate's own code.
- G-04: WHEN your own finding names N instances DO run the discriminating test on each one
  separately — a vacuity claim is a substring claim, and reading the first message then
  generalising to its siblings produces a remedy that is half unwarranted.
- G-05: WHEN a dispatch hands you a count, a premise or a figure DO re-derive it from the
  artifacts before building on it — narration is the least reliable input you receive, and in a
  distillation dispatch a wrong count loses a lesson permanently, since Expertise is written once.
- G-06: WHEN a member's role field carries a placeholder you would not have chosen DO check the
  digest validator's per-persona table before recording a convention mismatch — a scoped-out
  reviewer's `n/a` is the sanctioned spelling there, not drift.
- G-07: WHEN narrating a member's conduct or re-rating its finding DO re-read the passage and
  quote its words in that sentence — a completion notification is not the content, and an
  artifact read earlier then recalled is how a false claim about a member enters a signed
  record.
- G-08: WHEN the work lives in a worktree DO check the worktree prefix on every read path before
  using the result — the main checkout holds a stale copy at the identical path, and a conclusion
  drawn from it is wrong in exactly the way that looks right.
- G-09: WHEN relaying a handed-down candidate that characterises a member's conduct DO check it
  against that member's own artifact first — the account reaching you is a hypothesis, and a
  member forced to reject a false premise spends its distillation slot on your error.
- G-10: WHEN a member reports a signed criterion met under a narrowed reading DO record the
  literal status and the reading as two findings and route the reading up — endorsing it adopts
  an approval-gated decision, and the tier owning the goal can reject the reading outright.
- G-11: WHEN a signed decision records a two-sided trade DO verify the delivery half at source
  rather than from the task's status or its verify — each verify binds only its own mechanical
  form, so the deferral can ship while the delivery is dropped with every gate green.
- G-12: WHEN a dispatch states which capabilities or grants a member holds DO check the manifest
  and the agent definition yourself before routing around them — a routing branch built on an
  assumed missing capability spends your spawn on work its owner could have applied directly.
- G-13: WHEN two members return apparently contradictory answers to a probe you assigned DO check
  whether your question was direction-dependent before adjudicating either — a question with two
  correct answers reads as a contradiction, and the defect is in your dispatch rather than in
  either member.
- G-14: WHEN a plan's verify clauses are the evidence a gate rests on DO exercise each as an
  artifact in its own right — that it can fail, that it can pass, and that no later commit
  falsified the word it greps.

## Outcomes (max 10)
- O-01: WHEN dispatching a review panel DO name the already-ruled items in the prompt —
  pre-briefing suppressed every re-discovery without suppressing new probing, so it buys back
  reviewer attention at no cost to independence.
- O-02: WHEN a distillation round returns zero member rejections DO check your own relay before
  distrusting it — a lead that filtered already-covered or false candidates pre-relay produces
  zero legitimately, so record your pre-relay rejections beside the members'.
- O-03: WHEN a reviewer self-scopes out DO require the census or object check it actually measured
  before crediting the decline — a decline that looked survives cross-review, one that predicted
  absence does not, and only the first is evidence.

## Open (max 5)
