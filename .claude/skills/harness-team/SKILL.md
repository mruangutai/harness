---
name: harness-team
description: Run a harness team — a small DAG of agents hosted by a domain lead, passing state by file path. Use when asked to run a named team, to assemble a team for a goal, or to list the available teams.
---

# Harness: Team Runner

A team is a **DAG of steps, each dispatched to one agent**, hosted by a domain lead. This skill is
the algorithm; the teams are data at `<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/teams/*.yaml`.

**Four shipped teams**: `build` (eng-lead; one step per plan task, expanded at dispatch), `plan`
(product-lead), `validate` and `fix` (validator-lead). Only `build` is single-squad; the rest host
outside personas (independence is persona-level — `harness-zero-micro-management` loop step 1,
DEC-224).

**You are the host, and you are a lead** — never the orchestrator or the main session (DEC-100,
DEC-120, issue #83). Spawn allowlist, dispatch header, the `model:` ban and tool grants are
`harness-zero-micro-management`'s rules, enforced by `dispatch-guard.py`.

## The two rules that make this safe

**State passes by path (harness-handoff).** A step's return is control flow only; the next step
is told the artifact's *path* and reads it.

**Every step writes only inside the producing agent's own domain.** Members cannot write the run
dir — a step told to stage output there is blocked by `check-domain.py` on dispatch (DEC-116) —
and namespaced artifact paths keep parallel outputs disjoint.

## Process

### 1. Resolve the team

Lookup order (project override first, DEC-113) and the no-team-named listing:
`<HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/references/team-run-state.md` §Resolve the team.

### 2. Open the run

Seed `state.yaml` **before the first dispatch** — one `pending` step per team step, `steps_from:`
expanded first, `run_uid` minted by the harness, never you. Run-dir path, seed keys, the version-2
step-key contract `check-domain.py` enforces and the `steps_from:` expansion are
`team-run-state.md` §Open the run — read it when seeding.

**The run dir is yours alone** — `state.yaml`, collected DIGESTs, no per-step member directories.
`check-domain.py` refuses a `<run_dir>/digest.md` write that would discard existing content, so a
new cycle takes its own run directory.

**`state.yaml` is a checkpoint, not a notebook (DEC-154)**: identifiers, enums, counters, paths and
sequence markers a fresh context can match without reading. Findings and reasoning belong in
`digest.md`; a one-line `note:` per step is the ceiling for prose.

### 3. Loop

Until every step is terminal, or you halt:

This loop runs across turns, not inside one; each wake re-enters it at the step `state.yaml`
records.

**a. Compute the ready set** — every `pending` step whose `depends_on` are all `complete`.

**b. Checkpoint BEFORE dispatching.** Write `dispatched_at` into `state.yaml` *before* the spawn,
`completed_at` after the return; a step with the first and not the second is provably in flight,
which makes every recovery case decidable.

**Worktrees, if the project mandates them:** branch from the **local** branch, never
`origin/<branch>` — with unpushed commits origin is behind the pinned SHA (DEC-143).

**c. Serialize anything that mutates the repo.** `mutates_repo: true` steps dispatch **one at a
time** even when the DAG allows parallelism — `check-domain.py` cannot see `Bash` writes, and
every doer holds it (DEC-85).

**d. Dispatch the rest of the ready set in one turn** — **all task calls in one message, never
with a `name:` parameter** (teammate→teammate named spawns are rejected, DEC-147). One ready set is
one checkpoint write, so `state.yaml` never describes a half-dispatched wave (DEC-124). Caps: 20
concurrent, 200 per session, nested counting to both.

After the dispatch header, each item prompt's next line is the title
`<flow-id> · <step or task id> · <what, 3–6 words>` (DEC-142), then goal, resolved **input paths**
and **output paths**.

**Never wait for a member.** Every member is `blocking: true`; the `task` call holds in the host
until the member is terminal and your model is inactive. No `hub wait`, polling, sleeps,
heartbeats or manufactured work — zero such calls. The registry blocks a replacement parent while
the claim is live and the digest gate refuses a return with a child in flight (DEC-233); a host
suggestion to continue other work does not override this (DEC-201).

**e. Collect returns after the blocking task result.** Re-read
`state.yaml` first, verify the cited artifact, then record `VERDICT`, DIGEST fields, and
`completed_at`. A repeated delivery after resume is an idempotent no-op, never a second dispatch or
GitHub transition (DEC-204).

**The digest contract is enforced for you** — `validate-digest.py --hook` on `SubagentStop`
(DEC-122). Route *on* the fields, never re-adjudicate them: charitable normalization is how drift
stays invisible (DEC-101). The hook fails open, so a return can be well-formed yet substantively
wrong; on a missing or contradictory `VERDICT`, re-prompt **once**, then record
`BLOCKED (contract violation)` — never infer.

**f. Apply `on_fail`.** Only on `FAIL`; `BLOCKED` and `ESCALATE` always stop the branch and go up —
the agent could not proceed, so retrying is wrong. `halt` stops the run; `continue` records the
FAIL and carries on (advisory steps); `loop_back` re-dispatches the target with the failing
report's **path**, cycle-namespaced outputs (DEC-117), and per-step `cycles` counted in **your**
`state.yaml` as **send-backs** (DEC-157) — never `feature.json` (DEC-119) — taking `then:` at
`max_cycles`. **Read `team-run-state.md` §`loop_back` before re-dispatching a step.** The same step
failing twice for the same reason will not converge — say so in the escalation.

### 4. Collate

Collation is **not** concatenation — it is why the lead tier exists. In order:

| | Do |
|---|---|
| **a. roll up** | `BLOCKED > ESCALATE > FAIL > PASS`, worst wins — `ESCALATE` outranks `FAIL` so a user decision cannot hide behind a fixable failure. Every member that ran carries `verdict:`; only the optional external `fable-advisor` may carry `status: skipped` with the host reason, outside worst-wins, and at least one member must have run. You may report **worse** than your members |
| **b. merge** | union `must_fix`, `files_touched`, `open_questions`; one defect reported three ways is one entry naming all reporters. Re-rank `low`/`info` against **what the project does next** — you alone see priority (DEC-124) |
| **c. assess** | the table below — you alone saw every slice |
| **d. headline** | one line, conclusion first, what the team **achieved** — "Auth ship-ready; refresh path untested" routes; "Ran three steps" does not |

The orchestrator routes on your `VERDICT` alone, so a masked `FAIL` ships.

**c. Assess — decide, and say which:**

| What you found | What to do |
|---|---|
| Two members contradict each other | **Resolve or escalate** — never pass both up for the orchestrator to guess; if their artifacts decide it, decide and say why |
| A finding is real but not blocking | Keep it out of `must_fix` — padding the gating list makes the gate meaningless |
| A finding is out of the team's scope | `open_questions` if the user must decide, `escalations` if a peer lead owns it |
| A member's work is genuinely inadequate | **Send it back** (§3 `loop_back`) before you close — rework here costs one member spawn; after the orchestrator routes on your digest it costs a feature cycle |
| Everything passed and nothing is interesting | Say so in one line |

**Report what came back, never how you dispatched it** — you have no reliable view of your own
turn boundaries (DEC-124). **Never open an artifact to second-guess it line by line** — read one
only when a decision of *yours* turns on it.

### 5. Close out

Set `status: complete` (or `failed` / `blocked`), then **write your team digest to
`<run_dir>/digest.md`** and report it as your `artifact:` — the hook validates the **file** at that
path against the same schema (DEC-156); the file, not your transcript, is what a successor reads.
The digest-of-digests shape: `team-run-state.md` §Close out.

## Reporting up

**Every field is required** (DEC-121) — `[]` for an empty list, `none` for an inapplicable scalar;
the `SubagentStop` hook will not let you stop without them.

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
    - { step: should-not-exist, persona: fable-advisor, status: skipped, reason: "<host reason>" } # only optional external member
  must_fix: [<union of blocking findings>]
  files_touched: [<union across members>]    # universal — required of you too; [] if none
  branch: <branch | none>                    # `none` if the team mutated no repo
  open_questions: [...]                      # non-empty → the orchestrator surfaces it to the
                                             # MAIN SESSION, the only tier that can ask the user
  escalations: [{ id, raised_by, question, domain, routed_to, resolution, decided_by, recorded_as }]
  expertise_update: [<ops>]                  # [] except on a distillation dispatch
  adequacy_notes: [<what this PASS does not cover>]     # [] when nothing; required, NEVER omitted
  # Optional passthroughs from a member roll-up: sc_status, needs_approval, severity_max, matrix_ok, coverage_gaps, findings (each with kind), readers (plan: ran | skipped). Any other field is rejected; put qualifications in adequacy_notes or run-state evidence.
artifact: <run_dir>/digest.md                # your collated report — NOT state.yaml
```
````

`adequacy_notes` qualifies a PASS — act on nothing, read the verdict no wider than the list; it is
neither `must_fix` (gates) nor `open_questions` (reaches the user). A specific question a dispatch
asked is answered in `adequacy_notes` (qualification on PASS), the run-state step's `evidence`
(per-step fact), or the digest artifact (reasoning) — never a new digest key.

## Red flags

| Thought | Reality |
|---|---|
| "I'll track the cycle count as I go" | It lives in `state.yaml`. Your context may not survive to the next iteration |
| "The agent clearly meant PASS" | Missing `VERDICT` is `BLOCKED (contract violation)` after one re-prompt. Do not guess |
| "I'll dispatch these one at a time to be safe" | Independent, non-mutating steps go in one turn. Serial dispatch wastes the fan-out |
| "I'll record my assessment reasoning in state.yaml so it survives" | Prose survives in `digest.md`. state.yaml carries verdicts and markers a fresh context can match, not read (DEC-154) |
| "I'll reuse last cycle's run dir" | The digest write is refused rather than overwritten; a new cycle takes a run directory of its own |
