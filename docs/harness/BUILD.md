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
| `SubagentStart` fires for nested spawns? | **YES** — logged 1 top-level + 3 nested. Expertise reaches workers |
| Nested skill dirs discoverable? | **NO** — skills must be flat. The four artifacts were invisible until fixed |
| Parallel fan-out from inside a lead? | **YES** — 3 concurrent layer-2 spawns |
| `PreToolUse` `exit 2` blocks a subagent write? | **YES from `settings.json`** — verified live end-to-end. **NO from agent frontmatter** — 3 forms, 0 executions (DEC-110) |

### 0a — `settings.json` prerequisites (setup, not a spike)

Two platform features the design depends on must be set explicitly. **A project missing either
degrades silently rather than erroring** — and for the depth setting, what "missing" does depends on
the CLI version (below).

```json
{
  "env": {
    "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2"
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
    ]
  }
}
```

⚠️ **All THREE entries are required, and `PreToolUse` is the one most recently added.** It carries no
matcher on agent name deliberately — one global registration serves all 15, and the script dispatches on
`agent_type` from the payload (DEC-110). If it is omitted, agents get Expertise but **domain enforcement
is silently absent**.

| Setting | Enables | If missing |
|---|---|---|
| `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "2"` | Pins nesting to exactly orchestrator → lead → worker. Depth 2 means the worker layer **cannot** delegate further, enforcing "workers are always leaves" mechanically | **Depends on CLI version, and the current default is the risk.** At the current default of **3**, workers *can* delegate — the opposite of the intended guarantee. On 2.1.217–218 the default was 1, so leads could not spawn at all |
| `SubagentStart` hook | Expertise injection (SPEC §5.1) | Every agent starts with no Expertise and no error is raised |
| **`PreToolUse` hook** | **Domain enforcement** (SPEC §4.2) — must be here, not in agent frontmatter, which does not fire (DEC-110) | Every agent can write anywhere. **Fail-open, silent** — the exact failure class this design tries to avoid |

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
explicitly to `2` in every project. Setting it explicitly is correct in *all* bands — it is the only
value that both guarantees leads can spawn and guarantees workers cannot.

**Belt-and-suspenders, and the actually-reliable mechanism:** "workers are always leaves" is enforced
independently by **omitting `Agent` from every worker's `tools:` list**. Do that regardless of the
setting; the depth cap is defence in depth, not the primary control.

**`/harness-init` must write both settings, and the state-consistency check must verify them** — a
silent degradation to flat, to memoryless agents, or to delegating workers is exactly the failure class
this design tries to avoid.

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
> **agent identity comes from `agent_type` in the hook payload** — one global registration serves all 15.
> The `hooks:` blocks have been stripped from all 15 agent files as dead weight.

Two properties this arrangement must preserve, both verified:

- **The orchestrator is never governed.** No `agent_type` in the payload means the main session, which
  legitimately writes everywhere; the hook exits 0 immediately. Without this the harness could not
  maintain its own state.
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

