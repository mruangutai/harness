# Operator answers — FEAT-21 signature round, 2026-08-14

Asked via the main session, all four ruled in one pass.

- **Signature: APPROVED, conditional on the two edits below landing first.** The operator signs
  BRIEF and plan as revised; the main session writes the approval blocks once pm's revision is in.
- **Q1 CONFIRMED — the unit-9 override stands.** branch-create-gate.sh, the guard instruction
  paths, gh-sync.py and validate-feature-json.py ride inside the atomic commit. "Anytime" was a
  dependency-order claim, not a prohibition; two of the four break loudly post-move and two fail
  silently, and a known-broken window between merges is the worse trade.
- **Q2 CONFIRMED — tests.yml stays in, main-session-direct.** The lane against the live grant is
  accepted because its edits are meaningless outside this diff. FOLD IN: fix
  plan.yaml lanes.measurement to credit pm with taking the --resolve measurements.
- **Q3 RULED: add the checks.** T-06 and T-10 gain count-based verify clauses mirroring T-04's
  exactly-2 shape, so SC-14's test-backed claim is enforced rather than asserted (#247's class).
- Q4, Q5, Q6: defaults confirmed (defer the basename-collision to unit 5+; #356 stays open with
  only its two literals re-anchored; templates keep legacy paths pending #346).
- Q8: take the advisory — anchor tests.yml:119,125's measured numbers with "measured at <sha>,
  pre-move" as part of the T that edits the file.
- Q9 is the harness owner's, not this feature's; already noted for the backlog.
