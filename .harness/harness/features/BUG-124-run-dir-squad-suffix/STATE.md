# STATE

## Current

- feature: BUG-124-run-dir-squad-suffix
- run: .harness/harness/features/BUG-124-run-dir-squad-suffix/runs/panel-record-product/state.yaml
- squad: none
- status: awaiting-user

PLAN PHASE COMPLETE. Station `plan`, approval `pending`. Four runs, cycles_used 0 (nothing was
routed back). Next action is NOT a build: three `high` panel findings are open and DEC-176 puts
them in the operator's one batched signature review, not a pre-signature fix dispatch. After
`approval.status: approved`, T-01 dispatches to harness-eng-lead.

NO `notes/handoff-plan.md` EXISTS, and its absence is a blocked write, not an omission. See
Open Questions Q1. The disk-only successor path is the supported fallback; this section is it.

Trust (claim — pointer — verified-at 6d969ed3, all measured by the orchestrator itself):
- The defect is real: `check-domain.sh --resolve <feat>/runs/eng-t01/digest.md` answers
  `harness-orchestrator` ALONE; `<feat>/runs/t01-eng/digest.md` also answers `harness-eng-lead`.
  Both exit 0 — `--resolve` answers on stdout, never through the exit code.
- Exactly three write grants contain `/runs/`, all lead grants of shape `runs/*-<squad>/**` —
  team-config.yaml:306,315,324.
- A rule requiring only that the path resolve to SOME agent is VACUOUS: the orchestrator holds
  `.harness/*/features/**` — team-config.yaml:45. This is why D-01 scopes to the `/runs/` family.
- D-03's premise holds: `python3 -I -c "import yaml"` FAILS, plain `python3` succeeds (PyYAML is
  in user site-packages, which `-I` excludes).
- Panel finding F-4 is an OBSERVABILITY defect, not a dead gate: `import yaml` succeeds under
  /opt/homebrew/bin/python3, /usr/bin/python3 and `PATH=/usr/bin:/bin python3` on this machine.
- Panel finding F-2 is real and has a second site: T-01's verify (plan.yaml:87) embeds an
  anchored `eng-t01` path, not only T-02's (plan.yaml:159).
- check-plan-routes.py: 0 violations. panel: 2 readers both `ran`, 8 findings, all `open`,
  8 unique PF- ids.

Dead ends for the next phase:
- Do NOT route F-1/F-2/GOALCHECK-F1 as a fix cycle before signature (DEC-176).
- Do NOT re-derive whether issue #124 is real — settled above and by the operator's dispatch.
- Do NOT amend plan.yaml to fix a finding without re-running the panel: the recorded verdict is
  bound to the plan the readers actually read (plan-panel.yaml team spec).

Working set: plan.yaml, BRIEF.md, runs/planpanel-validator/digest.md,
notes/research-BUG-124-goalcheck-plan-c0.md, .claude/skills/harness/bin/dispatch-guard.sh

## Open Questions

- Q1 (harness defect, blocks the plan-phase handoff note for EVERY worktree-resident feature):
  `handoff_done_when.problems()` is called with the OWNER checkout root, while the note's
  feature-dir prefix comes from the note's own worktree-relative path. `FEATURE_RE` extracts
  `.harness/<repo>/features/<feat>` correctly, then `_feature_dir` joins it to the owner root
  (handoff_done_when.py:11,51-54), so every Authority pointer is looked up in a tree where the
  feature directory does not exist. Measured: the identical note text and identical rel_path
  returns `[]` rooted at the worktree and two "cannot resolve target" failures rooted at the
  owner checkout. Absolute pointers are separately refused as "is absolute"
  (`_unsafe_rel_path`, :69-70), so there is NO legal spelling. Blocked on: the harness owner.
- Q2 (operator decision at signature, from the goal-check): accept D-01's callee-INDEPENDENT
  rule in place of the operator's "against the callee's own domain glob"? It catches the
  reported inversion and refuses nothing that exists (309 of 309 live run dirs conform), but a
  well-formed WRONG-SQUAD slug still passes while remaining unwritable by the callee.