**And the depth cap is enforced by tool withholding, not by an error** (DEC-102). At layer 2 Claude Code
strips `Agent` from the loaded list *and* the deferred pool, so a worker cannot delegate even if granted
`Agent` in frontmatter. "Workers are always leaves" is a platform guarantee, and a worker that tries finds
no tool and does the work itself rather than failing.

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
| 8 | Expertise governance holes | pending — provenance, decay, curation for all 15, global tier. **Add: 14 of 15 `expertise/<agent>.md` files do not exist**, so `inject-expertise.sh` injects nothing on almost every spawn and says nothing about it (surfaced by the DEC-112 fixture run). Init creating the dir empty is per spec; what is missing is anything that ever populates it |
| 9 | The 15 agent definitions | **done** (DEC-106, DEC-107) |
| 10 | Crew runner + four v1 crews | **in progress** — runner done incl. gating and parallel dispatch, all proven from spawn records (DEC-116, DEC-117). **Scope corrected (DEC-118): only 2 of the 4 are crews** — `plan-feature` and `ship-feature` are orchestrator playbooks sequencing per-squad runs, since a crew is single-squad by construction. Built: `review-team`. Remaining: `debug` (crew), the two playbooks, and the question round-trip |
| 11 | Batch human touchpoints to two | pending |
| 12 | `/harness-init` + distributed templates | **done** — flat skill at `.claude/skills/harness-init/`, 8 templates, 3 merge scripts (DEC-112) |
| 13 | Rewrite `harness-deploy` (distribution only, **+ prune**) | **done** (DEC-113) — `bin/deploy.sh`, dry-run by default, reconciles rather than copies. The live risk was confirmed real before the fix: 3 deleted agents spawnable everywhere, the global skill tree still the April layout |
| 14 | Router + `harness.json` + CLAUDE.md — **and size** | pending — CLAUDE.md is ~164k tok/feature, 3× the rule cost (DEC-105) |
| 15 | Recover the five lost design GAPs | pending |
| 16 | GSD-removal migration (19 items) | pending — items #1–2 delete the running mechanism; sequence after rule delivery is proven |
| 17 | Take the full workflow through its paces in kaya-ai | pending — **blocked only on 10** now (3, 12, 13 done). Measure the DEC-114 open question: is the orchestrator really ~80% of spend? |
| 18 | Fix the propagation defect mechanically | **done** (DEC-104) |
| 19 | **Remove GSD globally** — the machine, not this repo | pending — **GATED on 17.** DEC-02's removal scope is *this repo* self-hosting: all 19 migration items are project-local, **zero** touch a global path. Unowned until now: 33 `gsd-*` agents, `~/.claude/get-shit-done/` (282 files), 8 global hooks, the `gsd-statusline.js` statusline, 14 GSD lines in the global CLAUDE.md, `~/.gsd/`. Do not start before the harness is proven end-to-end — the blast radius is every project, not one (DEC-115) |

## Task 12 — `/harness-init`: complete spec — **BUILT** (DEC-112)

**Self-contained: everything needed to build this without prior conversation.** The spec below is what
was built; the Done-when block at the end records how each criterion was verified.

### What it is

The onboarding interview, run **inside a target project**. It absorbs the deleted `bootstrap` crew
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

**1. `.claude/settings.json` — ALL THREE entries.** Omitting any degrades **silently**.

```json
{
  "env": { "CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "2" },
  "hooks": {
    "SubagentStart": [ { "matcher": "harness-.*",
      "hooks": [{ "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/inject-expertise.sh" }] } ],
    "PreToolUse": [ { "matcher": "Write|Edit",
      "hooks": [{ "type": "command",
        "command": "${CLAUDE_PROJECT_DIR}/.claude/skills/harness/bin/check-domain.sh" }] } ]
  }
}
```

- `PreToolUse` carries **no agent-name matcher** deliberately: one registration serves all 15 and the
  script dispatches on `agent_type` from the payload (DEC-110/111).
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
spawnable until it restarts. Say so at the end, or a user who runs a crew immediately gets "Agent type
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

- ✅ **`bin/check-state.sh` passes in a freshly-initialised project** (all three settings entries, INV-9).
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
2. Whether a `settings.json` `SubagentStart` hook fires for **nested** spawns (lead→worker). If it does
   not, the 9 workers silently lose Expertise while leads keep theirs.
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

- **SC-4 is measured** — base rate **0.44 defects/feature** from `kaya-ai` history, with the four
  artifacts addressing ~79% of them (`PILOT-SC4-BASELINE.md`, DEC-96). Still the best evidence for what
  the gates are worth.
- **SC-3 is partially met** — all four artifacts fired correctly in a throwaway run, and **review caught
  a fail-open defect that a green test suite missed** (DEC-97), reproducing `kaya-ai` #92. That was the
  inferred claim in DEC-96; it is now observed.
- **One real bug found and fixed** in `harness-qa-gate`'s state logic (DEC-98).

### Retained from the deferred list — now in scope

