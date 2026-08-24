# STATE

## Current

- feature: FEAT-35-orchestrator-stop-and-wake
- run: build phase COMPLETE. All five tasks built, every gate green. t04-product PASS (re-dispatch
  after its ESCALATE), t05-eng PASS. Nothing in flight.
- squad: none
- status: Building

<!-- phase: build, at its exit boundary. T-01/T-02/T-03 committed at d7e8c66 by the main session.
     T-04 landed DEC-201 (DECISIONS.md:6800, index row 219); its verify printed T-04-PASS, re-run by
     the orchestrator. T-05 registered at run-unit-tests.sh:17, 9/9 green at HEAD, 9 named failures
     against 569d417 covering all eight assertions, --kind unit exit 0.
     T-04 and T-05 both still read `building`, deliberately: the playbook couples the `done` write to
     the commit act and no commit was authorised. SEAM GAP TO NAME - both are execution_mode team, so
     the mirror table gives that write to the orchestrator, but the operator commits from the main
     session where no orchestrator exists. Whoever commits must write both.
     The DEC-200 collision is resolved by re-id to DEC-201 under the operator's ruling
     (notes/answers-t04-build-2026-08-24.md); plan.yaml now holds zero DEC-200 and its approval block
     is untouched. SKILL.md:50 reads (DEC-201) - fixed by the main session, whose own error it was.
     cycles_used 2: the T-04 re-dispatch was rework. Both leads reported 0 send-backs.
     feature.json's t04-product entry now reads PASS where it read ESCALATE; the escalation survives
     in that run's digest, the lead's escalations: trace, and cycles_used itself. Nothing erased.
     qa and SIMPLIFY still NOT run - out of scope by operator instruction, and they belong after the
     commit. Mirror: milestone #24, sub-issues #798-#802, parent #751; #801/#802 at Building. -->

## Open Questions

- BLOCKING BEFORE COMMIT. DEC-201's incident sentence attributes BOTH the 342 `echo hold` calls and
  the 600s watchdog death to ONE orchestrator, while the entry's own control paragraph states the two
  failing sidecars are DISTINCT and that the dead one had ZERO assistant events - which cannot be an
  agent that made 450 Bash calls. The plan's intent supplies 354/450 and the answers file supplies
  342 for a different swept sidecar; merging them is a synthesis neither source states. Settle
  against #744. It is one sentence in the permanent authority file.
- The `done` write for T-04 and T-05 has no owner in the commit path. See the phase note above.
- NON-BLOCKING. plan.yaml's T-04 intent still reads "after DEC-199" - correct when 200 was free,
  stale now. pm was scoped to the two id occurrences and correctly left it.
- NON-BLOCKING. T-04's gate cannot detect a missing hand-written index summary:
  gen-decisions-index.py:325 writes a sentinel for a new key and the gate diffs generated against
  file, so a sentinel row passes. The lead verified by hand - zero sentinel rows.
- NON-BLOCKING, operator is filing: T-05's line-scoped assertion 6, and the absent DEC-NN collision
  guard (check-plan-routes.py guards INV-NN as of 3df18d3).
- ACCEPTED, not to be fixed: the four INV-26 rows from opening the mirror. Three close from the PR's
  Closes lines at merge; do not move cards by hand.
- NOT THIS FEATURE'S: check-state.sh INV-26 on FEAT-33's parent (issue #675), from the merge at
  776dff2.
