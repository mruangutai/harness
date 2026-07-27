---
name: harness-crew
description: Run a harness crew — a small DAG of agents hosted by a domain lead, passing state by file path. Use when asked to run a named crew, to assemble a crew for a goal, or to list the available crews.
---

# Harness: Crew Runner

A crew is a **DAG of steps, each dispatched to one agent**, hosted by a domain lead. This skill is
the algorithm; the crews are data at `.claude/skills/harness/crews/*.yaml`.

**You are the host.** If you are a lead, you are running your own squad's DAG. If you are the main
session, you are running it flat. The algorithm is identical either way — only who spawns differs.

## The two rules that make this safe

**State passes by file path, never by conversation.** A step's return is control flow only. The
artifact is a file; the next step is told its *path* and reads it. Pasting a previous step's content
into the next prompt defeats the context budget the org exists to protect.

**Every step writes only inside the producing agent's own domain.** Members cannot write the run
dir — that is the lead's — so a step told to stage output there is blocked by `check-domain.sh` on
dispatch (DEC-116). Each member already owns a namespaced artifact path, and that is what keeps
outputs disjoint when steps run in parallel.

## Process

### 1. Resolve the crew

`.harness/crews/<name>.yaml` first, then `.claude/skills/harness/crews/<name>.yaml`. Project
overrides win: the shipped directory is replaced wholesale on every `/harness-deploy`, so anything
project-specific has to live outside it (DEC-113).

**No crew named?** List `name` + `purpose` from both directories and stop. The filesystem is the
registry — there is no catalog to keep in sync.

### 2. Open the run

```
.harness/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/
  state.yaml
```

**The run dir is yours alone.** `state.yaml`, collected DIGESTs, nothing a member writes. Do not
create per-step directories for members — they write into their own domains.

Seed `state.yaml` with `schema_version`, `run_id`, `feature`, `squad`, `host`, `status: running`,
and one `steps:` entry per crew step with `status: pending`.

### 3. Loop

Until every step is terminal, or you halt:

**a. Compute the ready set** — every `pending` step whose `depends_on` are all `complete`.

**b. Checkpoint BEFORE dispatching.** Write `dispatched_at` into `state.yaml` *before* the spawn,
`completed_at` after the return. A step with the first and not the second is provably in flight,
which is what makes every recovery case decidable. Cycle counters live in `state.yaml` and are
re-read each iteration — never carried in your head, because your context may not survive.

**c. Serialize anything that mutates the repo.** Steps with `mutates_repo: true` dispatch **one at
a time**, even when the DAG would allow parallelism. This is the actual write-safety mechanism —
`check-domain.sh` cannot see writes made through `Bash`, and every doer holds it (DEC-85). Do not
treat a passing domain hook as proof that parallel writes are safe.

**d. Dispatch the rest of the ready set in one turn** — one `Agent` call per step, all in the same
message so they run concurrently. Each prompt carries: the goal, the resolved **input paths**, the
**output paths** the step must write, and nothing else. Caps are 20 concurrent and 200 per session.

**e. Collect returns and evaluate.** Read `VERDICT` and the `DIGEST` fields. Record both in
`state.yaml`. On a missing or malformed `VERDICT`, re-prompt **once**, then record
`BLOCKED (contract violation)` — never infer what the agent meant.

### 4. Close out

Set `status: complete` (or `failed` / `blocked`) and report.

**Do not try to run `cost-report.py` if you are a lead — you have no `Bash`.** Leads hold
`Read, Glob, Grep, Agent` deliberately, so they cannot do a member's work; the same grant also
stops them metering their own run (DEC-116). Set `cost: pending_orchestrator` and let the
orchestrator fill it after you return:

```bash
# ORCHESTRATOR ONLY, after the lead returns:
.claude/skills/harness/bin/cost-report.py --yaml >> <run_dir>/state.yaml
```

This is the right owner anyway — the orchestrator already owns the feature-level cost rollup in
`feature.yaml` (§11.3) and is the only tier that can see every squad's runs. A complete run left
without a `cost:` block is an INV-11 violation: an unmetered run is indistinguishable from a free
one, and cost is the post-build signal (DEC-99).

**Timestamps, same cause.** No `Bash` means no clock, so use monotonic ordering markers
(`seq-1`, `seq-2`, …) rather than inventing wall-clock times. The checkpoint property does not need
real time — "dispatched with no matching completion" is decidable from presence alone.

Report per-step verdicts and the run dir path. Not the artifacts' contents — their paths.

## Reporting up

```
VERDICT: PASS | FAIL | BLOCKED | ESCALATE
DIGEST:
  headline: <one line — what the crew achieved, not what it did>
  steps: [<id>: <verdict>, ...]
  files_touched: [<paths>]
  cost_usd: <from the cost block>
  open_questions: [...]        # non-empty = the orchestrator must ask the user
artifact: <run_dir>/state.yaml
```

## Red flags

| Thought | Reality |
|---|---|
| "I'll paste the plan into the next step's prompt" | State passes by path. Pasting burns the budget the org exists to protect |
| "I'll have the step write its notes to the run dir" | Members cannot write there. It is blocked on dispatch — put outputs in the agent's own domain |
| "Both steps mutate the repo, but the DAG allows parallel" | `mutates_repo: true` serializes. The domain hook cannot see `Bash` writes |
| "I'll track the cycle count as I go" | It lives in `state.yaml`. Your context may not survive to the next iteration |
| "The agent clearly meant PASS" | Missing `VERDICT` is `BLOCKED (contract violation)` after one re-prompt. Do not guess |
| "I'll dispatch these one at a time to be safe" | Independent, non-mutating steps go in one turn. Serial dispatch wastes the fan-out |
| "I'll write state.yaml at the end" | Checkpoint before dispatch, or a crash leaves an undecidable run |