1. ~~**Cost instrumentation — do this first.**~~ **DONE (DEC-114).** Tokens and spawn count logged per
   run in `state.yaml`; per-crew budgets alongside `max_cycles`; a cost line in the CEO briefing.
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
   per-crew budgets beside `max_cycles`, a cost line in the CEO briefing, cheaper model tiers as the
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
3. **One linear crew.** A minimal runner + a single linear crew, no gating or loop-back yet. Prove
   file-path state passing, lead→member dispatch, and the `lead:` host field. **DONE** (DEC-116).

   > **Corrected (DEC-118).** This step originally specified `crew/SKILL.md` and a
   > `pm → backend-dev` crew under `lead: eng-lead`. Both were unbuildable. The runner path is
   > nested and undiscoverable (DEC-100) — it is `harness-crew/SKILL.md`. And `pm` is Product-squad
   > while `eng-lead` leads Engineering: a lead only dispatches its own members, and the depth-2 cap
   > means it cannot spawn a peer lead to reach across either. Step 3 predates the three-squad org
   > that step 2 of this same list creates. The three things it asks to prove are unchanged and were
   > proven; only the vehicle differs.

## Elaborations

Beyond "build personas + assemble them." Prune freely.

4. **Rewrite the existing reviewers** — drop GSD, repoint to `.harness/`, add the three-part return
   and a `skills:` list. Add `ui-reviewer` (modes A/B).
5. **Full crew semantics + the v1 crew catalog** — the `VERDICT:`/`DIGEST:` contract,
   `on_fail`/`loop_back`/`max_cycles` gating, parallelism, `validator-lead` panel assessment. Build
   the 4 v1 core crews (SPEC §13): `plan-feature`, `ship-feature`, `debug`, `review-team`. Flat and
   standalone — no sub-crew composition. Defer `understand-codebase` and `docs-refresh`.
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
| 9 | `skills/harness/SKILL.md` (router) | **Biggest edit.** Invert the selective-loading rule (currently *"Do NOT read subdirectory rule files… injected via agent_skills"*). Drop config.json/`agent_skills`. Point at `.harness/`. Rewrite the lifecycle table (GSD owners → personas; drop the "Injected Skills" column → add a stage→persona→gate mapping). Add the crew-runner reference. | <!-- ok-stale -->
| 10 | `harness.json` → `.harness/harness.json` | Remap `role_triggers` (new-project / discuss-phase / pre-ship → harness stages). **Delete `agent_skills_reference`.** Keep `gates`. **Add `test_matrix` + `test_kinds`** (generalizes `tdd_exempt_plan_types` — exempt types map to `[]`). Add `log_retention_days` (default 30). |
| 11 | Agents — the full org | *Keep + rewrite 3 existing:* `code-reviewer`, `security-reviewer`, `qa` (now a **doer**). Drop `/gsd-*` trigger vocabulary, repoint inputs to `.harness/`, add the three-part `VERDICT:`/`DIGEST:`/`artifact:` return. **Delete** `harness-ceo-reviewer` and `harness-eng-reviewer` (architecture review moves into `eng-lead`). **Add 12:** 3 leads (`product-lead`, `eng-lead`, `validator-lead`), 5 eng specialists (`frontend-dev`, `backend-dev`, `ai-dev`, `data-engineer`, `dev-ops`), `pm`, `visual-designer`, `documentor`, `ui-reviewer`. **Total: 15.** |
| 12 | `skills/harness/personas/` | **Delete** the stub dir — the roster lives in `.claude/agents/`. |
| 13 | `CLAUDE.md` | Rewrite "GSD Workflow Enforcement" (route via `/harness`, not `/gsd:*`). Update the `<!-- GSD:harness-* -->` block to describe `.harness/` + crews. Flag the stale STACK.md block for rewrite. GSD marker comments become inert — harmless, drop optionally. |
| 14 | `.claude/commands/harness-deploy.md` | **DONE** (DEC-113). Scoped to distribution only — it must never write project state. See the detail block below. |
| 15 | `.gitignore` | **NET-NEW FILE.** See the detail block below. |
| 16 | `.harness/README.md` | **REWRITE, not create** — it already exists and contradicts this design. See the detail block below. **Owner: `documentor`.** |
| 17 | `.harness/team-config.yaml` | **NET-NEW.** The team manifest (SPEC §3.1): orchestrator, paths, `shared_context`, and the 3 teams with leads, members and `consult-when`. Read by the orchestrator at every `/harness` entry and by each lead when delegating. **This is what makes the org data rather than prose.** Ships alongside **`bin/check-domain.sh`** (net-new): generic and stateless — takes an agent name + a path, reads that agent's `domain` from the project's manifest, exits non-zero if out of scope. No project-specific globs; identical in every project. |
| 18 | `/harness-init` + `templates/` | **DONE** (DEC-112). The onboarding interview (absorbs the deleted `bootstrap` crew): project type + frameworks + requirements; writes `harness.json`, `team-config.yaml`, and a draft `BRIEF.md` for approval; optionally chains a design pass. Delegates mechanical detection to `dev-ops` for `domain` globs and `test_kinds`. Supports `--upgrade` to merge newer template entries while preserving project values, driven by `schema_version`. **This is what makes deploy safe to be dumb.** |
| 19 | `rules/handoff.md` | **NET-NEW FILE** — referenced everywhere, scheduled nowhere. The universal artifact-output discipline (BLUF, pointers-not-payloads, open-questions, bounded length) plus the autonomy-by-reversibility rule, read by all 15 agents. Create it in MVP step 1 alongside the first persona. |

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
- Copy skills + **all 15 agents** (glob `harness-*.md`) + propagate `crews/`.
- ⚠️ **`cp -r .claude/skills/harness/.` is not enough, and this is easy to miss.** It copies the router,
  `bin/` and `templates/`, but **none of the flat skill dirs** — the seven rule skills *and*
  `harness-init` itself all live at `.claude/skills/harness-*/`, siblings of `harness/`, because a
  project skill is exactly one level down (DEC-100). Deploy must glob `.claude/skills/harness*/`. Without
  it a project gets templates it has no `/harness-init` to instantiate, and 15 agents whose `skills:`
  lists resolve to nothing — silently, since a missing skill is not an error.
