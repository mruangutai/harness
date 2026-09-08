# STATE

## Current

- feature: BUG-1309-mirror-build-entry
- run: .harness/harness/features/BUG-1309-mirror-build-entry/runs/2026-09-08-c14-validator/state.yaml
- squad: validator
- station: **review** (`plan.yaml:24`; moved from `building` by `gh-sync.py status … review`, which
  also put #1407 and its nine sub-issues at review). All thirteen tasks read `done`.
- `review_sha`: **da6da610b6576c6b844381377f2de0ab3daa5f62**. The panel and the goal-check both ran
  against **c8b23e03**, the first commit that CONTAINS the R-1/R-2/R-3 implementation (the prior
  d8f4dc49 pin predated it). The c14 record commit `da6da610` then wrote the station into `plan.yaml`,
  tripping INV-33 while the pin sat behind it, so the pin moved forward. **The re-pin reviews nothing
  new:** `git diff --name-only c8b23e03 da6da610` is confined to this feature's own directory and
  touches ZERO code paths — verified, not assumed.
- status: **NOT shippable.** The validate round ran and FAILED on a criterion, not on a gate.
- **Both approvals cover the current text.** `plan.yaml:3-6` reads `approved` / `Mike Ruangutai` /
  `date: '2026-09-08'`, the four 2026-09-06 `approval.rulings` intact at `plan.yaml:7-25`;
  `BRIEF.md:181-185` reads `approved` / `date: 2026-09-08`. The former Q2 (plan re-signature) is CLOSED.

### The gates are green, and green is not enough

Re-run by the orchestrator in the clean worktree at the pin, `env -u HARNESS_AGENT_TYPE`:
`tests/integration/test-merge-gate.py` exit 0 ALL PASSED · `tests/integration/test-gh-sync.py` exit 0,
323 ok / 0 FAIL · `tests/unit/test-gh-sync-build-entry.py`, `tests/unit/test-feature-schema-build-entry.py`
exit 0 · `tests/unit/test-omp-hooks.py` exit 0, 56 tests. The suite cannot see the defect below: no
fixture anywhere in `tests/integration/test-merge-gate.py` puts an option between `merge` and the ref.

### The gating finding — R-2 traded one hole for another (SC-04 clause (a), UNMET as BEHAVIOUR)

`git_merge` (`merge-gate.py:47-60`) returns `rest[index + 1]` the moment it matches the `merge` token,
so flag-skipping never resumes after the subcommand and the first option is taken as the branch.
`feature_for` then finds no owner and `main` returns with no permission decision.

Measured end-to-end through the real hook by the orchestrator, on a fixture recording
`branch: feature/test` + `github.build_entry: recovery-required` (`/tmp/bug1309-probe-e2e.py`, driving
the suite's own `fixture()`/`gate()` helpers):

| command | decision |
|---|---|
| `git merge feature/test` | **deny** |
| `git merge --no-ff feature/test` | **none — silent allow**, empty stdout AND empty stderr |
| `git merge --squash feature/test` | **none — silent allow** |

Against the pre-change source (`git show de04d841:.claude/skills/harness/bin/merge-gate.py`) both
escaping forms resolved to `feature/test` and denied. **They are a regression this delta introduced.**
The panel's scoping correction to the orchestrator's first, broader claim is accepted and recorded:
`git merge -m 'msg' X` (old parse → `msg`) and `git -C /repo merge --no-ff X` (old parse → not
detected at all) were ALREADY net-allow before the change — pre-existing holes closed by the same
remedy, not regressions.

Three independent readers reached this: `harness-code-reviewer` and `harness-security-reviewer` in the
c14 panel (`runs/2026-09-08-c14-validator/digest.md`, VP-01, high), `harness-pm` in the goal-check
(`notes/research-BUG-1309-goalcheck-c14.md`, F-04a — 7 of 16 enumerated operator merge forms reach no
deny; every other SC met, SC-10 pending-user), and the orchestrator's own probe above.

### Routing — no lead owns the remedy

`merge-gate.py` and `tests/integration/test-merge-gate.py` are DEC-174 enforcement-layer files. No
squad may execute the fix, so this routes to no lead and no fix cycle was opened. It returns to the
operator through the main session, exactly as R-1/R-2/R-3 were delivered.

### The rest of the panel — advisory, none gating alone; full text in the c14 validator digest

VP-02 (med) `takes_value` omits `--exec-path`, which signed T-05 step 2 (`plan.yaml:1029-1033`) names
while requiring the CLASS be handled — same remedy site. VP-03 (med) SC-04's stable-sorted-order clause
survives an unsorted mutant. VP-04 (med) no fixture combines `len(owners) > 1` with an era-exempt
claimant, though source order is correct (`merge-gate.py:150-155` precedes `:157-159`). VP-05 (med) the
`open` horn is asserted by no test and prints a command with no `<feature-dir>`; R-3 mandated it
verbatim, so it is contract-compliant, untested and unrunnable as printed at once. VP-06 (low) the
delta's own `single owner plus unrelated malformed record still allows` case is NON-DISCRIMINATING —
orchestrator-verified: `de04d841` already carried the `isinstance(document, dict)` guard at its line
107, so it passes identically against the pre-change source.

### Budget

cycles 13/14 — **UNCHANGED**. Both leads reported zero send-backs, and the unmet SC was not
re-dispatched to a squad because no squad may hold it (DEC-157 counts rework, and none occurred). One
cycle remains. runs 44 against a 20-run budget (INV-22, informational).

### SC-10 UAT — deliberately NOT requested

Remediation is not accepted, so no UAT was requested. Two reasons it must wait: the operator would be
hand-testing a build with a known silent-allow, and the script at
`notes/uat-BUG-1309-mirror-build-entry.md` issues only the bare `git merge feature/uat-scratch` form
(lines 155, 218, 239, 248, 274), so an operator PASS could not detect the escape.

### The canonical checker

`check-state.sh` findings about shared external worktrees and board/task divergence are NOT this
feature's current state and were not treated as clean or as cleared. Its BUG-1309 rows at this commit
are the INV-22 run-count note, five referenced-but-pruned run dirs, and several run dirs on disk that
`feature.json` does not record — pre-existing bookkeeping drift, none of it this round's work.

### Next, in order

operator fix of `git_merge` → regression cases for the post-subcommand-flag shape → VP-03/VP-04/VP-05/
VP-06 coverage in the same reserved bed → re-pin `review_sha` → re-run the panel over the new delta →
re-run the goal-check → add a `--no-ff` UAT step → SC-10 UAT → rewritten briefing → ship.

## Open Questions

- Q1 (blocking, operator — **the one actionable step**) — SC-04 clause (a) is unmet as behaviour:
  `git merge --no-ff <branch>` and `--squash` are a silent ALLOW where the pre-change gate denied.
  Fix or overrule. Shape of the fix, for convenience only: resolve the branch as the first non-option
  token AFTER `merge`, consuming merge's own value-taking options (`-m`, `-s`, `-X`, `--into-name`),
  and treat value-taking globals as a CLASS rather than a closed set — which signed T-05 step 2
  already required. DEC-174-reserved, so it cannot be delegated.
- Q2 (non-blocking, operator) — add a `--no-ff` step to the SC-10 UAT script, or accept that the hand
  test cannot see clause-(a) escapes. No script edit proposed.
- Q3 (non-blocking, coverage; depends on Q1) — VP-03/VP-04/VP-05/VP-06 are unpinned clauses and one
  non-discriminating case. Reserved bed, so they land with the Q1 fix rather than after it.
- Q4 (non-blocking, harness defect) — the `open` horn of the non-era recovery notice is specified by an
  UNNAMED intent bullet and asserted by no test. Backlog row, or a later amendment.
- Q5 (non-blocking, harness defect — **now observed twice**) — a lead run returned a complete,
  well-formed VERDICT/DIGEST/artifact and the host reported it `failed (exit 1)` with "Subagent called
  yield with null data": `harness-product-lead` earlier, `harness-validator-lead` in the c14 panel.
  Every claim in the c14 digest was verified against disk before it was used.
- The stale briefing at `notes/ship-review-2026-09-08-resume.md` and its B-1..B-13 backlog still await
  operator disposition; it is rewritten after the Q1 fix lands, before the ship decision.
