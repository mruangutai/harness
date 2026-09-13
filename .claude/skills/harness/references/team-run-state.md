# Run state — seeding `state.yaml`, expanding `steps_from:`, and `loop_back` bookkeeping

Read this when seeding `state.yaml` (`harness-team` §2), again whenever the team file carries a
`steps_from:` expansion rule instead of a literal `steps:` DAG, and again before re-dispatching a
step under `on_fail: loop_back` (§3f). The skill carries the rules — seed before the first
dispatch, checkpoint not notebook (DEC-154), cycles are send-backs counted in your `state.yaml`;
this is the key contract and the procedures. Evidence and history: DEC-117, DEC-119, DEC-154,
DEC-157, DEC-182, DEC-223.

## Seed keys

Top level: `schema_version: 2`, `run_id`, `feature`, `squad`, `host`, `status: running`, and one
`steps:` entry per team step with `status: pending`. `check-domain.sh` refuses a **new** run
checkpoint at any `schema_version` below 2; only updates to an already-existing version-1
`state.yaml` retain compatibility.

`run_uid` is minted by the harness on the first landed write. A lead never invents, edits, or drops
it, and every later write carries the same value read from the file itself.

## Step keys — version 2 closes each step to

`id`, `persona`, `task`, `seq`, `depends_on`, `outputs`, `mutates_repo`, `on_fail`,
`status`, `verdict`, `lead_verdict`, `cycles`, `max_cycles`, `redispatches`,
`dispatched_at`, `completed_at`, `redispatched_at`, `recompleted_at`, `routed_by`,
`note`, `artifact`, and `evidence`.

The declared set is `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/run-state-schema.json`,
and `check-domain.sh` refuses a write carrying any other step key. A per-step fact a dispatch asked
for goes under `evidence` with a lowercase identifier key (`^[a-z][a-z0-9_]*$`); it is never a new
step key and never a sentence used as a key. Each evidence value is a scalar or an array of scalars.
Nested objects are refused, and a value that must be read rather than matched still belongs in
`digest.md`.

## Expanding `steps_from:`

A team file carries EITHER a literal `steps:` DAG OR a `steps_from:` expansion rule, never both.
With `steps_from:`, expand it into concrete steps FIRST, then seed exactly as above:

1. **Read the source it names.** `plan_tasks` =
   `<HARNESS_FEATURE_TREE_ROOT>/.harness/harness/features/<feat>/plan.yaml`'s `tasks:` list, loaded
   with `harness_yaml.load_plan`. A feature still on the pre-DEC-182 format uses `PLAN.md`'s
   `## Tasks` instead — the two never coexist, and `check-plan-routes.py` refuses a feature carrying
   both.
2. **Take the task ids the caller handed you.** WHICH tasks arrive is the orchestrator's decision,
   already made, and no key in the file re-states it. A task the caller did not hand you is **not**
   silently dropped: it stays for the orchestrator to sequence as its own squad segment (DEC-118).
3. **Route each task to a member by `consult-when`** (`persona: by_consult_when`) — that IS your
   decision.
4. **Prompt.** With `prompt: from_task_intent`, each step's prompt is the task's own `intent:` block.
5. **Dependencies.** With `depends_on: from_task_depends_on`, build `depends_on` from each task's own
   `depends_on:` field, falling back to file order only for tasks declaring none — **file order is
   not a topological order**.
6. **Templates.** Substitute `{{task_id}}`/`{{persona}}` into the `id` and `outputs` templates.

From there the algorithm is unchanged.

## `loop_back` bookkeeping

Only a `FAIL` triggers `on_fail`; `BLOCKED` and `ESCALATE` stop the branch and go up. For
`loop_back`:

| What | Do |
|---|---|
| **target** | re-dispatch the step whose `files_touched` produced the rejection — or the one `to:` names |
| **`feed: [self]`** | inject the failing report's **path** into the re-dispatch, with the original inputs — without it the target repeats itself verbatim and cannot converge |
| **counting** | per-step `cycles` in **your** `state.yaml`, written before re-dispatch (`redispatched_at`), re-read each iteration — the loop is exactly where a context reset happens |
| | never `feature.json` — those counters are the orchestrator's and the hook blocks you (DEC-119); report cycles in your digest instead |
| | cycles means **send-backs**: a clean first pass reports `0` (DEC-157). Counting runs is how a healthy feature exhausts its budget |
| **downstream** | steps that ran after the target → `pending`; their verdicts are stale the moment their input changes |
| **outputs** | resolve `{{cycle}}` in any path that re-runs, else cycle 2's PASS overwrites the evidence for why cycle 1 was spent (DEC-117) |
| **at `max_cycles`** | take `then:` — `escalate` or `halt`. An unbounded fix loop is what the counter exists to prevent |

If the same step fails twice with the same reason, more cycles will not help — say so in the
escalation rather than spending the budget to prove it.
