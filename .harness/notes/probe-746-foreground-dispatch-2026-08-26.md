# Probe #746 — does a foreground child block its subagent parent? — 2026-08-26

**SPANS A RESTART.** `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` was written to
`.claude/settings.local.json` (gitignored) on 2026-08-26 at `ee66ae2`. The env block is read at
session start, so nothing measures until the session is restarted.

## Why this matters more than its size

#746, verbatim: *"If a foreground child BLOCKS its subagent parent, the parent waits without
polling and there is nothing for the stall watchdog to kill. No wake mechanism, no agent teams,
and no gate change are needed."*

**FEAT-37-lead-stop-and-wake is SIGNED and UNBUILT.** Its subject is the lead never-wait rule.
A PASS here removes the reason for that rule. How many of its six tasks survive is NOT yet
assessed — the premise is at risk, not proven dead.

`PR #745` ("The orchestrator playbook gains one rule: never wait for a lead, return") is already
CLOSED, and FEAT-35 shipped the orchestrator half of the rule by another route.

## Baseline, measured BEFORE the restart

- Neither `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` nor `CLAUDE_CODE_FORK_SUBAGENT` was set in
  `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json`,
  `~/.claude/settings.local.json`, or the process environment.
- The main session's `Agent` tool carried FIVE parameters and **no `run_in_background`**:
  `description`, `prompt`, `subagent_type`, `model`, `isolation`. Consistent with fork mode ON.
- `.claude/settings.json` env holds only `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "3"`.

## The steps, after the restart

1. **Confirm the variable took.** `env | grep CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` returns `1`.
2. **Confirm the tool schema changed.** The `Agent` tool now carries `run_in_background`. If it
   does not, the setting did not reach the tool layer and the probe stops here with that result.
3. **Dispatch a two-level chain.** A subagent that itself dispatches a child. Not the main
   session — the main session was never the subject.
4. **THE MEASUREMENT.** Read the PARENT subagent's transcript. Count idle calls: `echo hold`,
   `sleep`, or a repeated Glob on the child's output path. **Zero polling calls is the pass.**
   A parent that got "Async agent launched" is a fail.
5. **Confirm no stall death at 600s** on a child that runs longer than that.

## Pass and fail, fixed in advance so the result cannot be argued

- **PASS** — the parent shows no idle calls and resumes with the child's result. Then FEAT-37's
  premise is gone, and the children-in-flight gate stays as it is.
- **FAIL** — the parent gets an async child. Then `anthropics/claude-code#75043` is confirmed for
  this configuration, and FEAT-37 is built as signed.

## Cost to weigh if it passes

`DISABLE_BACKGROUND_TASKS=1` makes **every** dispatch blocking, the main session's included. No
parallel agents. The 2026-08-26 session ran three agents concurrently across three features, so
this is a real loss, not a theoretical one. `CLAUDE_CODE_FORK_SUBAGENT=0` is the weaker
alternative and leaves the choice to the model.

**Revert:** delete `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` from `.claude/settings.local.json` and
restart.

## What is waiting on the result

- **#746** closes on either result — it is a test, and a FAIL is an answer.
- **#742** ("Subagents inherit the main session's cwd...") holds #746 as its only open sub-issue.
  `gh-sync.py:1315` prints `HELD` and continues, so #742 does not block a ship; it just stays
  open. Closing #746 lets #742 close with the root-resolution work.
- **The root-resolution feature** is planned but not started. See
  `grilling-root-resolution-2026-08-26.md` — CLOSED, frontier empty.

## Result (SUPERSEDED — see "Step 4 result" below) — 2026-08-26

**This section stopped the probe at step 2. That stop was wrong: step 4 was run afterwards and passed.
Kept for the record; read the step 4 section as the finding.**

| Step | Predicted | Measured |
| --- | --- | --- |
| 1. Variable took | `=1` | `=1` — confirmed via `env` in the main session |
| 2. Tool schema changed | `Agent` gains `run_in_background` | **Unchanged.** Five parameters: `description`, `prompt`, `subagent_type`, `model`, `isolation`. Identical to the pre-set baseline. |
| 3-4. Two-level chain | — | Not run |

Step 2 was written as a hard stop: *"If it does not, the setting did not reach the tool layer and
the probe stops here with that result."* That rule fired.

**What this establishes:** `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` produced no observable change
at the tool layer in this configuration. The variable reached the process and did not reach the
`Agent` tool schema.

**What this does NOT establish:** whether a foreground child blocks its subagent parent. That is
step 4, and step 4 never ran. #746's question is still open.

**Unverified, and worth naming:** step 4's measurement — read the parent subagent's transcript,
count idle calls — does not obviously depend on the schema change step 2 gated on. Step 2 may have
been a stricter gate than the question needed. Nobody has tested that.

