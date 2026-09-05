# STATE

## Current

- feature: BUG-1306-agent-type-hermetic-tests
- run: .harness/harness/features/BUG-1306-agent-type-hermetic-tests/runs/2026-09-05-09-product/state.yaml
- squad: none
- status: validate-complete — SHIP-READY at review_sha `da05ea28`

Validate phase COMPLETE, no fix cycle required. `cycles_used` stays 1 of 8: both segments
returned PASS with zero send-backs. Feature station is `review`; the GitHub mirror is open
(parent #1309, T-01 #1310, milestone 45) and INV-26 is now green. Handoff at
`notes/handoff-validate.md`. Nothing merged, shipped, or pushed by this run.

The pin MOVED, on purpose: `536afda3` → `da05ea28`. INV-33 read the old pin as STALE because
the `status: building → review` station write and the mirror block postdated it. The two
commits that closed it touch lifecycle artifacts only — `git diff --stat 536afda3 da05ea28 --
tests bin .claude/skills .agents/skills` is EMPTY, and the test file's blob is the same object
(`8fde5efc…`) at `7e38d0ae`, `536afda3` and `da05ea28`. The reviewed CODE is unchanged; only
the paperwork moved, so the build-phase evidence transfers by object identity, not by trust.

Panel (`2026-09-05-08-validator`, review team, cycle 0): PASS, severity_max `info`, `must_fix`
empty, `code_grade: pass`. All four reviewers ran and reached their own verdict — ui self-scoped
out on a measured file census rather than on prediction. Two advisory findings, neither gating:
V-01 line-anchor drift (BRIEF SC-04 and D-02 say the raw `Popen` sites are "near lines 305/309";
at the pin they are 315/319), and V-02 a miscitation inside the security note's own prose.

Goal-check (`2026-09-05-09-product`): all five criteria MET, each by its declared `verify:`
method, re-measured that run — `notes/research-BUG-1306-goalcheck-validate-c0.md`.

Two adequacy gaps the panel declared against itself are now CLOSED by orchestrator measurement,
not by inheritance:

- Reachability at the pin. Executing the pinned source with the single pop line replaced by
  `pass`, under `HARNESS_AGENT_TYPE=harness-orchestrator`, returns exit 1 with 14 `FAIL` lines
  (265 PASS) — the exact pre-fix shape the BRIEF measured at `c369fb1`. Run by compiling a
  mutated in-memory copy under the original `__file__`; no repo file was written, `git status`
  stayed clean. The suite CAN report red at this pin, so its green means something.
- The `unit` kind, which qa reported satisfied without executing it. Run here both ways:
  `env -u HARNESS_AGENT_TYPE` and ambient governed, each exit 0, 0 `FAIL` lines, 27 files and
  342 check lines discovered — the gate discovers work, so its green is not a silent no-op.

Log:

- 2026-09-05: feature instantiated; station `plan`.
- 2026-09-05: advisor consult settled scope and mechanism (D-01..D-04).
- 2026-09-05: BRIEF + plan drafted; goal-check PASS; SC-05 pinned to a merge-base diff.
- 2026-09-05: plan panel FAIL (one HIGH); finding closed, panel transcribed; plan phase ends.
- 2026-09-05: operator signed BRIEF and plan; station `building`.
- 2026-09-05: eng segment PASS (T-01, backend-dev, 0 send-backs); committed at 7e38d0ae.
- 2026-09-05: qa segment PASS — test_matrix gate green, `notes/qa-BUG-1306-integration.md`.
- 2026-09-05: simplify PASS — four angles, nothing applied; three residual notes.
- 2026-09-05: T-01 station `done`; build ends at the validate seam; pin moved to 536afda3.
- 2026-09-05: station `review` + mirror committed at da05ea28; pin re-pinned there, INV-33 clear.
- 2026-09-05: review panel PASS (severity_max info, no must_fix, code_grade pass).
- 2026-09-05: goal-check PASS — SC-01..SC-05 all met; validate ends. Ship is the operator's call.

## Open Questions

- For the operator, non-blocking (pm Q1, panel V-01): BRIEF SC-04's parenthetical "near lines
  305/309" and plan D-02 name anchors that the fix's own insertion shifted to 315/319. The
  criterion's SUBSTANCE holds and was graded met — the pop is at line 41, the sole module-scope
  `os.environ` statement, ahead of the first case body at 165 and both `Popen` sites. Both files
  are approval-gated, so correcting the numerals needs a signature. Fix post-ship, or leave the
  numbers and carry this note?
- For the operator, non-blocking (pm Q2, EMERGENT — reported, deliberately NOT adopted): no
  standing gate exercises this suite under a governed ambient identity. CI sets no
  `HARNESS_AGENT_TYPE`, so deleting the module-level pop would leave CI green and reintroduce
  the bug for agents alone. pm recommends a separate dev-ops ticket adding a governed-identity
  leg to the integration job; BRIEF's Advisor-set constraints put it out of scope here, and
  adopting an emergent criterion is not the orchestrator's to do.
- Harness defect, tool false positive, nothing to fix: `check-state.sh` INV-35 reports a
  VIOLATION on `plan.yaml:112` for an unquoted ` #1103`. The value IS quoted — a single-quoted
  flow scalar opened on line 111 — and `yaml.safe_load` returns the text with `#1103` intact
  (re-measured this run). The check is line-based and cannot see the continuation.
- Harness defect, affecting every worktree flow: a `notes/handoff-*.md` written from a worktree
  cannot use a pathless authority pointer (`plan-task:`, `brief-sc:`). `handoff_done_when.py`
  derives the feature dir from the note's worktree-stripped path joined to the MAIN checkout
  root, where no in-flight feature dir exists. Worked around again here with path-carrying
  `finding:` and `approval:` pointers.
- Harness defect, non-blocking: the checkpoint-key allowlist rejects `applied_fixes`, a plain
  counter of the kind DEC-154 admits.
- Harness defect, non-blocking: two of the builder's early edit-tool calls landed in the sibling
  MAIN checkout instead of the assigned worktree; the builder detected and reverted them, and
  the orchestrator confirmed the main checkout clean. Only a shell-holding tier can confirm
  this, which argues for a guard.
- Harness defect, non-blocking: qa (build phase) reported the Edit tool returning a
  current-file hash inconsistent with two fresh identical reads of the same file, in a worktree
  several agents run against concurrently.
- Recorded, not a defect: run dir `2026-09-05-05-validator` stays unrecorded ON PURPOSE — its
  own state.yaml reads `status: superseded`, both steps noting the record moved to
  `2026-09-05-06-validator`, which IS recorded. Recording both would double-count one panel.
