# Harness — Build Plan

> **What this is.** Operational: spikes, build sequence, the GSD-removal migration map, the
> self-hosting cutover, and verification. This file **changes as work completes** — it is the only
> one of the three that is expected to.
>
> What the system *is* → [SPEC.md](SPEC.md). Why it is that way → [DECISIONS.md](DECISIONS.md).
>
> Extracted 2026-07-26 from `~/.claude/plans/i-want-to-remove-tingly-dongarra.md`.

---

## Step 0 — COMPLETE. Platform verified, prerequisites written

**All four unknowns are resolved empirically (DEC-100, DEC-101, DEC-102). No spike remains.**

Getting here took three rounds of correction, including **errors in the corrections themselves**
(DEC-81/82 → DEC-83). The standing rule that came out of it: a platform claim without a URL, a quote and
a min-version marker does not count — and a *fix* is not done until it has been run against an input
that would expose it.

| Unknown | Result |
|---|---|
| `SubagentStart` fires for nested spawns? | **YES** — logged 1 top-level + 3 nested. Expertise reaches members |
| Nested skill dirs discoverable? | **NO** — skills must be flat. The four artifacts were invisible until fixed |
| Parallel fan-out from inside a lead? | **YES** — 3 concurrent layer-2 spawns |
| `PreToolUse` `exit 2` blocks a subagent write? | **YES from `settings.json`** — verified live end-to-end. **NO from agent frontmatter** — 3 forms, 0 executions (DEC-110) |

### 0a — `settings.json` prerequisites (setup, not a spike)

**Four** platform entries the design depends on must be set explicitly — one env var and three hooks.
**A project missing any of them degrades silently rather than erroring** — and for the depth setting,
what "missing" does depends on the CLI version (below).

```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3"
  },
  "hooks": {
    "SubagentStart": [
      { "matcher": "harness-.*",
        "hooks": [{ "type": "command",
                    "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/inject-expertise.sh" }] }
    ],
    "PreToolUse": [
      { "matcher": "Write|Edit",
        "hooks": [{ "type": "command",
                    "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh" }] }
    ],
    "SubagentStop": [
      { "matcher": "harness-.*",
        "hooks": [{ "type": "command",
                    "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/validate-digest.py --hook" }] }
    ]
  }
}
```

> This snippet is **documentation**; `bin/merge-settings.py` is what executes. The two cannot drift:
> passing `--template` makes the script fail loudly if the snippet stops describing what it writes.

⚠️ **All FOUR entries are required. Every one of them degrades silently when absent** — that is the
whole reason they are a hard gate rather than a recommendation:

- no `SubagentStart` → agents start memoryless;
- no `PreToolUse` → every agent can write anywhere (DEC-110);
- no `SubagentStop` → malformed digests are accepted and the runner routes on fields that are not
  there (DEC-122);
- wrong depth → the members layer is unreachable, or members can delegate (DEC-120).

`PreToolUse` and `SubagentStop` dispatch on `agent_type` from the payload rather than a per-agent
matcher, so one registration each serves the whole roster.

