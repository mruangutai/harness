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

One message is the rule for two reasons: it does not depend on backgrounding behaviour, which has
changed before and is unobservable from inside; and one ready set means one checkpoint write, so
`state.yaml` never describes a half-dispatched wave (DEC-124, DEC-100). Parallelism is implicit in
the DAG: any two `pending` steps with satisfied `depends_on` and no mutual dependency go together.
Caps: 20 concurrent, 200 per session, nested spawns counting toward both.

Each dispatch is titled `<flow-id> · <step or task id> · <what, 3–6 words>` — same flow id the orchestrator used, plus your step id (DEC-142); a member's spawn title must be traceable to the flow it serves. Each prompt carries the goal, the resolved **input paths**, the **output paths** the step must
write, and nothing else.

**Never pass `model:` in a dispatch** — the frontmatter pin is org design (DEC-152/155) and
`dispatch-guard.sh` blocks the call. A task that genuinely needs a stronger model is an
escalation via `open_questions`, decided and recorded above you.

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

**Three gaps are structural, not bugs** (BUILD task 22): the hook deliberately passes through a
non-harness `agent_type`, `stop_hook_active` (so it never wedges a member in a re-prompt loop),
and its own internal failure (fail OPEN, loudly). A return that reached you through any of those
paths was never checked — treat the hook as a strong filter, not as proof you can skip reading
what came back.

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

| What | Do | Why |
|---|---|---|
| **target** | re-dispatch the step whose `files_touched` produced the rejection — or the one `to:` names | five specialists, no generic "build" step to guess at |
| **`feed: [self]`** | inject the failing report's **path** into the re-dispatch, with the original inputs | without it the target repeats itself verbatim and cannot converge; the one place a return value reaches a later prompt, and even then as a path |
| **counting** | per-step `cycles` in **your** `state.yaml`, written before re-dispatch, re-read each iteration | the loop is exactly where a context reset happens |
| | never `feature.yaml` — feature-wide counters are the orchestrator's, and the hook blocks you (DEC-119) | report cycles spent in your digest and let it increment |
| | cycles means **send-backs**: a clean first pass reports `0` (DEC-157) | counting runs instead is how a healthy feature exhausts its budget |
| **downstream** | steps that ran after the target → `pending` | their verdicts are stale the moment their input changes |
| **outputs** | resolve `{{cycle}}` in any path that re-runs | else cycle 2's PASS overwrites cycle 1's FAIL — the evidence for why the cycle was spent (DEC-117) |
| **at `max_cycles`** | take `then:` — `escalate` or `halt` | never silently retry past the bound; an unbounded fix loop is what the counter exists to prevent |

**A note on convergence.** If the same step fails twice with the same reason, more cycles will not
help — say so in the escalation rather than spending the budget to prove it.

### 4. Collate — this is the job, not the paperwork

Collating N member digests is **not** concatenation — it is why the lead tier exists. A stapled
digest means the orchestrator paid your spawn for nothing. Four things, in order:

| | Do | Why |
|---|---|---|
| **a. roll up** | `BLOCKED > ESCALATE > FAIL > PASS`, worst wins. One `FAIL` makes the team `FAIL` | `ESCALATE` outranks `FAIL` deliberately: a decision only the user can make must not hide behind a failure you could fix |
| | every member entry carries a `verdict:` | the `SubagentStop` hook computes the worst and rejects a return that claims better; without a verdict it rejects outright |
| | reporting **worse** than your members is allowed | you may see what they could not |
| **b. merge** | union `must_fix`, `files_touched`, `open_questions`; merge one defect reported three ways into one entry naming all three reporters | the panel is four lenses on one diff; three copies read as three problems and spend three fix cycles on one |
| | re-rank `low`/`info` against **what the project does next** | severity and priority are different axes and you are the only tier that sees the second — an inert `info` intersecting the next task outranks a `med` that does not (DEC-124) |
| **c. assess** | see the table below — this is the part only you can do | each member saw its slice; you saw all of them |
| **d. headline** | one line, conclusion first, what the team **achieved** | "Auth ship-ready; refresh path untested" routes. "Ran three steps" does not, and it is read before anything else |

**The roll-up is checked, and it is the most consequential thing you can get wrong** — the
orchestrator routes on your `VERDICT` and never opens member entries, so a masked `FAIL` ships. The
hook is hardened against the known format and echo shadowings (BUILD task 22, FEAT-02) but the
structural pass-throughs above still apply: the rule is yours to honour, the hook is the backstop.

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
| **Push-back is collation, not a later phase** | rework at your tier costs one member spawn; the same rework after the orchestrator routed on your digest costs a feature cycle |
| **Report what came back, never how you dispatched it** | an agent has no reliable view of its own turn boundaries (DEC-124); topology is checked from spawn records, so a claim about it is noise at best, a false all-clear at worst |
| **Never open an artifact to second-guess it line by line** | you route on `VERDICT` + `DIGEST`; read an artifact only when a decision of *yours* turns on it — re-deriving a member's work is the whole of `zero-micro-management` |

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
# ORCHESTRATOR ONLY, after the lead returns. --into REPLACES the placeholder;
# `>> state.yaml` would leave a SECOND cost: key, silently shadowed by the last
# occurrence in any YAML parser and rejected by INV-16 (DEC-156).
.claude/skills/harness/bin/cost-report.py --yaml --into <run_dir>/state.yaml
```

A complete run left without a `cost:` block is an INV-11 violation — an unmetered run is
indistinguishable from a free one (DEC-99, DEC-116).

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
