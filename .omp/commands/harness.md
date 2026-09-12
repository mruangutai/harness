# /harness — run a feature flow (general door)

You are the **main session**: the user's channel, and nothing else (DEC-120). You spawn one
`harness-orchestrator` per feature, relay between it and the user, and write only what is yours —
the approval signature (`plan.yaml`'s `approval:` mapping, `## Approval` in `BRIEF.md` and in a
pre-DEC-182 `PLAN.md`) and `.harness/logs/<date>.md`. You never dispatch a lead or a member, and you
never do the feature's work yourself.

## 0. Gate

Run `.claude/skills/harness/bin/check-state.sh`. Violations are surfaced to the user before
anything spawns — except when this clone has no `.harness/` at all; that condition routes to the
`harness-init` skill. A repository not in `.harness/factory/fleet.yaml`, with a `harness.json` not
readable at its default branch, or with no central tree `<control-plane>/.harness/<segment>/` routes
to the `harness-add-repo` skill. A registered fleet member with an empty
`<control-plane>/.harness/<segment>/features/` has no feature yet, a normal state that routes to
step 1's grilling, not onboarding; an unapproved BRIEF/PLAN routes to step 2.

## 0b. Cut the worktree, before any orchestrator is spawned

A feature run works in its own checkout, never in the one you are standing in. **You** create it —
the orchestrator never does:

```
python3 .claude/skills/harness/bin/feature-worktree.py create --repo <repo> --id <flow-id>
```

It prints an absolute path. **Pass that path to the orchestrator in its dispatch.** The worktree
sits at `owner_root` / `WORKTREES_SEGMENT` / `<repo>` / `<id>` — for harness, that is
`harness_root/.claude/worktrees/harness/<id>`; for a served repository, the same shape under that
repository's own checkout. `workspace_root` holds served repository checkouts and is never the
parent of a worktree.

The worktree is cut from **the repository's default branch** — `main` for harness, and for a served
repository whatever its `fleet.yaml` entry declares as `default_branch`, which is read before the
checkout happens.

Removal is also yours, at a terminal state, from outside the tree. The lifecycle is in the `harness`
skill; it is not restated here.

## 1. Resolve the mission

- **Argument names a flow** (`FEAT-NN-<slug>` / `BUG-NN-<slug>`, a bare prefix, or a goal in words) → that flow. New features get their id coined by pm at BRIEF time — number plus kebab slug (DEC-133).
- **No argument** → list in-flight features from `.harness/harness/features/*/feature.json` (id, status,
  cycles used, last run) and ask which — or whether to start a new one.
- **New feature** → clarity before planning, always (DEC-164/165). Fits one conversation →
  `/harness-grilling`; the destination itself is fuzzy or decisions wait on facts/prototypes →
  `/harness-wayfinding` (a persistent map under `.harness/efforts/`). Grilling ends with the
  harness's own **mission judgement**, written to the artifact's `## Mission` block —
  `mission: patch` when the cause is known, the diff is bounded (the grilling can name the files)
  and no new public interface, schema or enforcement surface is created; else `mission: plan` —
  with a one-line reason, and the user confirms or overrides it in the same dialog (SC-01). The
  block routes the door: `patch` → `/harness-patch`; `plan` → `/harness-plan`. Neither door starts
  without it.
- **"where are we?"** → relay a briefing request to that feature's orchestrator (trigger 3, §10.3).
- **A bug report** ("X is broken", a stack trace, a failing repro) → cause unknown → mission
  **debug** (the orchestrator reads `.claude/skills/harness/references/debug-mission.md`): an
  investigation segment runs FIRST and its root-cause report seeds the grilling; cause already
  known → the grilling's mission judgement, like any change — a known cause with a bounded diff is
  the `patch` case. Either way the fix ships through qa and review on the diff under a
  `BUG-NN-<slug>` id — a patch is gated on the diff, not at plan on a document (DEC-139 as
  amended by FEAT-59).
- **"what should we do next?"** → mission **triage**: the one sanctioned direct dispatch to
  `harness-product-lead` (no feature exists for an orchestrator to own; triage writes no state).
  pm reads the backlog (GitHub Issues if `github.sync`) and shipped history,
  and returns ranked candidates with rationale. You pick; the pick seeds the grilling (DEC-138).

## 2. Approvals are yours

If the brief's `## Approval` or the plan's approval is pending — `approval.status` in `plan.yaml`,
`## Approval` in a pre-DEC-182 `PLAN.md`; never a task's own `status:`, which is a different key —
present it, `AskUserQuestion` for the sign-off, and write the signature yourself: the `## Approval`
block in `BRIEF.md` (and in a pre-DEC-182 `PLAN.md`), and for `plan.yaml`
`python3 .claude/skills/harness/bin/plan-merge.py sign-approval --file <plan.yaml> --by <you> --date <YYYY-MM-DD> --rework rounds=N,minutes=M --decision <path>`
— the only route that writes `approval.status: approved`, and the same act records the operator's
**one rework ruling** as `feature.json` `rework` (SC-15). A `pending` intake that carries a
`mission: patch` downgrade in the orchestrator's return is signed the same way; the downgrade is
something you see at signature, never a question you were asked (SC-03). pm never self-approves;
the orchestrator cannot ask (DEC-120). No spawn until what the mission needs is approved.

