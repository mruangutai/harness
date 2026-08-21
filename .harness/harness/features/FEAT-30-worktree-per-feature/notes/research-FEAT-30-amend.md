# FEAT-30 amend round — the three items, applied. Plan stays UNSIGNED.

All three landed. `check-plan-routes.py` exits 0 with the three expected T-03/T-04/T-05 DEVIATIONs
and no VIOLATION. `approval.status` is still `pending`; `BRIEF.md ## Approval` is untouched at
`approved`.

Pre-write counts observed: `plan.yaml` 1171, `BRIEF.md` 219 — both matched the precondition.
Post-write: `plan.yaml` 1383, `BRIEF.md` 250.

## A. REQ-04 binds all sixteen. Anchors re-verified before citing.

`bash-write-guard.sh` at HEAD: `:50` reads `agent_type`, `:54-55` the exemption comment, `:56-57`
`if agent == "harness-dev-ops": sys.exit(0)`, `:58` the `harness-` prefix test. The handed anchors
were off by one; the dispatch's corrected set is what is cited.

Landed in three homes and no more (duplication is the drift this repo pays for):
`BRIEF.md` REQ-04 as `**SCOPED 2026-08-20, operator ruling — ...**` with the DEC-151 write-targets
reasoning and the accepted cost; `plan.yaml` `approval.rulings` R-01; and T-05's intent as a stated
requirement of the rule (`PLACEMENT IS A REQUIREMENT OF THIS RULE`). **No new `D-NN`.** I ran the
DEC-149 bar and all three legs hold, but a fourth restatement of one operator ruling is worse than
none — `approval.rulings` is the sanctioned home the `feature.json` gate itself named.

T-05 gains cases 10 and 11 as a **pair**: dev-ops REFUSED for a branch checkout (case 10 fails
against any implementation that places the rule after `:56-57`, which is what it is for), and
dev-ops still ALLOWED for a write the guard would otherwise check (case 11). Without 11, case 10 is
satisfied by deleting the exemption, which removes the recovery path.

### T-01, T-02, T-08, T-09 against the ruling — none needs a `HEAD` move.

- **T-09 is `main-session-direct`** (`plan.yaml`, T-09 `execution_mode`), not `harness-dev-ops`. The
  main session carries no `agent_type`, so this refusal cannot bind it at all. That is a *different*
  reason from "T-09 moves no HEAD", and it is the correct one. The framing I was handed was wrong;
  the correction I was given is right.
- **T-01, T-02, T-08 are `harness-dev-ops` and are genuinely in question.** None needs a `HEAD`
  move: T-08's verify contains no `git`; T-01's and T-02's contain only `git show <sha>:<path>`,
  which reads. Their tests fork git via `subprocess` inside python.
- **Q10's attributed measurement is now verified, not attributed.** `.claude/settings.json`
  registers `bash-write-guard.sh` on **PreToolUse Bash** only; `check-domain.sh` is PreToolUse
  `Write|Edit` and PostToolUse. A `subprocess` fork is not a tool call, so no hook fires on it.
  `notes/orchestrator-M16-sc01b-is-automatable.md` measured the same thing empirically.
- **One real defect the ruling creates, and it is fixed.** `git show` was in neither of T-05's two
  lists. Binding dev-ops means T-01's and T-02's own verify commands run under the rule, so an
  implementation reading its allow list as exhaustive would refuse a task's own verification. T-05's
  NOT-refused list now names read-only commit-naming commands (`show`, `rev-parse`, `merge-base`,
  `cat-file`, `ls-tree`, list-only `branch`, `worktree list`) and states that the **refuse list is
  the closed set** — only the UNDECIDABLE case is refused.

## B. SC-01b is `automated / integration`, owned by T-10.

Decomposition, each part with its disposition: the four-tree/distinct-file/HEAD-per-branch half is
already T-01's SC-01 cases; the **account budget and the board are out of scope by operator ruling**
(`BRIEF.md`, *Out of scope, deliberately*), so those clauses asserted what the brief excludes and are
**dropped, not automated**; Expertise contention is REQ-06/SC-08, already automated. What remains —
four concurrent writers, commits landing only on their own branch, no other branch advancing — is
what T-10 owns.

