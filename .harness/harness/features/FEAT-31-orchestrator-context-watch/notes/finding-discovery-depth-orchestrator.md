# FINDING — the discovery glob is one level too shallow, so the tool finds nothing by default

**BLUF.** `context-watch.py` reports `no orchestrators found` on every default invocation, because it
looks for session directories directly inside `~/.claude/projects` when the real layout interposes a
**project** directory. **103 `harness-orchestrator` sidecars exist and the tool sees 0 of them.**
Pointed one level down it works perfectly and reproduces the BRIEF's own FEAT-29 figure to the token.
This blocks **SC-01**, **REQ-01** and **REQ-05**.

The implementation is FAITHFUL to the signed plan — the plan's DISCOVERY clause is what is wrong, and
the plan contradicts itself about this. Found by the orchestrator during the T-01..T-13 eng run;
raised as a finding to be confirmed, not as a unilateral correction.

## The evidence

Measured on this machine at 2026-08-21, worktree `.claude/worktrees/FEAT-31`, HEAD e5f88c4:

| glob | matches |
|---|---|
| `~/.claude/projects/*/subagents/agent-*.meta.json` — what the code scans | **0** |
| `~/.claude/projects/*/*/subagents/agent-*.meta.json` — the real layout | **1999** |

Of those 1999, **103** carry `agentType: harness-orchestrator` (top types: `harness-pm` 263,
`harness-product-lead` 237, `harness-eng-lead` 201, `harness-backend-dev` 170). They sit in three
project dirs: `-Users-molchairuangutai-GitHub-harness` (89),
`-Users-molchairuangutai-GitHub-harness--claude-worktrees-fix-harness-tooling-backlog` (9),
`-private-tmp-uat-pyyaml` (5).

Run both ways, same binary, same machine:

- `context-watch.py --projects-dir ~/.claude/projects` (**what `main()` defaults to**) ->
  `no orchestrators found under /Users/molchairuangutai/.claude/projects`, exit 0.
- `context-watch.py --projects-dir ~/.claude/projects/-Users-molchairuangutai-GitHub-harness`
  (**one level down**) -> a full, correct table, exit 0. Sample rows:
  `a7783f0ec41e6a8c6 feature=FEAT-29 current=0 peak=696,472 entries=1046` and
  `a2565d59bd1cfd7c8 feature=FEAT-31 current=126,039 peak=126,039 entries=183`.

**The arithmetic is right.** That FEAT-29 peak of **696,472** matches `BRIEF.md:43` exactly
("FEAT-29's at 696,472"), and feature attribution, `current`, `peak` and `entries` all populate
sensibly. Only the discovery depth is wrong — which is why this is a small fix on a sound tool, not a
rewrite.

## Where the code and the spec meet

`discover_orchestrator_rows(projects_root)` (`context-watch.py:193-213`) iterates
`_safe_listdir(projects_root)`, joins `<name>/subagents`, and `continue`s when that is not a
directory. Given the projects ROOT, every child is a project dir whose `subagents` child does not
exist, so the loop `continue`s 23 times and returns `[]`. `main()` (`:261`) passes
`DEFAULT_PROJECTS_ROOT` straight in.

That is exactly what `plan.yaml:198-199` specifies: *"Under each session directory in the projects
root, read every subagents/agent-<id>.meta.json."* **The code is correct against the plan.** But the
same plan, two paragraphs earlier at `:195-196`, says *"Default projects root is ~/.claude/projects;
the directory for a cwd is that root joined with the slug of the cwd"* — which is the project level,
and correct. The two clauses cannot both describe the same directory. The tool also already carries
`transcript_dir_for_cwd()` (`:46-51`), which computes precisely the missing level and is **never
called by `main()`** — dead code that encodes the correct model.

## Why the task's own verify cannot catch it — the standing defect class, again

T-01's second verify line is
`context-watch.py --projects-dir /nonexistent-projects-dir 2>&1 | grep -qE "no orchestrator"`.
A tool that finds nothing *anywhere* satisfies it just as well as a correct one, because the broken
and correct states emit the identical string for a nonexistent directory. The assertion is green and
**incapable of going red for the reason it exists** — it was written to prove "no crash on an absent
dir" and it cannot distinguish that from "no discovery, ever". Both of this plan's previously repaired
verify blocks failed the same way; this is the third instance and it was not on the list.

The gate that WOULD have caught it is SC-01's live half, T-13's `verify-context-watch-live.py`, which
runs against real data — so the plan's own design does contain the catch. It just sits behind a task
that had not run yet.

## The fix, and the one judgement inside it

Discovery must descend one more level. The remaining choice is scope, and the BRIEF settles it rather
than leaving it open: **REQ-05** requires the reading to work "for an orchestrator running inside a
worktree, not only one running in the main checkout", and a worktree gets its OWN project dir (the
`fix-harness-tooling-backlog` slug above holds 9 orchestrator sidecars). A tool that scanned only the
cwd's project dir would fail REQ-05 whenever it was run from the main checkout. So discovery should
iterate **every project dir under the root, then every session dir within it** — which also keeps
`plan.yaml:236`'s "never read anything outside the projects root" and the OUTPUT clause's "every
orchestrator row is printed".

I am not editing the plan and I am not choosing this for the lead: SC-01 and REQ-01/REQ-05 are the
signed acceptance criteria and they are what the work owes. `plan.yaml`'s DISCOVERY sentence is a
plan-level defect for pm to correct at the next amendment, and it should be recorded as one even
though the SCs make the required behaviour unambiguous without it.

## Method

All figures re-derivable: globs over `~/.claude/projects` at 2026-08-21, `agentType` read with
`json.load` per sidecar, both CLI invocations run against the same file at HEAD e5f88c4. Note that
Claude Code transcript retention is 30 days, so the 1999/103 counts are a snapshot, not a constant.
