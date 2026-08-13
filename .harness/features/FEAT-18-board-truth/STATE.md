# STATE

## Current

- feature: FEAT-18-board-truth
- run: .harness/features/FEAT-18-board-truth/runs/2026-08-13-02-product/state.yaml
- squad: product
- status: awaiting-user

The plan mission is complete, revised, and still UNSIGNED. The operator's 2026-08-13 ruling struck
D-08 and SC-08: `gh issue develop` is not used at all and the build branch is created with a plain
`git checkout -b feat/FEAT-18-board-truth`. Nine sites were revised across `BRIEF.md` and
`plan.yaml`; the plan holds at 8 REQ, 6 tasks and 8 decisions, both struck entries kept with strike
records (DEC-188 shape). The DEC-174 lane assignments and D-02's loud-and-continue-with-no-retry
posture are untouched. `check-plan-routes.py` re-run by the orchestrator after the revision:
`0 violation(s) across 8 plan(s)`, exit 0. `check-state.sh` exits 1 with exactly one violation,
`BRIEF.md is NOT approved` — the designed terminal state of a plan mission, not a defect.
`notes/handoff-plan.md` was superseded (seq-2) because seq-1 carried the struck build-branch
instruction forward. Nothing was built and no file outside this feature directory was touched.

The phase ends here. The next action is the operator's signature on both artifacts; the build phase
starts from a fresh orchestrator once `approval.status` reads `approved` in both.

## Open Questions

- Q1 (non-blocking, for the operator at signature): D-05 adds `github.board` — `owner`, `number`,
  `station_field` — to `harness.json`. The grilling settled "never add its four config keys".
  Verified at source, stated exactly: THREE of the old four are pinned node ids, consumed at
  `branch-create-gate.sh:107-108` as `--project-id`, `--field-id` and `--single-select-option-id`,
  which is why a wrong id was silent. The fourth, `project_number`, is read at line 35 and used
  ONLY in the presence guard at line 102 — never consumed downstream — so it is functionally the
  same thing as D-05's new `number`. The surviving distinction is therefore by-name resolution plus
  loud failure versus silent id-pinning, not a clean four-versus-three. Confirm this is not the
  thing that was fenced off. **Unresolved by design — no agent can recover what the fence meant.**
- Q2 — OVERTAKEN by the 2026-08-13 revision, not in force. It asked whether to accept D-08's
  recorded gap (`branch-create-gate.sh` cannot see `gh issue develop`) or teach the gate that route.
  The advisor's ruling to accept is moot: D-08 is struck, the route is not used, and the gap cannot
  occur. Teaching the gate `gh` subcommands is now a named out-of-scope item.
- Q3 (non-blocking, for the operator at signature): D-08's strike record is carried in a new
  `struck:` key on the decision mapping. No schema and no gate reads `plan.yaml`'s `decisions:`
  block, so the key is inert — verified by the product lead. What remains is presentation: fold the
  record into `choice:` instead, if preferred. One line either way.