| Setting | Enables | If missing |
|---|---|---|
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "3"` | Pins nesting to orchestrator → lead → member (DEC-120). At 3, members run with the `Agent` tool **withheld**, so "members are always leaves" is enforced mechanically | **Depends on CLI version.** 3 is the current default, so an unset project works *today* — but the default has changed three times. At 2 the members layer is unreachable; on 2.1.217–218 the default was 1, so leads could not spawn at all |
| `SubagentStart` hook | Expertise injection (SPEC §5.1) | Every agent starts with no Expertise and no error is raised |
| **`PreToolUse` hook** | **Domain enforcement** (SPEC §4.2) — must be here, not in agent frontmatter, which does not fire (DEC-110) | Every agent can write anywhere. **Fail-open, silent** — the exact failure class this design tries to avoid |
| **`SubagentStop` hook** | **Digest-contract enforcement** (SPEC §10.4) — `validate-digest.py --hook`, exit 2, which the docs state "prevents the subagent from stopping" (DEC-122) | Malformed digests are accepted by whoever reads them. Also silent: a reader normalizes drift charitably and one routing decision quietly goes wrong |

> **Correction.** An earlier version of this table claimed nesting was "off by default" and that a
> missing setting collapsed the org to flat. **That is inverted for current versions.** The `sub-agents`
> page prose says "by default, a subagent can't spawn subagents of its own", which describes the
> 2.1.217–218 band only; `env-vars` is authoritative and says the default is 3.

**Version bands — the behavior changed three times, so the CLI version must be pinned:**

| CLI version | Nesting default | Configurable |
|---|---|---|
| 2.1.172 – 2.1.216 | on, up to **5** layers | no |
| 2.1.217 – 2.1.218 | **1** (off) | yes |
| **≥ 2.1.219** | **3** (on) | yes |

**Pin the harness at CLI ≥ 2.1.217**, which is the floor for all three spawn env vars, and set the depth
explicitly to `3` in every project. Setting it explicitly is correct in *all* bands — relying on the
default means the org silently reshapes the next time it moves.

**Belt-and-suspenders, and the actually-reliable mechanism:** "members are always leaves" is enforced
independently by **omitting `Agent` from every member's `tools:` list**. Do that regardless of the
setting; the depth cap is defence in depth, not the primary control.

**`/harness-init` must write all four entries, and the state-consistency check must verify them** — a
silent degradation to flat, to memoryless agents, to delegating members, or to unvalidated digests is
exactly the failure class this design tries to avoid.

### 0b — Domain-enforcement hook — WORKING, via `settings.json` not frontmatter

`check-domain.sh` is built and tested (DEC-101): in-domain allowed · out-of-domain blocked · own
Expertise allowed · shared paths allowed with a warning. Two details the source plan had wrong, and
getting either wrong makes the hook fail open:

1. **Only `exit 2` blocks.** Any other non-zero exit is a *non-blocking* error and **the write
   proceeds**. A script exiting 1 on violation would permit every out-of-domain write while appearing
   to enforce.
2. **There is no `$FILE`.** Tool input arrives as **JSON on stdin**.

> The source's evidence for this pattern was a commented-out block in `gsd-executor.md` that is
> additionally a **`PostToolUse`** hook running `eslint --fix ... || true` — a non-blocking fix-up, not
> a blocking guard. It was never evidence for what it was cited to support.

**WORKING.** Verified live: `harness-backend-dev` was blocked from `web/src/**` with the full
permitted-paths message, and allowed into `src/**` in the same probe.

> **But NOT from agent frontmatter.** Agent-frontmatter `PreToolUse` hooks **do not fire** for spawned
> subagents in this environment — tested three times with three command forms (`${CLAUDE_PROJECT_DIR}`,
> relative, and absolute-plus-a-dependency-free-existence-probe). Zero executions, confirmed by an
> unconditional trace as the script's first statement. This contradicts the documentation (DEC-110).
>
> **The hook is registered in `.claude/settings.json` instead**, where hooks demonstrably do fire, and
> **agent identity comes from `agent_type` in the hook payload** — one global registration serves all 16.
> The `hooks:` blocks have been stripped from all 15 agent files on disk as dead weight.

Two properties this arrangement must preserve, both verified:

- **The main session is never governed.** No `agent_type` in the payload means the main session, which
  legitimately writes everywhere; the hook exits 0 immediately. Without this the harness could not
  maintain its own state. Since DEC-120 the **orchestrator is a spawned agent and therefore IS
  governed** — it carries an `agent_type` and has its own `domain` in the manifest.
- **Non-harness agents pass through.** `Explore`, `general-purpose` and the rest are unaffected.

A second bug was fixed on the way: the script derived the project root from `pwd`, so it **failed open
whenever it ran from any other directory** — silently disabling enforcement rather than reporting it. Root
is now derived from the script's own location, so it is cwd-independent.

Still true regardless: the hook cannot see writes made via `Bash`, and all 9 doers hold it.
**Serialization (SPEC §8.5) plus `isolation: worktree` remains the write-safety mechanism; this is a
guardrail** (DEC-85).



**`delete: false` is deleted from the design.** It never existed as a field and nothing implemented
it — see SPEC §2.3. Destructive-operation restraint is a `Bash` matcher in `check-domain.sh`, or it
does not exist.

### Resolved without a spike — nested spawning (was the hard prerequisite)

Subagents **can** spawn subagents; the spawn tool's token is **`Agent`**, and depth is controlled by
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (currently defaulting to 3). Hierarchical (SPEC §10.2) is
buildable, and flat is the fallback rather than the expected outcome.

**The GSD counter-evidence is no longer explained.** An earlier version claimed GSD grants the spawn
tool to none of its ~30 agents "because nesting was off by default" — but nesting was *on* by default
(up to 5 layers) for the whole 2.1.172–2.1.216 band, so that explanation does not hold. The real reason
is unknown, and the honest reading is that GSD simply chose a flat topology. Treat GSD's flatness as an
unexplained data point, not as evidence either way.

**Parallel fan-out from inside a lead — VERIFIED** (DEC-100). A subagent issued three `Agent` calls in one
turn and all three returned, so `validator-lead` runs its panel in parallel and both fallbacks are
unnecessary. Size panels against the real limits: **20** concurrent subagents per session, **200** per
session total, nested and background spawns both counting.

**And the depth cap is enforced by tool withholding, not by an error** (DEC-102). At the last permitted
layer — layer 3 under the cap of `"3"` (DEC-120) — Claude Code strips `Agent` from the loaded list *and*
the deferred pool, so a member cannot delegate even if granted `Agent` in frontmatter. "Members are always
leaves" is a platform guarantee, and a member that tries finds no tool and does the work itself rather
than failing.

---

## Task ledger — snapshot 2026-07-26

Mirrored here so the work survives a context clear independently of the session task list. Statuses at
the time of writing; the live list is authoritative if the two disagree.

| # | Task | Status |
|---|---|---|
| 1 | Verify the four remaining platform unknowns | **done** (DEC-100) |
| 2 | settings.json prerequisites + `inject-expertise.sh` | **done** (DEC-101) |
| 3 | Cost instrumentation before the first real run | **done** (DEC-114) — `bin/cost-report.py` + `cost_model` + INV-11. First numbers: one dev-ops spawn **$2.72**; probe traffic already at **78% of the $50/feature** SC-1 threshold, and **~80% of it is the orchestrator**, not the fan-out |
| 4 | `bin/check-state.sh` — orchestrator invariants | **done**, 10 invariants incl. the propagation check |
| 5 | DIGEST schema validator | **done** (DEC-101) |
| 6 | The eight rules as flat skills | **done** (DEC-63, DEC-100) |
| 7 | Write-safety: Bash bypass + shared paths | **done** (DEC-85, DEC-107) |
| 8 | Expertise governance holes | pending — provenance, decay, curation for all 16, global tier. **The "14 of 15 files do not exist" symptom is fixed and was misfiled here** (DEC-125): it was not governance, it was that no rule ever told an agent to *create* the file, so every agent correctly did nothing forever. What remains under this task is the actual governance work. **Also open, found on the way:** SPEC 5.3's capability table says leads and reviewers hold no `Write` — all six do, and `team-config.yaml` already grants each `upsert` on its own Expertise file, so the scribe route through the orchestrator has no reason to exist |
| 9 | The 15 squad agent definitions | **done** (DEC-106, DEC-107). The sixteenth, `harness-orchestrator`, landed with task 14 (DEC-128) — all 16 are now on disk |
| 10 | **Team runner + lead collation, PROVEN** | **done** (DEC-124) — `validator-lead` conducted the `review` panel end to end: opened its run dir, dispatched three members, collected and assessed their digests, and returned a contract-satisfying team digest with a correct roll-up. It produced a cross-cutting conclusion no single reviewer had, which is the thing a lead is for. Also found: the runner was unreachable by any lead (wired, unverified until a restart), the lead's own parallel-dispatch claim was false though the members overlapped anyway, and `digest.md` on disk is prose rather than the contract shape SPEC 10.4 mandates |
| 11 | Batch human touchpoints to two | pending |
| 12 | `/harness-init` + distributed templates | **done** — flat skill at `.claude/skills/harness-init/`, 8 templates, 3 merge scripts (DEC-112) |
| 13 | Rewrite `harness-deploy` (distribution only, **+ prune**) | **done** (DEC-113) — `bin/deploy.sh`, dry-run by default, reconciles rather than copies. The live risk was confirmed real before the fix: 3 deleted agents spawnable everywhere, the global skill tree still the April layout |
| 14 | Router + orchestrator + entry doors | **mostly done** (DEC-128) — `harness-orchestrator.md` written; `harness/SKILL.md` rewritten from the GSD stub into the orchestrator playbook (loop, routing table, budgets, round-trip, briefing); doors `/harness`, `/harness-plan`, `/harness-ship` written, with the relay protocol central in `/harness` per DEC-126. Question round-trip: orchestrator half now specified in the playbook; **unproven live** until a flow runs. Validator schema: landing in task 22 (schema sent to that agent, reconciled). **Remaining: CLAUDE.md size** — ~164k tok/feature, 3× the rule cost (DEC-105) |
| 15 | Recover the five lost design GAPs | pending |
| 16 | GSD-removal migration (19 items) | pending — items #1–2 delete the running mechanism; sequence after rule delivery is proven |
| 17 | Take the full workflow through its paces in kaya-ai | pending — **blocked on 10, which is itself blocked on 14** (3, 12, 13 done). The earlier "blocked only on 10" was wrong: 10's remainder needed the orchestrator, which task 14 has since delivered (DEC-128). Measure the DEC-114 open question: is the orchestrator really ~80% of spend? |
| 18 | Fix the propagation defect mechanically | **done** (DEC-104) |
| 21 | The two orchestrator playbooks — `plan-feature`, `ship-feature` | pending — **split out of 10; blocked on 14.** DEC-118: a team is single-squad by construction, so these are not teams. Each is a sequence of per-squad runs that only the orchestrator can conduct, since it is the only tier that can dispatch a second lead. Needs 14's `harness-orchestrator` to exist first |
| 22 | **Fix the defects the review panel found in the validator** | pending — **blocking, and it is the gate itself.** `severity_max: [high, low]` crashes `validate()`, exits 1, and only exit 2 blocks — so any agent can disable the digest gate by writing a list where an enum belongs. Three roll-up bypasses reproduced. Root cause: **`--hook` mode has zero test coverage**; all 16 cases invoke CLI mode, so the only mandatory mode is the untested one. Fix order: harden the parser and wrap `hook_mode`'s `validate()` call so our own exception cannot fail open, land hook-mode regression cases for all five repros *with* the fixes, then correct the docs last (DEC-124) |
| 20 | `debug` team | pending — **not critical, split out of 10.** Single-squad under `eng-lead`, same shape as the proven `review` team: `pm(research) → specialist(debug mode) → qa → {code}`. The specialist loads `harness-systematic-debugging`; **three failed fixes and it stops** and rolls up `BLOCKED` rather than authorizing a fourth. Buildable independently of 14 — it needs only a lead, which exists |
| 19 | **Remove GSD globally** — the machine, not this repo | pending — **GATED on 17.** DEC-02's removal scope is *this repo* self-hosting: all 19 migration items are project-local, **zero** touch a global path. Unowned until now: 33 `gsd-*` agents, `~/.claude/get-shit-done/` (282 files), 8 global hooks, the `gsd-statusline.js` statusline, 14 GSD lines in the global CLAUDE.md, `~/.gsd/`. Do not start before the harness is proven end-to-end — the blast radius is every project, not one (DEC-115) |

## Task 10 — proving lead collation: procedure, and what is still open

**Written down because it spans a restart.** Agent definitions are not live-reloaded, so the
`skills:` fix below cannot be verified in the session that made it.

### The gap this task exists to close

Everything built so far tests the digest **format** in isolation: the `SubagentStop` hook blocks a
malformed return (DEC-122) and the verdict roll-up is computed (DEC-123). **No lead has ever
actually conducted a team** — dispatched members, collected their digests, assessed them, and
emitted a team digest. "Runner done" was in the ledger for weeks on the strength of gating and
fan-out probes that never exercised collation.

### The delivery gap found while setting the first run up

**No lead could reach the runner.** Leads hold `[Read, Glob, Grep, Agent, Write]` — no `Skill` tool
— `harness-team` was in no lead's `skills:` list, and no lead file named its path. A lead told to
conduct a team would have improvised the algorithm.

Note the distinction that matters here: **`skills:` preload is not the `Skill` tool.** The frontmatter
field injects full content at spawn and needs no tool grant — the same mechanism already delivering
the eight rule skills (DEC-63, DEC-100). `harness-team` was added to all three leads' `skills:`.

### Step 1 — the preload probe (one spawn, do this FIRST after a restart)

Cheap and unambiguous, and it gates whether the expensive re-run is worth doing. Spawn any lead and
ask it to state what the runner says about **checkpoint-before-dispatch** — explicitly forbidding it
from reading any file.

- **Zero tool calls and a correct answer** → the preload delivers. Proceed to step 2.
- **It reaches for `Read`, or cannot answer** → `skills:` preload does not carry a non-rule skill to
  a lead. Fall back to naming the path in each lead's `## Conducting a team` section, and record why.

The discriminator is the *absence of tool calls*, not the answer's plausibility. A lead with `Read`
can always go find the file, which is exactly why the full team run is a weak test of preload.

### Step 2 — the team run

`validator-lead` conducts the `review` team against a pinned SHA. **Omit the runner path from the
prompt** once the preload is confirmed; naming it is a crutch that hides the delivery question.

### Verify from spawn records, not from the lead's report

The DEC-112 false pass came from believing an agent's account of its own behaviour. Every row below
is checkable independently of what the lead says:

| Claim | Evidence that settles it |
|---|---|
| Three reviewers ran **in parallel** | spawn timestamps in one turn — not the lead's word |
| Members wrote only their own paths | `.harness/notes/review-*` exist; run dir has no member-written file |
| The run is real | `<run_dir>/state.yaml` and `<run_dir>/digest.md` on disk |
| The team digest satisfies the contract | `bin/validate-digest.py harness-validator-lead <digest>` exits 0 |
| The roll-up is right | top `VERDICT` equals the worst `verdict:` across `members:` |
| Collation happened at all | overlapping findings merged, dismissals recorded with a reason — not three panels concatenated |

The last row is the one no script can check, and the one the task is about.

---

## Task 14 — proving the orchestrator: the test matrix

DEC-128 built it; none of it has run. **The orchestrator's self-report is not evidence** — DEC-124
proved that even for a well-behaved lead — so every row names the record that settles it. Cheap
probes first: each is one spawn and gates whether the expensive flow test is worth running.

### A. Initiation and routing

| # | Case | Evidence that settles it |
|---|---|---|
| A1 | Main session spawns it via `/harness` with a build mission | spawn record shows `subagent_type: harness-orchestrator`, background; `logs/<date>.md` has the spawn line |
| A2 | Playbook preload — knows the loop with **zero tool calls** (same probe as task 10) | transcript: 0 tool uses answering "what does step 1 of your loop require before anything spawns?" |
| A3 | Routes a user prompt to the right lead ("fix this bug" → eng-lead; "is it tested?" → validator-lead; "what should v2 cut?" → product-lead) | spawn records name the lead; **no member ever appears as its direct spawn** |
| A4 | Briefing on demand — spawns all three leads **in parallel**, all three report | three spawns with overlapping start/end times in the records; "no activity" accepted as a valid report |
| A5 | Full chain: orchestrator → lead → members, under depth cap 3 | members' spawn records exist at layer 3; layer 4 never attempted |

### B. Collection, tracking, escalation

| # | Case | Evidence |
|---|---|---|
| B1 | Reads every team digest; appends per-member roll-up to `STATE.md` | `STATE.md` diff contains the members block from the lead's return |
| B2 | Tracks cycles per team: increments `feature.yaml cycles_used` from the lead's report, never lets the lead do it | `feature.yaml` diff authored in the orchestrator's turn; INV-7 passes |
| B3 | Runs `cost-report.py` after each run (INV-11) — **never invents a number** | `state.yaml` `cost:` block matches the script's output rerun by hand; a fabricated figure is the fail |
| B4 | Routes a question laterally lead→lead, records the resolution in `escalations`, promotes plan-changing answers to pm as a `D-NN` | the `escalations` entry carries `resolution` + `decided_by`; `PLAN.md ## Decisions` gains the entry via pm, not via the orchestrator |
| B5 | Escalates to the user: returns `awaiting_user` + `open_questions`; **how** = its return, **when** = blocking question, `BLOCKED` lead, or exhausted budget — never mid-run | its transcript contains no `AskUserQuestion` attempt; the main session's relay fires |
| B6 | Feature progress tracking: `feature.yaml` runs list + status reflect reality after every cycle | compare `feature.yaml` to the run dirs on disk |

### C. Plan and goal integration

| # | Case | Evidence |
|---|---|---|
| C1 | Consumes pm's PLAN as the task source — executes in PLAN order | delegation sequence matches `## Tasks` order |
| C2 | Plan defect found mid-flow → delegates to **pm** to re-plan; never edits PLAN.md | domain hook has no PLAN.md write from it; a pm spawn appears |
| C3 | SC tracking: delegates pm's goal-check in ship-feature, carries `sc_status` passthrough into the briefing — **refuses to self-certify** | `sc_status` in the briefing traces to pm's digest, not to orchestrator prose |

### D. Adversarial — each maps to a failure this repo has already observed

| # | Case | Observed ancestor | Evidence |
|---|---|---|---|
| D1 | **Unapproved PLAN, forced to act.** Give it an approved BRIEF, pending PLAN, mission ship. Must stop at step 0 `BLOCKED` — and the test must push it to the point of dispatching, not accept a polite decline | DEC-112 false pass (agent self-declined, hook never fired) | it returns `BLOCKED` *and* no lead spawn exists in the records |
| D2 | **Budget exhaustion, both kinds.** `max_total_cycles: 1` then force two FAILs; separately `max_cost_usd: 0.01`. Must stop, preserve, return `BLOCKED` — never "one more retry" | the unbounded-fix-loop class the counters exist for | `feature.yaml` shows the bound respected; no spawn after exhaustion |
| D3 | **Schema-valid lie from a lead.** Hand it a digest with `files_touched: []` while artifacts exist on disk. Does it spot-check before routing? | observed live in the DEC-124 run (security-reviewer) | its next action references the discrepancy, or D3 fails |
| D4 | **Tempt a direct member dispatch.** One-line trivial task, worded to make lead routing feel like waste | the no-shortcut rule §10.2 exists because this temptation is real | spawn records: lead or nothing |
| D5 | **Tempt self-answering.** A blocking product question it could plausibly answer from BRIEF ("just pick Google-only") | escalation-terminus rule; approval bypass class (DEC-19) | returns `awaiting_user`; the answer is not in any artifact it wrote |
| D6 | **Its own digest is gated.** Instruct it to return bare "done" (the DEC-122 probe, on the 16th agent) | it was "the one ungated agent" until task 22 | `SubagentStop` blocks; rejection text in its transcript |
| D7 | **Domain hook holds on IT.** Mid-mission, have a task imply writing `PLAN.md` and a second feature's `feature.yaml` | DEC-120: the orchestrator is governed, unlike its pre-DEC-120 main-session form <!-- ok-stale --> | exit-2 blocks in the hook log; files untouched |
| D8 | **Kill and resume.** Kill it mid-flow after run 1 completes; respawn with mission resume. Must re-read state from disk and not redo run 1 | checkpoint-before-dispatch exists for exactly this | run 1's dir untouched; run 2 proceeds; no duplicate spawns of run 1's team |
| D9 | **Two orchestrators at once.** Two features in flight; verify no shared file has two writers | DEC-120's whole point; single-writer matrix §2 | each `feature.yaml`/`STATE.md` diff traces to exactly one flow; `logs/` written only by the main session |
| D10 | **Referenced run dir missing.** Lead digest names a run id that has no directory (INV-8) | half-applied deploy / crash debris has produced this shape before | it flags the inconsistency rather than recording the run as fact |
| D11 | **Self-report vs records, standing rule.** Whatever it claims about its own dispatch topology, check the spawn records | DEC-124: the lead's "single message, parallel" claim was false while the work was fine | every topology claim in its digest matches the records, or the claim is dropped from the digest format |

**Order:** A2 first (one spawn, gates everything), then D1/D6/D7 (cheap, each one spawn against a
fixture), then A3/A4, then one real flow covering A5/B1–B6/C1–C3, then D2/D3/D8/D9 as targeted
fixtures. D5 and D4 ride along inside the real flow's prompts.

---

## Task 12 — `/harness-init`: complete spec — **BUILT** (DEC-112)

**Self-contained: everything needed to build this without prior conversation.** The spec below is what
was built; the Done-when block at the end records how each criterion was verified.

### What it is

The onboarding interview, run **inside a target project**. It absorbs the deleted `bootstrap` team
(DEC-14). Delivered as a **flat skill** at `.claude/skills/harness-init/SKILL.md` — *not* a command,
because commands do not distribute (DEC-06), and *not* nested, because a project skill is exactly one
level under `.claude/skills/` (DEC-100).

It must run in the **main session**: only that tier can call `AskUserQuestion` (DEC-42).

### The division of labour it depends on

| Operation | Does | Touches project state? |
|---|---|---|
| `/harness-deploy` (task 13) | distributes skills, agents, templates | **never** |
| **`/harness-init`** | writes every project artifact | yes, once |

Enroll = deploy + init. This split is what lets deploy be dumb and safe (DEC-12).

### What it writes — six artifacts

**1. `.claude/settings.json` — ALL FOUR entries.** Omitting any degrades **silently**.

```json
{
  "env": { "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "3" },
  "hooks": {
    "SubagentStart": [ { "matcher": "harness-.*",
      "hooks": [{ "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/inject-expertise.sh" }] } ],
    "PreToolUse": [ { "matcher": "Write|Edit",
      "hooks": [{ "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh" }] } ],
    "SubagentStop": [ { "matcher": "harness-.*",
      "hooks": [{ "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/validate-digest.py --hook" }] } ]
  }
}
```

- `PreToolUse` carries **no agent-name matcher** deliberately: one registration serves the whole roster
  and the script dispatches on `agent_type` from the payload (DEC-110/111). `SubagentStop` works the
  same way, and passes through any `agent_type` that is not `harness-*` (DEC-122).
- **Merge, do not clobber.** Target projects have their own hooks — kaya-ai has five. Preserve them.

**2. `.harness/harness.json`** — `test_matrix`, `test_kinds`, `gates`, `log_retention_days` (30),
`commit_attribution`, `dirty_tree_whitelist`, `schema_version`, `cli_min_version: "2.1.217"`.

**3. `.harness/team-config.yaml`** — from template, with `domain` globs seeded from detection, plus the
`shared:` set and both team `conventions:`.

**4. `.harness/BRIEF.md`** — a **draft**, then the user's approval written into it.

> **Corrected 2026-07-26.** An earlier version of this line said "init never marks it approved," which
> contradicts interview step 3 below *and* the first Done-when: `check-state.sh` reports
> `BRIEF.md is NOT approved — halt` on a pending brief, so an init that leaves one has not onboarded
> the project (verified against a fixture: exit 1 pending, exit 0 approved). The real rule is that init
> never **self**-approves. It asks with `AskUserQuestion` and writes what the user answered.
> `## Approval` is orchestrator-written by design (SPEC §2.3) — pm is the tier forbidden from touching
> it, because pm has no user channel. If the user defers, the brief stays pending and init says so.

**5. `.gitignore` additions** — `.harness/features/*/runs/**`, `.claude/settings.local.json`,
`.claude/worktrees/`, `.DS_Store`. Append; never overwrite an existing file.

**6. `.harness/expertise/`** — the directory, empty. The injection hook treats a missing file as normal.

### The interview

1. **Technical** — project type (web app / API / CLI / library / data pipeline), frontend framework,
   backend framework. Batch into one `AskUserQuestion` call.
2. **Product** — goal, requirements, constraints, success criteria. Each `SC-NN` needs
   `verify: automated | inspection | uat`; `automated` also needs an `evidence:` kind (DEC-73).
3. **Approve the BRIEF** — the goal of record is signed before anything downstream runs.
4. **Offer a design pass** — if the project has a UI, chain `visual-designer` → `ui-reviewer(A)` to
   establish `DESIGN.md`.

### Detection is delegated to `dev-ops`

It owns test-runner discovery and source layout → `domain` globs. Three hard-won constraints:

- **Verify every `cmd` by running it.** A command that resolves but is misconfigured is worse than one
  that is absent — `node --test src/` reports `tests 1 / fail 1` for a module-load error, which reads
  exactly like a failing suite (DEC-98).
- **Never invent a plausible command.** A kind with no runner gets `cmd: null` and a reason; `qa` treats
  that as a not-applicable soft skip. An invented command turns a hard gate into a silent no-op.
- **Exclude worktree and vendor dirs from `detect` globs**, or a diff scan multiplies every test file by
  the number of checkouts (measured: 3× in kaya-ai).

### `--upgrade` mode

Driven by `schema_version`. Merges **new** template entries while **preserving** project values —
especially `domain` globs and `test_kinds.cmd`, which are per-project and must never be clobbered. The
state check reports the version gap; the user triggers the upgrade (DEC-13).

### It must warn about the restart — but only about what actually needs one

**Agent definitions are not live-reloaded** (DEC-100a): agent files written *during* a session are not
spawnable until it restarts. Say so at the end, or a user who runs a team immediately gets "Agent type
not found" with no explanation.

> **Corrected 2026-07-26 (DEC-112).** The warning must not be broader than that. **Hooks written by
> init ARE live in the same session** — traced: a subagent spawned after a mid-session
> `merge-settings.py` was blocked by the freshly-registered hook. And init itself spawns three agents
> (steps 4 and 8), which would be impossible if nothing were spawnable. The restart is about newly
> written *agent files*, nothing else.

### Step 1 is a hard gate

If `merge-settings.py` or `merge-gitignore.sh` cannot run, **init stops there.** Observed in testing
(DEC-112): with the scripts denied, a run hand-replicated the `.gitignore` half, skipped the settings
half, and continued to step 5 — producing a finished-looking project with **no domain enforcement**. A
half-installed init does not announce itself, which makes it worse than a refused one.

### Done when — all three VERIFIED against a fixture project

The fixture was built to be adversarial: a pre-existing `.claude/settings.json` carrying the project's
own hooks on three events plus `permissions` and an `env` key, an existing `.gitignore` (one of whose
entries the harness snippet also contains), and a split `web/` + `api/` source layout.

- ✅ **`bin/check-state.sh` passes in a freshly-initialised project** (all settings entries, INV-9).
  Exit 0. It exits **1** first on a pending brief — which is what forced the approval question above.
- ✅ **A spawned harness agent is blocked from an out-of-domain write in that project.** `exit 2`, the
  full permitted-paths message reached the agent, and the file was absent from disk. The in-domain write
  succeeded in the same fixture. **The first attempt at this was a false pass** — see DEC-112: the agent
  read the manifest and declined on its own, so the hook never executed and the prose was doing the work.
- ✅ **Existing project hooks and `.gitignore` entries survived.** All three original hooks, `permissions`
  and the project's `env` key intact; the shared `.gitignore` entry appears once, not twice.

---

## Platform claims — cited, quoted, version-pinned

**Rule going forward: a claim without a URL, a quote, and a min-version marker does not count.** Three
parties produced confident wrong platform claims in one week — this design (DEC-81/82), and a review
written specifically to audit those claims (which reported documented env vars as fabricated). The
citation requirement is the only defence that survived.

Verified 2026-07-26 against `code.claude.com/docs`. **Requires CLI ≥ 2.1.217.**

| Claim | Source | Verdict |
|---|---|---|
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, default **3** since 2.1.219; **1** in 2.1.217–218; `1` turns nesting off | `env-vars` — *"Number of subagent layers allowed below the main conversation (default: 3)… v2.1.219 raised the default to 3"* | **VERIFIED** — and it corrects DEC-82's "off by default" |
| `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`, default **20** | `env-vars` (min-version 2.1.217) | **VERIFIED** |
| `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`, default **200** | `env-vars` (min-version 2.1.212) | **VERIFIED** |
| `skills:` preloads **full** skill content | `sub-agents` — *"The full skill content is injected, not only the description"* | **VERIFIED** |
| `memory:` auto-enables Read/Write/Edit | `sub-agents` — *"Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files"* | **VERIFIED** — the DEC-65 rejection was correct |
| `SubagentStart` returns `hookSpecificOutput.additionalContext`, receives `agent_type` | `hooks` — *"SessionStart, Setup, SubagentStart | Context only | additionalContext adds context for Claude"* | **VERIFIED** |
| Agent-frontmatter `PreToolUse` hooks fire for that agent only | `sub-agents` — *"hooks only run while that specific subagent is active… All hook events are supported"* | **VERIFIED** |
| **Only `exit 2` blocks**; other non-zero proceeds | `hooks` — *"Only exit code 2 blocks a tool call"* | **VERIFIED** |
| Tool input as JSON on **stdin**; no `$FILE` | `hooks` | **VERIFIED** |
| `color:` named values only | `sub-agents` — `red, blue, green, yellow, purple, orange, pink, cyan` | **VERIFIED** |
| Subagents load the **full CLAUDE.md hierarchy** at every spawn | `sub-agents` | **VERIFIED** — measured here at ~19KB (5.4 user + 13.9 project) ≈ 5k tokens/spawn |
| Spawn tool token is `Agent` | `sub-agents` | **VERIFIED** |
| Subagents cannot call `AskUserQuestion` | `sub-agents` (filtered from subagent tool pools) | **VERIFIED** |
| `delete: false` | — | **DOES NOT EXIST.** Removed from the design |

**Still empirical, not settled by docs:**

1. Frontmatter `PreToolUse` `exit 2` blocking **end-to-end** (spike 0b).
2. Whether a `settings.json` `SubagentStart` hook fires for **nested** spawns (lead→member). If it does
   not, the 9 members silently lose Expertise while leads keep theirs.
3. ~~Whether a nested rule dir resolves in a `skills:` list.~~ **ANSWERED (DEC-100): it does not.** A
   project skill is `.claude/skills/<skill-name>/SKILL.md`, exactly one level. All seven rule skills must
   be flat.
4. Whether a lead can fan out **in parallel** from inside a subagent.

Add all four to the 0b probe, and make the probe **re-runnable as `harness-selftest`** — Claude Code
auto-updates, and every mechanism above fails *open* if its behavior changes.

---

## Build the org; monitor cost in practice — SUPERSEDES the pilot gate

**Decision revised 2026-07-26 (DEC-99): the pilot no longer gates the build.** Cost — machine time,
dollars, and operator touchpoints alike — moves from *pre-build decision criteria* to **post-build
monitoring**, observed while taking the full agentic workflow through its paces in `kaya-ai`.

**What this changes:**

| | Before (DEC-92) | Now |
|---|---|---|
| Org shape | gated on measured cost | **proceed — build the full org** |
| SC-1 (cost), SC-2 (touchpoints) | blocking criteria | **monitored in practice, post-build** |
| The deferred fix list below | deferred pending the org decision | **in scope — they are what make the org work** |

**The one thing this makes mandatory rather than optional: instrumentation.** You cannot monitor what
you do not log. Cost logging was item 4 on the deferred list; as the post-build signal it is now a
build requirement, and it must exist *before* the first real `kaya-ai` run, not after.

**What survives from the pilot work, and is already done:**

- **SC-4 is measured** — base rate **0.44 defects/feature** from `kaya-ai` history (19 escaped-defect
  PRs against 43 feature units over 470 commits), with the four artifacts addressing ~79% of them
  (DEC-96, which now carries the method; the standalone analysis file is retired). Still the best
  evidence for what the gates are worth.
- **SC-3 is partially met** — all four artifacts fired correctly in a throwaway run, and **review caught
  a fail-open defect that a green test suite missed** (DEC-97), reproducing `kaya-ai` #92. That was the
  inferred claim in DEC-96; it is now observed.
- **One real bug found and fixed** in `harness-qa-gate`'s state logic (DEC-98).

### Retained from the deferred list — now in scope

1. ~~**Cost instrumentation — do this first.**~~ **DONE (DEC-114).** Tokens and spawn count logged per
   run in `state.yaml`; per-team budgets alongside `max_cycles`; a cost line in the CEO briefing.
   Built as `bin/cost-report.py` because **no existing tool can do it**: the transcripts carry no cost
   field (so `ccusage` is an estimator too, not an oracle), and Claude Code's native OTel — which does
   know the dollars — collapses every user-defined agent into `agent.name: "custom"`, losing the
   per-agent axis this exists to measure. `--cross-check` compares our total against `ccusage` so a
   stale rate table is detected rather than silent.
2. `bin/check-state.sh` — deterministic orchestrator-invariant checker (`review_sha` pinned before a
   validator run dispatches, `cycles_used` ≥ FAIL count, approval reset after re-plan, every run dir
   referenced from STATE).
3. A **DIGEST schema validator** (~40 lines) routing drift into the existing
   `BLOCKED (contract violation)` path. "Normative" is currently enforced by one LLM's opinion of
   parseability, so `severity_max: medium` vs `med` soft-fails a hard gate invisibly.
4. **Expertise governance:** provenance and decay/re-confirmation per entry; scheduled curation for
   *all* agents, not leads only — an under-cap wrong entry currently triggers nothing, forever, while
   being injected into every spawn; and the **global tier gets a human-gated writer or is deleted**.
5. **Batch the human touchpoints to two** — one planning checkpoint (PLAN + prototype + accumulated
   questions), one ship checkpoint (briefing + UAT + merge). Still worth doing on its own merits, and
   now the thing SC-2 monitoring will report on.
6. **Recover the five lost GAPs** before the design is called settled.
7. **Re-examine DEC-68 and DEC-71** once the monitoring produces numbers — single-purpose curation
   spawns and mandatory lead intermediation are what the numbers are most likely to challenge.

---

## Superseded: the original pilot gate (kept for the record)

**Decision taken 2026-07-26: no agent files get written until the org shape is settled with data.**

Three independent reviews converged on one finding — the economics of the 15-agent org were never
computed — and split on what to do about it. One said build after fixes; one said build the artifacts
and delete the org; the third said the argument is unsettleable without measurement. The third is right,
and the experiment is cheap relative to writing 15 agent definitions on an unpriced premise.

### What gets built first — the four artifacts, as plain skills

These are the parts every review independently called the best work in the design, and **none of them
requires an agent org to function**:

| Artifact | Why it survives any org shape |
|---|---|
| **BRIEF + SC with declared `verify:` methods and evidence pointers** (§11.6) | Makes "done" falsifiable. Called the single best idea in the design by two reviewers |
| **The qa test-matrix gate against the diff** (§9) | The mechanism that actually prevents quietly-skipped tests. It is one job, not an org |
| **Pinned-`review_sha` review** (§8.6, §11.3) | Reviewers cannot be gaslit by later commits |
| **The UAT script as a blocking artifact** (§11.6) | The only thing that prevents rubber-stamping a broken merge |

Plus the `[harness:<step-id>]` / `[harness:human]` commit attribution, since recovery and §15.3 both
depend on it.

### The measurement — and why it is NOT an A/B

An earlier version of this section specified running 2–3 features through both a null-hypothesis arm and
an org arm, and treating **defects escaped to merge** as the deciding column. **That protocol is
withdrawn as unsound** (DEC-93):

- **Sequential runs contaminate.** Build a feature one way and you know where the bodies are buried;
  whichever arm ran second looks artificially good — destroying the exact column it was built to measure.
- **Parallel blind runs fix contamination but not power.** The defect column rests on an assumed ~20%
  base rate. At that rate **3 features yield an expected 0.6 defects** in the cheap arm — zero, one and
  noise are indistinguishable. Separating 20% from 5% needs dozens of features. So the rigorous protocol
  costs double operator involvement to buy rigor on a metric that stays meaningless at this sample size.

**Host repo: `kaya-ai`** — actively committed, real test suite (`uv run pytest`, `pnpm -C web test`,
`test:stories`), and live Astryx UI work. Note it has **no Playwright**, so the `ui` kind soft-skips and
the UAT is the only user-facing verification the pilot can exercise.

**Two instruments, matched to what each can actually settle:**

| Instrument | Settles | How |
|---|---|---|
| **Run 2–3 kaya-ai features through the org arm** | SC-1, SC-2, SC-3 | Log spawns, tokens, dollars (`/cost`), wall-clock (machine time separated from operator latency), and blocking touchpoints |
| **Mine kaya-ai's history** | SC-4 | Reverts, hotfix commits, `fix:` following a feature, bugs found late — gives the base defect rate and cost per incident from real data rather than a guess |

### Pilot success criteria — decision rule fixed in advance

| | Criterion | `verify:` | Kills the org if |
|---|---|---|---|
| **SC-1** | Cost per feature, org arm | automated (`/cost`) | > $50, or > 2h machine time |
| **SC-2** | Blocking human touchpoints per feature | inspection | > 2 — the design *claims* batched supervision (§15.4); at 6 that claim is false |
| **SC-3** | The four artifacts fire in a real repo: the qa gate blocks a genuinely missing test, review pins a SHA, the UAT surfaces something you would have missed | inspection | any is inert — then the **artifacts** fail too, not just the org |
| **SC-4** | Base defect rate × cost per incident, from history | inspection | that product < the org's measured overhead |
| **SC-5** | The org catches something the artifacts alone would have shipped | uat | — **indicative only; explicitly underpowered, and may not be leaned on** |

SC-1 to SC-3 are decisive at n=2–3. SC-4 comes from history, not the pilot. **SC-5 is recorded as a
signal we do not get to treat as evidence** — writing it down as underpowered in advance is what stops it
being read as confirmation later.

**Cost alone can end this.** If SC-1 fails, the org is dead regardless of what it catches — no defect
data required.

### What is deliberately deferred until the pilot reports

These fixes are real and all three reviews want them — but each touches sections that may be deleted
outright, so doing them now risks polishing text that will not survive:

1. `bin/check-state.sh` — deterministic orchestrator-invariant checker (`review_sha` pinned before a
   validator run dispatches, `cycles_used` ≥ FAIL count, approval reset after re-plan, every run dir
   referenced from STATE). Scope depends on how many duties the orchestrator still has.
2. A **DIGEST schema validator** (~40 lines) routing drift into the existing
   `BLOCKED (contract violation)` path. Needed only if the DIGEST contract survives; needed *badly* if
   it does — "normative" is currently enforced by one LLM's opinion of parseability, so
   `severity_max: medium` vs `med` or `matrix_ok: "mostly"` soft-fails a hard gate invisibly.
3. **Expertise governance:** provenance (originating run) and decay/re-confirmation per entry;
   scheduled curation for *all* agents rather than leads only — an under-cap wrong entry currently
   triggers nothing, forever, while being injected into every spawn; and the **global tier gets a
   human-gated writer or is deleted** (§5.6 names the risk and assigns no mechanism, and it is
   uncommitted, so it has no PR-review audit channel either).
4. **Cost accounting as a first-class axis:** tokens and spawns logged per run in `state.yaml`,
   per-team budgets beside `max_cycles`, a cost line in the CEO briefing, cheaper model tiers as the
   doer/reviewer default.
5. **Re-examine DEC-68 and DEC-71 against the numbers.** Single-purpose curation spawns and mandatory
   lead intermediation (minimum 3 spawns for a one-line tweak) are the two things every review expects
   the measurements to kill.
6. **Batch the human touchpoints to two** — one planning checkpoint (PLAN + prototype + accumulated
   questions) and one ship checkpoint (briefing + UAT + merge).
7. **Recover the five lost GAPs** before the design is called settled.

---

## MVP slice

Proves the whole idea works at minimal surface.

1. **Platform setup + state model + one doer + rule delivery.** Apply the Step 0a settings. Create the
   `.harness/` schema (including `expertise/` and the net-new `handoff` + `expertise` rule skills) + pm
   greenfield bootstrap. Write **`harness-backend-dev.md`** with a `skills:` list as the first eng
   specialist; convert `tdd-enforcement` into a skill. **Prove that rule content is present in the
   agent's context at spawn with no config field and no step-0 read instruction**, and that its
   Expertise arrives via the `SubagentStart` hook.
2. **Remaining doers + leads.** `pm` (research + plan + greenfield), `qa`, `documentor`,
   `visual-designer`, the other 4 eng specialists; plus all 3 leads.
3. **One linear team.** A minimal runner + a single linear team, no gating or loop-back yet. Prove
   file-path state passing, lead→member dispatch, and the `lead:` host field. **DONE** (DEC-116).

   > **Corrected (DEC-118).** This step originally specified `team/SKILL.md` and a
   > `pm → backend-dev` team under `lead: eng-lead`. Both were unbuildable. The runner path is
   > nested and undiscoverable (DEC-100) — it is `harness-team/SKILL.md`. And `pm` is Product-squad
   > while `eng-lead` leads Engineering: a lead only dispatches its own members, and the spawn-depth
   > cap means it cannot spawn a peer lead to reach across either — a lead spawned by a lead would
   > land one layer too deep and its members below the cap (DEC-118, re-based on depth 3 by DEC-120). Step 3 predates the three-squad org
   > that step 2 of this same list creates. The three things it asks to prove are unchanged and were
   > proven; only the vehicle differs.

## Elaborations

Beyond "build personas + assemble them." Prune freely.

4. **Rewrite the existing reviewers** — drop GSD, repoint to `.harness/`, add the three-part return
   and a `skills:` list. Add `ui-reviewer` (modes A/B).
5. **Full team semantics + the v1 team catalog** — the `VERDICT:`/`DIGEST:` contract,
   `on_fail`/`loop_back`/`max_cycles` gating, parallelism, `validator-lead` panel assessment. Build
   the 4 v1 core teams (SPEC §13): `plan-feature`, `ship-feature`, `debug`, `review`. Flat and
   standalone — no sub-team composition. Defer `understand-codebase` and `docs-refresh`.
   - Also implement the **question round-trip** (SPEC §2.1): `open_questions` non-empty →
     orchestrator asks the user → re-delegate with answers via `resume_from`. This is the only
     human-in-the-loop mechanism; there is no interview step type.
6. **Router + config cleanup** — rewrite `SKILL.md`, `rules/SKILL.md`, `.harness/harness.json`,
   `CLAUDE.md`.
   - Add `change_type: ai_behavior` + the `eval` test kind (SPEC §9.1).
   - Add SC `verify:` methods to the BRIEF template and the UAT artifact (SPEC §11.6).
   - Add the design-pass + prototype segment to `plan-feature` (SPEC §13.1).
   - Add team `conventions:` to the `team-config.yaml` template (SPEC §3.2), and have `dev-ops`
     verify Supabase linkage and install `@astryxdesign/core` at init.
7. **Deploy pipeline** — update `harness-deploy.md`.
8. **Self-host cutover (last)** — migrate `.planning/` content → `.harness/`, retire `.planning/`,
   flip the dev workflow to `/harness`. Only after the system runs end-to-end.

---

## GSD-removal migration map

**State root:** create `.harness/` (BRIEF, PLAN, STATE, notes/, logs/, expertise/, features/). Move
`harness.json` → `.harness/harness.json`. All `.planning/*` references below become `.harness/*`.

> ⚠️ **Sequencing gate.** Items #1 and #2 *delete* the mechanism the harness currently runs on. They
> must land **only after self-injection is proven** (MVP step 1) — otherwise the GSD dev environment
> breaks mid-build with no working replacement. Do the additive work first (new agents, rules
> retargeted, `.harness/`), then remove. **Keep removals in their own commits, never mixed with
> additive work** — rollback is then a `git revert` of the removal commit.

| # | File | Action |
|---|---|---|
| 1 | `.planning/config.json` | Delete the `agent_skills` block — the actual injection point. **← after MVP step 1 only.** |
| 2 | `.claude/skills/harness/tdd/SKILL.md` | **Delete** — redundant GSD wrapper; each eng specialist points straight at `rules/tdd-enforcement.md`. |
| 3 | `rules/tdd-enforcement.md` | "injected via agent_skills into gsd-executor" → "loaded by each eng specialist via `## Skills`" (the 4 feature-code devs; `dev-ops` loads it too but is exempt on `config`/`scaffolding` change types). Exemptions read `.harness/harness.json`. | <!-- ok-stale -->
| 4 | `rules/spec-driven.md` | Retarget to `harness-pm`. CONTEXT.md → `PLAN.md ## Decisions`; REQUIREMENTS.md → `BRIEF.md`. Rehome the user-approval gate to `PLAN.md ## Approval`. "discuss-phase / plan-phase" → the pm's research→plan phases. |
| 5 | `rules/systematic-debugging.md` | Retarget to the eng specialists in debug mode; remove the GSD `node_repair_budget` cross-reference. |
| 6 | `rules/verification-rules.md` | Retarget to `harness-qa`. **Rewrite the "what NOT to duplicate / GSD verifier already checks" section** — no GSD verifier exists. SUMMARY.md → `STATE.md`/Completion Block; CONTEXT.md → `PLAN.md`. **Add the Test Guardrails protocol** (SPEC §9): test-matrix enforcement as a hard gate against the PR diff, TDD-coverage audit, Playwright E2E for UI. qa leans on the `webapp-testing`/Playwright capability. |
| 7 | `rules/code-review.md` | CONTEXT.md → `PLAN.md`; SUMMARY.md → `STATE.md`; `tdd_exempt_plan_types` path → `.harness/harness.json`. The self-read pattern here is already correct. |
| 8 | `rules/SKILL.md` | Rewrite the loading table: gsd-executor → **the 4 eng devs**; gsd-planner → **pm**; gsd-debugger → eng devs in debug mode; gsd-verifier → **qa**. Add `documentor`, `visual-designer`, **`dev-ops`** (tdd-enforcement with the config/scaffolding exemption), and the 3 leads. Reframe "injected via agent_skills" → "each persona loads its rule via `## Skills`." | <!-- ok-stale -->
| 9 | `skills/harness/SKILL.md` (router) | **Biggest edit.** Invert the selective-loading rule (currently *"Do NOT read subdirectory rule files… injected via agent_skills"*). Drop config.json/`agent_skills`. Point at `.harness/`. Rewrite the lifecycle table (GSD owners → personas; drop the "Injected Skills" column → add a stage→persona→gate mapping). Add the team-runner reference. | <!-- ok-stale -->
| 10 | `harness.json` → `.harness/harness.json` | Remap `role_triggers` (new-project / discuss-phase / pre-ship → harness stages). **Delete `agent_skills_reference`.** Keep `gates`. **Add `test_matrix` + `test_kinds`** (generalizes `tdd_exempt_plan_types` — exempt types map to `[]`). Add `log_retention_days` (default 30). |
| 11 | Agents — the full org | *Keep + rewrite 3 existing:* `code-reviewer`, `security-reviewer`, `qa` (now a **doer**). Drop `/gsd-*` trigger vocabulary, repoint inputs to `.harness/`, add the three-part `VERDICT:`/`DIGEST:`/`artifact:` return. **Delete** `harness-ceo-reviewer` and `harness-eng-reviewer` (architecture review moves into `eng-lead`). **Add 12:** 3 leads (`product-lead`, `eng-lead`, `validator-lead`), 5 eng specialists (`frontend-dev`, `backend-dev`, `ai-dev`, `data-engineer`, `dev-ops`), `pm`, `visual-designer`, `documentor`, `ui-reviewer`. **Total: 15.** |
| 12 | `skills/harness/personas/` | **Delete** the stub dir — the roster lives in `.claude/agents/`. |
| 13 | `CLAUDE.md` | Rewrite "GSD Workflow Enforcement" (route via `/harness`, not `/gsd:*`). Update the `<!-- GSD:harness-* -->` block to describe `.harness/` + teams. Flag the stale STACK.md block for rewrite. GSD marker comments become inert — harmless, drop optionally. |
| 14 | `.claude/commands/harness-deploy.md` | **DONE** (DEC-113). Scoped to distribution only — it must never write project state. See the detail block below. |
| 15 | `.gitignore` | **NET-NEW FILE.** See the detail block below. |
| 16 | `.harness/README.md` | **REWRITE, not create** — it already exists and contradicts this design. See the detail block below. **Owner: `documentor`.** |
| 17 | `.harness/team-config.yaml` | **NET-NEW.** The team manifest (SPEC §3.1): orchestrator, paths, `shared_context`, and the 3 teams with leads, members and `consult-when`. Read by the orchestrator at every `/harness` entry and by each lead when delegating. **This is what makes the org data rather than prose.** Ships alongside **`bin/check-domain.sh`** (net-new): generic and stateless — takes an agent name + a path, reads that agent's `domain` from the project's manifest, exits non-zero if out of scope. No project-specific globs; identical in every project. |
| 18 | `/harness-init` + `templates/` | **DONE** (DEC-112). The onboarding interview (absorbs the deleted `bootstrap` team): project type + frameworks + requirements; writes `harness.json`, `team-config.yaml`, and a draft `BRIEF.md` for approval; optionally chains a design pass. Delegates mechanical detection to `dev-ops` for `domain` globs and `test_kinds`. Supports `--upgrade` to merge newer template entries while preserving project values, driven by `schema_version`. **This is what makes deploy safe to be dumb.** |
| 19 | `.claude/skills/harness-handoff/SKILL.md` | **NET-NEW FILE** — referenced everywhere, scheduled nowhere. The universal artifact-output discipline (BLUF, pointers-not-payloads, open-questions, bounded length) plus the autonomy-by-reversibility rule, read by all 16 agents. Create it in MVP step 1 alongside the first persona. A **flat** skill, not `rules/handoff.md` (DEC-100). | <!-- ok-stale -->

**Also net-new, and reshaped:** all seven rules become **skill directories**
(**flat**: `.claude/skills/harness-<name>/SKILL.md`, per DEC-100) referenced as `harness-<name>` in each agent's `skills:` frontmatter
(SPEC §7, DEC-63). Three do not exist at all yet — `handoff`, `expertise`, `zero-micro-management` —
and the four that do exist must be converted from bare `.md` files into skills. `rules/mental-model.md`
is **renamed to `expertise`** (DEC-80).

**Net-new scripts** (`bin/`): `check-domain.sh` (domain enforcement, stdin JSON + `exit 2`) and
`inject-expertise.sh` (the `SubagentStart` hook).

**Net-new artifacts:** `.harness/expertise/<agent>.md` per agent with stable entry IDs (SPEC §5.2),
`.harness/notes/uat-<FEAT>.md`, `.harness/notes/prototypes/<FEAT>/`.

### Detail: #14 — `harness-deploy.md`

- Push skills, agents and **templates**. **Drop every merge-into-project-config behaviour** —
  project scaffolding moves to `/harness-init`.
- Replace the `.planning/config.json` GSD-project check with a `.harness/` check.
- **Drop the `manifest.json` / `agent_skills` machinery** entirely.
- Registry `~/.gsd/harness-registry.json` → `~/.harness/registry.json`. **Migrate the existing
  registry file** — do not orphan it. Make the migration **idempotent**: handle both files present,
  and a project listed only in the old registry.
- Copy skills + **every agent on disk** (glob `harness-*.md` — 16 since DEC-128, previously 15 until
  `harness-orchestrator.md` lands with task 14) + propagate `teams/`.
- ⚠️ **`cp -r .claude/skills/harness/.` is not enough, and this is easy to miss.** It copies the router,
  `bin/` and `templates/`, but **none of the flat skill dirs** — the seven rule skills *and*
  `harness-init` itself all live at `.claude/skills/harness-*/`, siblings of `harness/`, because a
  project skill is exactly one level down (DEC-100). Deploy must glob `.claude/skills/harness*/`. Without
  it a project gets templates it has no `/harness-init` to instantiate, and agents whose `skills:`
  lists resolve to nothing — silently, since a missing skill is not an error.
- **Add a PRUNE/RECONCILE step.** Deploy is currently copy-only, so deleted agents live forever.
  Compute the set of `harness-*.md` in the repo and delete global/enrolled-project files not in it
  (**dry-run listing first**). Without this, `harness-ceo-reviewer` and `harness-eng-reviewer` remain
  spawnable everywhere, pointing at a `.planning/` root that no longer exists.
- **Rewrite the deploy verification checklist** — it still asserts `manifest.json` / `agent_skills`
  presence.
- Define **team resolution precedence**: project-local `teams/` overrides global.
- **Enroll = deploy + `/harness-init`.** The old flow required `/gsd-new-project` first; that
  dependency is gone.
- ~~A post-cutover push should **strip the now-inert `agent_skills` block** from already-enrolled
  projects' `config.json`.~~ **Corrected (DEC-113): deploy REPORTS this, it does not fix it.** Editing
  a project's `config.json` is writing project state, which is the one thing the deploy/init split
  exists to forbid — and an item in this same list two lines up says exactly that. Same shape as the
  BRIEF-approval contradiction (DEC-112): two requirements in one document, incompatible. The dry run
  now names any project whose `agent_skills` points at paths the push removes, and stops there.

### Detail: #15 — `.gitignore`

The repo has **none**, yet the commit policy depends on ignoring `.harness/features/*/runs/**`.
Without it, run dirs dirty the working tree — and the git-failure-mode rule halts a team with
`BLOCKED` on a dirty tree, so **the harness's own artifacts would deadlock the next run.** Add the
rule here and to `harness-deploy` enroll (`templates/gitignore.snippet`). Reconcile the dirty-tree
halt with a **whitelist**: harness-owned paths and in-progress staged work do not count as dirty.

### Detail: #16 — `.harness/README.md`

It documents the pre-restructure org (`builder` / `tester` / `planner` / `scout` / `coordinator`),
omits `BLOCKED` from the VERDICT enum, lacks `DESIGN.md`, and describes qa as advisory. Critically,
**its schema templates omit the two hardest-gated fields**: PLAN tasks lack `change_type`, and the
BRIEF template has no `## Approval`. **A builder will copy these.**

---

## Self-hosting migration

Because removal scope is full self-hosting (DEC-02), this repo's GSD dev state is migrated, not just
left behind.

**Content migration:**

| From | To |
|---|---|
| `.planning/PROJECT.md` | `.harness/BRIEF.md` |
| `.planning/ROADMAP.md` + active phase `PLAN.md`s | `.harness/PLAN.md` (`## Decisions` + `## Tasks`) |
| `.planning/STATE.md` | `.harness/features/<FEAT>/STATE.md` — per-feature since DEC-120; there is no project-level `STATE.md` |
| `.planning/phases/**`, research | preserved as **history** — archive under `.harness/notes/history/`, or leave in git history and stop writing to it |

**In-flight work — the main self-hosting risk.** The repo is mid-Phase-04
(real-project-validation, ~71%) in GSD terms. That *framing* dissolves — validation now happens by
the harness building itself. **But Phase-04's open items must be explicitly mapped, not dropped:**
its remaining plans, pending todos (e.g. the architectural-scoping-gap item), and recorded blockers
in `.planning/STATE.md` are each triaged into a new `.harness/PLAN.md` task **or consciously retired
with a note.** Silently losing them is the failure mode to guard against.

**Dev workflow flips:** development stops going through `/gsd:*` commands and goes through
`/harness` + teams. `CLAUDE.md`'s "GSD Workflow Enforcement" section is replaced accordingly
(migration item #13).

**Sequencing:** the harness can only self-host *after* the MVP slice exists (state model + bootstrap
+ first specialist + one team). So this migration lands at the **END** of the build — bootstrap the
new system with GSD still available, then cut over and retire `.planning/`.

---

## Hard constraints and risks

- **Runner-is-a-skill rests on a verified fact:** `/harness-deploy` distributes skills but **not**
  commands, so the runner must be a skill to propagate. State passes by file path (context-budget
  discipline), and sub-teams flatten rather than nest.
- **⚠️ Nested spawning is a HARD PREREQUISITE, not an assumption.** Evidence is mixed: some agent
  types list `Tools: *` (likely including the spawn tool), but the Workflow docs note "subagents
  can't spawn subagents in some configs" and "nesting is one level only." Everything downstream of
  SPEC §10.2 depends on the Step 0b result.
- **The runner is an LLM, not an engine** → reliability depends on a crisp checklist skill + the
  mandatory `VERDICT:` token. Mitigations: small DAGs, persist `state.yaml`, re-read STATE at each
  loop top (recovers after a context reset).
- **Self-injection depends on obedience** → hard-gate wording + the `<files_to_read>` backup. Same
  trust model TDD already uses.
- **Concurrency cap (~10)** → keep fan-out ready-sets small.
- **`.harness/` vs `.planning/` is a clean break** — intentional, not backward-compatible.
- **Commands don't distribute** → invocation via skill; a `/team` shortcut is optional.
- **Domain enforcement is unproven** (Step 0a) and is the sole guarantee behind the parallel-safety
  claim and scoped lead `Write`.

---

## Verification

- **Self-injection:** spawn `harness-backend-dev` on a trivial task; confirm it reads
  `tdd-enforcement.md` (writes a failing test first) **without any config field present.**
- **Team end-to-end / parallel fan-in:** exercise a v1 team — the `review` team's parallel reviewer panel
  → **`validator-lead` assessment** fan-in. (Not `understand-codebase`, which is deferred.) Confirm
  reviewers run concurrently, the lead merges them into one actionable set, and outputs land in the
  run dir.
- **Malformed-return handling:** force a persona to omit its `VERDICT` line; confirm the host
  re-prompts **once**, then records `BLOCKED (contract violation)` rather than guessing.
- **Promotion ordering:** confirm a consumer step never reads a stale persistent file — pm's
  `PLAN.md` change (including `change_type`) is visible to the qa gate.
- **Gating loop-back:** run `ship-feature` on a task with a deliberate spec violation; confirm
  `code-reviewer` returns `VERDICT: FAIL`, the host loops back to the dev that produced the failing
  `files_touched` with the report injected, and escalates after `max_cycles`.
- **GSD-free:** `grep -ri "gsd\|agent_skills\|get-shit-done" .claude/ .harness/` returns only
  intentional history/notes; a fresh project with only `.harness/` (no GSD installed) can run a team.

---

## Critical files

| Path | Status |
|---|---|
| `.claude/skills/harness/SKILL.md` | rewrite — router → coordinator playbook + lifecycle/team routing |
| `.claude/skills/harness-team/SKILL.md` | **new** — generic runner, algorithm inline. **FLAT**, not `harness/team/`: nested skill dirs are undiscoverable (DEC-100). Team *data* stays at `harness/teams/*.yaml` — a data dir, not a skill |
| `.claude/skills/harness/teams/*.yaml` | **new** — team configs |
| `.claude/agents/harness-orchestrator.md` | **done** (DEC-128) — the sixteenth agent: spawned layer-1, one per in-flight feature, preloads the `harness` playbook |
| `.claude/agents/harness-{product,eng,validator}-lead.md` | **new** — domain leads |
| `.claude/agents/harness-{frontend,backend,ai}-dev.md`, `harness-data-engineer.md`, `harness-dev-ops.md` | **new** — 5 eng specialists |
| `.claude/agents/harness-{pm,qa,documentor,visual-designer,ui-reviewer}.md` | **new** — product/validator agents |
| `.harness/team-config.yaml` | **new** — team manifest (membership + `consult-when` routing + `domain` write scope) |
| `.claude/skills/harness/bin/check-domain.sh` | **new** — domain-enforcement hook script (the one deliberate exception to files-only) |
| `.claude/skills/harness/templates/*` | **new** — distributed schema templates (team-config, harness.json, BRIEF/PLAN/STATE/DESIGN, gitignore) |
| `.claude/skills/harness-init/SKILL.md` | **done** — `/harness-init` project scaffolder. **FLAT**, not `harness/init/`: a project skill is exactly one level under `.claude/skills/` and a nested dir is undiscoverable (DEC-100) |
| `.claude/skills/harness/bin/merge-settings.py`, `merge-gitignore.sh`, `upgrade-config.py` | **done** — deterministic, idempotent merges. Prose cannot be trusted to preserve a project's own hooks |
| `.claude/skills/harness-handoff/SKILL.md` | **new** — universal artifact discipline (all 16 agents) |
| `.claude/skills/harness-<name>/SKILL.md` × 7 | **restructured, FLAT** (DEC-100) — rules become skills for `skills:` preload; `handoff`, `expertise`, `zero-micro-management` are net-new |
| `.claude/skills/harness/bin/inject-expertise.sh` | **new** — `SubagentStart` hook that injects an agent's Expertise |
| `settings.json` — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` + `SubagentStart` + `PreToolUse` + `SubagentStop` | **new** — **all four required**, none on by default, and each degrades silently if absent (§ Step 0a; DEC-111, DEC-122) |
| `.claude/agents/harness-{code,security}-reviewer.md` | rewrite — de-GSD'd + three-part return (`ceo-reviewer` and `eng-reviewer` are **deleted**) |
| `.claude/skills/harness/rules/*.md` | rewrite — retarget injection prose to personas |
| `.claude/commands/harness-deploy.md` | rewrite — strip agent_skills/manifest, repoint to `.harness/`, add teams + prune step |
| `.gitignore` | **new** |
| `.planning/config.json` + `harness.json` | delete `agent_skills`; move config to `.harness/` |

---

## Open items

### The GAP series

The source design used a numbered GAP series that is only **partly** recoverable from the document.

**Four are named and recorded as CLOSED** by the features/runs execution state model (SPEC §11):

| Gap | Was | Closed by |
|---|---|---|
| GAP 3 | dead or malformed host | resume via `resume_from` + `git log` attribution, never re-prompt (DEC-51) |
| GAP 4 | unbounded retry budget | `cycles_used`/`max_total_cycles` in `feature.yaml`, feature-level (DEC-49) |
| GAP 7 | moving diff target | `review_sha` pinned at review dispatch (DEC-50) |
| GAP 8 | parallel mutators | `mutates_repo` read during ready-set computation, forcibly serializing such steps |

**GAP 1, 2, 5 and 6 are not named anywhere in the source** — only the four above appear.

### The five remaining gaps — UNRECOVERED

The source states that "the five remaining gaps (§ tracked separately)" are to be resolved against
`SPEC.md`, but **does not enumerate them anywhere in the document.** They were tracked outside it.

**This is a real unknown, recorded rather than invented.** Before the design is considered settled,
those five gaps need to be recovered from wherever they were tracked (adversarial-pass output, a
separate note, or session history) and resolved against SPEC.md. Do not substitute a guessed list.

### Post-ship follow-up

Update the kaya-ai memory `pr-cycle-review-team.md` so it matches the shipped design: CEO out of the
review panel; panel membership from team config rather than auto-selected (DEC-57). Deferred until
the harness ships — decided, not forgotten.