**Consequence for FEAT-37-lead-stop-and-wake:** its premise is neither confirmed nor removed. It
stays signed and unbuilt, with the same open question in front of it.

**Reverted.** `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` was deleted from
`.claude/settings.local.json` on 2026-08-26 at the user's instruction, to restore parallel
dispatch. A future attempt at step 4 must set it again and restart.

## Step 4 result — 2026-08-26 23:16-23:17 UTC — **PASS**

The step 2 stop was lifted and step 4 was run. `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` was live in
the session process (`env` confirmed it), so no further restart was needed.

**Setup.** Main session dispatched a `general-purpose` PARENT. The PARENT was told to make exactly
one `Agent` call spawning a `general-purpose` CHILD running `sleep 75 && echo
PROBE746-TOKEN-KX9QW2`, and was forbidden from Bash, Glob, Grep and Read so any polling would show
as a rule violation.

**The measurement — PARENT transcript**
`~/.claude/projects/-Users-molchairuangutai-GitHub-harness/12caac4e-.../subagents/agent-a48153eb8b3b1ceac.jsonl`

| Time | Entry |
| --- | --- |
| 23:16:11.832 | `tool_use: Agent` — the one dispatch |
| 23:17:33.280 | `tool_result` — `PROBE746-TOKEN-KX9QW2`, the child's real output |
| 23:17:34.377 | final text: the token |

- **Idle calls: ZERO.** No `sleep`, no `echo hold`, no repeated Glob.
- **No "Async agent launched".** The tool result was the child's finished output.
- **The parent blocked 81.4 seconds** across the child's 75-second sleep.
- `tool_uses: 1` on the parent, confirming the single call.

CHILD transcript `agent-a0d0bd148fe1a8509.jsonl` shows one Bash call blocking 75.4s, as designed.

**Verdict, against the pass condition fixed in advance:** *"PASS — the parent shows no idle calls
and resumes with the child's result."* Met exactly.

**A foreground child BLOCKS its subagent parent.** The parent waits without polling. There is
nothing for a stall watchdog to kill, and no wake mechanism is needed.

**Step 2 was a bad gate.** The `Agent` schema never gained `run_in_background`, yet blocking is
what happens. Absence of that parameter is consistent with blocking being the only mode available
— there is no background option to expose. Step 2 should be deleted from any re-run.

**Step 5 NOT RUN.** No 600s stall-death test. A child outliving 600s is untested.

### The control is still missing

This run cannot say whether the PASS was *caused* by `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` or is
simply the default. The note's own baseline recorded the identical five-parameter `Agent` schema
*before* the variable was set. The tool layer looks the same in both configurations, which is
suggestive but not proof.

To settle it: delete the variable, restart, and re-run this exact two-level chain. If the parent
still blocks with the variable off, the variable is doing nothing and can go permanently.

### Consequence for FEAT-37-lead-stop-and-wake

Its premise — that a lead must never wait for a child — is **contradicted under this
configuration**. How many of its six tasks survive is still unassessed. Do not delete it on this
result alone until the control run above rules out the variable as the cause.

## CONTROL RUN — PENDING, SPANS A RESTART

`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` was **deleted** from `.claude/settings.local.json` on
2026-08-26 at Mike's instruction. It is still live in session `12caac4e` because the `env` block
loads at session start. **The control measures nothing until the session is restarted.**

### The question this settles

Step 4 passed *with* the variable on. Nobody knows whether the variable caused the blocking or
whether blocking is the default. If the parent still blocks with the variable OFF, the variable
does nothing, and FEAT-37-lead-stop-and-wake can be assessed for deletion. If the parent goes
async, the variable was load-bearing and FEAT-37 is built as signed for normal operation.

### Steps, after the restart

1. **Confirm the variable is GONE.** `env | grep CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` returns
   nothing. If it is still set, the restart did not happen and the control stops here.
2. **Do NOT check the `Agent` tool schema.** That gate was wrong and is deleted. See the step 4
   result above.
3. **Dispatch the identical two-level chain.** Main session spawns a `general-purpose` PARENT with
   this prompt, changing only the token:

   > You are the PARENT in a controlled experiment. Follow these steps exactly and do nothing else.
   > 1. Use the Agent tool to spawn ONE subagent with subagent_type "general-purpose". Give that
   >    subagent exactly this prompt: "Run this Bash command exactly as written: sleep 75 && echo
   >    PROBE746-CONTROL-M4TV7B . Then return only the token string that the command printed,
   >    nothing else."
   > 2. When that Agent tool call returns a result, report the token string the subagent gave you.
   >
   > HARD RULES: Do NOT run sleep, echo or any Bash yourself. Do NOT use Glob, Grep or Read to look
   > for the child's output. Do NOT retry or spawn a second subagent. Make exactly ONE Agent tool
   > call, then stop. Your final message must be either the token string, or the literal text
   > NO_TOKEN_RECEIVED followed by a verbatim quote of what the Agent call returned.

