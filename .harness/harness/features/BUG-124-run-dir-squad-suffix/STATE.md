# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: .harness/harness/features/BUG-124-run-dir-squad-suffix/runs/planpanel-c1-validator/state.yaml
- squad: validator
- status: in_progress

PLAN PHASE, CYCLE 1. Station `plan`, approval `pending`, `cycles_used: 1`, six runs.
**THE CYCLE-1 PANEL PASSED** at `severity_max: med`, `must_fix: []`, pinned at `87205da9`, both
readers RAN. `gates.review` is `advisory_unless_high`, so nothing gates and the plan is signable.
The ONLY plan-phase step left is the panel RECORD (pm transcribes the c1 panel into plan.yaml's
top-level `panel:` key), after which this goes to the operator for signature. Nothing is built; no
`review_sha` exists and none is owed until the Building -> Review seam.

**Do NOT fix R-1..R-4 before signature.** They are advisory med/low, and DEC-176 puts non-gating
findings in the operator's ONE batched signature review, not a pre-signature fix dispatch. Amending
plan.yaml's substance now would also unbind the c1 panel verdict from the plan the readers read and
force a cycle-2 panel for cheap clauses. Only `approval.rulings`, written by the main session's
`sign-approval --overrule`, records acceptance.

Trust (claim — pointer — verified-at 87205da9):
- All SEVEN cycle-0 findings are CLOSED, re-derived independently by the c1 panel, not taken on
  pm's word: the three `high` self-refusing-prose findings (PF-d882b5400a23e07c2ab26d710e2219db,
  PF-018d8e2a2c8c5293baade75381864e6c, PF-b126afaed82b9b215606db591430fd8a) plus PF-05e45a58,
  PF-64c48fa9, PF-4f1b6dc3 and PF-6e184d4c. Evidence: runs/planpanel-c1-validator/digest.md.
- The remedy is D-05: a QUOTED or illustrated run-dir path is spelled `[.]harness/`, invisible to a
  detector that anchors on the literal `.harness/` segment. Both verify lines now build the anchored
  form at runtime with `q.replace("[.]", ".")`.
- ZERO refusable run-dir references survive in plan.yaml or BRIEF.md. Measured twice by two methods:
  by me (simulating the specified `run_dir_refs`) and independently by the `scope` reader, which
  rebuilt the detector from the plan's own spec and ran a positive control.
- Panel Q1 (blocking at cycle 0) is ANSWERED and folded into D-03: `import yaml` succeeds under
  `/opt/homebrew/bin/python3`, `/usr/bin/python3` and `PATH=/usr/bin:/bin python3`, while
  `python3 -I -c "import yaml"` fails. Not re-measured at c1, deliberately.
- Panel Q2 is RULED in D-05: state the convention in `.claude/skills/harness/SKILL.md` (T-03).
- D-01 carries the operator-accepted callee-INDEPENDENT rule; BRIEF's requirements section carries
  its `detected by nothing` disclosure naming the wrong-squad-slug case.
- SC-09 is NOT unrequested scope: both c1 readers independently dismissed that objection — REQ-05
  requires the skip reason be stated, and a skip line naming the wrong cause is not the reason.
- `check-plan-routes.py`: 0 violations. REQ-01..06 all traced; SC-01..09 all have producing cases.
- The `[.]` spelling does NOT expand under bash pathname expansion (a leading dot must be matched
  explicitly; a bracket expression does not count) — a reader contradiction the lead resolved.

Dead ends for the next phase:
- Do NOT re-derive whether issue #124 is real, do NOT re-measure the PyYAML question, do NOT
  re-check the seven closed findings. All settled above.
- Do NOT amend plan.yaml's substance before signature (see the DEC-176 paragraph above).
- Do NOT edit `plan.yaml` by hand: `plan-merge.py` is the only write route, and `approval:` is the
  main session's `sign-approval` alone.
- Do NOT rewrite the pre-D-05 run digests and the c0 goal-check note to carry the escape spelling
  (Q3 below): rewriting a recorded artifact to look better falsifies the record.

Working set: plan.yaml, BRIEF.md, runs/planpanel-c1-validator/digest.md,
notes/review-harness-code-reviewer-planpanel-c1.md, notes/research-BUG-124-goalcheck-plan-c1.md

## Open Questions

- Q1 (harness defect, blocks the plan-phase handoff note for EVERY worktree-resident feature):
  `handoff_done_when.problems()` is called with the OWNER checkout root, while the note's
  feature-dir prefix comes from the note's own worktree-relative path. `FEATURE_RE` extracts
  `.harness/<repo>/features/<feat>` correctly, then `_feature_dir` joins it to the owner root
  (handoff_done_when.py:11,51-54), so every Authority pointer is looked up in a tree where the
  feature directory does not exist. Absolute pointers are separately refused as "is absolute"
  (`_unsafe_rel_path`, :69-70), so there is NO legal spelling. Diagnosed; blocked on the harness
  owner. This section is the supported disk-only substitute for the missing handoff note.
- Q2 (record, the one remaining plan-phase step): the SEVEN cycle-0 dispositions still read
  `open` in plan.yaml's `panel:` block though all seven are closed, and the c1 panel's own five
  findings are not recorded at all. pm transcribes the c1 digest into `panel:` — `last_run`,
  `cycle: 1`, both readers `ran`, and every finding with a computed `PF-` id and disposition.
- Q3 (advisory, no task): three pre-D-05 artifacts keep raw anchored `eng-t01` paths
  (`runs/goalcheck-plan-product/digest.md:11`, `runs/planpanel-validator/digest.md:19`,
  `notes/research-BUG-124-goalcheck-plan-c0.md:67`). After T-02 lands, pasting one verbatim into a
  dispatch is refused, recoverable in one re-spelling. Left as-is on purpose.
- Q4 (operator, at signature): T-02 specifies a SECOND parse of `team-config.yaml` inside the
  derivation subprocess — one small file read per governed dispatch — because it is the only source
  of the derivation's failability. Both c1 readers dismissed it as over-build; accepted as designed
  unless the operator objects.
