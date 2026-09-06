# STATE

## Current

- feature: BUG-1306-agent-type-hermetic-tests
- run: .harness/harness/features/BUG-1306-agent-type-hermetic-tests/runs/2026-09-05-09-product/state.yaml
- squad: none
- status: validate-complete — SHIP-READY at review_sha `6b2ef992`

Validate phase COMPLETE, no fix cycle required. `cycles_used` stays 1 of 8: every segment
returned PASS with zero send-backs. Feature station is `review`; the GitHub mirror is open
(parent #1309, T-01 #1310, milestone 45). `check-state.sh` now exits **0 with zero violations
repo-wide**. Handoff at `notes/handoff-validate.md`. Nothing merged, shipped, or pushed.

The pin moved twice, both times for paperwork, never for code. `536afda3` → `da05ea28` closed
INV-33 after the `building` → `review` station write postdated the pin; `da05ea28` → `6b2ef992`
followed the owner's INV-35 remediation. The executable payload is IDENTICAL across all of them:
`tests/integration/test-plan-merge.py` is the same blob object `8fde5efc9c05eac9f3f312dd6191b45c89ad2f23`
at `7e38d0ae`, `536afda3`, `da05ea28`, `6b2ef992` and `e2bf649c`, and the diff of `tests bin
.claude .agents *.py *.sh` between the pins is empty. Every build- and panel-phase measurement
therefore transfers by object identity, not by trust.

The owner's remediation (`6b2ef992`, pin-only follow-up `e2bf649c`) changed exactly one panel
string — finding PF-15e50cd…'s `consequence` now reads `issue 1103` where it read `#1103` —
and nothing else: all six finding ids, `approval: approved`, `status: review` and T-01 `done`
survive a `yaml.safe_load` re-read unchanged. INV-35 is now green, so the false positive is
worked around in the data rather than fixed in the checker; the checker defect stands below.

Panel (`2026-09-05-08-validator`, review team, cycle 0): PASS, severity_max `info`, `must_fix`
empty, `code_grade: pass`. All four reviewers ran and reached their own verdict — ui self-scoped
out on a measured file census rather than on prediction. Two advisory findings, neither gating:
V-01 line-anchor drift (BRIEF SC-04 and D-02 say the raw `Popen` sites are "near lines 305/309";
at the pin they are 315/319), and V-02 a miscitation inside the security note's own prose.

Goal-check (`2026-09-05-09-product`): all five criteria MET, each by its declared `verify:`
method — `notes/research-BUG-1306-goalcheck-validate-c0.md`. Re-measured again at the final pin:
governed run exit 0 / 0 FAIL with both SC-02 literals present, clean run exit 0 / 0 FAIL, and the
merge-base diff names 23 paths — the one test file plus 22 lifecycle artifacts, no `bin/` path
and no second test file.

Two adequacy gaps the panel declared against itself are CLOSED by orchestrator measurement, not
by inheritance:

- Reachability at the pin. Executing the pinned source with the single pop line replaced by
  `pass`, under `HARNESS_AGENT_TYPE=harness-orchestrator`, returns exit 1 with 14 `FAIL` lines
  (265 PASS) — the exact pre-fix shape the BRIEF measured at `c369fb1`. Run by compiling a
  mutated in-memory copy under the original `__file__`; no repo file was written.
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
- 2026-09-05: goal-check PASS — SC-01..SC-05 all met; validate ends.
- 2026-09-05: owner normalized the INV-35 panel text (6b2ef992) and re-pinned (e2bf649c); delta
  validation confirms identical executable blobs, check-state exit 0, criteria still met.

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
- Harness defect, WORKED AROUND in the data but NOT fixed in the tool: `check-state.sh` INV-35
  is line-based and cannot see a quoted multi-line scalar, so it reported a VIOLATION for a
  ` #1103` that `yaml.safe_load` returned intact. The owner resolved this feature's instance by
  rewording the panel text to `issue 1103`; the checker will false-positive again on the next
  quoted continuation line that carries an issue reference.
- Harness defect, affecting every worktree flow: a `notes/handoff-*.md` written from a worktree
  cannot use a pathless authority pointer (`plan-task:`, `brief-sc:`) — `handoff_done_when.py`
  joins the worktree-stripped path to the MAIN checkout root, where no in-flight feature dir
  exists. Nor can it use `finding:`: FINDING_RE demands `F-\d+`/`PF-\d+`, pure digits, while
  every real finding id here is non-numeric. The only binding authority left is
  `approval:<path>#<heading with no status line>`, which is what this feature used twice.
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
