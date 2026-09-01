# Operator's stated intent — FEAT-50-run-artifact-integrity

Feature: FEAT-50-run-artifact-integrity · Run: plan phase, 2026-08-31
Recorded by harness-orchestrator from the main session's dispatch. This is the
intake artifact the plan is graded against at the panel's goal-check segment
(there was no grilling or wayfinding session; the dispatch is the stated intent).

## The mission

Plan — and only plan — the fix for three residual defects accepted at the
FEAT-45 ship briefing and filed as GitHub issues. No production implementation
in this phase. Deliverables are `BRIEF.md` and `plan.yaml`, both left
`approval.status: pending`; only the main session signs.

## The three defects, verbatim from the issues

- **#1056** (FEAT-45 B-4, bug): "Five structured returns came back empty or null
  across this feature and were only recovered because leads re-measured.
  `validate-digest.py`'s stop hook did not stop them."
- **#1057** (FEAT-45 B-5, bug): "Agents wrote feature artifacts into the main
  checkout rather than their worktree six times; three existed nowhere else. All
  recovered by hand."
- **#1058** (FEAT-45 B-6, bug): "A lead reusing a run directory across cycles
  overwrote an earlier lead digest, destroying the cycle-0 record."

## Constraints the operator stated

1. **Numbering.** New work starts at FEAT-50. FEAT-46 must never be created or
   referenced for this work. (This corrected an earlier numbering.)
2. **No regressions.** The two fixes FEAT-45 shipped must remain green:
   the missing-panel-finding-severity fail-closed fix (INV-32 in
   `check-state.sh`) and the zero-test-collection fix in the test runner.
3. **New deterministic regressions** for all three issues.
4. **Canonical commands must exit 0**:
   `.claude/skills/harness/bin/run-unit-tests.sh --kind unit`,
   `.claude/skills/harness/bin/run-unit-tests.sh --kind integration`, and
   `.claude/skills/harness/bin/check-state.sh`.
   See the open question below — the third does not hold today, for a reason
   unrelated to these issues.
5. **Scope is bounded** to these three issues and their tests. No unrelated
   documentation or enforcement changes.
6. **Stop conditions**: destructive data or history changes, contradictory
   governing decisions, or scope outside these issues.

## What the orchestrator measured before dispatching, at 75daa3b

These are premises, verified on disk, not conclusions about the remedy.

- **#1056.** `.claude/skills/harness/bin/validate-digest.py`, in `hook_mode()`:
  `text = d.get("last_assistant_message") or ""` followed by
  `if not text.strip(): ... return 0`. An empty or null return is passed through
  as *our* gap. It is indistinguishable there from a harness persona that
  genuinely produced nothing, which is a contract violation.
- **#1057.** `.claude/skills/harness/bin/check-domain.sh` matches the raw path
  and then the **worktree-stripped** path against the same globs (DEC-143), by
  design, so an agent inside a worktree writes exactly what its domain grants.
  The consequence is that a write to the **main checkout's** copy of the same
  feature path is equally domain-legal: nothing binds a write to the checkout
  the agent was dispatched into. The hook payload does carry `harness_feature`.
  `feature.json` has no `worktree` key and its schema is
  `additionalProperties: false`, so adding one is a schema change.
- **#1058.** `.claude/skills/harness-team/SKILL.md` §2 names run dirs
  `.harness/<repo>/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/` and states
  "the run dir is yours alone", but nothing enforces uniqueness and
  `<run_dir>/digest.md` is a plain overwrite.

Baselines at 75daa3b, for the no-regression criterion:
unit exit 0, `0` lines matching `^FAIL `, 1463 output lines;
integration exit 0, `0` lines matching `^FAIL `, 1945 output lines.
(Count `^FAIL ` lines and capture the runner's exit status separately — the
runner's last line is the last script's own summary, so a tail read of a red
suite reads green.)

## Routing, resolved at plan time (DEC-179)

`check-domain.sh --resolve` **grants** the enforcement scripts to
`harness-backend-dev`/`harness-dev-ops`, so the resolver alone does not route
them correctly. **DEC-174 governs and overrides the grant**: `check-domain.sh`,
`bash-write-guard.sh`, `validate-digest.py`, `check-state.sh`,
`check-plan-routes.py`, `dispatch-guard.sh` **and the test file of each** are
the enforcement layer, planned through the harness but never executed through
it. The FEAT-45 plan is the precedent: its T-07/T-08 (`check-state.sh` and
`test-check-state.py`) are `execution_mode: main-session-direct`, while
`panel_findings.py`, a library a gate imports, went to the team.

Measured `--resolve` verdicts:

| surface | resolve | lane |
|---|---|---|
| `bin/validate-digest.py`, `bin/test-validate-digest.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `bin/check-domain.sh`, `bin/test-check-domain.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `bin/check-state.sh`, `bin/test-check-state.py` | backend-dev, dev-ops | `main-session-direct` (DEC-174) |
| `skills/harness/SKILL.md`, `skills/harness-team/SKILL.md`, `skills/harness-handoff/SKILL.md` | NOBODY | `main-session-direct` |
| `.harness/harness/docs/DECISIONS.md` | harness-documentor | `team` |
| a new module a gate *imports* | backend-dev, dev-ops | `team`; the cutover that makes the gate use it is `main-session-direct` |

## Open question for the operator — raised by the orchestrator, blocking

**Constraint 4's `check-state.sh` clause cannot be met by fixing these three
issues.** Measured at HEAD in the main checkout: `check-state.sh` exits **1**
with **32 `INV-32` VIOLATION rows** — "plan is approved with no complete panel
result recorded" — one for every plan approved before FEAT-45 shipped the panel,
**including FEAT-45's own plan**, none of which carries a top-level `panel:`
key. INV-32 is retroactively red across the whole corpus. This was not disclosed
in the FEAT-45 ship briefing (B-7 discloses the same shape for INV-26, not this).

It is out of the stated scope and needs an operator ruling. Three options:

- **(a)** Scope INV-32 to plans whose `approval.date` is on or after DEC-207,
  so a plan that predates the panel is not asked for one. Smallest change;
  touches `check-state.sh`, which is `main-session-direct`.
- **(b)** Backfill a `panel:` key into 32 approved plans. Rewrites 32 signed
  records to describe a panel that never ran — falsifying the record, which
  PRINCIPLES rule 15 forbids. Recorded as available and not recommended.
- **(c)** Restate the criterion as: `check-state.sh` emits **no violation
  attributable to FEAT-50**, and the INV-32 row count is **identical before and
  after** this feature (32 at 75daa3b). Meets the intent of constraint 4 without
  touching the backlog, and leaves (a) as its own ticket.

Until this is answered the plan carries the criterion in form (c) with (a) named
as a decision the operator may take instead. Neither the orchestrator nor pm may
choose; it changes what "done" means.

---

# Operator rulings — recorded 2026-08-31, plan phase cycle 1

Recorded by harness-orchestrator from the main session's relay of the operator's
answers to the four open questions this plan phase returned (`STATE.md`
`## Open Questions`, `BRIEF.md ## Open ruling required from the operator`). These
are the operator's words as relayed, plus the consequence each one has for the
plan. Nothing below is the orchestrator's or pm's choice.

## Operator ruling — INV-32

```yaml
choice: d
who: operator
date: 2026-08-31
note: INV-32 is being fixed in another session; hold FEAT-50's signature and build
  until that fix lands. Do not alter INV-32 here and do not weaken the exact
  check-state exit-0 success criterion.
```

**Ruling, verbatim in substance:** INV-32 is being fixed in another session. Hold
signature and build until that lands. Do not alter INV-32, and do not weaken the
exact `check-state.sh` exit-0 success criterion.

This is none of options (a), (b) or (c) that the plan offered — it is a fourth
option the operator took instead, and it is recorded as `choice: d` rather than
forced into the a/b/c shape the BRIEF drafted, because recording it as (c) would
falsify what was ruled (PRINCIPLES rule 15).

**What it settles.**

1. **FEAT-50 plans NO INV-32 work.** Neither option (a)'s `approval.date` scoping
   nor option (b)'s 32-plan backfill enters this plan. `check-state.sh` is not
   edited by any task, and the lane row for it stays declared-but-unedited.
2. **The exit-0 criterion is restored, not weakened.** The operator's stated
   intent constraint 4 requires
   `.claude/skills/harness/bin/check-state.sh` to exit 0, and that clause stands
   as written. Form (c) — "no violation row names FEAT-50, exit code not graded" —
   was a WEAKENING and is refused. The criterion must require exit 0. The clause
   "no violation row names FEAT-50" may be KEPT alongside it, because adding a
   clause is not weakening one.
3. **Signature and build are BLOCKED on an external event.** The exit-0 criterion
   is not reachable from this feature's diff: the 32 retroactive `INV-32` rows are
   fixed in another session, outside FEAT-50's scope and outside its branch. So
   the plan is complete but UNSIGNABLE until that fix lands on the default branch
   and `check-state.sh` exits 0 with FEAT-50's directory present. That is a stated
   external blocker, not an unresolved plan defect, and it is the ONLY thing
   standing between this plan and signature.
4. **Q4 is unaffected.** See below.

## Operator ruling — the two open `high` panel findings

**Ruling:** fix both confirmed `high` findings. Do not overrule either.

`approval.rulings` is therefore NOT written — it exists only to record an
overrule, and no overrule was taken. Both findings are resolved in the plan
itself and `panel:` is re-transcribed afterwards from a fresh panel run, because a
reworded finding takes a new content-hash id and the old id stops applying.

