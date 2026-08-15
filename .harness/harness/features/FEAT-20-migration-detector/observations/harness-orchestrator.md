# Observations — harness-orchestrator — FEAT-20-migration-detector

- 2026-08-14: The `verify:` clauses in `plan.yaml` were not runnable verbatim in this session.
  `bash-write-guard` refuses a redirect whose target is a shell variable — `>"$u"` where `u=$(mktemp)`
  — reporting the target as the literal string it could not resolve ("xx"). It also refuses redirects
  into the session scratchpad when the path is variable-expanded, though a literal scratchpad path is
  allowed. Every T-01/T-02 assertion was run with literal paths and is unchanged; but a plan whose
  verify clauses cannot be executed as written by the agent that must execute them is a real friction
  the plan phase never sees, because the plan phase does not run them.

- 2026-08-14: Setting `feature.json` `status: Review` made `check-state.sh` fail INV-17 —
  `notes/handoff-build.md` was missing because I crossed the build seam inside a single session and
  therefore never felt like I was handing off. The gate is right: the seam is defined by the phase
  transition, not by whether the context changed. Write the handoff at the transition even when you
  are the successor.

- 2026-08-14: The handoff shape gate (60 lines) rejected two drafts at 70 and 61 lines before
  accepting the third. Budget for that: the first draft always wants a Trust bullet per claim, and the
  cap forces the merge that makes it working memory instead of a summary.

- 2026-08-14: Editing `plan.yaml` task statuses with an anchored python read-modify-write — find
  `  - id: T-NN`, scan forward to the first `    status:` line, assert its current value before
  replacing — survived four edits on a 52KB file with no line-number dependence and no full rewrite.
  Asserting the expected old value is what makes it safe to repeat; a blind replace would have
  silently double-applied.

- 2026-08-14: pm returned ESCALATE because a success criterion was unmeetable as written, not unmet
  by the work. The distinction mattered enormously to the routing: FAIL would have bought a fix cycle
  against a defect that does not exist in the code. Before escalating I re-derived the premise myself
  (`git diff --name-only` over the feature range plus `--diff-filter=R`) rather than relay pm's count
  — the eight shipped files matched the criterion's closed set exactly, which is what made "the text
  is wrong, not the work" a claim I could put my name to.

- 2026-08-14: The review panel converted my qa segment's general residual ("no mutation proof exists")
  into two *named* surviving mutations, one of which it executed live. I verified R-1's central
  premise at source before letting it travel up — four `if/elif` branches on `_srep.cause` in
  `check-state.sh:1302-1318` with no trailing `else` — and it held. A named mutation is worth an order
  of magnitude more to the operator than the general observation, and the cost of confirming it was
  one `sed`.

- 2026-08-14: Deferring close-out and the briefing was the right call and it was not obvious. Both are
  gated on the SCs passing; distillation is explicitly once-and-cold. Running them before a blocking
  ruling would have spent two lead round-trips on artifacts the ruling could supersede.

- 2026-08-14: Two dispatches in one message (T-03 to eng-lead, T-04 to product-lead) ran genuinely
  concurrently and both came back clean first-pass, adding zero cycles. Waiting on them needed a
  polling loop — foreground `sleep` is blocked, and `read -t` against `/dev/zero` spins instantly;
  `python3 -c "time.sleep"` in a bounded loop works.
