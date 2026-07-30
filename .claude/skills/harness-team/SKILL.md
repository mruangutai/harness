---
name: harness-team
description: Run a harness team — a small DAG of agents hosted by a domain lead, passing state by file path. Use when asked to run a named team, to assemble a team for a goal, or to list the available teams.
---

# Harness: Team Runner

A team is a **DAG of steps, each dispatched to one agent**, hosted by a domain lead. This skill is
the algorithm; the teams are data at `.claude/skills/harness/teams/*.yaml`.

**You are the host.** If you are a lead, you are running your own squad's DAG. If you are the
orchestrator, you are running it flat. The algorithm is identical either way — only who spawns
differs. **The main session never hosts a team** — since DEC-120 it is the user channel and nothing
else; it spawns an orchestrator per flow and that orchestrator hosts.

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

**`state.yaml` is a checkpoint, not a notebook (DEC-154).** Every value in it is an identifier, an
enum, a counter, a path, or a sequence marker — something a fresh context can act on without
reading it. Findings, code citations, assessment reasoning, and anything else written in sentences
belong in `digest.md`; a one-line `note:` per step is the ceiling for prose. The test: if a value
needs to be *read* rather than *matched*, it is in the wrong file. Ad-hoc top-level keys holding
prose lists (`pre_dispatch_checks:`, `lead_assessment_*:`) are the violation this rule exists to
name — record the *verdicts* they justify in the step entry, and the justification in the digest.

### 3. Loop

Until every step is terminal, or you halt:

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
never with a `name:` parameter** (a spawned host is itself a teammate, and teammate→teammate named
spawns are rejected — "the roster is flat"; plain subagents succeed, DEC-147).

*The reason is not what this used to say.* It claimed separate turns "run one after another and the
fan-out is lost". **Measured, that is false**: a lead that dispatched three reviewers across three
turns 16s and 8s apart still had all three running concurrently, because Claude Code backgrounds
subagents (DEC-124). So dispatch across turns is not a broken run. One message is still the rule for
two better reasons — it does not depend on backgrounding behaviour, which has changed before and is
not something you can observe from inside; and it keeps one ready set to one checkpoint write, so
`state.yaml` cannot describe a half-dispatched wave. Parallelism here is implicit in the DAG, not
requested: any two `pending` steps whose `depends_on` are satisfied and which do not depend on each
other go together. Verified to work from inside a lead (DEC-100). Caps: 20 concurrent, 200 per
session, nested spawns counting toward both.

Each dispatch is titled `<flow-id> · <step or task id> · <what, 3–6 words>` — same flow id the orchestrator used, plus your step id (DEC-142); a member's spawn title must be traceable to the flow it serves. Each prompt carries the goal, the resolved **input paths**, the **output paths** the step must
write, and nothing else.

