# Observations — harness-orchestrator — FEAT-10-software-factory

- 2026-08-08: The DELTA re-review after a fix cycle paid for itself twice over and cost ZERO
  cycles (DEC-157: a first-pass run that PASSes adds nothing). eng-lead's delta answered the
  blocking Q5 by *premise failure* — there is no per-task qa gate at all (`build.yaml:36-37`),
  so the ordering worry was void and no plan change was needed — and found MF-D1, a T-10 intent
  block that contradicted its own `verify`. validator's delta found MF-2 was never actually
  closed. I nearly skipped both rounds on cycle-budget grounds; the budget argument was wrong,
  because a passing delta is free and the alternative was editing an artifact after signature.

- 2026-08-08: Scoping a delta dispatch with an explicit LEAVE LIST plus "your previous run spent
  ~122k tokens, this one should not" held both leads to ~92k with sharper findings. The LEAVE
  list did the work — every item on it came back untouched and neither lead re-derived the DAG.

- 2026-08-08: Two reviewers' unverified premises both resolved WORSE than they guessed when I
  probed them. `gh project item-list`: board 3 already held 150 items against a planned
  `--limit 200`, closed issues persist as items, and the payload has no `state` key. That
  reversed the fix from "paginate" to a server-side query filter. Probing beat relaying.

- 2026-08-08: A question can VANISH between segments and no gate notices. eng-lead's first-pass
  Q2 asked to pin the `field-list` JSON shape; it appeared in no later digest, no STATE.md entry
  and no handoff line, and I only caught it re-reading the first digest at close. Running it took
  one command and found that board 2's Status options cannot satisfy DESIGN.md's one-word station
  rule while board 3's can — which converted the riskiest operator answer into a pick-from-list.
  Unioning `open_questions` upward is not enough; they need a carried ledger across segments.

- 2026-08-08: `dispatch-guard.sh` rejected a `model: opus` parameter on my first lead dispatch.
  The model pin is org design (DEC-152) and a dispatch-time override is an ESCALATION, not an
  option. Re-dispatching without the parameter was the whole fix.

- 2026-08-08: Both plan-time leaf reviews converged INDEPENDENTLY on the same root defect (the
  claim was not atomic) from different lenses — architecture and design contract. That
  convergence is what made the revision non-negotiable rather than a debate, and I said so in
  the fix dispatch. Later, two reviewers inside the validator squad converged on MF-2 the same
  way. Convergence from different lenses is the strongest signal available at plan time.

- 2026-08-08: Mission plan makes `check-state.sh` exit 1 for the whole session — INV-1 treats an
  unapproved BRIEF as a VIOLATION, not a warning. Expected and unavoidable; worth disclosing in
  the return so nobody reads a red board as a defect.