- **Add a PRUNE/RECONCILE step.** Deploy is currently copy-only, so deleted agents live forever.
  Compute the set of `harness-*.md` in the repo and delete global/enrolled-project files not in it
  (**dry-run listing first**). Without this, `harness-ceo-reviewer` and `harness-eng-reviewer` remain
  spawnable everywhere, pointing at a `.planning/` root that no longer exists.
- **Rewrite the deploy verification checklist** — it still asserts `manifest.json` / `agent_skills`
  presence.
- Define **crew resolution precedence**: project-local `crews/` overrides global.
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
Without it, run dirs dirty the working tree — and the git-failure-mode rule halts a crew with
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
| `.planning/STATE.md` | `.harness/STATE.md` |
| `.planning/phases/**`, research | preserved as **history** — archive under `.harness/notes/history/`, or leave in git history and stop writing to it |

**In-flight work — the main self-hosting risk.** The repo is mid-Phase-04
(real-project-validation, ~71%) in GSD terms. That *framing* dissolves — validation now happens by
the harness building itself. **But Phase-04's open items must be explicitly mapped, not dropped:**
its remaining plans, pending todos (e.g. the architectural-scoping-gap item), and recorded blockers
in `.planning/STATE.md` are each triaged into a new `.harness/PLAN.md` task **or consciously retired
with a note.** Silently losing them is the failure mode to guard against.

