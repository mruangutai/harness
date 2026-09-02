# STATE

## Current

- feature: FEAT-51-claude-code-lifecycle-safety
- run: none live — validation is complete and no squad run is open
- squad: none
- status: Review

BUILT, VALIDATED, MERGED, AND ACCEPTED FOR SHIPMENT. All nine tasks are at station `done`; eleven
success criteria are met; SC-10 and SC-12 are withdrawn by explicit operator rulings; and the review
panel is clean at `severity_max: low` with no `must_fix`. On 2026-09-02 the operator chose to skip
the Claude Code-specific hand-test and withdraw SC-10 after an OMP pre-flight demonstrated that OMP
cannot exercise the compatibility-host quarantine path. Claude Code parent resumption therefore
ships without live-host UAT evidence.

THE BRIEFING FOR THE OPERATOR IS `notes/ship-review-build-validate.md`, with the rendered reading
view beside it. It carries the ship decision, what validation caught, the success-criteria table,
the gate of record and a twenty-one-row proposed backlog.

`review_sha` IS PINNED AT `aab31504560627044a4d03cdcad611d5947d0b3e`. Commits after that pin add
only records under `.harness/harness/features/**`; no reviewed code moved.

GATES AT THE PIN, all measured by me and not taken on any squad's report: `--kind unit` exit 0,
519 PASS, 0 FAIL. `--kind integration` exit 1, 755 PASS, 7 FAIL. `test-quarantine.py` exit 0,
35 checks.

THE SEVEN INTEGRATION FAILURES ARE THE OPERATOR-ACCEPTED GATE OF RECORD, not defects. All seven are
`test-check-plan-routes.py`'s manifest DEVIATION family. `diff` of main's `team-config.yaml` against
the branch's returns exactly T-03's approved route plus its comment and nothing else;
`_manifest_deviation`'s own docstring records that a route change deviating is intended; clearing
the one other cause moved 9 to exactly 7; and `HARNESS_PROJECT_DIR` pointed at the worktree changes
nothing, because the checker resolves against the OWNER manifest, which is what the hook consults.
So the project's only blocking gate is unsatisfiable pre-merge for ANY route change. Gate placement,
not this feature — backlog B-13.

WHAT VALIDATION CAUGHT, and it earned its cost twice. The panel FAILed at the first pin `fa5ce88e`
on two high defects. F-1 was a REGRESSION IN THIS FEATURE'S OWN PROTECTION: the live-children
refusal had been narrowed from `if _kids:` to `if _kids and _return_verdict in VERDICTS:`, so a
parent with a live child and an absent, null or unparseable last message skipped the refusal, had
its claim released and exited 0 where it exited 2 before — the interrupted-parent case, exactly what
the feature governs, with no test covering it. I confirmed both lines at both commits with
`git show` before spending a cycle. F-2 was a new unauthenticated cross-feature overwrite through
`quarantine.py adopt`, reproduced end to end. Both fixed across two lanes to one shared
realpath-containment rule, and the scoped delta proved each closed by a red-on-the-old-binary
measurement rather than by inspection.

THREE VACUOUS GATES WERE CAUGHT ACROSS THIS FEATURE — a test that could not go red, a checker that
discovered nothing, and an OMP fixture whose claim was pruned before its assertion ran. The last was
SC-07, graded not-met until a mutation proof showed both hook-level cases going red with the
exemption removed.

CYCLES 13 OF 20. Four cycles of rework, each of which bought a named defect. `len(runs)` is 26
against `max_total_runs` 20 — informational, named in the briefing rather than buried, and
UNDER-REPORTING, because the six main-session-direct segments are not runs and never appear in
`runs:`.

Merge and PR #1151 are complete. The remaining operator act is the recorded ship transition.
Feature-close distillation remains after shipment.

## Open Questions

- OPERATOR RULING, resolved 2026-09-02: skip the Claude Code-specific hand-test and withdraw SC-10.
  The OMP pre-flight was not treated as a pass; it established that OMP cannot exercise the
  compatibility-host branch. Live Claude Code parent resumption remains unverified at ship time.
- OPERATOR DECISION, not gating: `PF-2545afb576b19ad86704f5bfcb556b9e` (low, open) asks to narrow
  SC-02's `awaiting` set-equality to a subset check. Narrowing a success criterion is the operator's.
- HARNESS DEFECT, measured TWICE independently in this feature: a repo-relative editor write
  resolved against the MAIN checkout instead of the dispatched worktree, succeeding silently because
  the two copies were byte-identical. One instance was exposed only because a generator then wrote
  no row. Both cleaned and verified clean. An absolute-path-plus-check-both-trees mitigation in the
  dispatch held for every run after I added it. Backlog B-14, plausibly
  `BUG-1030-stale-anchor-write-hazard`. — harness-orchestrator
- HARNESS DEFECT: the only blocking gate is unsatisfiable pre-merge for any `team-config.yaml` route
  change. Backlog B-13. — harness-validator-lead
- HARNESS DEFECT: `test-check-domain.py`'s crashing-schema-module case fails whenever the hook is
  fired from a copied bin dir, with or without a mutation, so `CHECK_DOMAIN_BIN` is an unreliable
  seam for mutation proofs. Backlog B-17. — harness-pm
- HARNESS DEFECT: a lead cannot correct its own `digest.md` in place, so a digest failing the
  validator's file-side check needs a second run directory and leaves a superseded copy. Two exist
  for the SIMPLIFY cycle. Backlog B-18. — harness-eng-lead
- PROCESS GAP: test-first compliance is structurally unauditable for the six main-session-direct
  tasks — that lane writes no receipt and each task landed as one commit, so commit order cannot
  show test-before-code. Absence of evidence, not evidence of absence. Backlog B-21. — harness-qa
- RECORD LOSS, stated rather than glossed: the T-04 run's `state.yaml` was overwritten by a later
  member seeding a checkpoint into the same directory. `runs/` is gitignored, so it was untracked
  and is unrecoverable. T-04's durable record is that run's `digest.md`, its committed receipt, the
  `feature.json` entry, and my own end-to-end verification of `quarantine.py`. I removed the bogus
  seeded file rather than leave a completed run reading `status: running`. — harness-orchestrator
- RESIDUAL: `#551`'s orchestrator-inferring-verdicts-from-disk consequence is now the only unclosed
  one and no decision entry owns closing it. Backlog B-19. — harness-documentor
- PRE-EXISTING, unrelated and still red: `check-state.sh` INV-29 on
  `.claude/worktrees/harness/BUG-1129-validate-handoff-sweep`, another effort's dirty terminal
  worktree. Untouched. Backlog B-12. — harness-orchestrator
