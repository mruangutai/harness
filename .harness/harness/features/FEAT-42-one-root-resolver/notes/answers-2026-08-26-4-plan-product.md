# Operator rulings, round 2 — FEAT-42 — 2026-08-26

Relayed by the main session. RULINGS, not proposals.

## Q1 — SCOPE IT IN

`.omp/extensions/harness-hooks.ts:144` reads verbatim `env: { ...process.env, HARNESS_PROJECT_DIR: cwd },`.
Verified by the operator and independently by the orchestrator.

**It is the ONLY occurrence outside `bin/`.** Orchestrator re-verified:
`grep -rn 'HARNESS_PROJECT_DIR' --include='*.ts' --include='*.js' --include='*.json'` across the repo,
excluding `/bin/` and `.git`, returns **exactly one code hit** — that line. Every other match is prose
in notes and observations. So this is one file, one line, one assertion. Not a second front.

### Three things the plan must do

1. **A task for `harness-hooks.ts:144`.** The env injection GOES. The script derives its own root
   under D-4, so handing it one is both redundant and the reopened hole. Enforcement-adjacent and
   outside every agent's domain -> **`main-session-direct`**.
2. **SC-01 must REACH it.** Its current scan root — tracked non-`test-` files under
   `.claude/skills/harness/bin/` — structurally cannot see `.omp/`. **Widen the scan root to every
   tracked non-test source file in the repo**, still excluding `harness_boundary.py`, still with **NO
   file list** in the assertion. Show it red at the NEW baseline before it goes green.
3. **Record the inheritance finding in the BRIEF**, so a reader six months out sees it was measured.

### THE CITATION NEEDS CARE — read this before writing it into the BRIEF

The operator cited `FEAT-40/observations/harness-orchestrator.md:58` as evidence the hole "has already
bitten". **The orchestrator read that line. It does not say quite that, and the BRIEF must not
overstate it.** The note reads:

> "I nearly recorded its failure as an artifact of my own invocation: the worktree run's message named
> MY worktree path, because the scratch clone's post-merge sweep inherited the HARNESS_PROJECT_DIR I
> had set, and feature-worktree.py remove then resolved the scratch worktree against the wrong root.
> **That reasoning was plausible and WRONG** — the main-clone run fails too."

What the note SUPPORTS: `HARNESS_PROJECT_DIR`, once set by a parent, is inherited by every child
process, and that inheritance was the author's mechanism for a misleading path in a failure message.

What the note DOES NOT support: that the inheritance caused a confirmed wrong-root failure. The author
explicitly labels that reasoning **"plausible and WRONG"**, because the test failed in the main clone
too. It is a considered-and-REJECTED explanation for one test failure.

**So write it accurately.** The durable, defensible claim is the mechanism, not a confirmed casualty:
env inheritance propagates a root to every child, and an orchestrator was misled by it far enough to
nearly file a wrong finding. That is real and worth recording. **Do NOT write "this defect has already
caused a failure" — the cited evidence does not carry it, and rule 15 says the record is what every
loop in the factory learns from.** If pm wants a stronger claim it must find stronger evidence and
cite it.

## Q2 — CONFIRMED. 13/6 stands.

DEC-174 am.4: *"A script that becomes a gate joins the list on the day it becomes one — the category
decides, the list records."* pm read it right; the wording was verified at `DECISIONS.md:5008-5009`.
No change.

## Q3 — YES, FILE IT. Do not task it here.

Six scripts joining the enforcement category makes am.4's list stale again, and am.4 obliges an
amendment when that happens. **File the ticket; do not task the amendment inside this feature.** The
decisions authority is not this feature's surface.

## Q4 — 1200 is RIGHT.

The cost was stated rather than hidden, which is what the operator wants. A legitimate run over 20
minutes losing its protection is the CHEAPER failure: tonight a stranded claim cascaded through three
tiers and locked the chain out of reporting, and recovery needed a shell only the main session holds.
**A too-short TTL self-heals; a too-long one needs the operator.**

## Carried forward, does NOT change FEAT-42

Probe #746 resolved: in the default configuration a subagent parent's dispatch returns "Async agent
launched" in ~1.5s with no result. With `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` the same parent
blocked 81.4s and received the child's real output. The variable is NOT set now. Transcripts at
`.harness/notes/probe-746-foreground-dispatch-2026-08-26.md`. This confirms the never-wait discipline
is correct rather than merely cautious. No FEAT-42 task changes.

## Unchanged

D-1..D-5 stand. The DEC-174 lane split stands. `HARNESS-FEATURE:` stays tasked separately. Every task
keeps a runnable `verify:`. Mutation proofs must assert the mutation APPLIED before trusting a
survivor. **Approval stays `pending` in BRIEF.md and plan.yaml — the operator signs.**