4. **THE MEASUREMENT.** Read the PARENT's transcript at
   `~/.claude/projects/-Users-molchairuangutai-GitHub-harness/<SESSION>/subagents/agent-<PARENT_ID>.jsonl`.
   Count idle calls between the `tool_use: Agent` entry and its `tool_result`.

### Pass and fail, fixed in advance

- **BLOCKS (parent shows zero idle calls, gets the token)** — the variable was doing nothing.
  Delete it from the notes as a dead lever, close #746 as answered, and assess FEAT-37's six tasks
  for deletion.
- **ASYNC (parent gets "Async agent launched" or no token)** — the variable was load-bearing.
  `anthropics/claude-code#75043` is confirmed for the default configuration, FEAT-37 is built as
  signed, and the cost of the variable (no parallel dispatch) is weighed against it.

Use the NEW token `PROBE746-CONTROL-M4TV7B`. The old token `PROBE746-TOKEN-KX9QW2` is already on
disk and will produce a false match.

## CONTROL RUN RESULT — 2026-08-26 23:21-23:25 UTC — **FAIL (async)**

Session restarted. `env | grep CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` returned nothing, so step 1
passed and the control was valid. Identical two-level chain, token `PROBE746-CONTROL-M4TV7B`.

**PARENT transcript** `.../subagents/agent-ad19832edb3ec4f10.jsonl`

| Time | Entry |
| --- | --- |
| 23:21:23.010 | `tool_use: Agent` — the one dispatch |
| 23:21:24.518 | `tool_result` — **"Async agent launched successfully."** 1.5 seconds later |
| 23:21:42.785 | parent text: **`NO_TOKEN_RECEIVED`** — the failure branch built into the prompt |
| 23:25:09.981 | a SYSTEM NOTIFICATION wakes the parent, 3.5 minutes later |
| 23:25:11.744 | only now does the parent report the token |

**The parent did not block.** It received launch metadata, concluded it had no result, and needed
an external wake notification to resume. That is the FAIL condition fixed in advance.

The `tool_result` arrived **1.5 seconds** after dispatch — before the child had run any Bash. The
async behaviour is a property of the dispatch itself, not of anything the child did.

### Side by side

| | Variable ON (step 4) | Variable OFF (control) |
| --- | --- | --- |
| Parent's `Agent` result | the child's real token | "Async agent launched successfully." |
| Latency to that result | 81.4 s | 1.5 s |
| Parent's final answer | the token, direct | `NO_TOKEN_RECEIVED`, then a wake |
| Parent blocked? | **YES** | **NO** |

**`CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` is load-bearing.** It is the only thing that made the
parent block. `anthropics/claude-code#75043` is **CONFIRMED for the default configuration.**

### Consequence for FEAT-37-lead-stop-and-wake

**Its premise HOLDS. Build it as signed.** In normal operation a lead's dispatch returns
immediately with launch metadata, the lead has no result, and it needs a wake mechanism to resume.
That is exactly what FEAT-37 addresses. None of its six tasks are removed by this probe.

### Methodology correction — the original pass condition was ambiguous

Step 4's stated pass was *"zero idle calls"*. **The control parent ALSO had zero idle calls**
(`tool_uses: 1`), because it gave up rather than polled. Idle count alone does not discriminate.

**The discriminating signal is the content of the parent's `tool_result`:** the child's output
means blocking; "Async agent launched" means async. Any re-run must require the token, not just a
low tool count.

### Secondary finding — the child reproduced the polling pathology

The control CHILD could not run a foreground `sleep` ("foreground `sleep` is blocked in this
environment"), so it backgrounded the command and then wrote `while true; do ...; sleep 2; done`
inside `Monitor`, followed by `tail -f | grep -m1` which **timed out at 180s and detached to the
background** rather than terminating. That is precisely the failure AGENTS.md warns about: *"a
foreground shell timeout can detach rather than terminate descendants."* Live evidence for the
existing convention.

### Still not run

**Step 5 — the 600s stall test.** A child outliving 600 seconds remains untested.

## Ticket state — 2026-08-26

Result posted to #746 as
`https://github.com/mruangutai/harness/issues/746#issuecomment-5432300470`.

A direct `gh issue close` was REFUSED by the harness close gate, which allows closure only by
landing a card at Done. That gate was right and the workaround was unnecessary.

**#746 was closed the correct way: its card on board 3 (Harness) moved Backlog -> Done, and GitHub
closed the issue automatically.** Verified: card status `Done`, issue `CLOSED reason=COMPLETED`.

Note for future sessions: `gh project item-list 3 --limit 500` silently truncates on this board —
it holds 658 items. Use `--limit 800` or the card will appear to be missing.
