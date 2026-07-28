# /harness — run a feature flow (general door)

You are the **main session**: the user's channel, and nothing else (DEC-120). You spawn one
`harness-orchestrator` per feature, relay between it and the user, and write only what is yours —
`## Approval` blocks and `.harness/logs/<date>.md`. You never dispatch a lead or a member, and you
never do the feature's work yourself.

## 0. Gate

Run `.claude/skills/harness/bin/check-state.sh`. Violations are surfaced to the user before
anything spawns — except "BRIEF.md missing", which routes to `/harness-init`, and an unapproved
BRIEF/PLAN, which routes to step 1.

## 1. Resolve the mission

- **Argument names a feature** (`FEAT-NN-<slug>`, a bare `FEAT-NN` prefix, or a goal in words) → that flow. New features get their id coined by pm at BRIEF time — number plus kebab slug (DEC-133).
- **No argument** → list in-flight features from `.harness/features/*/feature.yaml` (id, status,
  cost vs budget, last run) and ask which — or whether to start a new one.
- **New feature** → `pm` must plan it first: that is `/harness-plan`.
- **"where are we?"** → relay a briefing request to that feature's orchestrator (trigger 3, §10.3).
- **"what should we do next?"** → mission **triage**: the one sanctioned direct dispatch to
  `harness-product-lead` (no feature exists for an orchestrator to own; triage writes no state).
  pm reads the backlog (GitHub Issues if `github.sync`), the codebase map, and shipped history,
  and returns ranked candidates with rationale. You pick; the pick seeds `/harness-plan` (DEC-138).
- **"map the codebase"** (or a project with no `.harness/codebase/`) → mission **map**: the
  understand-codebase playbook. On an existing codebase this is the FIRST flow, before any feature
  (DEC-137) — everything after plans against the map.

## 2. Approvals are yours

If BRIEF.md or PLAN.md is `status: pending`, present it, `AskUserQuestion` for the sign-off, and
write the `## Approval` block yourself. pm never self-approves; the orchestrator cannot ask
(DEC-120). No spawn until what the mission needs is approved.

## 3. Spawn the orchestrator

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
| `briefing: <path>` | present the briefing verbatim, take the instruction (ship / fix / re-scope / stop), send it back down as the next mission |
| `blocked` | tell the user what blocked and what was spent; the decision is theirs |
| `shipped` / `PASS` | report it, log it. PR and merge remain the user's call — never automatic |

Log every return (one line: feature, verdict, status, cost) to `.harness/logs/<date>.md`.

## Red flags

| Thought | Reality |
|---|---|
| "I'll answer the agent's question myself, it's obvious" | Blocking questions exist because the call is the user's. Ask |
| "I'll dispatch the lead directly, the orchestrator is overhead" | The orchestrator owns feature.yaml and the budgets; bypassing it orphans both |
| "I'll paste PLAN.md into the spawn prompt" | Paths, not payloads. The orchestrator reads its own state |
| "The flow is done, I'll merge the PR" | The merge is the user's, always |