**Never pass a `model:` parameter in a dispatch (DEC-155).** A member's model is pinned in its
agent frontmatter — that pin is org design (DEC-152's tiers), and a per-invocation `model:`
silently outranks it. If you believe a task genuinely needs a stronger model, that is an
escalation, not a dispatch option: raise it in `open_questions` with the evidence and let it be
decided above you and recorded. A quiet upgrade is unbudgeted spend that no gate will ever
surface.

**Do not serialize out of caution.** A panel of reviewers dispatched one at a time still returns the
same verdicts, so the run looks correct while costing several times the wall-clock — the most
expensive way to be wrong, because nothing surfaces it. If steps genuinely conflict, that is what
`depends_on` and `mutates_repo` are for; encode it in the team rather than in how you dispatch.

**e. Collect returns.** Read `VERDICT` and the `DIGEST` fields and record both in `state.yaml`.

**The digest contract is enforced for you — mechanically, at source, not by your own reading of it.**
`validate-digest.py --hook` runs as a **`SubagentStop` hook**, one of the six mandatory
`settings.json` entries (DEC-122). `exit 2` prevents a subagent from stopping, so a member that
returned a malformed digest gets rejected and re-prompted before it can hand it to you. This
deliberately covers you too — leads have no `Bash` and could never have run a validator, which is
exactly why the check moved off the runner and into a hook.

**This is not the same as "every field is guaranteed present" (BUILD task 22).** A live review
panel proved the earlier wording here false: four ordinary digest formats — nothing exotic, no
malformed YAML by any normal reading — reached you with a masked `FAIL` at hook exit 0, because the
roll-up guard was decorative for anything but canonical input. Hardened since, but three gaps are
structural, not bugs to fix away: the hook deliberately **passes through** a non-harness
`agent_type`, `stop_hook_active` (so it never wedges a member in a re-prompt loop), and its own
internal failure (fail OPEN, loudly on stderr — never crash to an ambiguous exit). A return that
reached you through any of those three paths was never checked. Treat the hook as a strong filter
that catches drift and structural violations, not as proof you can skip reading what came back.

**So do not try to run it yourself, and do not substitute your reading for it.**
`severity_max: medium` instead of `med`, `must-fix` instead of `must_fix` — you would normalize all
of those charitably, which is why drift stays invisible until one routing decision quietly goes the
wrong way (DEC-101). Your job on collect is to *route on* the fields, not to re-adjudicate them.

What still lands on you is the residue the hook passes through: a return that is well-formed but
substantively wrong, or a member that stopped for a reason the hook does not govern. On a missing or
contradictory `VERDICT`, re-prompt **once**, then record `BLOCKED (contract violation)` — never
infer what the agent meant.

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
   increment (DEC-119). **Cycles spent means SEND-BACKS (DEC-157):** a clean run where every step
   passed first time reports `cycles_used: 0` — a first pass is work, not rework, and reporting
   `1` for it is how a healthy feature exhausts its budget with nothing wrong.
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

### 4. Collate — this is the job, not the paperwork

You have N member digests. Collating them is **not** concatenation, and it is not a step you perform
once the real work is done. It is the reason a lead tier exists: if your team digest is the members'
digests stapled together, the orchestrator would have been better off reading them directly and you
cost a spawn for nothing.

Four things, in order:

**a. Roll up the verdict.** `BLOCKED > ESCALATE > FAIL > PASS`, worst wins. **`ESCALATE` outranks
`FAIL` deliberately** — a decision only the user can make must not be masked by a failure you could
have fixed. Never report `PASS` because most members passed; one `FAIL` makes the team `FAIL`.

**This one is checked — but only partly, today.** The `SubagentStop` hook computes the worst verdict across your
`members:` entries and rejects a return that reports better than it. Reporting worse is allowed —
you may have a reason your members could not see. Every member entry therefore needs a `verdict:`;
without one the roll-up is undecidable and your return is rejected. It is the only part of collation
that is arithmetic rather than judgement, and it is the most consequential thing you can get wrong:
the orchestrator routes on your `VERDICT` and never opens member entries, so a masked `FAIL` ships.

> ⚠️ **Do not treat the check as complete.** A live review panel reproduced four member-entry
> formats that slip a masked `FAIL` past it, and one that disables the validator outright by
> crashing it — the hook then exits 1, and only exit 2 blocks (DEC-124, task 22). Until that is
> fixed, the roll-up rule is **yours to honour**, and the hook is a backstop that catches the
> canonical case rather than a guarantee.

**b. Merge, then dedupe.** `must_fix`, `files_touched` and `open_questions` are unions across
members. Reviewers overlap by design — the panel is four lenses on one diff — so **the same defect
will arrive three times in three vocabularies.** Merge those into one entry naming all three
reporters. Three copies of one finding reads to the orchestrator as three problems and spends three
fix cycles on one.

**Re-rank `low` and `info` against what the project does NEXT, not against each other.** Severity
and priority are different axes and you are the only tier that can see the second. A member grades
severity from inside its own lens; it cannot know the roadmap. So an `info` finding that blocks the
next task outranks a `med` that does not.

Observed (DEC-124): a panel filed "`harness-orchestrator` has no schema, so it is ungated the moment
that agent exists" as `info` — correctly, since the agent does not exist yet and the defect is inert
today. The lead sorted by inherited severity and dropped it. It was the single item on the list that
intersected the very next task on the ledger. **Nothing was mis-graded; it was mis-prioritised.**

**c. Assess — the part only you can do.** Each member saw its slice; you are the only agent that
saw all of them. So decide, and say which:

| What you found | What to do |
|---|---|
| Two members contradict each other | **Resolve it or escalate it.** Do not pass both up and let the orchestrator guess. If it is decidable from their artifacts, decide and say why |
| A finding is real but not blocking | Keep it out of `must_fix`. That list is what gates the run; padding it makes the gate meaningless |
| A finding is out of the team's scope | Route it — `open_questions` if the user must decide, `escalations` if a peer lead owns it |
| A member's work is genuinely inadequate | **Send it back** (§3 `loop_back`) before you close. Reporting weak work up with a note is the failure mode `zero-micro-management` warns about from the other direction |
| Everything passed and nothing is interesting | Say that in one line. A short digest is a good outcome, not an under-delivery |

**Push-back is collation, not a separate phase.** You are the last tier that can cheaply fix a bad
result: rework at your level costs one member spawn, and the same rework after the orchestrator has
routed on your digest costs a whole cycle against the feature budget.

**Do not assert anything about your own execution that you cannot verify.** The lead in DEC-124
reported "three reviewers dispatched in a single message"; the spawn records showed three separate
turns. It was not lying — an agent has no reliable view of its own turn boundaries. So report *what
came back*, never *how you dispatched it*: topology is checked externally from spawn records, and a
confident claim about it is noise at best and a false all-clear at worst.

**d. Write the headline last.** One line, conclusion first, about what the team *achieved* — not
what it did. "Auth endpoints ship-ready; refresh-token path still untested" routes. "Ran three steps
and collected digests" does not, and it is what the orchestrator reads before anything else.

**What you must NOT do:** open a member's artifact to second-guess its contents line by line. You
route on `VERDICT` + `DIGEST`; you read an artifact when a *decision of yours* depends on it (a
contradiction to resolve, a `must_fix` you doubt), not as a review pass. The one thing you never do
is re-derive a member's work yourself — that is the whole of `zero-micro-management`.

### 5. Close out

Set `status: complete` (or `failed` / `blocked`), then **write your team digest to
`<run_dir>/digest.md`** and report it as your `artifact:`.

**The team digest is a digest of digests, not a new document class.** Same shape as a member's,
plus the fields only you can supply: the per-member roll-up (`members:`), the union of `must_fix`,
`steps_run`, cycles spent, and your assessment of what the panel actually means. §10.4 is the
contract, and the `SubagentStop` hook enforces it on **your** return as well — you cannot finish
with a field missing. The hook also validates the **file** at your `artifact:` path against the
same schema (DEC-156): a narrative digest.md with no contract block is rejected exactly like a
malformed return, because the file — not your transcript — is what a successor context reads.
Prose assessment goes below the block, never instead of it. **The `members:` block is not optional** — it is what preserves per-member
granularity in `STATE.md` under hierarchy, and without it the orchestrator cannot log who did what.

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

**Every field is required** (DEC-121) — `[]` for an empty list, `none` for a scalar that is
genuinely inapplicable. The `SubagentStop` hook will not let you stop without them.

```
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
  files_touched: [<union across members>]    # universal field — `[]` if the team touched nothing
  open_questions: [...]                      # non-empty → the orchestrator surfaces it to the
                                             # MAIN SESSION, the only tier that can ask the user
  escalations: [{ id, raised_by, question, domain, routed_to, resolution, decided_by, recorded_as }]
  expertise_update: [<ops>]                  # [] except on a distillation dispatch
  sc_status: [{ id, verdict, method, evidence }]   # passthrough from pm's goal-check; [] if none ran
artifact: <run_dir>/digest.md                # your collated report — NOT state.yaml
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
| "I'll record my assessment reasoning in state.yaml so it survives" | Prose survives in `digest.md`. state.yaml carries verdicts and markers a fresh context can match, not read (DEC-154) |
