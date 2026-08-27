# CEO briefing — FEAT-42 One root resolver — plan phase complete, awaiting signature

## The one-liner

**The plan is signature-ready: 19 tasks, 13 main-session-direct / 6 squad, all 20 chain sites covered
and SC-01 rewritten as a count-to-zero with no file list in it.** One question should be answered
knowingly before you sign — a hole the plan's own gate structurally cannot see — and I have measured
how far it actually reaches.

## How this briefing was assembled

No report round was spawned. I read the two run digests from disk:
`runs/2026-08-26-2-plan-product/digest.md` (BLOCKED) and `runs/2026-08-26-3-plan-product/digest.md`
(PASS). Everything I assert about `plan.yaml` below I verified against the file myself rather than
relaying the lead's numbers.

## What I verified rather than took on trust

| Claim | Verified |
| --- | --- |
| `plan.yaml` exists, 71,702 bytes | yes |
| 19 tasks | yes — parsed the YAML |
| 13 `main-session-direct` / 6 `team` | yes |
| Every task has `id`, `files:`, `execution_mode`, `verify:` | yes — zero omissions |
| All 16 env-chain files tasked | yes — each named in at least one task |
| `approval: pending` in plan.yaml and BRIEF.md | yes — `plan.yaml:5-6`, `BRIEF.md:172-174` |
| The 20-occurrence / 16-file baseline | yes — re-derived independently at `3952814` |

My earlier "15 files" was an undercount. Your 16 is correct, and I confirmed it before dispatching.

## The one thing to decide before signing

pm found, and I verified verbatim, that `.omp/extensions/harness-hooks.ts:144` runs every policy
script with `env: { ...process.env, HARNESS_PROJECT_DIR: cwd }`. Under D-2/D-3 a worktree legitimately
carries `.harness/team-config.yaml`, so an accidental cwd probes **valid** and is honoured as the
override. That is the input this feature exists to remove, walking back in through the override the
design deliberately keeps. The file sits outside `.claude/skills/harness/bin/`, so SC-01 cannot see it
and no task touches it.

**How far it actually reaches — my measurement, and it changes the answer.** `.claude/settings.json`
wires all nine live hooks to `${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/<script>`. None of them
is `harness-hooks.ts`. **So `:144` does not execute under Claude Code, the host running this feature.**
It executes under OMP — which DEC-202 makes canonical. The hole is real but host-conditional: it opens
when OMP becomes the runtime, not today.

That converts the question from "the plan ships a live hole" to "the plan ships a hole that arms
itself at the OMP cutover". Both answers let you sign. My recommendation: **accept knowingly and file
it against the OMP cutover** rather than widening FEAT-42 again — the feature already grew from 7
sites to 20 this cycle, and the defect cannot fire on the current host. But it must be a decision in
the record, not an omission, because the whole point of widening SC-01 was to stop exactly this shape
of gap from being invisible.

## Three smaller calls, none blocking

- **The lane split is 13/6, not 7/12**, because pm read DEC-174 am.4 as naming a *category* rather
  than a closed six-file list. The lead checked the wording verbatim at `DECISIONS.md:5008-5009` and
  endorses it. This is the single biggest determinant of task shape — worth a nod at signature.
- **am.4 itself needs amending.** It says a script joining the enforcement category means "this entry
  is amended when that happens". pm's reading adds six such scripts, and no task carries the
  amendment.
- **`CLAIM_TTL_SECONDS` becomes 1200.** The cost is stated rather than hidden: a legitimate run over
  20 minutes loses its protection.

pm also took **SC-11 off `verify: uat`**, settling it with a `test-dispatch-guard.py` case that drives
the real gate through its existing payload seam. That is the right instinct — an operator-only check
that is not really operator-only is a gate nobody fires.

## What it cost

Cycles 0 of 10. Runs 2 of 20. **Zero send-backs** — the plan passed first time. The one BLOCKED run
cost a spawn and produced the send-back criteria the successful run reused, so it was not wasted. Both
runs wrote their criteria *before* dispatching, so they could not be fitted to the answer.

Nothing is committed. No doer produced source and no gate ran; the tree holds plan artifacts only.

## Proposed backlog

| ID | Finding | Nature |
| --- | --- | --- |
| B-1 | `harness-hooks.ts:144` injects cwd as `HARNESS_PROJECT_DIR`, re-opening the override hole under the OMP host — if you accept rather than scope it | bug |
| B-2 | DEC-174 am.4 needs amending to record the six scripts pm's category reading adds to the enforcement layer | chore |
| B-3 | `validate-digest.py`'s children-in-flight check shares the dispatch guard's registry, so one stranded claim blocks a return as well as a dispatch — tasked in this plan, listed here in case the task is cut | bug |
| B-4 | The analysis note's Section 5 item 2 ("wayfind has ZERO test coverage") is false at HEAD; it is a signed input carrying a wrong fact | chore |
| B-5 | An orchestrator cannot clear a stranded claim — no tier below the main session has both the need and the permission | enhancement |
| B-6 | `gh_cost_log.py:111` derives root from its own file location; pm found it as a caller cluster D-5's map omitted | bug |

Anything you do not strike becomes a backlog issue on acceptance. Anything not listed dies silently.
