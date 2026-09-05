# Handoff — BUG-1306, validate → ship — written at da05ea28, seq-3

## Next

Ship is the operator's gate, not a squad's: no fix cycle is owed. Put the two non-blocking
operator questions in front of the user — pm Q1 (BRIEF SC-04 / plan D-02 cite the raw `Popen`
sites as "near lines 305/309"; at the pin they are 315/319, both files approval-gated) and pm
Q2 (EMERGENT: no standing gate exercises this suite under a governed ambient identity, so
deleting the pop keeps CI green and reintroduces the bug for agents only — pm recommends a
separate dev-ops ticket, out of scope here per BRIEF ## Constraints). Then run the ship phase
against `review_sha` `da05ea28`. Backlog candidates for the ship briefing, all advisory, none
gating: B-1 the SC-04/D-02 anchor drift (chore), B-2 the governed-identity CI leg (enhancement),
B-3 the security note's internal miscitation of the guard's owning issue (chore), B-4 the
standing `plan.yaml` finding PF-15e50cd4137f8309fac4057506bd40a5 — SC-05 gates which FILES
changed, not which LINES (bug, standing gap for FUTURE edits, discharged for this one).

## Trust

- All five criteria are met and each was re-measured by pm this run, not inherited — notes/research-BUG-1306-goalcheck-validate-c0.md — verified-at da05ea28
- The panel is PASS with `must_fix` empty, severity_max `info`, `code_grade: pass`; all four reviewers ran and ui declined on a measured census, not a prediction — notes/review-harness-code-reviewer-c0.md, notes/review-harness-qa-c0.md, notes/review-harness-security-reviewer-c0.md, notes/review-harness-ui-reviewer-c0.md — verified-at da05ea28
- The reviewed CODE is identical to the earlier pin 536afda3 and to build's 7e38d0ae — same blob object `8fde5efc9c05eac9f3f312dd6191b45c89ad2f23` at all three, and `git diff --stat` over tests/ bin/ .claude/skills .agents/skills between them is empty — verified-at da05ea28
- The suite CAN report red at THIS pin: the pinned source with its one pop line replaced by `pass`, run under `HARNESS_AGENT_TYPE=harness-orchestrator`, exits 1 with 14 FAIL lines — the BRIEF's pre-fix shape. Compiled in memory under the original `__file__`; no repo file written, `git status` clean after — verified-at da05ea28
- The `unit` kind is EXECUTED, not inherited: exit 0 / 0 FAIL both with `env -u HARNESS_AGENT_TYPE` and ambient governed, 27 files and 342 check lines discovered — verified-at da05ea28
- SC-04's ordering holds first-hand at the pin: pop at :41 and the only module-scope `os.environ` statement, first case def at :165, `Popen` at :315 and :319, read via `git show da05ea28:tests/integration/test-plan-merge.py` — verified-at da05ea28
- `check-state.sh` is clean for this feature apart from INV-35, a proven tool false positive: the ` #1103` on plan.yaml:112 sits inside a single-quoted scalar opened on line 111 and `yaml.safe_load` returns it intact — verified-at da05ea28

## Dead ends

- Do not re-pin away from da05ea28 or re-run the panel; the pin is current, INV-33 is green, and plan.yaml has not moved since — .harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json — verified-at da05ea28
- Do not edit `plan-merge.py`, add a shared `tests/integration/` helper, a second test file, a runner scrub, or a tree-wide env lint — plan.yaml D-01, D-03, D-04 — verified-at da05ea28
- Do not "fix" the SC-04 / D-02 line numbers on the branch: BRIEF and plan are approval-gated and only the main session signs — .harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md ## Approval — verified-at da05ea28
- Do not treat a green `run-unit-tests.sh --kind integration` as hermeticity evidence; `run_pool.py` passes ambient env through, so only the direct invocation measures it — notes/review-harness-qa-c0.md — verified-at da05ea28
- Do not record run dir `2026-09-05-05-validator`; its own state.yaml reads `status: superseded` and its record moved to `2026-09-05-06-validator` — runs/2026-09-05-05-validator/state.yaml — verified-at da05ea28

## Working set

- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/feature.json
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/research-BUG-1306-goalcheck-validate-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-code-reviewer-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/notes/review-harness-qa-c0.md
- .harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md

## Done when

Scope: the operator has ruled on Q1 and Q2 and the ship phase has run against da05ea28
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Success Criteria
Authority: approval:.claude/worktrees/harness/BUG-1306-agent-type-hermetic-tests/.harness/harness/features/BUG-1306-agent-type-hermetic-tests/BRIEF.md#Approval
