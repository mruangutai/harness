# /harness — run a feature flow (general door)

You are the **main session**: the user's channel, and nothing else (DEC-120). You spawn one
`harness-orchestrator` per feature, relay between it and the user, and write only what is yours —
the approval signature (`plan.yaml`'s `approval:` mapping, `## Approval` in `BRIEF.md` and in a
pre-DEC-182 `PLAN.md`) and `.harness/logs/<date>.md`. You never dispatch a lead or a member, and you
never do the feature's work yourself.

## 0. Gate

Run `.claude/skills/harness/bin/check-state.sh`. Violations are surfaced to the user before
anything spawns — except "BRIEF.md missing", which routes to `/harness-init`, and an unapproved
BRIEF/PLAN, which routes to step 1.

## 1. Resolve the mission

- **Argument names a flow** (`FEAT-NN-<slug>` / `BUG-NN-<slug>`, a bare prefix, or a goal in words) → that flow. New features get their id coined by pm at BRIEF time — number plus kebab slug (DEC-133).
- **No argument** → list in-flight features from `.harness/features/*/feature.yaml` (id, status,
  cycles used, last run) and ask which — or whether to start a new one.
- **New feature** → clarity before planning, always (DEC-164/165). Fits one conversation →
  `/harness-grilling`; the destination itself is fuzzy or decisions wait on facts/prototypes →
  `/harness-wayfinding` (a persistent map under `.harness/efforts/`). Then `pm` plans it:
  `/harness-plan`.
- **"where are we?"** → relay a briefing request to that feature's orchestrator (trigger 3, §10.3).
- **A bug report** ("X is broken", a stack trace, a failing repro) → mission **debug**: cause
  unknown → an investigation segment runs FIRST and its root-cause report seeds the plan; cause
  already known → straight to `/harness-plan` (the FEAT-02 pattern). Either way the fix ships
  through the normal gates under a `BUG-NN-<slug>` id — there is no ungated bug lane (DEC-139).
- **"what should we do next?"** → mission **triage**: the one sanctioned direct dispatch to
  `harness-product-lead` (no feature exists for an orchestrator to own; triage writes no state).
  pm reads the backlog (GitHub Issues if `github.sync`), the codebase map, and shipped history,
  and returns ranked candidates with rationale. You pick; the pick seeds `/harness-plan` (DEC-138).
- **"deepen" / "review the architecture"** → mission **deepen** (DEC-149) — between features
  only; `/harness-deepen` is the explicit door.
- **"map the codebase"** (or INV-14 warning of code without a map) → mission **map**
  (`/harness-map` is the explicit door). Normally
  this ran AT INIT (DEC-140) and this route is for re-maps and projects onboarded before the rule;
  everything plans against the map, so run it before the next feature if it is missing.

## 2. Approvals are yours

If the brief's `## Approval` or the plan's approval is pending — `approval.status` in `plan.yaml`,
`## Approval` in a pre-DEC-182 `PLAN.md`; never a task's own `status:`, which is a different key —
present it, `AskUserQuestion` for the sign-off, and
write the signature yourself — `approval.status: approved` in `plan.yaml`, the `## Approval` block in
`BRIEF.md` and in a pre-DEC-182 `PLAN.md`. pm never self-approves; the orchestrator cannot ask
(DEC-120). No spawn until what the mission needs is approved.

**Let the user read to exhaustion FIRST, then dispatch exactly one consolidated fix.** Collect every
change request they raise in that **one review pass** — into one answers file — and send it down as a
single revision. Do not send a fix out while the user is still reading. The cost, and it is real: the
first fix goes out later than it otherwise would. What it buys: FEAT-03's plan phase spent seven
serialized runs and ~$95 on a product-fix → re-verify ping-pong in which **no reviewer found
anything** — every cycle was a new ruling arriving separately.

## 3. Spawn the orchestrator

**Dispatch titles follow one convention at every layer** (DEC-142): `<flow-id> · <step or task id> · <what, 3–6 words>` — e.g. `FEAT-02 · plan · draft brief and plan`. The flow id appears in EVERY spawn title all the way down, so the user watching the agent tree sees one chain, not three unrelated tasks.

One `Agent` call, `subagent_type: harness-orchestrator`, **in the background** — that is what lets
N flows run at once while you stay free. The prompt carries only: the feature id, the mission
(plan / ship / resume / brief), and file paths — never file contents.

**Do not author success criteria in the spawn prompt.** pm owns SC-NN and their `verify:` methods —
that derivation is the product work the role exists for, and the user's signature is the check on it
(observed: a pre-written SC list reduced pm to a transcriber, DEC-132). What the user mandates about
the outcome rides as **goal constraints** — "must reject the echo repro" — which pm must honor while
authoring the criteria. Wording, numbering and verify methods stay pm's — and pm is **expected to add criteria beyond the user's**, not just translate: the user states what done must include; pm's job includes finding what done ALSO requires that nobody said (regression safety, failure modes research surfaces). A brief whose SCs are exactly the user's list, restated, is under-delivery. Log the spawn to
`.harness/logs/<date>.md` (append; create the file if it is the day's first entry).

## 4. Relay on return — route on `status`, never re-derive the work

| Orchestrator returned | You do |
|---|---|
| `awaiting_user` + `open_questions` | `AskUserQuestion` (batch them), write the answers to `.harness/features/<FEAT>/notes/answers-<runid>.md`, re-spawn the orchestrator with that path and mission `resume` |
| `briefing: <path>` | present the briefing verbatim, take the instruction (ship / fix / re-scope / stop), send it back down as the next mission. A `.html` sibling is rendered beside it for reading — offer it, and if it is missing or older than the markdown run `bin/render-brief.py <path>` |
| `blocked` | tell the user what blocked and what was spent; the decision is theirs |
| `shipped` / `PASS` | report it, log it, and if `github.sync` is on run `bin/gh-sync.py ship <feature-dir>` (closes the milestone), and offer the briefing's residual-findings list as proposed backlog — entries the user does not strike become plain backlog issues via `gh-sync.py backlog` (labeled by nature, no milestone; DEC-138 am.4). PR and merge remain the user's call — never automatic |

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
| "I'll dispatch the lead directly, the orchestrator is overhead" | The orchestrator owns feature.yaml and the budgets; bypassing it orphans both |
| "I'll paste PLAN.md into the spawn prompt" | Paths, not payloads. The orchestrator reads its own state |
| "The flow is done, I'll merge the PR" | The merge is the user's, always |
