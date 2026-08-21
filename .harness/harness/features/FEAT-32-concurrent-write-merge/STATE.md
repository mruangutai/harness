# STATE — FEAT-32-concurrent-write-merge

## Current

Phase: **plan**, at its terminus. The amend round is **complete on substance**: all seven operator
rulings and the DEC-197 item landed in `plan.yaml`. `approval.status` is still `pending` — the
operator signs, and nothing here approves anything.

`plan.yaml` is **1692 lines / 108804 bytes, 15 tasks, 10 decisions**, committed on
`feat/FEAT-32` at **`7463b80`** as `+632/−152` against `6d83e91`, together with BRIEF.md
(`+118/−52`), pm's `notes/research-FEAT-32-ruling-amendments.md` and both observation logs. The tree
is clean. The file was last written at 11:59:37 by an **orphaned pm still running after its lead
closed**, so the commit is a snapshot of an orphan's output rather than of an acknowledged return —
every sample of it parsed, with the task, decision and approval counts intact at each one, and both
approval artifacts verified untouched and `pending` immediately before the commit. It grew from 13 tasks and 8 decisions because R3 and
R4 ruled two new surfaces IN: **T-14** makes the approval-block exclusion real in
`check-domain.sh`, **T-15** makes the three signer artifacts agree, and **D-09/D-10** record the
reasoning. Execution modes split 8 `main-session-direct` (T-01, T-07, T-08, T-09, T-11, T-12, T-14,
T-15 — every gate script and its test) and 7 `team` (T-02..T-06, T-10, T-13 — the libraries and the
docs), which is DEC-174 am.4's category test applied: a module a gate imports is not itself a gate.

**Ruling-by-ruling, verified by the orchestrator reading `plan.yaml` off disk at `c32f332`, not from
the lead's digest:** R1 — D-01's precondition records DISCHARGED, citing `47a9935` as an ancestor of
`c32f332`; the two-lock-dialect alternative is recorded rejected. R2 — no strike task exists, T-13
item 5 now reads "DEC-90 IS ALREADY STRUCK … merged as `16b30c6`", credits **FEAT-30** with
falsifying it, and carries a guard clause for a branch that is behind. R3 — D-09 records the wait as
an **impossibility** and ships two mechanisms that can hold: a once-only SubagentStop return contract
against false reporting, and D-06's unbounded PreToolUse refusal against the actual loss. R4 — D-10
rules the **main session** the signer on DEC-120 grounds and converts the comment into a check.
R5(a) — the vacuous lock-absence assertions are replaced by SIGKILL-then-second-apply cases, plus a
verify at `:750` that FAILS if a lock-absence assertion survives. R5(b) — **13** `export
CLAUDE_PROJECT_DIR="$PWD"` pins, far beyond the two anchors named. R5(c) — D-04 now reads "THE MAIN
SESSION — not the orchestrator". R5(d) — T-01 narrows to one key and its verify FAILS on a
re-measurement of the settled `agent_type`. R6 — occurrences 5 and 6 recorded, anchored to run dir
`2026-08-21-1-product`, with the gitignore note. R7 — #627, #560, #605 explicitly out of scope, no
task may absorb them.

**The run returned BLOCKED for a reason that is not about the work.** `runs/2026-08-21-2-product/`:
the SubagentStop hook forced `harness-product-lead` terminal while its only pm was in flight — #551
**occurrence 7**, live, one round after 5 and 6 were ruled in for recording. The lead reported
`files_touched: []` for pm and "no ruling can be reported as landed". **That is false about the
world, and true about the lead:** pm ran on as an orphan (DEC-131) until ~11:57 and its writes
landed. The lead had already done the thing that saved the round — it caught the stale worktree
*before* dispatching and redirected pm's three doc reads to the main checkout, so pm did not
"correct" the plan in the wrong direction.

`cycles_used` **0** of 10, 2 runs of 20. A forced close is not rework, and charging it would hide
the defect (DEC-157).

Route check re-run by the orchestrator at `c32f332`: `check-plan-routes.py` exits 0, **zero
VIOLATIONs**, 11 DEVIATIONs tree-wide of which **4 are FEAT-32's** — T-01, T-07, T-08, T-09, the
deliberate DEC-174 shape under DEC-179. A grep of that output for "FEAT-32" returns only 1; six
DEVIATION lines name `bin/` paths with no feature directory, so the id must be attributed per item,
not counted by grep.