The `uat` was **not forced by the mechanism**, and this is measured, not reasoned back to:
`notes/orchestrator-M16-sc01b-is-automatable.md` drove the exact shape twelve times, zero
isolated-shape failures, and the shared-checkout negative detected four independent collision
signals. T-10 builds the measured shape rather than an invented one.

**The discriminating negative — the reason it can go RED.** One named module-level predicate,
`def assert_commit_isolation(trees):`, used twice. Case A: the four worktrees, per-tree assertions
(twelve absence assertions via `ls-tree -r` over each branch's full history plus
`merge-base --is-ancestor`, and every unrelated branch tip unchanged by sha). Case B: the **same**
driver against **one shared checkout**, requiring the same predicate to RAISE `IsolationViolation`,
with a `try/except/else` whose `else` is a failure. Anti-vacuity is enforced twice more: the driver
asserts the four write windows **pairwise overlapped** (a serialised fixture proves nothing about
contention), and the task's `verify` **neuters `assert_commit_isolation` by name in a copy and
requires the suite to go red**.

**Mechanical consequences, both discharged rather than left.** T-10 adds **no new test file** — it
extends `test-feature-worktree.py`, which T-08 already registers in `INTEGRATION_SCRIPTS` and in
`harness.json integration.detect`. That is deliberate: `run-unit-tests.sh:41-55` exits 2
MISCONFIGURED for any `bin/test-*.py` absent from either array, and `integration.detect` is an
explicit pipe list. A third file would have needed both, and T-08 is not reopened.

**Lane hand-check against DEC-174, done by hand because the checker cannot do it.**
`check-plan-routes.py` resolves `bin/**` to `harness-backend-dev harness-dev-ops` and would OK an
enforcement-layer file laned to the team. T-10's only file is
`.claude/skills/harness/bin/test-feature-worktree.py` — not `bash-write-guard.sh`, not
`check-domain.sh`, not `harness_boundary.py`, and not either guard's test file. It is nobody's gate.
**Verdict: legitimately `team`, `harness-dev-ops`.** No lane in the plan changed.

**Consistency.** `BRIEF.md`'s verification-gaps paragraph said *"10 of 12 criteria are `automated`"*
and named SC-01b as the `uat` one. That is now **11 of 12, and none is `uat`**, with SC-06 the one
remaining `inspection`. Leaving the old sentence would have been a rule-15 defect nothing detects
(DEC-188).

**Budget for failure, checked rather than adopted.** Recorded in `approval.rulings` R-02 alongside
the `max_total_cycles` 10 → 13 raise (verified at 13 in `feature.json`) under
`fix_surfaces_if_sc01b_fails`. The operator's provisional list is **two-thirds wrong**: T-02 cannot
fail SC-01b because T-10 never calls `remove`; T-05 cannot because its refusal is a PreToolUse Bash
hook and T-10's git calls are forks; T-06 cannot because T-10 asserts nothing about Expertise. The
real surfaces are **T-10's own fixture** (new concurrency code, the likeliest) and **T-01's `create`
and destination derivation**. The consequence for the budget: no SC-01b fix cycle lands in the
enforcement layer, so none costs the operator's own hands.

## C. must_fix M-1 discharged.

T-09 point 3 now states that **the main session runs the removal, from outside the tree**, never the
orchestrator from inside it — symmetric with point 1's attribution of creation, and citing why
(`check-domain.sh:428-431`, `bash-write-guard.sh:135-137`, `check-state.sh:1082-1085`, plus T-05 on
the Bash route). It adds that the orchestrator's part of a terminal state is to finish landing and
report; removal is not its act.

## Out of scope, untouched

Q11, Q12, Q13, Q14-Q16 were not acted on. Nothing here reaches them. FEAT-26/28/29/31 untouched; no
commit made.
