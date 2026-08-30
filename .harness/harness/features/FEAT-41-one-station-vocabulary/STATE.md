# STATE

## Current

- feature: FEAT-41-one-station-vocabulary
- run: 2026-08-30-01-orchestrator. Build phase attempted; NO squad was dispatched and no run row
  was added, because there is nothing in this plan a squad may lawfully execute.
- squad: none
- status: Ready. UNCHANGED, and deliberately so. Not one line of build work landed, so advancing
  the station to Building would assert something the tree does not support (PRINCIPLES rule 15).
- THE BUILD PHASE CANNOT OPEN FROM THIS TIER, AND THE FINDING IS MEASURED, NOT INFERRED. All 13
  tasks carry `execution_mode: main-session-direct` in the signed plan, and neither I nor any
  squad member may execute a single one:
  - `check-domain.sh` DENIES `harness-orchestrator` at exit 2 on every surface class this plan
    touches — `.claude/skills/harness/bin/**`, `.harness/harness.json`,
    `.agents/skills/harness/templates/**`, `.claude/settings.json`, `.omp/agents/**`, both
    `SKILL.md` paths, `.harness/team-config.yaml`, `.harness/harness/docs/DECISIONS.md`. Probed
    once per class with a real PreToolUse payload; the hook names my permitted set, which is the
    feature dir, my answers/ship-review notes, my Expertise and my observations log. Nothing else.
  - `check-domain.sh --resolve` returns NOBODY for the templates, `.claude/settings.json`, both
    agent trees, both `SKILL.md` paths and `team-config.yaml`, so no member is granted them
    either. Probed directly: `harness-backend-dev` is DENIED `.claude/settings.json` at exit 2.
  - DEC-174 bars the rest. Its amendment 4 enumerates `check-domain.sh`, `bash-write-guard.sh`,
    `validate-digest.py`, `check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh` AND the
    test file of each, and declares the category — hooks, validators, gate scripts — governing
    and the list non-exhaustive. Every task touches at least one of those or a NOBODY path.
  - DECISIONS.md:6733 states it outright: "DEC-174 forbids the orchestrator
    `main-session-direct` tasks". The sentence sits in DEC-200's lineage prose, not in DEC-174's
    own section, which is why grepping the id found it and reading the entry would not have.
- THE GATE ITSELF CORROBORATES, in one run at exit 0. `check-plan-routes.py` prints, for all 13
  tasks, either `OK <task>: declared main-session-direct (... ungranted)` or
  `DEVIATION <task> ... granted to harness-backend-dev, harness-dev-ops but declared
  main-session-direct`. Not one task prints the ordinary team-lane shape `OK <task> granted to ...`.
  A plan carrying no dispatchable task is legible in the gate's own output.
- THIS SHAPE IS PRECEDENTED AND THE HARNESS ALREADY NAMES IT — FEAT-41 is the fifth instance, not
  an anomaly. `check-state.sh` INV-17 emits for FEAT-21, FEAT-40, FEAT-22 and FEAT-15: "exempt
  from handoff notes — every task in its plan.yaml is execution_mode main-session-direct
  (DEC-174), so no squad ran and no seam was crossed." The absence of run rows and handoff notes
  on this feature is that same exemption, not work quietly skipped.