- `PF-3d9ac1d054341cec6611f63aa2ce457a` (high, scope reader). The worktree binding
  reaches `check-domain.sh` only. Re-measured at `5d12e68`:
  `bash-write-guard.sh:747` reads
  `if verdict["outcome"] in ("allow", "not_a_domain_question"): continue`, so a
  governed agent's `cat >` / `perl -pi` at the same main-checkout feature artifact
  is allowed at exit 0 by a route the plan never reaches. **The plan must include
  the Bash governed-write route**, with the same binding, its own regression and
  its own reachability proof.
- `PF-964d635693c0db3e5803d36ed0df70a4` (high, scope reader). Re-measured at
  `5d12e68`: `test-validate-digest.py:738-739` asserts exit **0** for
  `hook_case("pass-through: empty last_assistant_message passes with a stated
  reason", "harness-qa", "", 0, mentions="no final message")` — exactly the
  payload D-01 redirects to exit 2. **The plan must reconcile that obsolete
  expectation explicitly**, in the task that owns the file, rather than leaving a
  main-session doer to invent the resolution unreviewed.

## Operator ruling — the fourth defect found live in this run

**Ruling:** expand FEAT-50 to cover it. It does not become its own ticket.

The defect, re-measured at `5d12e68`: `validate-digest.py`'s
`check_artifact_file` resolves a lead's RELATIVE `artifact:` path with
`os.path.join(_root_or_none() or "", path)` (`validate-digest.py:1414`), and
`_root_or_none()` (`:1343-1357`) resolves the root from the INSTALLED script's own
location, which is always the MAIN checkout. For every lead running in a worktree
the digest file is therefore not found, the DEC-156 file-shape check is SKIPPED,
and the hook prints a pass-through line nobody reads as a failure. Three lead
`digest.md` files in this very feature fail the DEC-156 contract and were passed
by this hook for exactly that reason.

Scope after this ruling is issues **#1056, #1057, #1058 and this defect** — and
nothing else. No other behaviour is authorized.

## Q4 — INV-6 versus a plan-phase validator run

**Ruling:** non-blocking, out of scope for FEAT-50. Unchanged from how it was
raised. It stays a harness-owner question and no task, requirement or criterion in
this plan addresses it.

## Operator report — the external INV-32 fix has MERGED (2026-08-31, later the same day)

Relayed by the main session mid-run, after the cycle-1 panel returned:

> The INV-32 fix has merged into main. The external hold is lifted. Finish the amended
> panel and return the pending approval gate; do not begin build. Main will update the
> feature branch from `origin/main` after the plan-phase commit.

**What this changes.** D-09's precondition is REPORTED MET. The hold it records was
never a defect in this plan — it was a stated dependency, and the dependency has
landed. Nothing in `BRIEF.md` or `plan.yaml` is falsified by this: D-09 states a
condition, and the condition is now satisfied rather than contradicted. No
requirement, task, decision choice or success criterion changes.

**What it does NOT change.**

1. **The plan phase still ends at the user gate.** `approval.status` stays `pending`;
   only the main session signs. Returning the gate is the completion of this phase,
   not a step before more work.
2. **Build does not begin.** The operator's instruction is explicit, and it agrees
   with the phase boundary this orchestrator was dispatched against.
3. **SC-11 is not yet gradeable in this worktree**, and that is expected rather than a
   failure. The feature branch has not been updated from `origin/main` — the main
   session does that after the plan-phase commit — so the 32 retroactive `INV-32` rows
   are still present here. SC-11 becomes gradeable once the branch carries the merged
   fix. The measurement recorded against SC-11 in `BRIEF.md` keeps its date and its
   sha and stays true as written.

## Orchestrator measurement — panel finding F-C1-01's reachability (panel Q3, non-blocking)

The cycle-1 panel raised one `med` finding whose PREMISE it could not settle without a
shell, and asked for the measurement. Taken here at `5d12e68`, in this worktree:

`HARNESS_PROJECT_DIR` appears in exactly one production file,
`.claude/skills/harness/bin/harness_boundary.py`, which READS it (`:65-73`). Every other
occurrence in the repository is a test fixture setting it for a subprocess, or a
`plan.yaml` describing that behaviour. **No production code SETS it.**

So a governed agent's resolved root is always the derived root — computed from the
INSTALLED script's own directory, which is the main checkout — and never a feature
worktree. With root equal to the main checkout, a main-checkout feature target is
inside root and cannot classify `not_a_domain_question`, which is the outcome
F-C1-01's consequence depends on.

**F-C1-01 is therefore a latent asymmetry and not a live hole today.** It is recorded,
not dismissed: it stays `disposition: open` at the reader's own `med`, because a
finding's severity is never reassigned and a premise that does not hold TODAY is not a
premise that cannot hold. It does not gate the signature — `med` is below INV-32's
gating threshold (`check-state.sh:218-219`) — and the operator may read it as advisory.
