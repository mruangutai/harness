# Operator answers — adversarial plan panel at 73898a3 — 2026-08-29

Written by the main session. **ONE consolidated revision covers everything below.** The panel was
three independent readers dispatched against the SIGNED plan: `fable-advisor` (TRIM),
`harness-pm` goal-check (ESCALATE), `scout` scope hunt (one LOW defect). Their artifacts:

- `notes/review-fable-advisor-plan-73898a3.md`
- `notes/research-FEAT-38-goalcheck-plan-73898a3.md`
- scout's note was **never written** — that persona is read-only with no write tool, so its content
  exists only in its return. Treat `history://Feat38ScopeHunt` as the source; do not cite a path.

The plan is SIGNED at `ec05940`. This revision REOPENS it, so the signature is withdrawn again on
dispatch and re-taken by the main session afterwards.

## Must fix

- **F1 (high) — T-24's blast-radius sweep is unsatisfiable at its own completion.** Reproduced by the
  main session, clause run verbatim in the worktree: 5 matches, exit 0, so the verify's
  "references survive" branch fires and T-24 exits 1. The live blocker is `.harness/harness.json`,
  whose cleanup is **T-25, which `depends_on: T-24`** — a cycle under the plan's own completion-time
  evaluation model. `DECISIONS.md` is NOT the problem: T-24 already depends on T-27.
  **Fix: add `:!.harness/harness.json` to T-24's sweep pathspec**, or move the unscoped sweep to
  T-25's verify. pm chooses; the first is smaller.
  Also correct T-24's intent, which claims this sweep is "the only thing that proves no sixth
  reference site exists" — false. SC-14's third assertion is the identical sweep graded at
  `review_sha`.

- **F2 (blocking escalation) — SC-11's re-grade reaches FIVE entries, not six.** DEC-205 is not in
  SC-11's set and has no pre-fold form, so DEC-205's marker-adjacent paragraph
  (`DECISIONS.md:6293-6299`) would go ungraded by both SC-11 and SC-16 as written.
  **OPERATOR RULING: extend SC-16 to cover that paragraph**, and state SC-11's set as the five
  entries it actually reaches. Chosen over accepting an ungraded paragraph because SC-16 already owns
  DEC-205's counting sentences, so this is coverage added without a new criterion.

## Should fix, in the same revision

- **F3 (med) — REQ-10 vs the recorded Destination.** The grilling note promises "no remaining script
  that builds a command line from document or config text"; signed REQ-10 delivers sweep-and-name
  with remediation explicitly out of scope. A non-empty `TEXT-DERIVED-ARGV` result from T-29 would
  satisfy the brief while missing the destination, which is a ship-review bounce waiting to happen.
  One reconciling sentence. The signature already endorses REQ-10's conditioning — do NOT widen the
  requirement, reconcile the wording.

- **F4 (med) — SC-17 names no inspector, and its verify grades FORMAT, not truth.** T-29's per-file
  verdicts are a subprocess-provenance judgement; the mechanical verify checks that rows exist with a
  non-empty rationale. A mislabelled `FIXED-LITERAL-ARGV` passes every gate and signs a false clean
  bill. **No plan-structure change: route SC-17's inspection to a code-reading persona**
  (`harness-code-reviewer` or `harness-backend-dev`) rather than leaving it with the author of the
  table.

- **F5 (low) — SC-15 is carried in no task's `traces`.** The plan's own convention is explicit
  elsewhere ("the grader looks for the id here"): SC-14 -> T-24, SC-16 -> T-28, SC-17 -> T-29. A
  grader following it finds nobody claiming SC-15. T-24 and T-25's verifies jointly produce the
  evidence, so no build cycle is at risk — add the trace. SC-18 is likewise untraced and is left
  alone deliberately: it is a nothing-changed criterion no task can own.

## Rulings that need no change

- **T-29 and SC-17 STAY IN FEAT-38.** pm called them droppable; fable verified T-29 was a deliberate
  ruling (pre-existing backlog row B-9) rather than a reflex. The operator's grilling ruling put the
  class sweep in scope and it stands. The reader disagreement is recorded, not resolved by silence.
- **Build-then-delete is accepted and the plan is honest about it.** T-20/T-21 built what T-24/T-27
  delete; `traces: []` with stated reasons, two-sided reversal verifies, D-10/D-14/D-15 recording it.
  fable argued the rejected keep-it side and still sided with deletion: the mechanism was itself an
  instance of the disease it was meant to police — a mid-feature decision that reversed within days.
- **Sequencing: finish FEAT-38 before the approval-guard defect.** Remaining work is ~3-5 cycles of
  16 available and orthogonal to the guard; stopping now strands a 15-entry rewrite against the
  highest-churn file in the repository. The guard becomes the next feature the day FEAT-38 ships.
- **Uncosted consequence, recorded rather than fixed:** DEC-181's markers guarded facts with a
  demonstrated rot rate, so losing semantic-rot detection is not hypothetical for that entry
  specifically.
- **Remaining build is five tasks:** T-27 -> {T-24, T-28} -> {T-25, T-29}. No cycle, longest chain 3.
  scout verified every pending verify against deletion order — no other gate asserts something a
  predecessor removes — and confirmed both retained-anchor-checker registrations are intact at the
  pin with positive retention assertions in T-24/T-25.

## Process deviations by the main session, on the record

- The three readers were dispatched **directly from the main session**, bypassing the orchestrator.
  That is a DEC-120 deviation. It produced good findings and it is not repeatable as a pattern; the
  durable version of this panel is being planned as its own feature.
- The panel's own composition exposed three defects worth carrying into that feature: no single lead
  can host all three personas (pm is a Product member, the reviewers are Validation);
  `fable-advisor` is outside the 16-agent organization and has no digest contract, passing the
  `SubagentStop` hook only through its documented non-harness `agent_type` fail-through; and a
  read-only persona cannot satisfy an `outputs:` path.