- 2026-08-08: The map's decisions were the SPEC of the thing being built, not process rules for
  the planning run. I put that distinction at the top of the pm dispatch with three named traps
  (#196 task format, #197 dispatch memos, #192 seats). Nobody applied a target-state rule to
  their own method. Worth repeating verbatim on any effort-to-feature handoff.

- 2026-08-08: A LEAD OVERRODE MY SUGGESTED CRITERION AND WAS RIGHT. I handed pm a day-one example
  as the enforcement test — twelve tasks at ready, claim an unblocked root, never T-12. It goes
  GREEN against a blocker-ignoring tool, because candidates sort by issue number ascending and
  T-01 is itself an unblocked root. The lead replaced it with: make the LOWEST-numbered candidate
  the blocked one and assert which issue the create call was made for. Lesson: when I propose a
  criterion, I am proposing a test, and a test I have not tried to defeat is a suggestion, not a
  spec. Hand the RULE and let the squad write the falsifier.

- 2026-08-08: The same defect found INDEPENDENTLY by two leads from different angles is the
  strongest signal available at plan time, and it happened three times here — the non-atomic
  claim (arch + design contract), MF-2's false point-of-no-return (ui + code reviewer), and the
  step-5b missing stderr reason (eng must_fix + validator Q3). Each time I stopped weighing and
  routed the fix. Convergence from different lenses is worth more than either lens's confidence.

- 2026-08-08: A REVIEWER'S OWN LEAD CAUGHT WHAT THE REVIEWER PASSED. The code-reviewer returned
  PASS on "does SC-22 falsify un-enforcement"; its lead then found no case gave any candidate a
  MIXED blocker set, so a depends_on[0]-only tool passed all six cases while T-12 has six
  blockers. The lens tested whole-behaviour substitutes and never a PARTIALLY correct one. When
  a dispatch names one question as the one that matters, expect the answer to need the lead's
  own pass on top of the member's.

- 2026-08-08: Probing beat relaying a third and fourth time, and both reversed a stated premise.
  Re-POSTing an existing blocked_by edge returns 422, which made E-1 a real deterministic wedge
  rather than a hypothetical; a repeat sub_issues attach returns a 422 that CONFLATES two causes,
  which proved the conservative scoping right rather than merely cautious. Both were declared
  unmeasurable by the squad that raised them ("leads have no shell"). If a finding turns on a
  fact and I hold Bash, the measurement is mine and it is cheap.

- 2026-08-08: Rulings arrived mid-flight FIVE times, twice while a dispatch was already running.
  Folding each into ONE consolidated cycle rather than starting a cycle per ruling kept the
  budget at 8 of 10 across an amendment that deleted a criterion, enforced a new behaviour and
  rewrote every requirement. The cost of a separate cycle per ruling is a full lead round-trip
  each; the cost of folding is one longer dispatch prompt.

- 2026-08-08: I nearly duplicated a rule the main session had already written. A late scope
  correction moved the plain-English rule from harness-brief to harness-handoff and said so
  explicitly. Verifying it had landed took one grep; writing it again would have created exactly
  the two-copies drift the correction existed to prevent. Verify-then-skip beats assume-and-write.

- 2026-08-09: I WROTE A REPAIR DISPATCH AGAINST TOOLS THE ADDRESSEE DOES NOT HOLD. I told
  validator-lead "do both yourself, no member spawns needed" and then demanded three exit codes —
  but leads hold no Bash, and one of the two target paths was qa's write domain, not the lead's.
  Both bounds forced the very member spawn I said was unnecessary, and the lead had to raise it as
  a defect in my dispatch. Before writing "do it yourself" to a lead, check the tier's tool grant
  and the target path's domain owner; a lead can Read and route, it cannot measure.

- 2026-08-09: A BLOCKED gate that turns out to be a CONFIG defect costs ZERO cycles to re-run, and
  saying so explicitly in the dispatch stopped the lead from padding. DEC-157 counts rework — work
  redone because someone produced a bad artifact. Nobody did here: the matrix bound a kind that
  could not run, the operator fixed the config directly, and the re-run was a first pass against
  corrected config. Naming the reason in the dispatch also stops the lead reporting a defensive 1.

- 2026-08-09: A LEAD DIGEST CAN PASS THE SUBAGENT HOOK AND STILL FAIL check-state. The panel digest
  reported PASS over two member FAILs; the hook let it through at return time and only the
  standalone `validate-digest.py lead` sweep caught it, days later. The repair is the roll-up field
  alone and it changes no finding — but it changes what a successor reads, so it must be paired
  with an explicit "this gates nothing, do not start a fix loop" note or the correction manufactures
  the cycle it was supposed to prevent.

- 2026-08-09: MY OWN STATE.md WRITE INTRODUCED A VIOLATION THAT DID NOT EXIST BEFORE. I wrote the
  literal placeholder `T-NN` in prose ("absent T-NN issues are not a defect") and check-state read
  it as a reference to a task absent from plan.yaml. Re-running check-state AFTER my own write, not
  just after the squad's, is what caught it. Placeholder task ids do not survive contact with the
  state checker — spell the concept out instead.

- 2026-08-09: THREE OF FOUR INHERITED "COMMIT TRAPS" IN MY OWN PREDECESSOR'S STATE.md WERE STALE,
  and I nearly relayed all four verbatim into a return that framed the commit as non-mechanical.
  Four commands settled it: the branch was already cut (`git rev-parse --abbrev-ref HEAD`), the two
  "staged deletions" were committed (`git diff --cached` empty), the OMP stream was committed, and
  check-state.sh's "unsplittable foreign dirt" was ONE hunk of 52 additions opening "INV-24" — the
  feature's own work. Git-state claims rot faster than any other kind in STATE.md because every
  commit invalidates them silently, and STATE.md is superseded-not-appended so nothing flags the
  rot. Re-derive every git claim at HEAD before relaying it, however confident the predecessor was.

- 2026-08-09: THE DOMAIN HOOK CORRECTLY DENIED ME MY OWN RED-PROOF. I tried to `cp` a production
  file to the scratchpad to reproduce a member's red demonstration myself; bash-write-guard blocked
  it as guardrail evasion (DEC-151), which is right — an orchestrator that can stage writes under
  `bin/` via the shell has no domain. The substitute is a STATIC read of the assertion: the test
  compares `pid == "PVT_kwFAKE" and pid != "3"` against board number 3, so it excludes the buggy
  value by construction and cannot be vacuous. I can verify a red's DISCRIMINATING POWER by reading
  the predicate even when I cannot execute the mutation. Disclose which of the two I did.

- 2026-08-09: AN OPERATOR'S NAMED GAP LIST CAN DISAGREE WITH THE ARTIFACT IT CITES. The dispatch
  named three SC-19 clauses "each named by pm's goal-check", but two of the three were already
  asserted at `test-factory-integration.py:643-644` and `:684-685`, both predating the digest by an
  hour (file mtime 10:00, digest 10:59). Closing the named list would have shipped SC-19 still
  partial. The citation outranks the paraphrase: I substituted pm's three actually-unbound clauses,
  disclosed the swap with line cites, and did not spend a round-trip asking. Check a named gap
  against the artifact cited for it before dispatching — a paraphrase slip is invisible downstream.
