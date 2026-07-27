---
name: harness-team
description: Run a harness team — a small DAG of agents hosted by a domain lead, passing state by file path. Use when asked to run a named team, to assemble a team for a goal, or to list the available teams.
---

# Harness: Team Runner

A team is a **DAG of steps, each dispatched to one agent**, hosted by a domain lead. This skill is
the algorithm; the teams are data at `.claude/skills/harness/teams/*.yaml`.

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

### 1. Resolve the team

`.harness/teams/<name>.yaml` first, then `.claude/skills/harness/teams/<name>.yaml`. Project
overrides win: the shipped directory is replaced wholesale on every `/harness-deploy`, so anything
project-specific has to live outside it (DEC-113).

**No team named?** List `name` + `purpose` from both directories and stop. The filesystem is the
registry — there is no catalog to keep in sync.

### 2. Open the run

```
.harness/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/
  state.yaml
```

**The run dir is yours alone.** `state.yaml`, collected DIGESTs, nothing a member writes. Do not
create per-step directories for members — they write into their own domains.

Seed `state.yaml` with `schema_version`, `run_id`, `feature`, `squad`, `host`, `status: running`,
and one `steps:` entry per team step with `status: pending`.

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

**d. Dispatch the rest of the ready set in one turn** — **all `Agent` calls in a single message**,
or they run one after another and the fan-out is lost. Parallelism here is implicit in the DAG, not
requested: any two `pending` steps whose `depends_on` are satisfied and which do not depend on each
other go together. Verified to work from inside a lead (DEC-100). Caps: 20 concurrent, 200 per
session, nested spawns counting toward both.

Each prompt carries the goal, the resolved **input paths**, the **output paths** the step must
write, and nothing else.

**Do not serialize out of caution.** A panel of reviewers dispatched one at a time still returns the
same verdicts, so the run looks correct while costing several times the wall-clock — the most
expensive way to be wrong, because nothing surfaces it. If steps genuinely conflict, that is what
`depends_on` and `mutates_repo` are for; encode it in the team rather than in how you dispatch.

**e. Collect returns and validate them mechanically.** Read `VERDICT` and the `DIGEST` fields,
record both in `state.yaml` — then check the digest against the schema rather than against your
own judgement:

```bash
.claude/skills/harness/bin/validate-digest.py <persona> <<< "<the member's return>"
```

**Your reading is not the check.** `severity_max: medium` instead of `med`, `must-fix` instead of
`must_fix` — you will normalize all of those charitably, which is exactly why drift is invisible
until one routing decision quietly goes the wrong way (DEC-101). A failing validation takes the
existing `BLOCKED (contract violation)` path. On a missing or malformed `VERDICT`, re-prompt
**once**, then record the violation — never infer what the agent meant.

*If you have no `Bash` (leads do not), you cannot run this yourself. Say so in your team digest and
the orchestrator validates on receipt — the same split as cost and the feature counter.*

**f. Apply `on_fail`.** Only on `FAIL`. `BLOCKED` and `ESCALATE` always stop the branch and go up —
they mean the agent could not proceed, not that its work was rejected, so retrying is wrong.

| `action` | Behaviour |
|---|---|
| `halt` | stop the run, report what completed |
| `continue` | record the FAIL and carry on — for advisory steps that must not gate |
| `loop_back` | re-dispatch a prior step with the failure report injected |

For `loop_back`:

1. **Choose the target by evidence, not by position.** Re-dispatch the step whose `files_touched`
   produced the rejected work, which `to:` names explicitly or the failing DIGEST identifies. With
   five eng specialists there is no single "build" step to fall back on, so guessing sends the fix
   to the wrong agent.
2. **`feed: [self]` means inject the failing step's report** — pass the reviewer's artifact **path**
   into the re-dispatched prompt, alongside the original inputs. Without it the target repeats
   itself verbatim and the loop cannot converge; this is the one place a return value must reach a
   later prompt, and even then it travels as a path.
3. **Count in your own `state.yaml`, not in your head — and not on the feature.** Increment the
   per-step `cycles` and write it before re-dispatching; re-read it at the top of every iteration,
   because the loop is exactly where a context reset happens. **Do not touch `feature.yaml`**: the
   feature-wide `cycles_used` / `max_total_cycles` is the orchestrator's, and the domain hook blocks
   you from writing it anyway. Report cycles spent in your team digest and let the orchestrator
   increment (DEC-119).
4. **Reset the downstream.** Steps that already ran after the target return to `pending`; their
   previous verdicts are stale the moment their input changes.
5. **Cycle-namespace the outputs of anything that re-runs.** Resolve `{{cycle}}` in output paths to
   the current count. A step with a fixed output path overwrites its own earlier attempt, so the
   PASS on cycle 2 destroys the FAIL report from cycle 1 — the evidence for why the cycle was spent
   (observed: DEC-117). Reviewer reports especially: the failing one is the record.
6. **On `max_cycles`, take `then:`** — `escalate` (up to the orchestrator, for the user) or `halt`.
   Never silently retry past the bound. An unbounded fix loop is the failure this counter exists to
   prevent.

**A note on convergence.** If the same step fails twice with the same reason, more cycles will not
help — say so in the escalation rather than spending the budget to prove it.

### 4. Close out

Set `status: complete` (or `failed` / `blocked`), then **write your team digest to
`<run_dir>/digest.md`** and report it as your `artifact:`.

**The team digest is a digest of digests, not a new document class.** Same shape as a member's,
plus the fields only you can supply: the per-member roll-up (`members:`), the union of `must_fix`,
`steps_run`, cycles spent, and your assessment of what the panel actually means. §10.4 is the
contract; `validate-digest.py <lead-persona>` checks it. **The `members:` block is not optional** —
it is what preserves per-worker granularity in `STATE.md` under hierarchy, and without it the
orchestrator cannot log who did what.

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
  headline: <one line — what the team achieved, not what it did>
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