**Dev workflow flips:** development stops going through `/gsd:*` commands and goes through
`/harness` + crews. `CLAUDE.md`'s "GSD Workflow Enforcement" section is replaced accordingly
(migration item #13).

**Sequencing:** the harness can only self-host *after* the MVP slice exists (state model + bootstrap
+ first specialist + one crew). So this migration lands at the **END** of the build — bootstrap the
new system with GSD still available, then cut over and retire `.planning/`.

---

## Hard constraints and risks

- **Runner-is-a-skill rests on a verified fact:** `/harness-deploy` distributes skills but **not**
  commands, so the runner must be a skill to propagate. State passes by file path (context-budget
  discipline), and sub-crews flatten rather than nest.
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
- **Commands don't distribute** → invocation via skill; a `/crew` shortcut is optional.
- **Domain enforcement is unproven** (Step 0a) and is the sole guarantee behind the parallel-safety
  claim and scoped lead `Write`.

---

## Verification

- **Self-injection:** spawn `harness-backend-dev` on a trivial task; confirm it reads
  `tdd-enforcement.md` (writes a failing test first) **without any config field present.**
- **Crew end-to-end / parallel fan-in:** exercise a v1 crew — `review-team`'s parallel reviewer panel
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
  intentional history/notes; a fresh project with only `.harness/` (no GSD installed) can run a crew.

---

## Critical files

| Path | Status |
|---|---|
| `.claude/skills/harness/SKILL.md` | rewrite — router → coordinator playbook + lifecycle/crew routing |
| `.claude/skills/harness-crew/SKILL.md` | **new** — generic runner, algorithm inline. **FLAT**, not `harness/crew/`: nested skill dirs are undiscoverable (DEC-100). Crew *data* stays at `harness/crews/*.yaml` — a data dir, not a skill |
| `.claude/skills/harness/crews/*.yaml` | **new** — crew configs |
| `.claude/agents/harness-{product,eng,validator}-lead.md` | **new** — domain leads |
| `.claude/agents/harness-{frontend,backend,ai}-dev.md`, `harness-data-engineer.md`, `harness-dev-ops.md` | **new** — 5 eng specialists |
| `.claude/agents/harness-{pm,qa,documentor,visual-designer,ui-reviewer}.md` | **new** — product/validator agents |
| `.harness/team-config.yaml` | **new** — team manifest (membership + `consult-when` routing + `domain` write scope) |
| `.claude/skills/harness/bin/check-domain.sh` | **new** — domain-enforcement hook script (the one deliberate exception to files-only) |
| `.claude/skills/harness/templates/*` | **new** — distributed schema templates (team-config, harness.json, BRIEF/PLAN/STATE/DESIGN, gitignore) |
| `.claude/skills/harness-init/SKILL.md` | **done** — `/harness-init` project scaffolder. **FLAT**, not `harness/init/`: a project skill is exactly one level under `.claude/skills/` and a nested dir is undiscoverable (DEC-100) |
| `.claude/skills/harness/bin/merge-settings.py`, `merge-gitignore.sh`, `upgrade-config.py` | **done** — deterministic, idempotent merges. Prose cannot be trusted to preserve a project's own hooks |
| `.claude/skills/harness-handoff/SKILL.md` | **new** — universal artifact discipline (all 15 agents) |
| `.claude/skills/harness-<name>/SKILL.md` × 7 | **restructured, FLAT** (DEC-100) — rules become skills for `skills:` preload; `handoff`, `expertise`, `zero-micro-management` are net-new |
| `.claude/skills/harness/bin/inject-expertise.sh` | **new** — `SubagentStart` hook that injects an agent's Expertise |
| `settings.json` — `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` + `SubagentStart` | **new** — both required, neither on by default (§ Step 0a) |
| `.claude/agents/harness-{code,security}-reviewer.md` | rewrite — de-GSD'd + three-part return (`ceo-reviewer` and `eng-reviewer` are **deleted**) |
| `.claude/skills/harness/rules/*.md` | rewrite — retarget injection prose to personas |
| `.claude/commands/harness-deploy.md` | rewrite — strip agent_skills/manifest, repoint to `.harness/`, add crews + prune step |
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
review panel; panel membership from crew config rather than auto-selected (DEC-57). Deferred until
the harness ships — decided, not forgotten.
