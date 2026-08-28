# CEO briefing — FEAT-42 One root resolver — plan phase, one ruling from signature

## The one-liner

**The plan is finished and verified — 20 tasks, 15 main-session-direct / 5 squad — and one
approval-gated edit stands between it and your signature.** SC-01 works today and breaks the moment
the plan is committed, because the plan quotes the variable 49 times precisely in order to remove it.

## How this briefing was assembled

No report round was spawned. I read the run digests from disk under
`.harness/harness/features/FEAT-42-one-root-resolver/runs/` — `2026-08-26-2-plan-product` (BLOCKED)
through `2026-08-26-6-plan-product` (ESCALATE). Every number below I re-derived myself.

## The one thing you must rule on

The lead reported SC-01 already broken at **72 occurrences across 19 files**. **That number is
wrong, and I checked rather than relaying it.** Measured over SC-01's actual scan set — `git ls-files`
minus basename `test-*`, minus `harness_boundary.py`, minus `*.md` — the count is **21 across 17,
exactly the recorded baseline.** The lead grepped the worktree, which includes untracked files.

**But its conclusion is right, one step later, and that is the part that matters.** The entire feature
directory is untracked today (`git status` shows `??`), which is the only reason `plan.yaml`'s 49
occurrences are invisible. I hold the commit pen and the plan artifacts must be committed. **The
moment `git add` runs, `plan.yaml` becomes tracked, the count passes 70, and SC-01 can never reach
zero.** The act of recording the work breaks the gate that grades it.

This is why I have committed nothing.

**The remedy, which the lead recommended and I endorse:** SC-01 gains a **fourth exclusion** for the
harness's own record tree — `.harness/harness/features/**`, `.harness/notes/**`, `.harness/logs/**` —
on exactly the rationale the `*.md` exclusion already carries: these are records that discuss the
variable by name and always will, not code. The existing `*.md` rule encoded that reasoning correctly
and was simply too narrow, missing `.yaml` and `.html` records. Crucially this **keeps
`.omp/extensions/harness-hooks.ts` in scope**, which is the entire reason you widened the scan.

**It needs you because it edits an approved success criterion.** That is not mine and not pm's.
Riding with it: the 21/17 baseline was itself derived by grepping `bin/` plus `.omp/` — a
directory-scoped measurement standing in for a repo-wide criterion, which is the very scoping defect
SC-01 exists to kill. It happens to be correct, which I confirmed independently, but it should be
re-pinned over the real scan set once the exclusions change.

## What is finished and verified

| Claim | How I checked it |
| --- | --- |
| 20 tasks, 15 main-session-direct / 5 team | parsed the YAML |
| Every task has `id`, `files`, `execution_mode`, `verify` | parsed — zero omissions |
| SC-01 widened repo-wide, baseline 21/17 | re-derived over `git ls-files` |
| T-07 re-laned, `depends_on` carries T-20, mutant outside the old scan root | read the task |
| `approval: pending` in both artifacts | read both |
| `harness-hooks.ts:144` is the only chain site outside `bin/` | repo-wide grep |

## Three findings that outlive this feature

**1. DEC-179's route check is blind to `verify:` blocks.** It resolves routing from each task's
literal `files:` paths. T-07's `files:` sat in a granted domain while its ungranted write lived in the
`verify:` command — so a task assigned to an agent that provably could not execute it passed pm, the
lead, and my own review, and was caught only by a lead reading the shell by eye. The mechanism meant
to make "an ungranted surface becomes a declared main-session-direct step" automatic never fired,
because it was looking at the wrong field.

**2. A stranded claim cascades upward through three tiers.** Reported earlier and now tasked. Worth
restating because it recurred: the same guard also blocks a parent that correctly declines to report,
so a parent whose dispatch went async has no legal way to yield while a child runs.

**3. The feature's own defect kept demonstrating itself.** `validate-feature-json.py` scanned the
wrong tree from my cwd and reported **"0 file(s)"** — confident, clean, wrong, and reading as a pass.
Pointed at the right root it found 38.

## What it cost

Cycles **3 of 10**, runs **5 of 20** — both comfortably inside budget. Three of the five runs returned
ESCALATE, and I want to be plain that this is the process working rather than thrashing: each one
found a real defect the previous review missed, and each was caught before build rather than after.
Two I resolved myself without spending your time — the T-07 lane (DEC-179 already prescribed it) and
a constraint I had wrongly imposed and then relaxed.

My context is ~25% over its advisory threshold, so I wrote the phase handoff at
`notes/handoff-plan.md`. A successor can take the SC-01 edit cold from it.

## Proposed backlog

| ID | Finding | Nature |
| --- | --- | --- |
| B-1 | DEC-179's route check ignores `verify:` blocks, so an ungranted write in a verify passes plan-time routing | bug |
| B-2 | `validate-digest.py`'s children-in-flight check blocks a parent that emits no verdict at all, leaving an async-dispatching parent no legal way to yield | bug |
| B-3 | DEC-174 am.4 needs amending to record the six scripts pm's category reading adds — issue #869, UNVERIFIED by me | chore |
| B-4 | `bash-write-guard.sh` may false-positive on an ASCII arrow inside a heredoc body, parsing prose as a redirect | bug |
| B-5 | The analysis note's Section 5 item 2 ("wayfind has ZERO test coverage") is false at HEAD | chore |
| B-6 | `gh_cost_log.py:111` derives root from its own file location — a caller cluster D-5's map omitted | bug |
| B-7 | An orchestrator cannot clear a stranded claim; no tier below the main session has both the need and the permission | enhancement |
| B-8 | D-05 records 20/16 while D-12 supersedes with 21/17, because `plan-merge.py` is add-only | chore |

Anything you do not strike becomes a backlog issue on acceptance. Anything not listed dies silently.