## Open Questions

- Q1 **BLOCKING — the worktree is two commits behind `origin/main` and only the main session can fix
  it.** `git merge-base --is-ancestor` at `c32f332`: `16b30c6` (the DEC-90 strike) and `1d2b036`
  (DEC-197) are fetched objects but **not ancestors of HEAD**; `origin/main` is `1d2b036`. Both are
  **docs-only** (`git show --stat`: DECISIONS.md, DECISIONS-INDEX.md, SPEC.md), so no code or
  `harness.json` divergence — `test_kinds` is byte-identical between HEAD and `origin/main`. The
  concrete bite: T-13 mints the next free DEC number by reading the file, and this checkout's highest
  is **196** while `origin/main`'s is **197**, so a build run here would mint a **duplicate
  DEC-197**. pm defended against it in prose; the merge is the real fix. HEAD is frozen for every
  governed agent, so this is the main session's act.
- Q2 **BLOCKING — `plan.yaml`'s `approval:` mapping is granted to nobody, so "who signs" is a gap as
  well as a disagreement.** `check-domain.sh --resolve` on a plan.yaml prints `harness-orchestrator`
  **and** `harness-pm`, exit 0 — both may write the whole file including the mapping, and
  `grep -n approval check-domain.sh` returns exactly one line, `:858`, a comment. Meanwhile
  `team-config.yaml:18` grants the main session only the pre-DEC-182 **heading** forms
  (`BRIEF.md ## Approval`, `PLAN.md ## Approval`) and names the mapping nowhere. D-10 and T-14/T-15
  are the plan's answer; the operator should confirm the direction — extend the grant, or enforce the
  exclusion with no positive grant anywhere.
- Q3 **NOT blocking, and the answer is no.** The lead asked to approve one clean re-dispatch of one
  pm. **It is not needed and should be declined:** pm's amend is on disk, parses, and carries every
  ruling. A re-dispatch would be a second pm against the same file — the exact #628 shape this
  feature exists to prevent. Two residual one-line fixes are all that is left, in Q4.
- Q4 **NOT blocking — two citation defects, pm's to fix, not mine (I hold no write on the field).**
  (a) `dec: DEC-129` on **D-04** (`:151`) and **D-10** (`:295`) miscites: DEC-129 spans
  `DECISIONS.md:2946-2969` and contains **zero** occurrences of "approval" — it is about feature
  folders and `## Problem` before `## Goal`. The real authority is **DEC-120 at `:2423`**. The same
  wrong citation sits in `team-config.yaml:90-91`. (b) D-04's `because` says the main-session writes
  list "is the only place any signer is granted"; per Q2 that list never names the mapping, so the
  claim overstates.
- Q5 **NOT blocking — DEC-174 am.4's enumeration omits a gate that is demonstrably one.** The list at
  `DECISIONS.md:4851-4853` names `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
  `check-state.sh`, `check-plan-routes.py` and their tests. **`dispatch-guard.sh` is absent, and it
  refused this orchestrator's own dispatch this run** (a `model:` parameter, per DEC-152/DEC-155).
  "The category decides, the list records" means T-07/T-08 are correctly `main-session-direct`; the
  list should be amended to record it. pm's routing already assumes this.
- Q6 **NOT blocking — the 8-file kind divergence is still live and is not what DEC-197 fixed.**
  `run-unit-tests.sh:18` lists 14 `INTEGRATION_SCRIPTS`; `integration.detect` names 6 explicitly, so
  8 files run as integration while the qa matrix reads them as unit: `test-validate-digest.py`,
  `test-check-expertise.py`, `test-gen-decisions-index.py`, `test-bash-write-guard.py`,
  `test-check-domain.py`, `test-harness-yaml.py`, `test-upgrade-config.py`,
  `test-merge-settings.py`. Identical at `c32f332` and at `origin/main`. T-10 is scoped to close it.
- Q7 **NOT blocking — the orchestrator playbook instructs a write the schema rejects.**
  `.claude/skills/harness/SKILL.md` says to record the phase in `feature.json` `phase:`;
  `bin/feature-schema.json` sets `additionalProperties: false` and has no `phase` property, so the
  write would be invalid. This STATE.md carries the phase instead.