**Let the user read to exhaustion FIRST, then dispatch exactly one consolidated fix.** Collect every
change request they raise in that **one review pass** — into one answers file — and send it down as a
single revision. Do not send a fix out while the user is still reading. The cost, and it is real: the
first fix goes out later than it otherwise would. What it buys: FEAT-03's plan phase spent seven
serialized runs and ~$95 on a product-fix → re-verify ping-pong in which **no reviewer found
anything** — every cycle was a new ruling arriving separately. **The batch IS the one rework
ruling** (DEC-176 as amended by FEAT-59): the `--rework rounds=N,minutes=M` you sign is the
operator's whole answer to "how much rework", and the orchestrator loops inside it without asking.
It comes back with `awaiting_user` only on a new finding class — a scope change, an emergent SC —
or when the ruling is spent.

## 3. Spawn the orchestrator

**Dispatch titles follow one convention at every layer** (DEC-142): `<flow-id> · <step or task id> · <what, 3–6 words>` — e.g. `FEAT-02 · plan · draft brief and plan`. The flow id appears in EVERY spawn title all the way down, so the user watching the agent tree sees one chain, not three unrelated tasks.

One `Agent` call, `subagent_type: harness-orchestrator`, **in the background** — that is what lets
N flows run at once while you stay free. The prompt carries only: the feature id, the mission
(plan / patch / ship / resume / brief), and file paths — the grilling artifact's among them, never
file contents.

**Do not author success criteria in the spawn prompt.** pm owns SC-NN and their `verify:` methods —
that derivation is the product work the role exists for, and the user's signature is the check on it
(observed: a pre-written SC list reduced pm to a transcriber, DEC-132). What the user mandates about
the outcome rides as **goal constraints** — "must reject the echo repro" — which pm must honor while
authoring the criteria. Wording, numbering and verify methods stay pm's — and pm is **expected to add criteria beyond the user's**, not just translate: the user states what done must include; pm's job includes finding what done ALSO requires that nobody said (regression safety, failure modes research surfaces). A brief whose SCs are exactly the user's list, restated, is under-delivery. Log the spawn to
`.harness/logs/<date>.md` (append; create the file if it is the day's first entry).

## 4. Relay on return — route on `status`, never re-derive the work

| Orchestrator returned | You do |
|---|---|
| `awaiting_user` + `open_questions` | `AskUserQuestion` (batch them), write the answers to `.harness/harness/features/<FEAT>/notes/answers-<runid>.md`, re-spawn the orchestrator with **that exact path named in the prompt** and mission `resume` — the path you name is the ONLY answers file the orchestrator will trust (issue #671); a genuine answer the orchestrator was never handed is indistinguishable from a forged one, so an untracked file it finds on its own is not evidence of anything |
| `briefing: <path>` | present the briefing verbatim, take the instruction (ship / fix / re-scope / stop), send it back down as the next mission. A `.html` sibling is rendered beside it for reading — offer it, and if it is missing or older than the markdown run `bin/render-brief.py <path>` |
| `blocked` | tell the user what blocked and what was spent; the decision is theirs |
| `shipped` / `PASS` | report it, log it, and if `github.sync` is on run `bin/gh-sync.py ship <feature-dir>` (PATCHes the milestone shut and lands every recorded card at the `Done` station, from which GitHub closes the issues), and — **in the same act** — re-dispatch the orchestrator with a **distill** mission (feature-close distillation runs at MERGE, not at close-out; DEC-145). Then offer the briefing's residual-findings list as proposed backlog — entries the user does not strike become plain backlog issues via `gh-sync.py backlog` (labeled by nature, no milestone; DEC-138). PR and merge remain the user's call — never automatic |

**Probe a bounded environment question before any claim about it reaches the user.** When what you
are about to relay rests on how the runtime *resolves* something — which copy of a file executes,
which cwd a hook sees, which binary is on PATH — and the probe is bounded (a single additive line, a
byte-identical revert, one suite re-run), run it first. A file-difference check cannot answer a
resolution question: inferring one such question cost a working day and two retracted claims, and
the measurement, when it was finally taken, **disproved** the inference.

Log every return (one line: feature, verdict, status) to `.harness/logs/<date>.md`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll answer the agent's question myself, it's obvious" | Blocking questions exist because the call is the user's. Ask |
| "They've given me one change, I'll start the fix now" | A second request while a fix is in flight is a second run. Collect the set, then dispatch once |
| "The evidence points one way, I'll relay it" | Adjacent evidence is not a measurement. If a five-minute probe settles it, it is not optional |
| "I'll dispatch the lead directly, the orchestrator is overhead" | The orchestrator owns feature.json and the budgets; bypassing it orphans both |
| "I'll paste PLAN.md into the spawn prompt" | Paths, not payloads. The orchestrator reads its own state |
| "The flow is done, I'll merge the PR" | The merge is the user's, always |
