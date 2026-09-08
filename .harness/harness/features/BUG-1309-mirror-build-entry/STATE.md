# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-c13b-product/state.yaml
- squad: product
- station: **building** (was review). The operator ruled FIX on all three surviving panel-c7 high
  findings, the signed plan was amended to specify those remedies, and T-04/T-05 therefore no longer
  match their delivered code. T-04 and T-05 are back at `building`; the other eleven tasks stay
  `done`. `review_sha` still reads 894adc0f and is now STALE by construction — it must be re-pinned
  at the tip of the direct implementation before any validator run (INV-6).
- status: the feature is blocked on **main-session-direct implementation**, not on a decision.
- the four operator rulings, transcribed with provenance and one corrected miscount:
  notes/rulings-2026-09-08-panel-c7.md. R-0 the amended BRIEF is re-signed (corroborated at ea0bdd6b,
  BRIEF ## Approval now 2026-09-08); R-1 refuse ambiguity when two VALID records claim the merge
  branch; R-2 fix the parser for value-taking git globals; R-3 derive the recovery command and amend
  the plan string that pinned `open`. There is no answers-<runid>.md for this round — the rulings came
  inline in the resume dispatch, and the orchestrator may not author that file (issue #671).
- plan amended in two pm passes, both PASS, `approval:` byte-identical throughout (earliest changed
  line 203, approval is 3-25): notes/research-BUG-1309-planamend-c13.md and -c13b.md. T-04 `intent`
  now derives the non-era recovery command from feature_schema.recovery_command_for and pins no
  literal; T-05 `intent` carries the flag-aware subcommand walk and the two-or-more-owners DENY with
  the unattributable-record bound restated; T-05 `verify` gates 19 case names, T-04's gates 6;
  decisions D-13/D-14/D-15 record the rulings. check-plan-routes.py: 0 violations.
- the implementation is fully specified for the main session in
  notes/direct-packet-2026-09-08-panel-c7.md — three code edits (merge-gate.py `git_merge`,
  merge-gate.py `feature_for` + caller, gh-sync.py `_build_entry_recovery_notice`), six test cases
  (five in tests/integration/test-merge-gate.py, one in tests/integration/test-gh-sync.py), the exact
  verification commands, and the regression fence that must not move.
- cycles 13/14. runs 41 against a 20-run budget (INV-22, informational, surfaced in the briefing).
- the briefing at notes/ship-review-2026-09-08-resume.md is now STALE on the three findings; it is
  rewritten after the implementation lands, before the ship decision.

## Open Questions

- Q1 (blocking, operator) — SC-04 under-covers the new ambiguity DENY: it enumerates deny for a
  SINGLE feature and pins a reason shape naming one feature and a re-run command, while an ambiguity
  deny names every claiming feature and no command clears it. The behaviour is gated by T-05 `verify`
  but traces to no success criterion. Widen SC-04, add an SC, or disclose in BRIEF ## Verification
  gaps. BRIEF was re-signed today, so all three are operator acts.
- Q2 (blocking, operator) — `plan-merge.py sign-approval` on the amended plan. `amend` holds the
  approval bytes by design, so the plan reads `approved 2026-09-04` over text amended 2026-09-08.
- Q3 (blocking, operator) — SC-10 UAT: notes/uat-BUG-1309-mirror-build-entry.md, 8 steps. Independent
  of R-1..R-3, but it must run BEFORE the worktree is released, because the script points at that
  checkout.
- Q4 (non-blocking, harness defect) — the `open` horn of the non-era recovery-required notice is
  specified by an UNNAMED intent bullet and is asserted by no test today: `grep -rn "MERGE is
  refused" tests/` returns nothing. Backlog row, or a later amendment.
- Q5 (non-blocking, harness defect) — a harness-product-lead run returned a complete, well-formed
  VERDICT/DIGEST/artifact and the host reported it `failed (exit 1)` with "Subagent called yield with
  null data". A correct return read as a failed run; every claim in it was verified at source.
- B-12 and the B-1..B-13 ship backlog in the stale briefing still await operator disposition.