- gates, all three run BY ME at 855a356, in this worktree. check-state.sh: EXIT 0 — zero hard
  failures, 13 NOTE lines, and NOT ONE of them concerns FEAT-41. The plan-phase violation (this
  feature's unapproved BRIEF) closed at the signature exactly as the previous entry predicted.
  check-plan-routes.py: exit 0, "0 violation(s) across 1 plan(s)", 40 dirs examined, 39 skipped
  as shipped — the known-good shape, unchanged. run-unit-tests.sh: EXIT 0, full suite, 3374
  lines, ZERO `FAIL` lines, ~248s. Counted by `grep -c '^FAIL '` with the exit status captured
  in a variable, never by a tail read — the runner's last line is the last script's own tally.
  This is the clean pre-build baseline: any red the build produces belongs to the build.
- SIGNATURE VERIFIED ON BOTH FRAGMENTS, because an approval usually touches one and leaves the
  other stale: plan.yaml `approval.status: approved` and BRIEF.md:255 `status: approved`, both
  Mike Ruangutai, 2026-08-29. They agree.
- SC BASELINES MEASURED AT 855a356 so the successor inherits numbers rather than re-deriving
  them: SC-02's quoted-literal grep returns 27, SC-01's `_STATION_KEYS` returns 7, SC-12's
  `plan-merge` grep returns 35. The last matches the BRIEF's own reading at 0d4845b, so the
  rebase moved none of them.
- cycles: 8 of 10 — UNCHANGED. Zero rework, zero send-backs, zero dispatches (DEC-157: only
  rework counts). runs: 15 of 20, unchanged; no run row is added because no lead ran.
- review_sha: 49638bf, UNCHANGED. DEC-89 re-pins when the build's own commits land. None did.
- next: THE MAIN SESSION EXECUTES THE 13 TASKS DIRECTLY, in the dependency order recorded in the
  ship-review note below. This is the sanctioned DEC-174 route — ordinary edits, each task's
  `verify:` run explicitly, a human reading the diff — and it is the ONLY route this plan has.
- briefing: notes/ship-review-2026-08-30-01.md — the task-by-task disposition, the dependency
  segments, the measured lane evidence and the backlog table.

## Open Questions

- Q1: RESOLVED 2026-08-29 by the operator. The external dependency is declined and the
  decision-record task is removed; its subject re-files with the decisions-authority triage,
  outside this feature. See BRIEF.md PB-04 and plan.yaml D-09.
- Q2: MOVES WITH THE RE-FILED WORK. It was input to the recording-form choice — DEC-188's own text
  bearing on strike-in-place versus subsuming rewrite. Preserved in D-09 for the triage.
- Q4: RESOLVED by events, 2026-08-29. The INV-26 FEAT-40 violation is gone — FEAT-40 shipped.
- Q6: RESOLVED and APPLIED. INV-32 is scoped to non-terminal stations. FEAT-27's pin is NOT
  repaired: shipped history stays untouched, per the operator.
- Q7: RESOLVED and APPLIED, folded into the same edit site as Q6.
- Q8: HARNESS DEFECT, unchanged and not re-triggered this run — nothing allocates run-dir slugs.
  The 2026-08-29 collision stands recorded in runs/2026-08-29-01-product/OVERWRITTEN.md rather
  than reconstructed (rule 15). No squad ran this time, so no slug was allocated.
- Q9: unchanged. The stale-pin task traces REQ-07 and pm calls the stretch knowingly. DEC-89
  already decides its invariant and says the state check re-pins review_sha; nothing implements
  that re-pin, so #867 is the unbuilt detection half of an already-decided invariant.
- Q10: non-blocking harness defect. Gitignored `__pycache__/*.pyc` defeat every absence-grep over
  the bin directory, a compiled constant still carrying the searched string. Should
  `--exclude-dir=__pycache__` be a standing convention, or should run-unit-tests.sh clear it?
- Q11: non-blocking HARNESS DEFECT, confirmed by measurement. The shell substitutes PHANTOM
  pathnames for an unmatched glob member, so `grep -rn PAT dir/*/f.yaml` exits 2 on ENOENT even
  when it matches, making `grep ... ; test $? -eq 1` unusable harness-wide. I could not file it
  via xd://report_issue — check-domain denies the orchestrator that path.
- Q12: REOPENED, AND ITS EARLIER PREMISE WAS FALSE. The previous entry called the
  `.harness/harness/docs/**` lanes row vestigial because "no surviving task touches that
  surface". A surviving task DOES: the rename task lists `.harness/harness/docs/DECISIONS.md`
  among its files at plan.yaml:1177, and that path resolves to harness-documentor. The row is
  LIVE, not vestigial. It stayed invisible because check-plan-routes.py short-circuits on
  `nobody_paths` before reaching the DEVIATION branch, so that task reports OK on its three
  ungranted paths and its one granted surface is never printed. Changes nothing about
  executability — the task is main-session-direct and carries NOBODY paths regardless — but
  BRIEF.md's claim that the plan has no team-lane task is now the thing a reader could misread.
- Q13: CONFIRMED BY MEASUREMENT, still open, and it should be closed before the build starts.
  SC-02's own quoted-literal grep appears at BRIEF.md:110 and :113 and in NO task's `verify:`
  block. The criterion is graded against a command nothing in the plan runs. One line added to
  the vocabulary task's verify closes it. Baseline today: the grep returns 27.
