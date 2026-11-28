# FEAT-2557 — ship review — 2026-11-27

**Ready to ship.** The second validate run (`r-20261127-2-validate-validator`) passed at
`afd20116` with an empty must-fix list and maximum severity `low`. Every perspective in the
definition of done is met. The feature used its one rework round: c1 found that DEC-259 presented
FEAT-70 as following the no-shim rule when it does not, and a one-paragraph fix closed it.

No report round was spawned. I assembled this from the four run digests that `feature.json`
`runs:` names:
- `runs/plan-product/digest.md`
- `runs/revise-product/digest.md`
- `runs/r-20261127-1-validate-validator/digest.md`
- `runs/r-20261127-2-validate-validator/digest.md`

## Definition of done, graded (validate c2 goal-check)

| Perspective (as signed) | Verdict | SCs | Evidence |
|---|---|---|---|
| **code maintainer** — When I split a long file, in any repository Harness builds, the skill I already load tells me where the split lands and what the modules are called; in Harness `bin/`, one short file tells me the Python mechanics and shows me the two existing examples. | met | SC-01, SC-03, SC-04 | `notes/research-FEAT-2557-code-layout-pattern-goalcheck-validate-c2.md`; c2 digest `sc_status` |
| **reader** — I can name a layout defect as a finding by pointing at a written rule, rather than at my own taste. | met | SC-02 | same; SKILL.md Applying-it bullet |
| **operator** — The convention and where it came from are in the decision record, so I can audit it later without reconstructing FEAT-69/70 from history, and this change touched only the prose it promised. | met | SC-05, SC-06 | same; DEC-259 at the pin; scope is exactly five files outside the feature directory |

## What shipped (T-01, main-session-direct, five files)

- `harness-codebase-design`: a language-neutral `## Layout — where a split lands` section, plus one
  Applying-it bullet that turns five layout defects into review findings.
- `.claude/skills/harness/bin/LAYOUT.md`: the Harness Python mechanics (21 lines).
- `AGENTS.md`: a project map row and a Conventions bullet with no path in it.
- DEC-259 and its index row.
- Preload: eng-lead rises from 4931 to 5178 of 5500 words, and no agent is over budget.

## Lead summaries

- **plan-product** (PASS): BRIEF with six inspection SCs and a 3-task plan. Signing it surfaced
  INV-32 (a patch must be one task).
- **revise-product** (PASS): under your INV-32 ruling, collapsed the plan to one main-session-direct
  task. The BRIEF changed only in its routing bullet.
- **validate c1** (FAIL): code-reviewer, substance/high. DEC-259 presented FEAT-70 as conformant,
  but `plan-merge.py` still re-exports `signed_task_hash` for INV-40's path loader. qa, security,
  ui and goalcheck passed. The lead sided with code-reviewer over pm after verifying at source.
- **validate c2** (PASS): the fix is confirmed closed by execution, with no regression. The four
  unchanged files are byte-identical to the c1 pin.

## Amendments

| at | decision | reason | overruled |
|---|---|---|---|
| 2026-11-27T15:01:46Z | T-01.files | INV-32 ruling: one main-session-direct task folds the old T-02/T-03 files in | no |
| 2026-11-27T15:01:53Z | T-01.intent | same ruling | no |
| 2026-11-27T15:01:54Z | T-01.verify | same ruling | no |

overrule rate: 0/3. These three record pm's plan revision before re-signature, not departures
made during the build. They read `by: main-session` although pm wrote them; that is filed as #2563.

## Spend and ledger

- Runs: 4. Wall clock: 28 min, of which rework took 14 min, inside the 45-minute ruling. Rework
  rounds: 1 of 1. cycles_used: 0 of 10.
- Measured tokens: 143,666, from the two product runs only. Both validate runs carry `tokens: null`:
  the host stamps tokens onto the orchestrator's open run, and in this main-session-direct feature
  the main session dispatched the validator lead directly, so nothing stamped them.
- Judgements: 7 (mission, 3 amendments, 2 successions, 1 regate).

## Open questions and escalations

None open. Escalations: none. The three non-gating c1 questions are in the backlog below.

## Process notes

- **The schema-field bug recurred four times in this feature.** Every task dispatch I made to a
  harness lead or orchestrator carried `outputSchema`/`schemaMode`, including two right after I
  stated the call would not. The guard accepted each one, and the hook re-injected the canonical
  bundle, so no run was affected. Instructions don't prevent it; see B-5.
- **A receipt raced its own evidence.** The fix-c1 receipt was first written in parallel with the
  re-verify, so it captured the earlier failing output. I caught it before committing and rewrote it
  with the passing output.

## Proposed backlog

Strike any row by ID. Unstruck rows become backlog issues on ship acceptance.

| ID | Nature | Item |
|---|---|---|
| B-1 | chore | Migrate check-state INV-40's path loader (`check_state/ctx.py` `_load_hash_module`) to import `plan_merge.approval.signed_task_hash` directly, then drop `plan-merge.py`'s re-export, the one DEC-259 deviation (c1 OQ-1). |
| B-2 | enhancement | Decide whether the language-neutral Layout section should carry a DEC-259 pointer, as DEC-158's "rule + why + DEC pointer" asks, given the skill binds every repository and DEC-259 lives in Harness's DECISIONS.md (c1 OQ-2). |
| B-3 | chore | Rewrite DEC-149's "doers receive harness-codebase-design by dispatch, not preload" under DEC-205: eight agents autoload it (c1 OQ-3). |
| B-4 | chore | DEC-259 wording: "with one exception" can read as FEAT-70 being an exhaustive precedent, while `plan_merge/guards.py` is grouped by kind. Describe the shared shape without an exception count (c2 low form advisory). |
| B-5 | bug | For `harness-*` targets, the task hook should strip any caller-supplied `outputSchema`/`schemaMode` and always re-inject the bundle, or move the schema to agent frontmatter `output:`, so dispatchers cannot copy the fields at all. It recurred four times here. Fold into #2482 rather than open a duplicate. |
| B-6 | chore | QA's six low guard weaknesses in T-01's one-shot verify (vacuous post-commit `git diff HEAD`, `-w` missing inflections, a case-sensitive heading guard, line-not-occurrence counting, DEC extraction to EOF, a letter-only language guard). Applies only if the verify pattern is reused as a template. |

Already filed during this feature: #2562 (gh-sync has no verb to drop one task's card), #2563
(amend judgements ledgered as `by: main-session`), #2564 (check-state from the control plane skips a
worktree's feature).

## Instruction needed

Ship, fix, re-scope or stop. Shipping opens the PR from `feat/FEAT-2557-code-layout-pattern`; the
merge stays yours.
