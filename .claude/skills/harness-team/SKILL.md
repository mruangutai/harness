---
name: harness-team
description: Run a harness team — a small DAG of agents hosted by a domain lead, passing state by file path. Use when asked to run a named team, to assemble a team for a goal, or to list the available teams.
---

# Harness: Team Runner

A team is a **DAG of steps, each dispatched to one agent**, hosted by a domain lead. This skill is
the algorithm; the teams are data at `.agents/skills/harness/teams/*.yaml`.

**You are the host, and you are a lead.** You are running your own squad's DAG.

**The orchestrator does not host teams and no longer preloads this skill** (issue #83). It was
carried for flat mode — the orchestrator hosting a DAG itself — and flat mode is dead: `SPEC.md`
records *"hierarchical works, the flat fallback is not needed"* (DEC-100, DEC-102), and
`harness/SKILL.md` forbids the orchestrator→member path with no exceptions. The orchestrator
sequences squad segments and delegates each to its lead; it reads this file by path only if it
needs the algorithm. **The main session never hosts a team either** — since DEC-120 it is the user
channel and nothing else.

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

`.harness/teams/<name>.yaml` first, then `.agents/skills/harness/teams/<name>.yaml`. Project
overrides win, and anything project-specific has to live outside the shipped directory (DEC-113).

**No team named?** List `name` + `purpose` from both directories and stop. The filesystem is the
registry — there is no catalog to keep in sync.

### 2. Open the run

```
.harness/harness/features/<feat>/runs/<YYYY-MM-DD>-<seq>-<squad>/
  state.yaml
```

**The run dir is yours alone.** `state.yaml`, collected DIGESTs, nothing a member writes. Do not
create per-step directories for members — they write into their own domains.

Seed `state.yaml` with `schema_version`, `run_id`, `feature`, `squad`, `host`, `status: running`,
and one `steps:` entry per team step with `status: pending`.

**A team file carries EITHER a literal `steps:` DAG OR a `steps_from:` expansion rule.** With
`steps_from:`, expand it into concrete steps FIRST, then seed exactly as above: read the source it
names (`plan_tasks` = `.harness/harness/features/<feat>/plan.yaml`'s `tasks:` list, loaded with
`harness_yaml.load_plan`; a feature still on the pre-DEC-182 format uses `PLAN.md`'s `## Tasks`
instead — the two never coexist, and `check-plan-routes.py` refuses a feature carrying both);
take the task ids
**the caller handed you** — WHICH tasks arrive is the orchestrator's decision, already made, and
no key in the file re-states it; **route each one to a member by `consult-when`, which IS your
decision**; take each step's prompt from the task's own
`intent:` block when `prompt: from_task_intent`; build `depends_on` from each task's own
`depends_on:` field when `depends_on: from_task_depends_on`, falling back to file order only
for tasks declaring none — **file order is not a topological order**; substitute
`{{task_id}}`/`{{persona}}` into the `id` and `outputs` templates. From there the algorithm is
unchanged. A task the caller did not hand you is **not** silently dropped: it stays for the
orchestrator to sequence as its own squad segment (DEC-118).

**`state.yaml` is a checkpoint, not a notebook (DEC-154).** Every value in it is an identifier, an
enum, a counter, a path, or a sequence marker — something a fresh context can act on without
reading it. Findings, code citations, assessment reasoning, and anything else written in sentences
belong in `digest.md`; a one-line `note:` per step is the ceiling for prose. The test: if a value
needs to be *read* rather than *matched*, it is in the wrong file. Ad-hoc top-level keys holding
prose lists (`pre_dispatch_checks:`, `lead_assessment_*:`) are the violation this rule exists to
name — record the *verdicts* they justify in the step entry, and the justification in the digest.

### 3. Loop

Until every step is terminal, or you halt:

This loop runs across turns, not inside one. Each wake re-enters it at the step `state.yaml`
records, because your context may not survive the gap — `state.yaml` carries the loop's
position, you do not.

**a. Compute the ready set** — every `pending` step whose `depends_on` are all `complete`.

**b. Checkpoint BEFORE dispatching.** Write `dispatched_at` into `state.yaml` *before* the spawn,
`completed_at` after the return. A step with the first and not the second is provably in flight,
which is what makes every recovery case decidable. Cycle counters live in `state.yaml` and are
re-read each iteration — never carried in your head, because your context may not survive.

**Worktrees, if the project mandates them:** branch from the **local** branch, never `origin/<branch>` — with unpushed commits origin is behind the pinned SHA and the worktree silently builds against the wrong base (DEC-143).

**c. Serialize anything that mutates the repo.** Steps with `mutates_repo: true` dispatch **one at
a time**, even when the DAG would allow parallelism. This is the actual write-safety mechanism —
`check-domain.sh` cannot see writes made through `Bash`, and every doer holds it (DEC-85). Do not
treat a passing domain hook as proof that parallel writes are safe.

**d. Dispatch the rest of the ready set in one turn** — **all `Agent` calls in a single message,
never with a `name:` parameter** (teammate→teammate named spawns are rejected, DEC-147). One ready
set is one checkpoint write, so `state.yaml` never describes a half-dispatched wave (DEC-124,
DEC-100). Parallelism is implicit in the DAG: any two `pending` steps with satisfied `depends_on`
and no mutual dependency go together. Caps: 20 concurrent, 200 per session, nested counting to both.

Title each dispatch `<flow-id> · <step or task id> · <what, 3–6 words>` (DEC-142). Each prompt
carries the goal, the resolved **input paths**, the **output paths**, and nothing else.

**Never pass `model:`** — `dispatch-guard.sh` blocks the call (DEC-152/155). A task that needs a
stronger model is an escalation via `open_questions`.

**Do not serialize out of caution.** Serial dispatch returns the same verdicts at several times the
wall-clock, and nothing surfaces it. Genuine conflicts belong in `depends_on`/`mutates_repo`.

**Never wait for a member — end your turn.** Having dispatched, you end your turn; you do not
poll, do not sleep, do not re-read files to look busy, and do not restate that you are waiting.
Stopping is safe, because the platform wakes you when the member completes — ending your turn is HOW
you wait, not a way of giving up. The dispatch tool will tell you to continue other work in the
meantime, and that is not licence to manufacture activity: this rule overrides it. Your first
turn-end after a dispatch meets a live child, and that refusal is expected — stderr reads BLOCKED,
returned with children in flight. Answer it the same way: end your turn again, and expect it to
recur on each wake while a child is still live. It is never a bar on returning; it is a prompt to
correct any claim you made about a child you cannot see. (DEC-201)

**e. Collect returns.** You collect on waking, after the turn ended — never by staying alive to
receive. Read `VERDICT` and the `DIGEST` fields and record both in `state.yaml`.

**The digest contract is enforced for you**, mechanically — `validate-digest.py --hook` on
`SubagentStop` (DEC-122). Route *on* the fields; do not re-adjudicate them. You would normalize
`medium` to `med` charitably, and that is how drift stays invisible until one routing decision
quietly goes the wrong way (DEC-101).

**Treat the hook as a strong filter, not as proof.** It passes through a non-harness `agent_type`,
`stop_hook_active`, and its own failure (fail OPEN) — BUILD task 22. What lands on you is the
residue: a return that is well-formed but substantively wrong. On a missing or contradictory
`VERDICT`, re-prompt **once**, then record `BLOCKED (contract violation)` — never infer.

**f. Apply `on_fail`.** Only on `FAIL`. `BLOCKED` and `ESCALATE` always stop the branch and go up —
they mean the agent could not proceed, not that its work was rejected, so retrying is wrong.

| `action` | Behaviour |
|---|---|
| `halt` | stop the run, report what completed |
| `continue` | record the FAIL and carry on — for advisory steps that must not gate |
| `loop_back` | re-dispatch a prior step with the failure report injected |

For `loop_back`:

| What | Do |
|---|---|
| **target** | re-dispatch the step whose `files_touched` produced the rejection — or the one `to:` names |
| **`feed: [self]`** | inject the failing report's **path** into the re-dispatch, with the original inputs — without it the target repeats itself verbatim and cannot converge |
| **counting** | per-step `cycles` in **your** `state.yaml`, written before re-dispatch, re-read each iteration — the loop is exactly where a context reset happens |
| | never `feature.json` — those are the orchestrator's and the hook blocks you (DEC-119); report cycles in your digest instead |
| | cycles means **send-backs**: a clean first pass reports `0` (DEC-157). Counting runs is how a healthy feature exhausts its budget |
| **downstream** | steps that ran after the target → `pending`; their verdicts are stale the moment their input changes |
| **outputs** | resolve `{{cycle}}` in any path that re-runs, else cycle 2's PASS overwrites the evidence for why cycle 1 was spent (DEC-117) |
| **at `max_cycles`** | take `then:` — `escalate` or `halt`. An unbounded fix loop is what the counter exists to prevent |

**A note on convergence.** If the same step fails twice with the same reason, more cycles will not
help — say so in the escalation rather than spending the budget to prove it.

### 4. Collate — this is the job, not the paperwork

Collating N member digests is **not** concatenation — it is why the lead tier exists. A stapled
digest means the orchestrator paid your spawn for nothing. Four things, in order:

| | Do |
|---|---|
| **a. roll up** | `BLOCKED > ESCALATE > FAIL > PASS`, worst wins. One `FAIL` makes the team `FAIL`. `ESCALATE` outranks `FAIL` deliberately: a decision only the user can make must not hide behind a failure you could fix |
| | every member entry carries a `verdict:` — the hook rejects a return claiming better than its members, and rejects outright if one is missing |
| | reporting **worse** than your members is allowed — you may see what they could not |
| **b. merge** | union `must_fix`, `files_touched`, `open_questions`; merge one defect reported three ways into one entry naming all three reporters, else three copies spend three fix cycles on one problem |
| | re-rank `low`/`info` against **what the project does next** — you are the only tier that sees priority, so an inert `info` intersecting the next task outranks a `med` that does not (DEC-124) |
| **c. assess** | see the table below — each member saw its slice; you saw all of them |
| **d. headline** | one line, conclusion first, what the team **achieved**. "Auth ship-ready; refresh path untested" routes; "Ran three steps" does not |

**The roll-up is the most consequential thing you can get wrong** — the orchestrator routes on your
`VERDICT` and never opens member entries, so a masked `FAIL` ships. The hook is the backstop, not
the rule.

**c. Assess — decide, and say which:**

| What you found | What to do |
|---|---|
| Two members contradict each other | **Resolve or escalate.** Do not pass both up and let the orchestrator guess. Decidable from their artifacts? Decide, and say why |
| A finding is real but not blocking | Keep it out of `must_fix` — that list gates the run, and padding it makes the gate meaningless |
| A finding is out of the team's scope | Route it: `open_questions` if the user must decide, `escalations` if a peer lead owns it |
| A member's work is genuinely inadequate | **Send it back** (§3 `loop_back`) before you close. Reporting weak work up with a note is `zero-micro-management`'s failure mode from the other side |
| Everything passed and nothing is interesting | Say so in one line. A short digest is a good outcome |

| Rule | Why |
|---|---|
| **Push-back is collation, not a later phase** | rework at your tier costs one member spawn; after the orchestrator routes on your digest it costs a feature cycle |
| **Report what came back, never how you dispatched it** | you have no reliable view of your own turn boundaries (DEC-124), so a topology claim is a false all-clear at worst |
| **Never open an artifact to second-guess it line by line** | read one only when a decision of *yours* turns on it; re-deriving a member's work is the whole of `zero-micro-management` |

### 5. Close out

Set `status: complete` (or `failed` / `blocked`), then **write your team digest to
`<run_dir>/digest.md`** and report it as your `artifact:`.

**The team digest is a digest of digests, not a new document class.** Same shape as a member's,
plus the fields only you can supply: the per-member roll-up (`members:`), the union of `must_fix`,
`steps_run`, cycles spent, and your assessment. The hook enforces it on **your** return, and
validates the **file** at your `artifact:` path against the same schema (DEC-156) — the file, not
your transcript, is what a successor context reads. Prose goes below the block, never instead of
it. **`members:` is not optional** — without it the orchestrator cannot log who did what.

**You have no `Bash`** — leads hold `Read, Glob, Grep, Agent` so they cannot do a member's work
(DEC-116). Anything needing a shell belongs to the orchestrator. No shell also means no clock: use
ordering markers (`seq-1`, `seq-2`, …), never invented wall-clock times.

Report per-step verdicts and the run dir path. Not the artifacts' contents — their paths.

## Reporting up

**Every field is required** (DEC-121) — `[]` for an empty list, `none` for a scalar that is
genuinely inapplicable. The `SubagentStop` hook will not let you stop without them.

````
```yaml
VERDICT: PASS | FAIL | BLOCKED | ESCALATE     # worst member verdict: BLOCKED > ESCALATE > FAIL > PASS
DIGEST:
  headline: <one line — what the team achieved, not what it did>
  team: <name>                               # ONE KEY PER LINE — three on one line is not YAML,
  steps_run: <n>                             # and the two trailing ones vanish silently
  cycles_used: <n>
  members:                                   # per-member roll-up — NOT optional
    - { step: <id>, persona: <p>, verdict: <v>, headline: "...", files_touched: [...] }
  must_fix: [<union of blocking findings>]
  files_touched: [<union across members>]    # universal — required of you too; [] if none
  branch: <branch | none>                    # `none` if the team mutated no repo
  open_questions: [...]                      # non-empty → the orchestrator surfaces it to the
                                             # MAIN SESSION, the only tier that can ask the user
  escalations: [{ id, raised_by, question, domain, routed_to, resolution, decided_by, recorded_as }]
  expertise_update: [<ops>]                  # [] except on a distillation dispatch
  sc_status: [{ id, verdict, method, evidence }]   # passthrough from pm's goal-check; [] if none ran
artifact: <run_dir>/digest.md                # your collated report — NOT state.yaml
```
````

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
| "I'll record my assessment reasoning in state.yaml so it survives" | Prose survives in `digest.md`. state.yaml carries verdicts and markers a fresh context can match, not read (DEC-154) |
