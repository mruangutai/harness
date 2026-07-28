# Harness — Decision Log

> **APPEND-ONLY. Never rewrite or renumber an existing entry.** If a decision changes, add a new
> entry that references and supersedes the old one. This is the whole point of the file: a settled
> question stays settled, and reversals are visible as reversals rather than as edits.
>
> **Numbering:** entries are `DEC-NN`. Note that `D-NN` means something different and is **not** used
> here — it is the ID for `PLAN.md ## Decisions` entries, a runtime artifact of the harness itself
> (SPEC §11.2).
>
> **What belongs here:** why a choice was made, what it was chosen over, what tradeoff was accepted.
> **What does not:** how the system works — that is [SPEC.md](SPEC.md). Rule of thumb: if removing
> the sentence changes what someone would *build*, it belongs in SPEC; if it only changes whether
> they'd *agree*, it belongs here.
>
> Extracted 2026-07-26 from `~/.claude/plans/i-want-to-remove-tingly-dongarra.md`.

---

## DEC-01 — Remove GSD entirely; treat it as a re-founding, not a refactor

**Chose:** remove GSD as the harness's backbone and build native replacements for everything it
provided.
**Over:** continuing to layer the harness on GSD, or a partial decoupling.
**Because:** the pre-existing `PROJECT.md` states the harness "uses GSD's context engine as the
backbone… extend it, not rebuild it." Removing GSD invalidates that premise outright. GSD supplied
four distinct things — orchestration, persistent state (the `.planning/` artifact chain), the
execution engine (`gsd-executor`), and the `agent_skills` injection mechanism that delivered harness
rule files into agents at spawn time. Each needs a native replacement; calling that a refactor would
understate the work and leave the design half-anchored to a removed dependency.
**Tradeoff accepted:** the harness's own assets before this were only 5 read-only reviewer agents
plus rule files. Almost everything else is net-new.

## DEC-02 — Removal scope is FULL SELF-HOSTING

**Chose:** the harness stops dogfooding GSD too. This repo's own `.planning/` dev tracking retires
and migrates onto `.harness/` + crews.
**Over:** removing GSD only from the shipped artifacts while continuing to develop the harness with
`/gsd:*` commands.
**Because:** the harness becomes the first project built with the harness, which is the only honest
validation available.
**Tradeoff accepted:** the self-hosting cutover lands at the *end* of the build, not the start — the
new system must exist before it can host its own development. Chief risk is silently losing
in-flight GSD state (see BUILD.md § Self-Hosting Migration).

## DEC-03 — Backbone = harness-owned state files, not a full orchestrator engine

**Chose:** lightweight harness-owned state files.
**Over:** GSD's `.planning/` chain; a full orchestrator engine.
**Because:** the harness needs persistent state and phase continuity, not a second execution engine.
GSD's 7-file chain is more structure than the design requires; a bespoke engine is more machinery
than files-only delivery permits.
**Tradeoff accepted:** replaced by 4 files + `harness.json` + one directory (SPEC §2), which means
some GSD affordances (wave-based parallel phase execution, `gsd-tools.cjs` metadata) have no
successor.

## DEC-04 — Fresh root `.harness/`, a clean break from `.planning/`

**Chose:** a new state root.
**Over:** reusing or migrating in place under `.planning/`.
**Because:** it cleanly severs GSD and avoids collision if GSD is co-installed in the same repo.
**Tradeoff accepted:** intentionally **not** backward-compatible. Existing `.planning/` content must
be migrated deliberately (BUILD.md).

## DEC-05 — Composition = declarative crew config

**Chose:** crews as YAML data + one generic runner.
**Over:** (a) a command per crew; (b) a free-form dynamic orchestrator that assembles teams at
runtime.
**Because:** declarative config gives the property that matters — **the orchestrator routes; workers
never pick who runs next.** A command-per-crew multiplies files and cannot express DAG shape; a
dynamic orchestrator puts routing inside a model's judgment on every run, which is exactly the
non-determinism the crew config exists to remove.
**Tradeoff accepted:** crews are fixed shapes; anything genuinely novel needs a new YAML file rather
than emergent assembly.

## DEC-06 — Crews live under `.claude/skills/`, and the runner is a skill not a command

**Chose:** runner at `.claude/skills/harness/crew/SKILL.md`; crew configs at
`.claude/skills/harness/crews/*.yaml`.
**Over:** a `/crew` command.
**Because:** **verified fact** — `/harness-deploy` distributes skills to every enrolled project and
agents globally, but does **not** distribute `.claude/commands/`. A command-based runner would not
propagate.
**Tradeoff accepted:** invocation is by skill trigger phrase rather than a slash command. A local
`/crew` shortcut is optional in the harness repo but needs a one-line deploy extension to travel.

## DEC-07 — 15 agents in 3 squads under 3 domain leads; no CEO agent

**Chose:** three squads (product / engineering / validation), each with a domain lead, coordinated by
the orchestrator. **You are the CEO.**
**Over:** a `harness-ceo-reviewer` agent; a single generic `harness-lead`; a flat roster with no
leads.
**Because:** a CEO agent would simulate the one role the human actually occupies — you already define
the goal, approve BRIEF/PLAN and own the merge, so a CEO persona adds a voice with no authority. One
generic lead would have to be parametrized per crew and would own every domain's judgment; three
domain leads let each lead genuinely assess its own squad's work.
**Tradeoff accepted:** 15 agents is a large roster to maintain and reason about.

## DEC-08 — Role merges and deletions

**Chose:** `pm` = research + planning in one context; `qa` = test-writing + coverage-assessment;
`eng-lead` owns architecture review.
**Deleted / merged:** `ceo-reviewer` (you are the CEO) · `eng-reviewer` (→ `eng-lead`) · `tester`
(→ merged into `qa`) · the generic `harness-lead` (→ three domain leads) · `scout` + `planner`
(→ `pm`).
**Because:** research and planning share the same context — splitting them forces a handoff artifact
between two halves of one thought. Test-writing and coverage-assessment likewise: the agent that
writes the tests is the one that knows what is uncovered. Architecture review belongs to the role
that routes the build, not to a separate reviewer with no routing authority.
**Tradeoff accepted:** each merge concentrates more judgment in one agent, and two of them create
self-review (DEC-34).

## DEC-09 — `consult-when` replaces a rigid task `domain:` field

**Chose:** each member declares in the manifest what it is consulted for; the lead matches the
request semantically at delegation time.
**Over:** tagging each PLAN task with a fixed domain enum.
**Because:** three reasons. (1) **No second taxonomy** — `change_type` stays purely a
test-obligation axis (SPEC §9) and never doubles as ownership. (2) **Multi-domain work just works** —
a "UI + API" feature matches both `frontend-dev` and `backend-dev`, so the lead delegates to both
serially instead of being forced to pick one; this is precisely what made a rigid `domain:` field
unworkable. (3) **Agents are self-describing** — adding a specialist is one manifest entry, not
extending an enum in three places.
**Tradeoff accepted:** routing becomes a model judgment rather than a lookup. Mitigated by making
the no-match case a halt rather than a guess (SPEC §3.1).

## DEC-10 — The org is data (`team-config.yaml`), not prose

**Chose:** a per-project team manifest holding teams, leads, members, `consult-when` and `domain`.
**Over:** describing the org in the router `SKILL.md` and agent bodies.
**Because:** without it, "the orchestrator knows a UI change is engineering" is an inference a model
must re-derive from prose on every single request. It also gives the domain-enforcement hook one
canonical place to read `domain` from.
**Tradeoff accepted:** one more file per project to keep in sync, handled by template versioning
(DEC-13).

## DEC-11 — Manifest = policy, frontmatter = capability; nothing declared twice

**Chose:** team membership, lead, `consult-when` and `domain` in the manifest; `name`, `description`,
`tools`, `model`, `color`, `hooks` in agent frontmatter.
**Over:** putting `domain` in the agent body, or duplicating agent metadata into the manifest.
**Because:** `domain` must be readable by `check-domain.sh` from one canonical place, so it cannot
live in the agent body. Conversely, agent `description` and `tools` are frontmatter's job — copying
them into the manifest would create text that drifts. No file `path` in the manifest either, since
Claude Code resolves agents by name.
**Tradeoff accepted:** an agent's full picture requires reading two files.

## DEC-12 — Distribution: templates + `init`, NOT deploy-merge

**Chose:** `/harness-deploy` distributes the tool and **never** touches project state;
`/harness-init` writes every project artifact. Enroll = deploy + init.
**Over:** deploy merging config into each project (the previous behavior).
**Because:** the manifest mixes generic org structure (teams, `consult-when` — identical everywhere)
with project-specific data (`domain` globs — one repo's UI is `src/components/`, another's is
`app/ui/`). If deploy pushed the manifest it would clobber every project's paths. Separating the two
operations makes deploy safe to be dumb.
**Tradeoff accepted:** two commands instead of one; a project needs an explicit init step.

## DEC-13 — Template versioning; upgrades are user-triggered, not a deploy side effect

**Chose:** templates carry `schema_version`; deploy pushes the new template but leaves the project's
manifest alone; the state check notices the gap and tells you to run `/harness-init --upgrade`.
**Over:** deploy silently merging new agents into existing project manifests.
**Because:** merge complexity becomes an explicit, user-triggered action instead of a silent side
effect that could overwrite `domain` values.
**Tradeoff accepted:** projects can sit on a stale org until someone runs the upgrade.

## DEC-14 — `/harness-init` absorbs the `bootstrap` crew, which is deleted

**Chose:** one onboarding interview covering technical detection + product requirements + BRIEF
approval + an optional design pass.
**Over:** a `bootstrap` crew (`pm(greenfield)` + BRIEF approval + design pass) alongside a separate
init.
**Because:** both were interviewing you at project start about overlapping things. Only the main
session can call `AskUserQuestion`, so the interview cannot live in a crew anyway — a subagent
cannot ask you a question.
**Tradeoff accepted:** mechanical detection is delegated to `dev-ops` from inside the interview
rather than being one uniform flow.

## DEC-15 — `ideate` crew deleted

**Chose:** ideation is the orchestrator working directly with you, plus `pm` research.
**Over:** an `ideate` crew.
**Because:** with no `ceo-reviewer`, there is no agent to ideate *with* — you are the CEO, and the
orchestrator already owns the user relationship.
**Tradeoff accepted:** none identified.

## DEC-16 — The roster is NOT pruned per project

**Chose:** all 15 agents present in every project; irrelevant ones self-scope to "not in scope."
**Over:** activating a subset per project based on its type.
**Because:** a uniform manifest means one template, no activation state to track, and no failure mode
where a project silently lacks a reviewer it turned out to need.
**Tradeoff accepted:** one cheap wasted spawn per irrelevant agent. Crew configs may still omit an
obviously-irrelevant reviewer from a specific panel.

## DEC-17 — `shared_context` stays minimal — `handoff.md` only

**Chose:** one entry.
**Over:** the reference config's practice of adding README and CLAUDE.md.
**Because:** every entry is loaded by all 15 agents at every spawn; a heavy list reintroduces exactly
the context bloat the compact-return design exists to prevent.
**Tradeoff accepted:** agents needing project context must read it explicitly per task.

## DEC-18 — Leads have no `Edit` and no `Bash`; `Write` is scoped to their own run dir

**Chose:** limit lead capability rather than rely on instruction.
**Over:** granting leads full doer tools and telling them to delegate; or making leads fully
write-less.
**Because:** an LLM lead under pressure will otherwise just fix the bug itself rather than delegate.
Capability limits stop that where prose would not; `zero-micro-management` is the behavioral layer on
top. Leads need *some* `Write` because each owns its squad's run bookkeeping — writing your own state
file is not "executing"; writing deliverables is.
**Tradeoff accepted:** a lead cannot run `git diff` to assess its squad's work; it reads members'
artifacts and DIGESTs instead. **And lead safety depends on the domain hook actually enforcing
(DEC-19)** — if it does not, the guarantee reduces to prose. Fallback: leads stay fully write-less
and return run state in the DIGEST for the orchestrator to persist, at the cost of putting the
orchestrator in the loop for every step (which pushes toward flat hosting).

## DEC-19 — `check-domain.sh` is the one deliberate exception to files-only delivery

**Chose:** ship one shell script that enforces `domain` globs via a `PreToolUse` hook in each agent's
frontmatter.
**Over:** keeping `## Domain` as prose; using `settings.json` permission rules; relying on `tools:`.
**Because:** single-owner paths are the **entire justification for running agents in parallel**
("disjoint writers, therefore safe to fan out"). Claude Code's `tools:` grant is all-or-nothing — an
agent with `Write` can write anywhere — so prose alone would let two parallel doers clobber each
other with **no error**: one write silently wins, and the lost change surfaces later with nothing
pointing at the cause. Silent corruption is the worst failure class in this design.
`settings.json` rules are global and `tools:` is too coarse; a per-agent, path-scoped hook is the
only mechanism that is both.
**Tradeoff accepted:** a break from files-only delivery — justified because the alternative is
unenforceable prose guarding the parallel-safety claim. It is one shell file, not a build system.
**Unproven:** GSD ships this pattern commented-out only, so it must be verified (BUILD.md § 0a).
Fallback if it fails: strictly serialize mutators, or use worktree isolation to preserve parallelism.

## DEC-20 — Self-injection replaces `agent_skills`

**Chose:** each rule-carrying persona reads its own rule file as Step 0 of its protocol.
**Over:** GSD's `agent_skills` block in `config.json`, read by `gsd-tools.cjs` at spawn.
**Because:** `agent_skills` was the **only** mechanism delivering rules into agents — remove GSD and
nothing reads it, so every rule goes inert. This was the critical coupling to replace. Self-injection
keeps rules single-sourced in `rules/`, needs zero config, and requires no persona→rule map in the
coordinator. It also **generalizes a pattern already working today** in
`harness-code-reviewer.md`.
**Tradeoff accepted:** depends on the agent obeying an instruction — the same trust model TDD already
uses. Mitigated belt-and-suspenders by having the crew runner also list the rule file in the spawn's
`<files_to_read>` block. Requires inverting the router `SKILL.md`, which currently says *"Do NOT read
subdirectory rule files… injected via agent_skills."*

## DEC-21 — Rules are static, uniform, and human-authored; agents never write them

**Chose:** `rules/*.md` are the constitution — distributed, overwritten on every deploy, edited only
by you in the harness repo. No per-project rule overlay.
**Over:** letting agents refine their own rules; per-project rule customization.
**Because:** structural, not stylistic — `rules/` is distributed, so an agent's edit would survive
until the next `harness-deploy` and then vanish silently. Rules therefore *cannot* be agent-writable
without breaking distribution. And a rule governs all 15 agents, so no single agent should rewrite
the constitution off one bad run. One set of rules everywhere is the point of a harness.
**Tradeoff accepted:** rule improvement is human-gated and slower. Project-specific *values* still
vary (`domain` globs, `test_kinds`); project-specific *behavior* does not.

## DEC-22 — Per-agent expertise supersedes GSD's `auto_copy_learnings`

**Chose:** each agent keeps a bounded, structured mental model at `.harness/expertise/<agent>.md`,
read at task start and updated on completion.
**Over:** GSD's shared learnings bucket; discarding learnings entirely.
**Because:** durable knowledge should land in the agent that will act on it, not in a shared bucket
nobody reads. A stateless-subagent design otherwise discards, at every spawn, eng-lead's sense of
what works in this codebase, qa's knowledge of which tests are flaky, and pm's feel for where scope
creeps.
**Tradeoff accepted:** 15 more files, and memory that could itself become context bloat — bounded by
per-section caps and `max-lines`.

## DEC-23 — Hard boundary between a decision and an observation

**Chose:** a *choice* goes to `PLAN.md ## Decisions` (approval-gated); an *observation about how the
codebase behaves* goes to the mental model.
**Over:** letting agents record whatever they learned wherever it fits.
**Because:** without the boundary, mental models become a **shadow decision log that bypasses your
approval**. "We decided on Postgres" is yours to sign; "migrations fail if run before the seed
script" is not.
**Tradeoff accepted:** agents must classify, and misclassification is possible.

## DEC-24 — Expertise write discipline is advisory, in three layers

**Chose:** one shared `rules/mental-model.md` ("update ONLY if you learned something that would
change how you'd act next time"), plus DIGEST visibility (`expertise_updated` + a one-line why), plus
lead curation.
**Over:** mechanically enforcing quality.
**Because:** a hook can block a path; it cannot judge an insight. Content quality is not mechanically
enforceable, so the design makes junk writes *observable* instead of preventing them. One shared rule
file means one place to tune the behavior, not fifteen.
**Tradeoff accepted:** low-value entries will get written; they are caught downstream rather than at
write time.

## DEC-25 — Curation: the lead recommends, the member applies

**Chose:** on overflow the member flags `expertise_full`; the lead reads and emits a
`KEEP`/`DROP`/`MERGE` note; the note is injected into the member's next spawn and applied verbatim.
**Over:** the member self-pruning; the lead editing the member's file directly.
**Because:** leads have no `Edit` tool, so a lead *cannot* edit a member's file — which turns out to
be the right constraint: single-owner writes hold, while the lead supplies the cross-run view the
member lacks. Recommendations are binding because the lead saw the outcomes.
**Tradeoff accepted:** curation is one delegation-cycle delayed. On overflow the rule is condense,
not truncate, per-section, so one bad prune cannot gut the file.

## DEC-26 — Leads monitor squads via outputs, not memories

**Chose:** per-run, the lead reads members' DIGESTs and artifacts; longitudinally, squad-level
patterns accumulate in the **lead's own** mental model.
**Over:** leads reading whole squads' mental models, and the orchestrator reading all fifteen.
**Because:** that would rebuild exactly the context bloat this design exists to prevent. The lead is
already the only agent that sees every member's output, so the pattern accumulates naturally with no
extra mechanism.
**Tradeoff accepted:** one bounded exception — a lead may read a member's mental model during a
curation pass.

## DEC-27 — Two expertise tiers; promotion to global requires cross-project evidence

**Chose:** project-scoped `.harness/expertise/` (committed) and global `~/.harness/expertise/`
(local). Promotion only after an observation has held in **more than one project**. Project wins on
conflict. Global entries stay shorter than project ones.
**Over:** one tier; or automatic promotion.
**Because:** automatic promotion would export a single repo's quirk as universal craft. Global
entries load on every spawn in every repo, so they must be heuristics about *how to work*, never
facts about a codebase.
**Tradeoff accepted:** a wrong global entry silently misleads every project at once — which is why
promotion requires cross-project evidence and why global stays small.

## DEC-28 — CEO feedback is classified by kind, and addresses LEADS only

**Chose:** requirement changes → BRIEF/PLAN via pm (approval-gated); craft/behavioral feedback → the
addressed **lead's** mental model, routed through `.harness/notes/feedback.md` and cleared once
absorbed; course-corrections → the orchestrator's next instruction, not persisted.
**Over:** treating all feedback uniformly; writing feedback into any agent's memory directly.
**Because:** the three kinds persist differently, and you are not an agent so you cannot write a
lead's memory yourself. Feedback addressed to one lead has no business loading into every worker's
context — hence leads-only, matching the delegation rule that the orchestrator never reaches past a
lead into its squad. Clearing absorbed entries keeps `feedback.md` a queue, not a growing archive.
**Tradeoff accepted:** behavioral feedback reaches a worker only through how its lead delegates.

## DEC-29 — The three-part return; the orchestrator never opens member artifacts

**Chose:** every agent returns `VERDICT:` (control) + `DIGEST:` (routing) + `artifact:` (a path).
**Over:** a bare verdict token; returning artifact content inline.
**Because:** it resolves two competing pressures at once. The artifact is the focal, high-SNR handoff
document, so its full content must stay on disk and be read only by the downstream persona that needs
it — never pasted into a return. But VERDICT alone cannot drive conditional routing. The DIGEST gives
just enough structured signal to route **without opening the artifact**, keeping the coordinator's
context small. A lead *may* read its members' artifacts, and must, in order to assess.
**Tradeoff accepted:** DIGEST field names and enums become a contract that may not drift per
persona — the runner routes on exact values.

## DEC-30 — A malformed return is re-prompted once, then BLOCKED — never guessed

**Chose:** re-prompt the step once for the contract block; on a second failure record
`VERDICT: BLOCKED (contract violation)` and escalate.
**Over:** inferring a verdict from the text; failing the whole crew immediately.
**Because:** this is the most common LLM-runner failure and was previously unhandled. **Silent
misrouting is worse than a halt.**
**Tradeoff accepted:** one wasted re-prompt per occurrence.

## DEC-31 — Reviewers are advisory-only; no hard blocks on style or opinion

**Chose:** `must_fix` non-empty **or** `severity_max ≥ high` → `FAIL`; concerns at `≤ med` with empty
`must_fix` → `PASS` (with notes), logged and surfaced but not blocking.
**Over:** any reviewer finding gating the pipeline.
**Because:** preserves a decision already LOCKED in `.planning/STATE.md` Phase-03, and prevents the
non-convergence trap where a permanent minor nit loops forever to `max_cycles`.
**Tradeoff accepted:** genuine medium-severity issues can ship if the reviewer does not escalate them
to `must_fix`.

## DEC-32 — Autonomy is scoped by reversibility, not switched on or off

**Chose:** cheap and reversible → decide autonomously and record it; expensive or hard to reverse →
ask via `open_questions`; scope/goal/decision changes → always ask.
**Over:** (a) the reference config's blanket `high-autonomy: "act autonomously, zero questions"`;
(b) rejecting autonomy wholesale.
**Because:** adopting the blanket version would invert this design — the orchestrator exists to brief
you and take instructions. But rejecting it wholesale creates the opposite failure: agents escalating
trivia through `open_questions` until you are the bottleneck on every judgment call. Reversibility is
the axis that separates the two. Stated once in `rules/handoff.md` so all agents share it.
**Tradeoff accepted:** "reversible" is a judgment call. Note the asymmetry by design: the tier that
owns the human relationship (the orchestrator) is never itself autonomous; the workers below it mostly
do not need to ask.

## DEC-33 — Merge is user-gated by default; the orchestrator never auto-merges

**Chose:** gates pass → surface for approval. `harness.json` may opt into autonomous merge
per-project.
**Over:** auto-merging on green.
**Because:** merge is the CEO's, by the same logic that makes BRIEF and PLAN approval yours.
**Tradeoff accepted:** you are in the loop on every ship. PR creation is a soft skip if `gh` is
unavailable, so a missing CLI never fails a crew.

## DEC-34 — Two acknowledged self-review softnesses, tolerated with your approval as the control

**Chose:** accept that (1) `pm` authors `PLAN.md` and also checks the feature goal, and (2)
`eng-lead` routes the build and also owns architecture review for its own squad.
**Over:** adding independent reviewers for those two gates.
**Because:** pm owns intent, so the goal-check sits naturally with it; architecture review sits
naturally with the role that routes the build. **Your two approvals (BRIEF and PLAN) plus the merge
gate are the real compensating control.** Stated plainly rather than presented as principle — these
are weaker gates than qa, code and security enjoy.
**Tradeoff accepted:** exactly that weakness. If either proves too soft in practice, the fix is an
independent reviewer for that gate.

## DEC-35 — The test matrix is a floor, with structured predicates rather than prose

**Chose:** a static change-type → required-test-kinds table in `harness.json` that qa may *add* to
but never drop below; conditionals expressed as named predicates (`touches_db_or_external`,
`has_interaction_flow`, `match_bug_class`).
**Over:** prose conditionals; a fixed ceiling; qa's unaided judgment.
**Because:** if the "if touches DB/external" cells were prose they would silently vanish and
high-risk changes would ship untested. Fixing the predicate *names* as data keeps qa's judgment
auditable even though the evaluation is a judgment. `test_kinds` supplies the two things without which
"missing required kind → FAIL" is not computable: how to detect a kind in a diff, and what command
runs it.
**Tradeoff accepted:** `test_kinds.cmd` is per-project and must be detected at init by `dev-ops`.

## DEC-36 — An unresolvable test command is a LOUD third state, not a soft skip

**Chose:** missing or unresolvable `cmd` → `VERDICT: BLOCKED — test command unresolved`, distinct
from the not-applicable soft skip.
**Over:** folding it into the soft skip alongside "no browser target."
**Because:** **a silently no-op'd hard gate is worse than a halt.** The soft skip exists for
genuinely-absent tooling (no web project, no Playwright) — blocking legitimate non-web work on a
missing browser would be a bug. A broken test command is a different thing entirely.
**Tradeoff accepted:** an init that failed to detect a runner blocks the qa gate until fixed.

## DEC-37 — AI/LLM behavior coverage is a declared v1 gap, not a hidden one

**Chose:** state explicitly that prompt / model / agent changes are not meaningfully covered by the
test matrix, and that `ai-dev` work therefore passes on human judgment alone in v1.
**Over:** pretending the existing change types cover it; blocking v1 on building an eval system.
**Because:** a prompt edit is not logic, api, frontend or config. GSD's `gsd-eval-planner` and
`gsd-eval-auditor` (failure modes, rubrics, reference datasets, guardrails, production monitoring)
have **no successor here**. The consequence to accept consciously: the harness building *itself* — an
LLM-behavior system — is unevaluable by its own gates.
**Tradeoff accepted:** exactly that. Post-v1 shape if adopted: `change_type: ai_behavior` + an `eval`
required kind + an eval artifact authored by `ai-dev` and audited by validator-lead.

## DEC-38 — One orchestrator, not a separate coordinator and runner

**Correction to an earlier design.** The earlier "coordinator" and "runner" were the same actor at
two delegation granularities. The orchestrator is the main session running the `/harness` playbook;
"the runner" is its delegate-to-a-team subroutine (`crew/SKILL.md`). Delegating to one persona =
spawn directly; delegating to a team = run that crew's DAG.
**Because:** two names for one actor produced contradictory statements about who owns the run dir and
who routes.
**Note:** it plays a project-management *function* but is deliberately **not** named "PM" — that
abbreviation belongs to the `harness-pm` product-manager persona. It is not a persona at all.

## DEC-39 — Hierarchical org, one nesting level — the unproven bet, gated on a spike

**Chose:** orchestrator → domain lead → workers, with the crew's `lead:` field naming the host.
**Over:** flat (the orchestrator hosts every crew DAG from the main session).
**Because:** hierarchy keeps the orchestrator's context tiny — member spawns and DIGESTs live in the
lead's context, and the orchestrator sees one consolidated DIGEST per crew. GSD ships the pattern:
`gsd-debug-session-manager` holds the spawn tool and spawns `gsd-debugger` members from inside a
subagent, so depth-2 delegation works in production today.
**Counter-evidence weighed:** GSD ships ~30 agents and grants the spawn tool to **none** of them;
`gsd-executor` is a leaf; `gsd-execute-phase` orchestrates from the main session at "~15%
orchestrator" context. **The proven pattern in this environment is flat.** Hierarchical is the
unproven bet, which is why it is BUILD.md Step 0b.
**Tradeoff accepted:** a load-bearing dependency on unverified capability. Mitigated so the bet is
cheap to lose: **all three leads exist as spawnable personas in both modes**, and in flat mode
`eng-lead` (architecture review) and `validator-lead` (panel assessment) are spawned as leaf steps.
The spike decides only *who hosts the DAG*, never whether leads exist — **no named gate disappears on
the fallback branch, and no `harness-synthesizer` is needed.**

## DEC-40 — Parallel fan-out from inside a lead is a performance question, not an architectural one

**Chose:** leave it unresolved until measured, with two acceptable answers that both preserve lead
authority — `validator-lead` spawns its reviewers serially, or the orchestrator runs the panel in
parallel and hands results to `validator-lead` to assess.
**Because:** GSD proves nested spawning (serial) and parallel fan-out (from the main session) but
never both at once. This affects exactly one thing: the review panel. Everything else in the org is
the proven serial path.
**Tradeoff accepted:** possibly slower panels in v1.

## DEC-41 — `validator-lead` assessment replaces a generic `synthesize` step

**Correction to an earlier design.** Panels needed a `harness-synthesizer` or a generic lead to
consolidate findings; they no longer do.
**Because:** running the panel and assessing its feedback is the validator lead's *defining job*.
This also resolves the earlier gap where flat mode left synthesis ownerless — synthesis now has a
named owner by construction, in both hosting modes.

## DEC-42 — Approval steps sit at crew boundaries, never mid-DAG inside a lead

**Chose:** questions ride up via `open_questions` and the orchestrator asks.
**Over:** a lead pausing mid-DAG to ask you.
**Because:** a subagent cannot call `AskUserQuestion` — nested contexts break it — so a lead can
*never* pause to ask. This is a capability fact, not a preference.
**Tradeoff accepted:** a crew hosted by a lead cannot contain an approval step; approvals go between
crews.

## DEC-43 — The question round-trip is the single human-in-the-loop mechanism

**Chose:** one mechanism — `open_questions` up, orchestrator asks, re-delegate with answers via
`resume_from` + an answers path — for plan approval, pm ambiguity, a dev needing a decision, and
lead-to-lead input alike.
**Over:** an `interview` step type in the DAG; per-persona "ask the user" modes.
**Because:** subagents have no channel to the user and the orchestrator does, so every case has the
same shape. Reusing `resume_from` means **human pauses and crash recovery share one code path.**
**Tradeoff accepted:** every human interaction costs a full re-delegation.

## DEC-44 — User answers are durable, not ephemeral

**Chose:** write answers to `.harness/notes/answers-<runid>.md`, never only into a run dir.
**Because:** run dirs are pruned, and durable artifacts may be written from these answers. Lateral
lead→lead routing needs the same file, since two leads share no run dir.
**Tradeoff accepted:** more files under `notes/`.

## DEC-45 — Growth is handled by SEPARATION, not rotation

**Chose:** `STATE.md` holds no history at all (only `## Current` + `## Open Questions`, both
self-clearing); the activity stream lives in `.harness/logs/<YYYY-MM-DD>.md`, never loaded at spawn;
pruning runs opportunistically at `/harness` entry.
**Over:** a trimming/rotation rule on `STATE.md`.
**Because:** `STATE.md` is read by every agent at spawn, so history there would bloat all 15 contexts
and defeat the compact-return design. Separating it makes `STATE.md` **bounded by construction** —
there is no trimming rule to enforce, and therefore none to get wrong. Pruning needs no scheduler
because the state-consistency check already runs at every entry, and because `logs/` is committed,
pruning clears only the working tree while git history retains everything.
**Tradeoff accepted:** history requires an explicit read.

## DEC-46 — One branch and one PR per feature; runs are per-squad

**Chose:** all runs for a feature commit to `harness/<slug>`; each run belongs to one squad, so one
lead owns its `state.yaml`.
**Over:** a branch per run; one shared per-run state file.
**Because:** seven runs for one feature would otherwise mean seven branches. And a shared per-run
file would have 2–3 leads writing it in a multi-squad flow, breaking single-writer.
**Tradeoff accepted:** `ls features/<feat>/runs/` is the feature's full history, which grows.

## DEC-47 — Declaration and live state are separated; feature status lives only in `feature.yaml`

**Chose:** `PLAN.md ## Features` is the pm-owned, approval-gated declaration; `feature.yaml` is
orchestrator-owned execution fact and holds **no** name, traces or task list — only a `feature_id`
join key.
**Over:** status on the PLAN feature entry; or a self-describing `feature.yaml`.
**Because:** declaring status in both places gives two sources of truth that diverge. And duplicating
the declaration into `feature.yaml` would let an agent redefine what FEAT-01 *means* without your
signature.
**Tradeoff accepted:** reading a feature's full picture requires both files.

## DEC-48 — REQ / FEAT / D / T are four distinct levels; a technical dependency is a decision

**Chose:** REQ-NN in BRIEF (what the product must do), FEAT-NN in PLAN (the unit of work), D-NN
(architectural how), T-NN (concrete steps). **The test: a REQ survives changing your mind about
implementation.**
**Over:** collapsing requirements and technical choices.
**Because:** this matters beyond tidiness. `pm` goal-checks REQ coverage against the approved BRIEF —
if implementation choices were logged as REQs, the goal-check would "verify" that you delivered your
own technical decisions rather than the outcomes you committed to, **passing green while missing the
point.** Swap Supabase for Auth0: REQ-02 unchanged, FEAT-01 unchanged, D-03 and several tasks
changed.
**Tradeoff accepted:** FEAT ↔ REQ is many-to-many, so **REQ coverage is computed, never tracked** —
no status field on a REQ that could drift.

## DEC-49 — The retry budget is feature-level, not run-level

**Chose:** `cycles_used` / `max_total_cycles` in `feature.yaml`.
**Over:** a counter inside a run's `state.yaml`.
**Because:** a fix cycle spawns a *new eng run* plus a *new validator run*, so the loop spans runs. A
counter inside one run's file cannot bound it.
**Tradeoff accepted:** none identified. Exhaustion → `BLOCKED` → CEO briefing.

## DEC-50 — Reviewers diff a pinned `review_sha`, never `…HEAD`

**Chose:** pin `review_sha` at review dispatch; reviewers diff `base…review_sha`. Ground truth is
local `git diff` — no `gh`, no network, no auth.
**Over:** reviewing `base…HEAD`; requiring a live PR.
**Because:** a later commit would otherwise shift what a reviewer is reviewing mid-review.
**Tradeoff accepted:** `review_sha` is feature-level state to maintain, because the branch is.

## DEC-51 — Resume rather than re-prompt a dead host; derive side effects from git

**Chose:** re-spawn the host with `resume_from: <in-flight step>`; it reads `state.yaml` for what was
dispatched and **`git log` for what actually landed**, aided by a mandatory `[harness:<step-id>]`
commit prefix.
**Over:** re-prompting the host.
**Because:** re-prompting re-runs the whole DAG and risks double-commits. `dispatched_at` written
before the spawn and `completed_at` after makes a step with the first and not the second **provably
in flight** — which is what makes every recovery case decidable. Reading git rather than trusting the
log makes side effects derivable rather than guessed.
**Tradeoff accepted:** honest scope — crews are resumable **at step boundaries**, not mid-step.

## DEC-52 — Canonical files are written in place; only staged files need promotion

**Chose:** a persona whose deliverable is a canonical file (pm → `PLAN.md`) writes directly to the
persistent path; run dirs hold reports and intermediates only.
**Over:** every step staging output in its run dir and promoting afterward.
**Because:** staging invites stale-read corruption — a consumer step reads the previous version
silently. Where a crew *does* stage a canonical file, promotion must complete **before any consumer
step dispatches.**
**Tradeoff accepted:** persistent files change mid-crew, so a crash can leave them partially updated.

## DEC-53 — Reviewer reports are namespaced per persona and run

**Chose:** `notes/review-<persona>-<runid>.md`.
**Because:** a parallel reviewer panel would otherwise collide on one report path — the same
single-owner logic as everything else in SPEC §2.3.

## DEC-54 — Flat, standalone crews in v1; panel duplication accepted

**Chose:** no sub-crew composition in v1. The review panel is listed in both `ship-feature` and
`review-team`.
**Over:** flattening sub-crews now to keep it DRY.
**Because:** readability, and no dependency on a flattening step in the runner.
**Tradeoff accepted:** the duplication itself — revisit post-v1. **Post-v1 shape, specified so it is
not re-litigated:** sub-crews resolve by **flattening** the child DAG into the parent at load time
(ids namespaced, edges rewired), never a nested runner. That is what would remove the duplication. The
v1 runner algorithm has no flattening step.

## DEC-55 — `review-team` is advisory: it never fixes and never merges

**Chose:** the panel returns `must_fix`; the caller owns remediation (`ship-feature` loops its dev;
standalone, the orchestrator delegates a fix).
**Because:** it keeps the reviewer/doer separation intact and makes the crew reusable from any
caller.

## DEC-56 — pm's goal-check is kept out of the quality panel

**Chose:** `pm(goal-check)` is its own step in `ship-feature`, after the panel and its assessment.
**Over:** including it in the `{code ∥ security ∥ ui}` panel.
**Because:** "did we deliver?" should not be averaged with code nits.
**Tradeoff accepted:** one more serial step.

## DEC-57 — Deliberate divergence from the kaya-ai `/review-team` pattern

The existing kaya-ai memory describes the panel as "code/qa/security/eng/**ceo**, auto-selected for
the diff." Three changes here, noted as deliberate rather than accidental:

1. **No CEO** — you are the CEO, and a diff is not a CEO context.
2. **No separate eng-reviewer** — `eng-lead` owns architecture review (DEC-08).
3. **Panel membership is crew config, not auto-selected** — reviewers self-scope, which preserves
   per-diff efficiency without runtime panel guessing.

**Follow-up owed:** update that memory once the harness ships (BUILD.md § Post-ship follow-up).

## DEC-58 — Five eng domains with no catch-all

**Chose:** `dev-ops` is a peer specialist owning infra / CI / config / tooling / deploy; eng-lead
routes each task to exactly one of five.
**Over:** four feature-code devs plus a catch-all bucket.
**Because:** infra work is genuinely different from feature code and largely TDD-exempt via the
`config` / `scaffolding` change types, so it deserves a named owner rather than being the place
unclassifiable tasks land. This also means no task has to be forced into a feature domain.
**Tradeoff accepted:** `dev-ops` holds `Bash`, which bypasses path reasoning entirely — it is the
sharp edge of domain enforcement (DEC-19). Either its hook also matches `Bash`, or dev-ops is trusted
by design and merge/deploy stay user-gated.

## DEC-59 — `## Skills` buys consistency, not enforcement — stated honestly

**Chose:** keep the declarative `## Skills` / `## Expertise` / `## Domain` body shape while stating
plainly that Claude Code does not parse it.
**Over:** presenting it as a mechanism; or dropping the structure as decorative.
**Because:** it is prose the agent must choose to obey — no more parsed than the old `## Discipline`
prose it replaces. What it genuinely buys: a uniform shape across all 15 agents, greppable auditing
("which agents load `tdd-enforcement`?"), and one place per agent to see its whole rule set. The only
*mechanical* rule in the system is the domain hook, and that governs writes, not reads. (Some
runtimes act on these keys; this one does not.)
**Tradeoff accepted:** the honest answer is that most discipline rests on obedience.

## DEC-60 — `.harness/README.md` is rewritten, not created

**Chose:** treat the existing on-disk `.harness/README.md` as a defect to fix, owned by
`documentor`.
**Because:** it already exists and **contradicts this design**: it documents a pre-restructure org
(`builder` / `tester` / `planner` / `scout` / `coordinator`), omits `BLOCKED` from the VERDICT enum,
lacks `DESIGN.md`, and describes qa as advisory. Critically, its schema templates omit the two
hardest-gated fields — PLAN tasks lack `change_type`, and the BRIEF template has no `## Approval`. A
builder will copy those.
**Tradeoff accepted:** none. Leaving it would actively mislead.

## DEC-61 — The Phase-1 exploration findings are not preserved as a standalone section

**Chose:** fold the durable findings into the `Because` clauses of the decisions they support; drop
the exploration log.
**Over:** keeping a "Findings" section.
**Because:** a point-in-time exploration log is exactly the kind of history the SPEC/DECISIONS split
exists to move out of the spec. The three load-bearing findings live on as rationale: `personas/` was
entirely stubs, so the roster was a clean slate (DEC-07); `agent_skills` was the only rule-delivery
mechanism (DEC-20); `/harness-deploy` distributes skills but not commands (DEC-06).

## DEC-62 — The GSD UI trio maps onto two agents, splitting authorship from audit

**Chose:** three GSD roles collapse into two harness agents —

| GSD role | Successor |
|---|---|
| `gsd-ui-researcher` | `harness-visual-designer` (authors `DESIGN.md`) |
| `gsd-ui-checker` | `harness-ui-reviewer` **mode A** — pre-build: is `DESIGN.md` sound? |
| `gsd-ui-auditor` | `harness-ui-reviewer` **mode B** — post-build: adversarial scored audit of built UI vs `DESIGN.md` |

**Over:** one UI agent doing all three; or three separate agents mirroring GSD one-for-one.
**Because:** the checker and auditor are the same *stance* (audit against the contract) at two points
in time, so they belong to one reviewer with two modes — and that reviewer must not be the agent that
authored the contract. Splitting it this way is what keeps authorship separate from audit for visual
work, matching every other gate except the two in DEC-34.
**Tradeoff accepted:** `ui-reviewer` carries mode logic and must self-scope out on non-UI diffs.
**Note:** `DESIGN.md` and the design pass are net-new capability relative to GSD's "(v1) no browser
automation" limitation, which is superseded — `qa` owns Playwright E2E execution (DEC-35).

## DEC-63 — Rule delivery switches to native `skills:` preload — SUPERSEDES DEC-20
<!-- stale: "injected via agent_skills" -->
<!-- stale: "## Discipline" -->

**Chose:** each rule becomes a skill; each agent declares its rules in the `skills:` frontmatter
field, and Claude Code injects the **full content** at spawn.
**Over:** self-injection (DEC-20), where the agent read its rule file as step 0 of its protocol.
**Because:** DEC-20's one accepted weakness was that it *depends on obedience* — an agent under
pressure can skip a step-0 instruction and nothing detects it. `skills:` removes that weakness at the
runtime level: the rule is in context before the agent's first action. The `<files_to_read>`
belt-and-suspenders is no longer needed, and the `## Skills` prose section is deleted.
**Tradeoff accepted:** rules load unconditionally with no "use-when" laziness, so every listed rule
costs its full length on every spawn of that agent — rules must stay short, and an agent lists only
what genuinely binds it. Each rule also needs a directory with a `SKILL.md` rather than being a bare
`.md` file.
**Evidence:** verified in the Claude Code subagent documentation — `skills:` is a supported
frontmatter field and injects full skill content, not just descriptions.

## DEC-64 — Expertise is delivered by a `SubagentStart` hook, not read by the agent

**Chose:** a `SubagentStart` hook in `settings.json` receives `agent_type` and returns the agent's
expertise file as `hookSpecificOutput.additionalContext`.
**Over:** the agent reading its own expertise file; native `memory:`.
**Because:** two properties, both decisive. (1) **No obedience dependency** — the agent starts with
its expertise already in context. (2) **No tool grant required** — a reviewer holding only
`Read`/`Grep` still receives it, which a read-based approach could manage but native `memory:` could
not (see DEC-65).
**Tradeoff accepted:** one more hook in `settings.json`, and the injection is read-only — the write
path is separate (DEC-66).

## DEC-65 — Native `memory:` is REJECTED despite being a near-exact match

**Chose:** hand-rolled `.harness/expertise/<agent>.md`.
**Over:** `memory: project` in frontmatter, which gives each agent a persistent directory with
MEMORY.md auto-injected and curation instructions built in.
**Because:** enabling `memory:` **auto-enables Read, Write and Edit** for that agent. That silently
breaks two capability guarantees the design treats as load-bearing: leads have no `Edit` so an LLM
lead cannot fix a bug itself instead of delegating (DEC-18), and reviewers have no `Write` so an
auditor cannot mutate what it audits. Losing both to gain free memory machinery is the wrong trade —
those guarantees are enforced by tool grant precisely because prose does not hold under pressure.
**Tradeoff accepted:** we maintain section caps, entry IDs, ops and curation ourselves (DEC-66,
DEC-67) instead of inheriting them. Also: hand-rolled expertise is unaffected by
`autoMemoryEnabled` / `CLAUDE_CODE_DISABLE_AUTO_MEMORY`, which would silently disable the native
version.

## DEC-66 — Expertise updates are validated ops with stable entry IDs — REFINES DEC-22/DEC-24

**Chose:** entries carry stable per-section IDs (`P-01`, `G-01`, `O-01`, `Q-01`); updates are
**ops** — `add | replace | merge | drop` — each naming its target and carrying a `why`.
Reconciliation happens **at propose time**, by the agent that already has the file in context.
**Over:** appending entries and reconciling only on cap overflow.
**Because:** a **contradicting or stale entry can land while well under the cap**, and an
overflow-triggered pass would never see it. The agent proposing the update is also the best-positioned
to spot the contradiction, because the injection hook already put the file in its context. Without IDs,
an update can only append.
**Tradeoff accepted:** IDs must be assigned and never reused after a drop. An op naming a nonexistent
target is a contract violation, handled by DEC-30's existing re-prompt-once-then-`BLOCKED` discipline
rather than by guessing.

## DEC-67 — Applier splits by capability: doers self-apply, write-less agents go through the orchestrator

**Chose:** the 8 doers reconcile and apply their own expertise file in place (domain hook scopes them
to it), reporting the op upward in the DIGEST for logging. The 3 leads and 4 reviewers propose ops and
the **orchestrator** validates and applies them.
**Over:** (a) uniform — orchestrator applies for all 15; (b) granting leads and reviewers a narrow
`Write` scoped to their own file.
**Because:** doers already hold `Write`, so routing them through the orchestrator would add a hop for
no gain. The write-less tiers reuse a pattern already in the design — the orchestrator is the single
writer for `STATE.md`, `logs/`, `feedback.md` and `## Approval` precisely because it is the tier that
holds the pen. Granting reviewers `Write` was rejected because "reviewers never mutate" would weaken
to "reviewers mutate one file", and it would rest entirely on the unproven domain hook.
**Tradeoff accepted:** two write paths for one concept, so op-validation and cap enforcement exist in
two places, and a doer validates its own ops. **No file ever has two writers**, which is the property
that actually matters. Under hierarchy a doer's op rides the per-member block already carried by the
consolidated DIGEST, so no new channel is needed.

## DEC-68 — Curation is applied IMMEDIATELY, spawning a closed agent if necessary — REVISES DEC-25

**Chose:** a curation note is applied at once. If the target agent is no longer running, the
recommending tier **spawns it solely to apply the note**.
**Over:** DEC-25's "injected into the member's next spawn."
**Because:** the recommendation is only as good as the context that produced it. The lead holds the
cross-run view *now* — the member's file, its recent DIGESTs, what happened this run. Deferring to the
next natural delegation means that context is gone, and either the note must carry its own
justification forward or the lead must reconstruct it later. **A cheap single-purpose spawn is
strictly better than a stale or re-derived recommendation.** Applies one tier up too: the orchestrator
spawns a lead immediately for its condense ops.
**Tradeoff accepted:** extra spawns whose only work is a file edit.

## DEC-69 — The orchestrator curates the leads; you see it and can object

**Chose:** the orchestrator recommends curation for a lead's own expertise, using the cross-lead view
it holds at the CEO briefing. The lead converts the recommendation into ops; the orchestrator applies
them. A compact summary appears in the briefing and **applies unless you object**.
**Over:** (a) leads self-curating with no external check; (b) requiring your explicit approval;
(c) applying silently and letting you find it in the PR diff.
**Because:** leads curate members, but nothing curated leads — a wrong lead entry shapes every
delegation that lead makes. The orchestrator already receives all three consolidated DIGESTs at the
briefing, so it has the cross-lead view at no extra spawn cost. Your leads are your direct reports, so
you get the final say; making it apply-unless-objected keeps it a skimmable list rather than a
blocking review task.
**Tradeoff accepted:** the briefing grows a few lines per lead. **It must be written in plain English
with light technical detail, not ID shorthand** — a curation block that reads as `merge P-04+P-09` has
failed at being reviewable by a human.

## DEC-70 — `ai_behavior` becomes a real change type: ai-dev authors the eval, qa owns the gate — SUPERSEDES DEC-37

**Chose:** add `change_type: ai_behavior` with `eval` as a required test kind. `ai-dev` **authors** the
eval (failure modes, rubric, reference dataset, threshold); `qa` **runs it and owns the gate**;
`validator-lead` assesses eval *adequacy* in its panel synthesis.
**Over:** DEC-37's declared v1 gap (ai-dev work passing on human judgment alone), and over
validator-lead auditing evals qualitatively outside the matrix.
**Because:** it mirrors every other change type — the specialist authors, the validator gates — so an
AI change with no eval FAILs exactly as a missing unit test does. Only the agent that wrote the prompt
knows what "wrong" looks like for it, so authorship must sit with `ai-dev`; but a gate the author also
owns is not a gate, so enforcement sits with `qa`.
**Tradeoff accepted, stated honestly:** a passing eval is weaker evidence than a passing unit test.
Non-determinism means a **threshold and a measured rate**, not a boolean. A green eval bounds only what
its dataset covers, and coverage gaps go in qa's `coverage_gaps` like any untested path. Production
monitoring and guardrails remain out of scope for v1. The reflexive problem is improved, not resolved:
the harness is an LLM-behavior system now gated by evals its own `ai-dev` writes.

## DEC-71 — The orchestrator delegates only to leads; there is no orchestrator→worker path

**Chose:** even a single-task request enters through the lead that owns the relevant persona.
**Over:** the orchestrator spawning a persona directly for one-off work.
**Because:** a direct path would bypass the three things a lead exists for — routing by
`consult-when`, assessing the result, and its own Expertise. It would also give identical work two
different shapes depending on how it happened to be requested, and would put un-assessed work into
`STATE.md`.
**Tradeoff accepted:** one extra spawn for trivial single-task work. In exchange `STATE.md` sees a
uniform stream of consolidated DIGESTs and no work is ever unassessed.

## DEC-72 — A crew's `goal` is a success-criteria set; work continues until SC are met

**Chose:** `(crew, goal)` resolves `goal` to the FEAT plus the `SC-NN` entries its REQs trace to. A
crew is done when its SC are **met**, not when its steps complete.
**Over:** treating the goal as a prose instruction and the DAG's completion as success.
**Because:** "the team keeps working until the goal is met" is only mechanical if the goal is a
checkable set. A DAG that ran to completion with `SC-05: not_met` is a `FAIL` that loops back.
**Tradeoff accepted:** the loop needs a bound, and there is exactly one — `max_total_cycles`. Unmet SC
plus remaining budget → another cycle; unmet SC plus exhausted budget → `BLOCKED` and your decision
(DEC-73).

## DEC-73 — Every SC declares its verification method when authored; pm collects evidence rather than re-testing

**Chose:** each `SC-NN` in `BRIEF.md` carries `verify: automated | inspection | uat`. pm's goal-check
**assembles evidence from the validators** — qa's results for `automated`, a reviewer's cited finding
for `inspection`, your UAT result for `uat` — and emits `sc_status` with an evidence pointer per SC.
**Over:** leaving "how does pm verify SC" undefined, which it was.
**Because:** "pm checks the feature goal" is unfalsifiable without a method per criterion. Making the
method part of authoring means an unverifiable SC is caught at plan time, not at ship time — an SC with
no method blocks the goal-check the same way a task missing `change_type` blocks the qa gate.
**Explicitly:** **a passing suite is not automatically a met SC.** pm must find the specific test that
exercises that criterion; if none exists the SC is `not_met` and the gap returns to qa, not to you.
**Tradeoff accepted:** pm still authors the plan and runs the check (DEC-34), but this is the weakest
form of that self-review available — pm cannot manufacture evidence, only report what others produced.

## DEC-74 — UAT is a pm-owned artifact and a blocking gate inside the CEO briefing

**Chose:** any SC marked `verify: uat` produces a step in `.harness/notes/uat-<FEAT>.md`. **pm decides
when the UAT is `ready`** — and only once every `automated` and `inspection` SC has already passed. It
is a required, blocking section of the ship-review briefing; your pass/fail **is** the ship
instruction.
**Over:** (a) UAT as its own gate before the briefing; (b) UAT as advisory.
**Because:** one user-facing moment beats two — the briefing already exists to collect your shipping
decision, and a UAT is the evidence for the part of that decision only you can make. Gating pm's
`ready` on the automated criteria means you are never asked to hand-test a feature whose tests are red.
**Tradeoff accepted:** a feature with a required UAT cannot ship without you, whatever else is green. A
failed UAT step is a `FAIL`, not a discussion: it loops back to the responsible squad with your
`result:` text attached and consumes a cycle.

## DEC-75 — High-fidelity prototype gate for any feature with end-user interaction

**Chose:** `visual-designer` decides during the design pass in `plan-feature` whether a feature
requires end-user interaction; if so it builds a high-fidelity, interactive prototype on the team's
design-system convention, and **you must approve it — bundled with PLAN approval as one signature.**
**Over:** (a) deriving the trigger mechanically from `change_type: frontend`; (b) pm deciding at plan
time; (c) a separate `prototype-feature` crew; (d) two separate approvals.
**Because:** the design pass sits at the end of the product planning cycle, so the call lands before
any build and inside what you approve. Deriving it from change types would demand prototypes for
padding tweaks and would miss user-facing surfaces that are not yet code paths. One approval because the
prototype and the plan answer the same question from two angles — *are we building the right thing?*
**Tradeoff accepted:** `plan-feature` gets materially longer for user-facing features, and **the trigger
is one agent's judgment**, wrong in either direction. Mitigation: the decision and its reason appear in
the crew's DIGEST at the approval gate, so you can demand a prototype it thought unnecessary or waive
one it did not.

## DEC-76 — Teams carry binding technology conventions in the manifest

**Chose:** a `conventions:` block per team in `team-config.yaml` — Engineering uses the **Supabase
plugin**; Product implements all UI against the **Astryx design system** (`@astryxdesign/core`,
pinned). Templates ship the defaults; deviating requires a `## Decisions` entry and therefore your
approval.
**Over:** encoding them as rule skills, or leaving them to per-feature judgment.
**Because:** rules are behavioral and identical in every project; conventions are *technology choices*
that vary by team and project, so the manifest is the right home — it lets a project override one
without forking the constitution. Putting them in data also stops the choice being re-litigated per
feature or re-derived from prose.
**Correction to a stated assumption:** **Astryx is not globally available as a Claude Code
capability.** It is an npm package (`@astryxdesign/core`, React ≥19 peer, StyleX internal, runtime
`defineTheme` with `[light, dark]` tuples) plus a reference clone — so "ensure it's available" is a real
provisioning step, delegated to `dev-ops` at `/harness-init`, and a missing dependency is reported
rather than worked around. Supabase *is* available as a plugin.
**Tradeoff accepted:** version pinning is the default, so upgrades are deliberate decisions rather than
silent drift.

## DEC-77 — `max_cycles` exhaustion preserves everything and escalates; it never abandons

**Chose:** on exhaustion — stop that branch only, preserve `state.yaml` history and the branch and all
commits, leave feature `status: in_progress`, roll up `VERDICT: BLOCKED` **with what was tried each
cycle**, and trigger the CEO briefing. You then raise the budget, re-scope via pm, take the partial
work, or abandon.
**Over:** marking the feature `abandoned`, reverting the branch, or silently continuing.
**Because:** an exhausted loop is only actionable if you can see *why it did not converge*, so the
per-cycle history is the point. Setting `abandoned` is your call, not the orchestrator's. And
independent DAG branches should be allowed to finish — exhaustion fails a branch, not necessarily a
crew.
**Tradeoff accepted:** blocked features accumulate until addressed; the state-consistency check surfaces
them at every `/harness` entry so they cannot be quietly forgotten.

## DEC-78 — Escalation resolutions are recorded in the DIGEST, and plan-level ones must be promoted

**Chose:** the consolidated DIGEST carries an `escalations:` list capturing the question, who raised it,
where it was routed, **how it was resolved, and by whom**. A resolution that constitutes a real
architectural or scope choice names the resulting `D-NN` in `PLAN.md ## Decisions`.
**Over:** routing questions via `open_questions` and letting the answer live only in one lead's
context.
**Because:** lateral lead-to-lead resolution was a new capability with no audit trail — "who decided
this, and when" was unanswerable after the run. More seriously, without the promotion rule a
lead-to-lead exchange becomes **a back door around your approval**: two leads could settle an
architectural question that should have been a gated decision.
**Tradeoff accepted:** more DIGEST surface, and resolutions are logged to `logs/<date>.md`.

## DEC-79 — Feature-scoped durable artifacts carry the FEAT id in the filename

**Chose:** `answers-<FEAT>-<runid>.md`, `ship-review-<FEAT>-<runid>.md`, `uat-<FEAT>.md`,
`prototypes/<FEAT>/`; each file's header repeats the feature and run.
**Over:** naming them by `runid` alone.
**Because:** a feature accumulates several runs across several squads, so a bare `runid` leaves you
grepping `state.yaml` files to discover which feature an artifact belongs to. The id belongs in the
filename so `ls` answers the question.
**Tradeoff accepted:** longer filenames.

## DEC-80 — Terminology unified on "Expertise"; "mental model" retired

**Chose:** one name — the file is `.harness/expertise/<agent>.md`, the rule is the `harness-expertise`
skill.
**Over:** the source's three interchangeable names — "Expertise" (section, path, body section),
"mental model" (prose throughout, and the rule filename `mental-model.md`), and "institutional memory"
(subtitle).
**Because:** they described one artifact, and the drift was a defect rather than a distinction. It
mattered more once rules became named skills (DEC-63), since the skill name is now referenced in
frontmatter across 15 agents.
**Considered and rejected:** splitting codebase knowledge from collaborator/routing knowledge into two
artifacts, or adding a fifth `## Collaborators` section for leads. A lead's observation that
*"frontend-dev skips a11y"* files under Patterns.

## DEC-81 — Agent frontmatter corrections found by verifying against the documentation

Four claims inherited from the source plan were wrong. Recorded because each was load-bearing:

| Claim | Reality |
|---|---|
| `color: "#0B7A6E"` (hex) | **Named colors only** — `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan`. Team colors are now names |
| domain hook "exits non-zero to block" | **Only `exit 2` blocks.** Any other non-zero exit is a *non-blocking* error and **the write proceeds** — a script exiting 1 on violation would silently permit every out-of-domain write while appearing to enforce |
| hook receives `$FILE` | **No such variable.** Tool input arrives as **JSON on stdin**; only `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}` interpolate into `command` |
| concurrency cap ~10 | **20** concurrent by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), **200** per session (`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`); nested and background spawns both count |

The `$FILE` error traces to GSD's commented-out example, which is additionally a **`PostToolUse`** hook
running `eslint --fix` — a non-blocking fix-up, not the blocking guard the source presented it as. The
exit-code error is the dangerous one: it would have shipped a hook that fails open, which is the exact
silent corruption it exists to prevent (DEC-19).

## DEC-82 — Nested spawning is confirmed supported and gated on a setting — RESOLVES DEC-39

**Confirmed:** subagents **can** spawn subagents. It is off by default and enabled by setting
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` in `settings.json` — `"2"` gives exactly the
orchestrator → lead → worker depth this design specifies, with the second layer unable to delegate
further (which enforces "workers are always leaves" mechanically rather than by convention).
**The token is `Agent`**, and omitting it from a `tools:` list keeps an agent from spawning — so
reviewers stay leaves by capability.
**This resolves the hard prerequisite in DEC-39**: hierarchical is buildable, and the flat fallback is
no longer the expected outcome. DEC-39's counter-evidence (GSD grants the spawn tool to none of ~30
agents) is explained — nesting was off by default, so GSD had no reason to.
**Also largely resolves DEC-40** (parallel fan-out from inside a lead): the documentation's own example
of nesting is "a reviewer subagent that dispatches a verifier per finding", which is the
`validator-lead` panel. What remains is empirical confirmation, not an architectural question.
**Caveat retained:** this is a **settings dependency**, so `/harness-init` must set it and the
state-consistency check should verify it — a project with depth unset silently degrades to flat.

## DEC-83 — Nesting default is 3, not off — CORRECTS DEC-82, and DEC-82 corrected DEC-39

Third correction to the same fact, which is itself the finding.

**Verified** (`env-vars`, 2026-07-26): *"Number of subagent layers allowed below the main conversation
**(default: 3)**… In v2.1.217 through v2.1.218, the default was 1… v2.1.219 raised the default to 3."*

| CLI band | Nesting default | Configurable |
|---|---|---|
| 2.1.172 – 2.1.216 | on, up to 5 layers | no |
| 2.1.217 – 2.1.218 | 1 (off) | yes |
| **≥ 2.1.219** | **3 (on)** | yes |

**What DEC-82 got wrong:** it said nesting is "off by default and enabled by setting the depth" — true
only for the 2.1.217–218 band. It relied on `sub-agents` page prose (*"by default, a subagent can't spawn
subagents of its own"*), which is **stale relative to `env-vars`**. The two doc pages disagree; `env-vars`
carries the version markers and wins.

**Consequences:**
- **BUILD §0a's "if missing" row was inverted.** A missing setting does not collapse the org to flat — at
  the current default it lets **workers delegate**, the opposite of the intended guarantee.
- **Set depth explicitly to `2` in every project.** It is the only value correct in all three bands.
- **The primary control is capability, not the setting:** omit `Agent` from every worker's `tools:`. The
  depth cap is defence in depth.
- **Pin CLI ≥ 2.1.217** — the floor for all three spawn env vars. Nothing pinned a version before.
- **DEC-82's GSD explanation is withdrawn.** It claimed GSD grants the spawn tool to none of its ~30
  agents "because nesting was off by default" — but nesting was *on* by default for the entire
  2.1.172–2.1.216 band, so that reasoning fails. GSD's flat topology is an unexplained data point, not
  evidence.

**Standing rule, and the real lesson:** three parties produced confident wrong platform claims in one
week — this design twice, and a review commissioned specifically to catch the design's doc errors, which
reported three documented env vars as fabricated. **A platform claim without a URL, a quote, and a
min-version marker does not count.** BUILD.md now carries the cited table.

## DEC-84 — `delete: false` is deleted; it never existed — CORRECTS DEC-19's safety rail

**Chose:** remove it. Destructive-operation restraint is a `Bash` matcher in `check-domain.sh` with
`exit 2`, or it does not exist.
**Because:** `delete: false` was asserted as "a blanket safety rail… regardless of outcome" in both SPEC
and BUILD. **No such field exists in any Claude Code surface and nothing implemented it.** It was a
sentence that read like a mechanism — the most dangerous kind of specification error, because a builder
would have shipped believing deletion was guarded.
**Tradeoff accepted:** a `Bash` matcher cannot reliably extract targets from arbitrary shell, so this is
partial (DEC-85).

## DEC-85 — Serialization is the write-safety mechanism; the domain hook is a guardrail — INVERTS DEC-19

**Chose:** state plainly that **serialization** (§8.5's strictly-serial repo-mutators on one branch),
plus `isolation: worktree` for genuinely parallel mutation, is what makes fan-out safe. The domain hook
is a useful guardrail over the common `Write`/`Edit` case, **not** a guarantee.
**Over:** DEC-19's framing, which called single-owner domains "the entire justification for running
agents in parallel" and treated serialization as the fallback.
**Because:** two independent problems, both verified in the repo.
1. **All 9 doers hold `Bash`** (not just `dev-ops`, as §4.2 claimed). A `matcher: "Write|Edit"` hook sees
   none of `sed -i`, `cat > f`, `tee`, or a build script — and models reach for shell redirection
   constantly, so this is ordinary drift. Matching `Bash` properly is unwinnable: you cannot reliably
   extract write targets from arbitrary shell.
2. **Disjoint domains are unachievable for shared files.** `package.json`, lockfiles, schema and type
   barrels, route registries and CI config are legitimately written by several specialists. Either the
   globs overlap — so disjointness is void even with a perfect hook — or they don't, and routine tasks
   BLOCK on files nobody may touch. *"Eng-lead routing guarantees two specialists never own the same
   file"* holds at the roster level and is false at the file level.
**Aggravating irony:** §8.5 already serializes repo-mutators, so the hook apparatus protected a surface
the design mostly does not parallelize — maximum machinery, minimum protected surface.
**Added:** a `shared:` path set in the manifest. Writes to a shared path are always serialized and
attributed to whichever specialist the lead routed; no agent owns them.
**Tradeoff accepted:** less parallelism than the design implied it had. It never actually had it.

## DEC-86 — Roster arithmetic corrected: 3 leads + 9 doers + 3 reviewers — CORRECTS DEC-67

**The count was wrong in the spec and every reviewer inherited it.** DEC-67 and SPEC §5.3 said "8 doers"
and "3 leads + 4 reviewers", making 7 agents write-less. Correct: **9 doers** (pm, visual-designer,
documentor, frontend-dev, backend-dev, ai-dev, data-engineer, dev-ops, **qa**) + **3 reviewers** (code,
security, ui) + 3 leads = 15. `qa` is a doer — it writes tests. **Six** agents are write-less, not seven.
**Why it matters beyond tidiness:** it widens the `Bash`-bypass surface from 8 to 9 (DEC-85), and it
means all three reviews under-counted it.
**Process note:** all three independent reviewers repeated the error, because they were auditing the
document that contained it. Independent review does not catch a shared premise.

## DEC-87 — Spec bug: a doer's Expertise path must appear in its `domain`

**Fixed.** §5.3 has doers self-apply their Expertise ops in place, "scoped by the domain hook to its own
file" — but no manifest `domain` listed `.harness/expertise/<agent>.md`. **A working hook would have
blocked the mechanism §5.3 depends on**, and the failure would have looked like agents mysteriously
never learning.
**Caught by review before any agent file was written**, which is the cheapest place to catch it.

## DEC-88 — One feature in flight; the multi-feature promise is withdrawn

**Chose:** one feature at a time, stated as an operating constraint (§15.2).
**Over:** §10.5's claim that "a `BLOCKED` feature does not silently block the whole project — independent
features remain workable."
**Because:** the state model cannot support it. `STATE.md ## Current` is **singular by construction**
(§2), mutator serialization is per-crew rather than cross-feature, and two features in flight means two
branches diverging from `main` with committed Expertise files, daily logs and `PLAN.md` task statuses
guaranteed to conflict at merge. The promise and the mechanism contradicted each other.
**Consequence:** a `BLOCKED` feature is a stop-and-decide, not a switch-tasks.

## DEC-89 — Human edits get a legal path instead of being treated as corruption

**Chose:** hand edits commit with a `[harness:human]` prefix; the state check reports any such commit
since the last pinned `review_sha` and **re-pins it** so the next review covers the change; the
dirty-tree whitelist is defined as `.harness/**` plus staged paths.
**Over:** the implicit assumption that all repo mutations flow through agents.
**Because:** a hands-on solo CTO **will** hotfix a file mid-feature, and the design punished it twice:
§8.6 halts a crew with `BLOCKED` on a dirty tree, so **your own uncommitted edit deadlocks the system**;
and a manual commit lands unreviewed and unattributed between pinned SHAs, invisible to the reviewers and
to the qa matrix gate, both of which work from the diff.
**The invariant:** a hand edit must never be *ignored*. It does not inherit a passing review — it
re-opens the reviewer and qa gates for the affected paths. Shipping on a green review that never saw your
change is worse than halting.
**Note:** two reviews modelled "two developers" as the concurrency threat and missed the one that happens
on day one — *one* developer who doesn't always use the front door.

## DEC-90 — Single-operator by design, stated as a constraint

**Chose:** record it (§15.1) rather than leave it implicit. Every "single writer" guarantee means one
agent in one session on one machine; two terminals means two orchestrators writing `STATE.md`,
`feature.yaml`, `logs/` and committed Expertise files, with no lock anywhere.
**Because:** an unstated assumption is a latent bug; a stated one is a scope boundary.

## DEC-91 — The value claim is restated as "without mid-stage supervision"

**Chose:** "Claude executes reliably at each stage **without mid-stage supervision**."
**Over:** "without constant supervision."
**Because:** with 4–8 blocking touchpoints per feature, the original claim is false as written. What the
design delivers is supervision **batched at decision boundaries** rather than removed — a real
improvement over continuous oversight, and not the same as its absence. All three reviews flagged the
overclaim independently.

## DEC-92 — Pilot the org before building it; no agent files until the numbers exist

**Chose:** build the four surviving artifacts as plain skills, run 2–3 real features through them and
through a mocked org slice, measure spawns / tokens / dollars / wall-clock / touchpoints / **defects
escaped to merge**, and only then decide whether the 15-agent org exists.
**Over:** (a) building the org and fixing the review findings against it; (b) deleting the org outright
on the strength of the cost argument.
**Because:** the reviews split precisely because nobody had the numbers. The measured facts are
uncomfortable — every spawn loads ~19KB of CLAUDE.md hierarchy before doing any work, a feature costs
19–45 largely-serialized spawns, and **the only "budgets" in the entire design are retry counters** — but
the conclusion drawn from them (~$15–250 and 1.5–4h per feature versus ~$2–10 and 20–60min for a plain
session) rests on guessed defect rates its own author marked ±2×. Deleting a design on a ±2× estimate is
as unsound as building it on none.
**The deciding column is defects escaped to merge.** The cheap arm is certain to be cheaper; the org
earns itself only if it catches something the cheap arm ships broken.
**Tradeoff accepted:** the org may be deleted after this, making some of §3, §5 and §10 dead text. That
is the cheaper mistake — the alternative is 15 agent definitions written against an unpriced premise.
Fixes that depend on the outcome are listed as deferred in BUILD.md rather than applied now.

## DEC-93 — The pilot's A/B defect comparison is withdrawn as underpowered — CORRECTS DEC-92

**Chose:** two instruments — run 2–3 features through the org arm to settle cost, touchpoints and
whether the artifacts fire; mine `kaya-ai`'s history for the base defect rate and cost per incident.
**Over:** DEC-92's design, which ran the same features through a null-hypothesis arm and an org arm and
treated **defects escaped to merge** as the deciding column.
**Because:** two compounding problems, the second fatal.
1. **Sequential runs contaminate.** Building a feature one way teaches you where its problems are, so
   whichever arm runs second looks artificially good — destroying the very column the design named as
   deciding. Parallel isolated worktrees fix this.
2. **Parallel runs fix contamination but not statistical power.** The defect column rests on an assumed
   ~20% base rate. At that rate **three features yield an expected 0.6 defects** in the cheap arm; zero,
   one and noise are indistinguishable. Distinguishing a 20% rate from a 5% rate needs dozens of
   features. So the rigorous protocol costs double operator involvement to buy rigor on a metric that
   remains meaningless at the available sample size.
**Consequence:** the base rate is a **history** question, not a pilot question — and it is already
recorded in the repo (reverts, hotfixes, late bug discoveries), which is both cheaper and far
better-powered than three fresh features.
**Also:** **cost alone can decide this.** If a feature costs > $50 or > 2h of machine time, the org is
dead for someone shipping several a day regardless of what it catches — no defect data required.
**SC-5 is retained but explicitly labelled underpowered and inadmissible as evidence.** Recording that
in advance is what prevents a single lucky catch being read as confirmation afterward.
**Process note:** this is the third protocol error caught by stepping back rather than by review — the
question "why is a pilot needed, and what would it prove?" invalidated a design that had already been
approved. Cheap to ask; expensive to skip.

## DEC-94 — Pilot host is `kaya-ai`; no Playwright constrains what it can test

**Chose:** `kaya-ai` as the pilot host.
**Over:** `implentio-app` (the actual product, but untouched since 2025-12, so re-familiarization would
pollute the wall-clock numbers), the harness repo itself (markdown "features", no test suite, no UI — the
qa gate, prototype gate and UAT path would all be inert), and a scratch repo (synthetic features give an
unrealistic defect rate).
**Because:** it is actively committed, has a real and executable test suite, and its live Astryx UI work
exercises the prototype and UAT paths.
**Measured setup:** `uv run pytest` (testpaths `tests/`), `pnpm -C web test` (vitest `unit` project),
`pnpm -C web test:stories` (storybook project). **No Playwright.**
**Constraint to state honestly:** the `ui` test kind has no runner here, so it soft-skips per DEC-36 —
which means **the UAT is the only user-facing verification the pilot can exercise.** The pilot therefore
cannot claim to have tested the browser-automation path.

## DEC-95 — A git worktree is the unit of concurrency — CORRECTS DEC-88

**Chose:** one feature **per worktree**, as many worktrees as you like. `.harness/` is per-worktree
state, not per-repository state.
**Over:** DEC-88's "one feature in flight at a time."
**Because:** **the pilot host already disproves DEC-88.** `kaya-ai` runs three concurrent
`git worktree`s on three feature branches (`feat/26-persistence-schema-design`,
`feat/121-spec-family-followup`, `feat/277-acceptance-transcript`) under `.claude/worktrees/`. That is how
its operator actually works, so a constraint forbidding it would have been violated on day one — the same
class of error as assuming all repo mutations flow through agents (DEC-89).

A worktree has its own working tree and therefore its own `.harness/`, which dissolves the objection
DEC-88 rested on: `STATE.md ## Current` being singular is *correct within a worktree* (one feature, one
in-flight run), features in separate checkouts are genuinely independent, and merge is ordinary git.

**Honest residue — what this does not solve:**
- **Committed Expertise files diverge and will conflict.** Two worktrees whose agents both learn produce
  competing edits to `.harness/expertise/<agent>.md`. Merging Expertise is unlike merging code: the right
  answer is usually the union, which no tool will choose for you.
- **The global Expertise tier is shared across all worktrees simultaneously** (`~/.harness/`), unlocked.
  Two concurrent sessions can both write it — which strengthens the case for the global tier being
  human-gated or deleted.
- **`logs/` diverge** per worktree, so the daily log stops being a single timeline. Harmless.

**Consequence:** a `BLOCKED` feature blocks *its worktree*; you may work another (§10.5). And worktree
isolation is evidently a proven pattern in this repo, which raises confidence in `isolation: worktree` as
the write-safety mechanism (DEC-85).
**Also:** `detect` globs and the dirty-tree whitelist must exclude `.claude/worktrees/**`, or a diff scan
double-counts every test file three times over.

## DEC-96 — SC-4 measured: base rate is 0.44 defects/feature, but the artifacts cover ~79% of them

**Measured** from `kaya-ai` history, 2026-07-04 → 2026-07-25 (470 commits). Method, kept here because
the standalone analysis file was later retired: **43 feature units** (22 `feat` squash-PRs on master +
21 `feat/*` merge-commit PRs — the repo merges both ways, so counting one style would have halved the
denominator) against **19 escaped-defect units** (`fix` PRs on master, 18 of 19 citing a filed issue),
with **0 reverts**. 19/43 = 0.44.

| | |
|---|---|
| Feature units shipped | **43** (22 squash-PRs + 21 merge-commit PRs) |
| Escaped-defect PRs | **19**, 18 citing a filed issue |
| **Base rate** | **0.44 defects per feature** |
| Cost per incident | **+111 lines** across 2–4 files; ~10% of feature line volume spent on rework |
| Reverts / hotfix branches / production incidents | **0** |

**Two findings that cut in opposite directions, which is why this had to be measured rather than
assumed:**

1. **The rate is more than double the reviewers' 20% assumption.** The CTO review's case against the org
   rested on that number; at 44% the expected loss from shipping ungated is roughly twice what was
   modelled. **This strengthens the case for gating.**
2. **But the four artifacts address ~79% of it.** Classifying each defect by the gate most likely to catch
   it: **code review 9, UAT 5, BRIEF/spec 1** = 15 of 19 reachable without an org. Only **3** need
   org-specific gates — one security defect (CSV formula injection in an export path, #283), one
   architecture coupling (#150), and one prompt defect (#245) that **neither arm can currently catch**
   because `kaya-ai` has eval helpers but no eval harness. **This weakens the case for the org
   specifically**, as distinct from gating in general.

**The reviewers' cost model was also wrong in the org's disfavour.** It priced an escaped defect at "a
rework day." The data shows ~111 lines and — decisively — **zero production incidents**: every defect was
caught by the operator or a filed issue, never by a customer. That is a substantially cheaper class of
failure than was modelled, so the overhead the org must justify is smaller than the CTO review assumed.

**Honest limits, recorded so this is not over-read:** the gate attribution is *inference, not evidence* —
real code review catches perhaps 30–60% of what it could, so applying that to the addressable 15 gives
~7–8 defects actually prevented, not 15. Cost per incident in hours is estimated; only the line counts
are measured. And 21 days on a young, fast-moving repo likely overstates the steady-state rate.

**Bearing on the decision:** the bar the org must clear is now a real number — roughly 1–2.7h/day of
rework, of which the artifacts plausibly prevent half to four-fifths, leaving a marginal contribution of
about 3 defects in 21 days. **SC-1's measured cost is still required** before the org call is made; this
only replaces the assumption it gets weighed against.

## DEC-97 — SC-3 partially settled: all four artifacts fire, and review caught what tests missed

**Throwaway dry run**, 2026-07-26, in a disposable scratch repo using a real `kaya-ai` spec
(`2026-07-17-25-per-transaction-citation-design.md`) as input and a seeded defect as ground truth. Not
`kaya-ai` itself — nothing was installed there.

**All four artifacts behaved as specified:**

| Artifact | Result |
|---|---|
| `harness-brief` | 3 REQ / 4 SC, every SC carrying `verify:`. **The REQ test worked** — it demoted "use `pdfplumber`" to a constraint, correctly identifying a library chosen on licensing grounds as a *decision*, not a requirement |
| `harness-qa-gate` | Correctly `FAIL`ed on a missing unit test (`change_type: logic` → requires `unit` → detect glob matched nothing), then `PASS`ed once a test existed, while reporting `coverage_gaps: [SC-02, SC-04]` |
| `harness-review` | **Halted on a dirty tree** (`package.json` outside the `.harness/**` whitelist), flagged the `[harness:human]` commit as unreviewed work in scope, and **caught the seeded defect** |
| `harness-uat` | Correctly **declined to invent a UAT** — the source spec makes the overlay UI an explicit non-goal, so there were no `verify: uat` criteria and a backend-only change cost no hand-test |

**The load-bearing result — the defect escaped tests and was caught by review.** A happy-path-only test
suite went green (2/2) against an implementation that returned a fabricated region on a *partial* token
match, violating SC-02 ("never a guessed region"). Review caught it on spec compliance with a concrete
failure scenario: `locateTransaction(['cash','-99.99'], …)` returned a region for a transaction that is
not on the line.

**This reproduces `kaya-ai` #92** (`dangling category_ref` **failing open**) — the same fail-open class,
caught the same way. It is direct evidence for `DEC-96`'s classification that **code review, not tests,
is the gate for the largest defect category (9 of 19)**, which had until now been my inference rather
than a measurement.

**A real gap found in `harness-qa-gate`'s own logic.** The skill specifies three states — satisfied /
missing / not-applicable — plus `BLOCKED` for an unresolvable command. **A fourth state exists and is
unhandled: the command resolves and runs, but is misconfigured.** `node --test src/` on Node 26 treats
`src` as a module rather than a directory and exits non-zero; at first glance this is indistinguishable
from a genuine test failure. A gate that reports "tests failed" when the truth is "your config is wrong"
sends the reader hunting in the wrong place. **Fix:** on a non-zero exit with zero tests *collected*,
report `BLOCKED — test command misconfigured`, not `FAIL`.

**What this does NOT settle.** SC-3 is only *partially* met: the run was executed inline with **no
subagent spawns**, so it measures the artifacts' logic and says **nothing about SC-1 (cost)** — the
number the org decision actually turns on. It also used a synthetic seeded defect rather than an
organically-introduced one, and a JS analogue of a Python feature. Cost still requires real features in
a real repo.

## DEC-98 — qa-gate's fourth state discriminates on FAILURE KIND, not test count

**Fixed** in `harness-qa-gate`: a kind resolves to `satisfied` / `missing` / `not applicable` /
**`misconfigured`**, and `misconfigured` returns `BLOCKED`, never `FAIL`.

**The first fix was wrong, and testing it caught that.** The obvious discriminator — "non-zero exit with
zero tests collected means the command is broken" — **does not work**, because some runners synthesize a
failing test out of a load error. Verified live: `node --test src/` on Node 26 reports

```
Error: Cannot find module '.../src'   code: 'MODULE_NOT_FOUND'
ℹ tests 1      ℹ pass 0      ℹ fail 1
```

`tests 1`, not `tests 0`. A count-based rule reads that as a genuine failure and sends the reader hunting
a bug that does not exist — the exact harm the fourth state was added to prevent.

**The working discriminator is the failure *kind*:** a load / import / collection / syntax error, or no
test files matched, means the configuration is broken (`BLOCKED`). A **named** test failing an assertion
means the code is broken (`FAIL`). Per-runner signatures are tabled in the skill.

Re-verified across three cases — misconfigured cmd → `BLOCKED`; correct cmd with broken code → `FAIL`;
correct cmd with working code → `satisfied`.

**Process note:** this is the second time in two days that a fix was wrong and only empirical
verification caught it (the first being the nesting-default correction, DEC-83). Both times the error
was a plausible-sounding heuristic adopted without testing it. The throwaway pilot repo earned its
keep here.

## DEC-99 — Cost moves to post-build monitoring; the pilot no longer gates the build — SUPERSEDES DEC-92

**Chose:** build the full agentic workflow, then take it through its paces in `kaya-ai` and monitor cost
in practice. Machine time, dollars **and** operator touchpoints all move from pre-build decision criteria
to observed metrics.
**Over:** DEC-92's gate — "no agent files until the org shape is settled with data."
**Because:** the operator's call. Cost is not a major factor at this stage, so measuring it before
building answers a question nobody is asking.

**Consequences, stated plainly because they are not all comfortable:**

1. **The CTO review's case against the org is now moot.** That argument was purely economic — "the
   insurance premium exceeds the expected loss." With cost off the critical path, the remaining case
   against the 15-agent org is complexity and the unresolved review findings, not price. **The org
   proceeds.**
2. **Instrumentation becomes mandatory, not optional.** You cannot monitor what you do not log. Cost
   logging was item 4 on the deferred list; as the post-build signal it is now a **build requirement**,
   and it must exist before the first real `kaya-ai` run rather than after.
3. **The entire deferred fix list comes back into scope** — `check-state.sh`, the DIGEST validator,
   expertise governance, touchpoint batching, the five lost GAPs. They were deferred *pending the org
   decision*; the decision is made, so they are now the work that makes the org function.
4. **The risk DEC-92 was hedging is accepted knowingly:** 15 agent definitions get written against a
   premise whose economics remain unmeasured. If the monitoring later shows the cost is intolerable,
   some of §3, §5 and §10 becomes dead text. That is now a conscious bet rather than an oversight.

**What the pilot work bought before being superseded** — worth recording, because it was not wasted:
SC-4 measured at **0.44 defects/feature** with the artifacts addressing ~79% (DEC-96); SC-3 partially met
with **review catching a fail-open defect a green suite missed** (DEC-97), converting DEC-96's inference
into an observation; and one real bug found and fixed in `harness-qa-gate` (DEC-98).

**Retained as monitored, not abandoned:** SC-1 (cost/feature) and SC-2 (blocking touchpoints, threshold
>2). They have no kill authority now, but they are the metrics the post-build review reports on — and
SC-2 is the one cost that cannot be absorbed by spending more.

## DEC-100 — All four platform unknowns resolved empirically
<!-- stale: "rules/handoff.md" -->

Probed 2026-07-26 with throwaway agents and hooks, since cleaned up. Three of four settled outright; the
fourth is settled in substance with one link resting on documentation.

### 1. `SubagentStart` DOES fire for nested spawns — RESOLVED, and it was the highest-risk unknown

A `settings.local.json` `SubagentStart` hook logging `agent_type` produced **four** entries when the main
session spawned one `general-purpose` agent which itself spawned three `Explore` agents:

```
SUBAGENT_START agent_type=general-purpose     <- top-level
SUBAGENT_START agent_type=Explore   x3        <- NESTED
```

**Expertise injection therefore reaches workers in hierarchical mode.** The failure this ruled out was
severe and silent: had it fired only at top level, the 9 workers would have started with no Expertise
while the 3 leads kept theirs, with nothing in any output to reveal it.

### 2. Nested skill directories are NOT discoverable — RESOLVED against the design

`skills.md` is explicit: a project skill is `.claude/skills/<skill-name>/SKILL.md` — **exactly one level**
under `.claude/skills/`. What the docs call "nested skills" are nested `.claude/skills/` *directories*
elsewhere in the tree (`apps/web/.claude/skills/deploy/` → the qualified name `apps/web:deploy`), which is
a different mechanism entirely.

**Consequence: the four artifacts as first built were undiscoverable.** They were at
`.claude/skills/harness/{brief,qa-gate,review,uat}/SKILL.md`, which is depth 2 and therefore not a skill
at all. **Fixed** — flattened to `.claude/skills/harness-<name>/SKILL.md`. This also settles the layout
question for task 6: **the seven rule skills must be flat**, `rules/<name>/SKILL.md` will not resolve.

*Note on a confounded first attempt:* the pre-existing `harness/{rules,personas,tdd}/SKILL.md` files were
initially read as evidence that nesting fails, since none appeared in the session's skill list. That
reasoning was unsound — **none of them has YAML frontmatter**, so they are invalid skills regardless of
depth. The docs settled it; the natural experiment could not have.

### 3. Parallel fan-out from inside a subagent WORKS — RESOLVED

A `general-purpose` subagent issued three `Agent` calls in a single turn and all three returned. So
nested spawning and parallel fan-out both work, and `validator-lead` can run its reviewer panel in
parallel. **DEC-40's concern is closed** — it was never architectural.

### 4. `PreToolUse` `exit 2` DOES block a subagent's Write — RESOLVED in substance

A probe agent attempted two writes under a `PreToolUse: Write|Edit` hook:

```
DENIED_PATH_RESULT:  BLOCKED
DENIED_PATH_ERROR:   PreToolUse:Write hook error: [...deny.sh]:
                     probe-deny: /tmp/probe-denied/blocked.txt is out of domain (exit 2)
ALLOWED_PATH_RESULT: SUCCEEDED
```

Selective path blocking works, `exit 2` blocks, and the stderr reason reaches the agent.

**Residual gap, stated honestly:** this used a `settings.json` hook, not an *agent-frontmatter* hook.
Agent definitions are **not live-reloaded** (see below), so the frontmatter variant could not be loaded
this session. The docs assert it directly — *"Define hooks directly in the subagent's markdown file…
these hooks only run while that specific subagent is active. All hook events are supported"* — and the
blocking mechanism is now proven, so only the declaration site is unconfirmed. **On the restart
checklist, not the risk register.**

### Two incidental findings worth more than the probe

**(a) Agent definitions are NOT live-reloaded; skills and settings hooks ARE.** Creating
`.claude/agents/probe-lead.md` mid-session produced `Agent type 'probe-lead' not found`, while an edited
`settings.local.json` hook fired immediately. Operational consequence for the harness: **adding or
editing an agent requires a session restart**, so `/harness-init` and `harness-deploy` must both say so,
and any workflow that writes an agent cannot then use it in the same session.

**(b) The domain-hook error message is not actionable — a real defect in `check-domain.sh`'s spec.**
Asked whether the block told it what to do differently, the probe answered:

> `ERROR_ACTIONABLE: NO` — *"out of domain" names the rejected path but never defines what the permitted
> domain is, so it gives no basis for choosing a valid alternative path.*

An agent that cannot tell what it *may* write will thrash or give up. **Fix:** `check-domain.sh` must
print the agent's permitted globs alongside the rejection, e.g.
`harness: harness-frontend-dev may not write X. Permitted: web/src/**, .harness/expertise/harness-frontend-dev.md`.
Folded into task 7.

## DEC-101 — Four bin/ scripts shipped and verified; two bugs found by testing them

Built together because they share conventions and a directory. All verified against real inputs, not
just written.

| Script | Purpose | Verified |
|---|---|---|
| `inject-expertise.sh` | `SubagentStart` hook — injects an agent's Expertise as `additionalContext` | Emits correct JSON for a harness agent; **emits nothing** for non-harness agents; always exits 0 so it can never block a spawn |
| `check-domain.sh` | `PreToolUse` guardrail — blocks out-of-domain writes with `exit 2` | 5/5 cases: in-domain allowed · out-of-domain blocked · own Expertise allowed (DEC-87) · shared path allowed **with a warning** · second agent's domain allowed |
| `check-state.sh` | Deterministic orchestrator-invariant checker, 9 invariants | Run against this repo: correctly found the two real gaps (no BRIEF, no settings.json), and the settings violation cleared once `settings.json` was written |
| `validate-digest.py` | Normative DIGEST schema validator | Catches `VERDICT: PASSED`, `severity_max: medium`, `matrix_ok: "mostly"`, `must-fix` vs `must_fix`, and `open_questions` as a count |

**Design choices worth recording:**

- **`check-domain.sh` fails OPEN when the manifest is missing**, loudly. Blocking every write in a project
  that has not run `/harness-init` would be worse than not enforcing. It also fails open on an unparseable
  payload — a hook that blocks on its own parse failure breaks every write the moment the payload shape
  changes.
- **`check-state.sh` exits 1, not 2.** It gates the *orchestrator*, not a tool call; the exit-2 rule
  applies only to `PreToolUse` hooks.
- **`validate-digest.py` refuses to pass an unknown persona.** Silently accepting an unrecognized agent's
  return would defeat the point.
- **Zero dependencies.** No YAML library — the manifest reader is a narrow line scanner, because these must
  run on any machine without an install step.

### Two bugs found by testing, not by writing

**1. The validator was blind to the exact defect class it exists to catch.** Its key regex was
`[a-z_][a-z0-9_]*`, which **excludes hyphens** — so a drifted key like `must-fix` was never parsed into the
seen-keys map, and the drift check never saw it. `must-fix: [thing]` returned `digest ok`. Fixed by adding
`-` to the character class. The irony is instructive: a contract validator with a silent blind spot is
exactly the failure mode it was built to prevent, and only running it revealed that.

**2. `check-domain.sh`'s first draft would have blocked my own edits.** The initial probe script denied
anything outside an allowlist, which under a `settings.json` hook applies to *every* agent including the
main session. Narrowed to an explicit deny-list before wiring it up. Lesson for the real deployment: a
domain hook belongs in **agent frontmatter**, never in `settings.json`, or it governs the orchestrator too.

**This is the third and fourth time in three days that a plausible fix was wrong and only empirical
verification caught it** (after the nesting default, DEC-83, and the qa-gate state discriminator, DEC-98).
The pattern is consistent enough to state as a rule: **in this project, a fix is not done when it is
written — it is done when it has been run against an input that would expose it.**

## DEC-102 — depth="2" is exactly the harness shape, and the platform enforces workers-as-leaves by WITHHOLDING the Agent tool

Probed 2026-07-26 with `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "2"` active in this repo.

**Depth counts layers BELOW the main conversation**, which maps onto the org exactly:

```
main session (orchestrator)   layer 0 — not counted
  └─ leads                    layer 1   ✓ can spawn
      └─ team members         layer 2   ✓ RUN, but cannot spawn
          └─ anything         layer 3   ✗ unreachable
```

**Verified: leads CAN delegate to individual team members.** `LAYER2_SPAWN: SUCCEEDED` in one probe, and
three concurrent layer-2 spawns in another (DEC-100). Delegation to specialists is not impaired.

**The enforcement mechanism is tool absence, not a runtime error.** A `general-purpose` agent at layer 2 —
an agent type that advertises `Tools: *` at top level — reported:

> `AGENT_TOOL: NO` … *"`ToolSearch` with `select:Agent` returned literally: `No matching deferred tools
> found`"* … *"this is tool **absence**, not a **refusal** — no error or refusal text was ever produced,
> because there was no callable tool to invoke."*

`Agent` is stripped from both the loaded list **and** the deferred pool at the depth limit. Three
consequences:

1. **"Workers are always leaves" is enforced by the platform**, not merely by our agent definitions. A
   worker cannot delegate even if someone later grants it `Agent` in frontmatter — the depth filter
   overrides the top-level tool grant.
2. **The failure mode is benign.** A worker that tries to delegate finds no tool and does the work itself,
   rather than erroring or halting a crew.
3. **Our belt-and-suspenders (omit `Agent` from worker `tools:`) is now redundant — keep it anyway.** It
   documents intent in the agent file, and it is the only protection if the depth setting is ever lost
   (which `check-state.sh` INV-9 now also guards).

**Evidence that the `env` setting is live mid-session:** at the default depth of 3, a layer-2 agent should
retain `Agent` and be able to reach layer 3. It did not have it. That is only consistent with depth=2
being in force — so the `settings.json` `env` block takes effect without a restart, unlike agent
definitions (DEC-100a).

**One confound resolved along the way.** A first probe used `Explore` at layer 2 and saw no `Agent` tool —
but `Explore` is *defined* as "All tools except Agent", so that result was uninformative about depth. The
probe agent flagged this itself, and the re-test with `general-purpose` (which does carry `Agent` at top
level) is what made the finding sound. Worth noting as a method point: the confound was caught by the
subagent, not by me.

## DEC-103 — The propagation defect recurred, and the fix was a sweep not a habit

**Audit finding, 2026-07-26.** After 12 decisions were recorded (DEC-91…DEC-102), a check of SPEC and
BUILD found **ten stale statements** that those decisions had already invalidated:

| Stale claim | Contradicted by |
|---|---|
| 6× rule skills at `rules/<name>/SKILL.md` | DEC-100 — nested skill dirs are not discoverable |
| "scoped lead `Write` depends on spike 0a" | DEC-101 — verified, script shipped |
| "what remains for spike 0a is confirming…" | DEC-101 |
| "hosting model pending spike 0b" | DEC-100/102 — hierarchical verified |
| "parallel fan-out is the one unproven narrow case" | DEC-100 — verified, 3 concurrent spawns |
| BUILD Step 0 titled "one remaining spike" | all four resolved |

**This is precisely the defect the SPEC/DECISIONS/BUILD split was created to prevent** — the source plan's
own diagnosis was *"a decision lands in one section and never propagates."* The split did not prevent it.

**Why it recurred, honestly:** appending to DECISIONS is cheap and satisfying; re-reading SPEC is not.
SPEC is now **1831 lines**, four times the ~450 I originally targeted and well past what anyone re-reads
after each change. The mechanism the split relied on — *"short enough to re-read entirely"* — was never
actually achieved, so the propagation discipline had no support.

**All ten are now fixed**, and SPEC gained the depth-semantics diagram it lacked entirely. Verified clean:
0 stale skill paths, 0 unresolved spike markers, 0 dangling `DEC-NN` refs, 0 dangling `§N` refs.

**The durable fix is mechanical, not behavioral.** Relying on remembering to re-read a 1831-line file has
now failed once; it will fail again. Two options, neither yet chosen:
- **A propagation check in `check-state.sh`** — grep SPEC/BUILD for phrases that superseded DECs
  invalidate (`pending spike`, a superseded path form) and fail the state check. Cheap, catches the
  literal-string class of staleness, misses the semantic class.
- **Split SPEC further** — move the normative payload (manifest, roster, DIGEST schemas, test matrix,
  `feature.yaml`/`state.yaml`, crew YAML — ~300 lines that cannot shrink) into a `SCHEMAS.md` appendix,
  leaving a genuinely re-readable spec. Addresses the root cause rather than the symptom.

Recorded as an open item rather than silently deferred: **the split's central property is currently
unmet, and that is a live defect, not a stylistic preference.**

## DEC-104 — Propagation is enforced by a checker whose registry is DECISIONS itself

**Chose:** `bin/check-docs.sh`, wired into `check-state.sh` as INV-10. A decision that supersedes
something declares the stale wording inline, in the same paragraph as the reasoning:

```
## DEC-83 — Nesting default is 3, not off
<!-- stale: "pending spike" -->
<!-- stale: "nesting is off by default" -->
```

The checker reads those markers out of DECISIONS.md and greps SPEC/BUILD for them, naming the DEC that
invalidated each hit. **There is no separate registry to drift** — which matters, because a stale-claim
registry going stale would be the same defect one level up.

**Over:** (a) remembering to re-read SPEC — that has now failed once (DEC-103) and would again;
(b) a standalone list of forbidden phrases, which drifts;
(c) splitting SPEC to make it re-readable — see below, it does not work.

**Verified against real history and one injected regression.** Declaring 12 markers on 6 superseding
decisions surfaced 4 hits, **all of them false positives** — and the false positives were the useful part:
the migration map legitimately quotes old wording in its «change *"old"* → new» rows, and §7 legitimately
*describes* the mechanism it retired. Fixed with an **explicit** `<!-- ok-stale -->` escape rather than a
heuristic, because a heuristic that guesses which quotes are intentional will be wrong in both directions.
Re-injecting `pending spike 0b` was then caught and correctly attributed to DEC-83.

### The size fix does NOT work — recorded so it is not attempted again

DEC-103 offered "split the normative payload" as the root-cause fix. **Measured, it fails:**

| | Lines |
|---|---|
| SPEC.md today | **1853** |
| Normative payload extractable to a `SCHEMAS.md` (manifest 112, frontmatter 63, test_matrix 64, crew YAML 40, roster 31, `state.yaml` 27, DIGEST 23, `feature.yaml` 18) | −378 |
| Correction narration that belongs in DECISIONS (8 sites: *"An earlier draft claimed…"*, *"that overstated it twice over"*) | ≈ −50 |
| Result | **≈ 1425 — still 3× the 450-line target** |

**The 450-line target was never achievable** for a system with 15 sections of genuine specification. The
split's founding premise — *"short enough to re-read entirely after each change"* — was wishful, and
building a discipline on it was the actual mistake. Extracting schemas remains defensible for
*navigability*, but it must not be sold as fixing propagation. **Mechanical enforcement is the fix;
document size is a comfort.**

**Residual honesty:** this catches the *literal-string* class of staleness only. A statement that
contradicts a decision in different words still passes. That class needs a reader, and no script will
substitute for one.

## DEC-105 — The per-spawn baseline is ~15.3k tokens; CLAUDE.md is 31% of it, the rules 11%

Measured 2026-07-26 with a spawn-by-spawn ledger, replacing the reviewers' estimates.

**One user-facing feature = 19 spawns on the happy path, ~34 realistic:**

| Segment | Spawns |
|---|---|
| `plan-feature` | product-lead (host) · pm · eng-lead (arch review) · visual-designer (+prototype) · ui-reviewer(A) |
| `ship-feature` eng | eng-lead (host) · 2 specialist devs |
| `ship-feature` validator | validator-lead (host) · qa · code ∥ security ∥ ui |
| `ship-feature` product | product-lead (host) · pm goal-check · documentor |
| CEO briefing | all 3 leads in parallel |
| **+ 2 fix cycles** | +10 (each spawns a fresh eng run *and* validator run) |
| **+ 2 question round-trips** | +4 · **+ curation** +1 |

**10 of the 34 are lead spawns — 29% of the cost is intermediation**, and `eng-lead` alone is spawned
4×. That is DEC-71's mandatory routing, priced.

**Per-spawn baseline, before any work happens:**

| Component | Tokens | Share |
|---|---|---|
| **CLAUDE.md hierarchy** (measured 5.4KB user + 13.9KB project) | ~4,829 | **31%** |
| system prompt + tool defs | ~3,000 | 19% |
| BRIEF + PLAN + STATE | ~3,000 | 19% |
| **universal rules** (`handoff` + `expertise`) | ~1,727 | **11%** |
| injected Expertise | ~1,500 | 9% |
| role rule · `team-config.yaml` | ~1,284 | 8% |
| **total** | **~15,340** | |

**≈ 522k tokens of baseline per feature**, of which the eight rule skills are ~59k and CLAUDE.md is
~164k — **nearly 3× more expensive than everything the harness added.**

**Consequence, folded into task 14:** trimming CLAUDE.md is a larger lever than any rule optimization.
The project file is 13.9KB, mostly GSD-era — the STACK.md framework analysis and comparison tables are
*reference* material that belongs in `docs/`, not in all 34 spawns. Target ~5KB, saving ~80k/feature.
Conventions, architecture notes and the developer profile stay; agents genuinely use those.

**Two cautions.** Cutting carries a real risk — an agent silently depending on removed context fails
invisibly — so the rewrite must state what moved and where. And these are *baseline* figures only:
each spawn then accumulates working context on top, which is where the reviewers' 1.5–4M/feature
estimate comes from. Only task 3's instrumentation will replace that with measurement.

## DEC-106 — Reviewers need scoped `Write` — resolves a contradiction between SPEC §4.1 and §2.3

**Found while building the roster.** §4.1 granted reviewers `Read, Glob, Grep (+Bash)` and no `Write`,
while §2.3 simultaneously listed them as writers of `notes/review-<persona>-<runid>.md`. **A reviewer
with no `Write` cannot produce its own artifact**, which the three-part return requires (§8).

**Chose:** grant reviewers `Write`, scoped by the domain hook to exactly two paths — their namespaced
report and their own Expertise file. **No `Edit` at all, and no source path in the domain.**
**Over:** returning findings inline in the DIGEST (violates "artifact is a path, never a payload"), or
having the lead write the reviewer's report (absurd — the lead has no `Bash` and did not do the review).
**Because:** it is the same shape already used for leads, whose `Write` is scoped to their run dir. The
guarantee that matters — *reviewers never mutate what they audit* — is now enforced **two ways**: no
`Edit`, and a domain containing no source path. Writing your own findings is not mutating the subject.

## DEC-107 — The 15 agents are built, and a glob bug in `check-domain.sh` is fixed

**Roster complete:** 3 leads + 9 doers + 3 reviewers, all validated mechanically.

| Tier | Agents | Tools | Skills |
|---|---|---|---|
| leads | product, eng, validator | Read Glob Grep **Agent** Write · **no Edit, no Bash** | +`zero-micro-management` |
| doers | pm · visual-designer · documentor · frontend · backend · ai · data · dev-ops · qa | Read Glob Grep Edit Write Bash | + role rule |
| reviewers | code · security · ui | Read Glob Grep Bash Write(2 paths) · **no Edit** | + role rule |

**Deleted:** `harness-ceo-reviewer` (the user is the CEO), `harness-eng-reviewer` (architecture review
moved into `eng-lead`), `harness-qa-reviewer` (`qa` is now a doer that writes tests).

**Validated by script, not by eye** — 15/15 pass: frontmatter name matches filename · description
present · **color is a valid named colour** (hex is invalid) · no `memory:` field anywhere (it would
auto-enable `Write`/`Edit` and break the lead and reviewer guarantees, DEC-65) · both universal rules
preloaded · every `skills:` entry resolves to a real skill dir · tier-correct tool grants · domain hook
present and naming itself · **an entry in `team-config.yaml`**.

### The bug: every lead was blocked from its own run dir

`check-domain.sh`'s `/**` handling did a literal `str.startswith` on the text before `/**`. That works
for `src/**` and fails silently for **any pattern with an earlier wildcard** — including
`features/*/runs/*-eng/**`, which is exactly the leads' domain. So all three leads were blocked from
the run bookkeeping that DEC-18 grants them `Write` for in the first place.

Fixed with a proper glob→regex translation where `**` crosses separators and `*` does not. Note
`fnmatch` cannot do this either — its `*` matches `/`, so `web/*/x` would wrongly match `web/a/b/x`.

**Verified with a 23-case regression matrix**, all passing, plus per-squad isolation (eng-lead blocked
from validator's run dir and vice versa) and per-reviewer isolation (code-reviewer blocked from
security-reviewer's report path).

**This is the fifth time in this project that a plausible implementation was wrong and only a test
found it.** The pattern is now reliable enough to plan around: write the test matrix *before* believing
the implementation.

### Model tiers

`model:` is omitted almost everywhere, which means `inherit` — the agent matches the session model. Only
`documentor` is pinned to `sonnet`, as the most mechanical role. Deliberately conservative: the measured
failure mode here is *fail-open bugs that pass their tests*, which is a capability failure, so
downgrading reviewers and devs to save tokens would trade away the thing the org exists to provide.
Revisit once task 3's instrumentation produces real cost data.

### Still required before any of these can run

**Agent definitions are not live-reloaded** (DEC-100a). A session must restart before any of the 15 is
spawnable, and the first post-restart run should confirm the one residual platform unknown: that a
`PreToolUse` hook declared in *agent frontmatter* fires. The `settings.json` variant is proven to block
with `exit 2`; the docs assert the frontmatter variant, and it is now declared on all 15.

## DEC-108 — Post-restart validation: Expertise injection WORKS, the domain hook DID NOT FIRE
<!-- stale: "Domain-enforcement hook — VERIFIED" -->
<!-- stale: "blocking works, and the stderr reason" -->

First run with all 15 agents spawnable. Three results, one of them bad.

### ✅ Expertise injection works, including the hook path

Planted `CANARY-7f3a9b` in `.harness/expertise/harness-backend-dev.md`, spawned that agent, and asked it
to search its own context:

> `CANARY_IN_CONTEXT: YES` — *"- P-01: CANARY-7f3a9b — this line exists only to prove Expertise
> injection fires."*

So `SubagentStart` → `inject-expertise.sh` → `additionalContext` works end to end for a **real harness
agent**, and `${CLAUDE_PROJECT_DIR}` **does** interpolate in `settings.json` hooks. DEC-64 confirmed in
production rather than by probe.

### ✅ Project agent definitions override global ones

`harness-code-reviewer` resolved to the **project** version, not the stale global: it reported `Write`
available (the old one had none), all three expected skills preloaded, first heading
`# Harness: Code Reviewer`, and no GSD in its role prompt.

### ❌ The agent-frontmatter domain hook did not fire

`harness-backend-dev` was asked to write `web/src/…` — a path the manifest assigns to
`harness-frontend-dev`. **The write succeeded with no error and no hook output.** An unconditional trace
placed as the first statement of `check-domain.sh` recorded **nothing**, so the script never executed.

The script itself is correct: invoked directly with the same payload it blocks with `exit 2` and prints
the permitted globs, and a 23-case matrix passes. The failure is in **delivery, not logic.**

**Two candidates remain, and they cannot be distinguished without a restart** (frontmatter is not
live-reloaded, DEC-100a):

1. `${CLAUDE_PROJECT_DIR}` does not interpolate in *agent frontmatter* — the command path would then be
   literal, the command not found, and a not-found exit is **non-zero but not 2**, which is a
   *non-blocking* error. The write proceeds silently. This fits the evidence exactly, including the
   absent trace.
2. Agent-frontmatter `PreToolUse` does not fire for spawned subagents at all — contradicting the docs,
   which state *"hooks only run while that specific subagent is active. All hook events are supported."*

**Action taken:** all 15 hooks switched to a **relative** command path
(`.claude/skills/harness/bin/check-domain.sh <agent>`), which needs no interpolation and matches the
documented example form. The trace is retained, so the next session's first spawn is decisive: trace
present → candidate 1 was the cause and it is fixed; trace still absent → candidate 2 is proven and
frontmatter hooks cannot be relied on.

### Why this does not sink the design

**DEC-85 already demoted this hook to a guardrail** and named **serialization** (SPEC §8.5) plus
`isolation: worktree` as the actual write-safety mechanism — because the `Bash` bypass makes the hook
non-load-bearing regardless of whether it fires. That call now looks less like caution and more like the
thing that saved the architecture: had the parallel-safety claim still rested on this hook, today's
result would have invalidated it.

**What is genuinely lost while the hook is down:** the cheap catch of an *accidental* out-of-domain
`Write`/`Edit`, and the actionable "here is what you may write instead" message. Both are conveniences.
The guarantee was never theirs to provide.

**Consequence for task 10:** the crew runner's `mutates_repo` serialization is now the *only* enforcement
of disjoint writes, which raises its priority from bookkeeping to safety-critical.

### Incidental: `Grep` and `Glob` are unavailable in this environment

Two agents independently reported `No such tool available: Grep` / `Glob`, with errors steering them to
Bash `grep`/`find`. **This is inherited, not a defect in the agent files** — the main session does not
have these tools either, and subagents inherit the main conversation's pool. The docs list both as
retained for background subagents, so this is environment-specific.

Left in the `tools:` lists deliberately: unresolved entries are dropped without error as long as
something resolves, so naming them costs nothing here and keeps the definitions portable to environments
that do have them.

## DEC-109 — Attempt 2 (relative path) also failed; and the propagation defect recurred a third time

**Second post-restart test, relative command path.** `harness-backend-dev` wrote into
`harness-frontend-dev`'s domain again: **succeeded, no error, no trace.** The script never executed.

| Attempt | Command form | Trace | Blocked |
|---|---|---|---|
| 1 | `${CLAUDE_PROJECT_DIR}/…/check-domain.sh <agent>` | absent | no |
| 2 | `.claude/skills/harness/bin/check-domain.sh <agent>` | absent | no |
| 3 | absolute path **+ a dependency-free existence probe** | *pending a restart* | — |

Attempt 2 **eliminates `${CLAUDE_PROJECT_DIR}` interpolation** as the cause. It does **not** eliminate
path resolution generally — a relative path only resolves if the hook's cwd is the project root, which is
unverified. Attempt 3 removes that variable and adds a probe that distinguishes *"hooks do not fire"* from
*"my command was wrong"*.

**The subagent diagnosed it correctly and unprompted**, flagging fail-open enforcement as a blocking
`open_question` and naming the relative-path commit as the suspect hypothesis while explicitly marking it
unverified. It also proposed a `G-02` Gotcha — *"do not treat the hook as the guard; self-police paths."*
Worth noting: it *proposed* the op rather than self-applying it, though DEC-67 gives doers that authority.
Whether that is caution or a gap in the `harness-expertise` wording is worth watching.

### The propagation defect recurred — a third time, and my own checker missed it

BUILD.md §0b still read **"Domain-enforcement hook — VERIFIED, script shipped"** and *"blocking works"*
after DEC-108 had recorded the opposite. `check-docs.sh` did not catch it **because I never declared a
`<!-- stale: -->` marker on DEC-108** — the checker enforces what it is told, and I recorded the finding
without registering the wording it invalidated.

**So the mechanism is sound and the discipline around it is not.** Two markers now declared, and the
lesson generalises: **writing a superseding decision is only half the work — declaring what it
invalidates is the other half**, and skipping the second half puts the claim right back into circulation.

This is the third recurrence (DEC-103, then the §0b claim, now caught only by reading). The honest
conclusion is that no amount of care substitutes for the marker being part of writing the DEC.

## DEC-110 — Agent-frontmatter `PreToolUse` does not fire; the domain hook moves to `settings.json` and WORKS
<!-- stale: in each agent's frontmatter -->
<!-- stale: "SCRIPT WORKS, DELIVERY DOES NOT" -->
<!-- stale: "Domain enforcement is currently fail-open" -->

**Settled after three attempts.** Agent-frontmatter `PreToolUse` hooks **do not fire for spawned
subagents** in this environment:

| Attempt | Command form | Existence probe | Real trace | Blocked |
|---|---|---|---|---|
| 1 | `${CLAUDE_PROJECT_DIR}/…` | — | absent | no |
| 2 | relative path | — | absent | no |
| 3 | **absolute path + a dependency-free `touch`-style probe** | **absent** | absent | no |

Attempt 3 is decisive: a hook whose entire command was an absolute-path script with no arguments and no
dependencies **also never ran**. That eliminates interpolation, cwd, path resolution, arguments and script
errors, leaving only one explanation. **This contradicts the documentation**, which states *"hooks only run
while that specific subagent is active. All hook events are supported."*

**Fix: register in `.claude/settings.json`, take identity from the payload.** Settings hooks demonstrably
fire (proven earlier by `SubagentStart`), and the hook payload carries **`agent_type`** when the caller is
a subagent — so one global registration serves all 15 agents and dispatches on identity.

**Verified live**, in a single probe: `harness-backend-dev` **blocked** from `web/src/**` with the full
permitted-paths message, and **allowed** into `src/**`.

Two properties this arrangement must preserve, both tested:

- **The orchestrator is never governed.** No `agent_type` means the main session, which legitimately
  writes everywhere → exit 0 immediately. Without this the harness could not maintain its own state, and
  a global `PreToolUse` hook would otherwise catch every write the orchestrator makes.
- **Non-harness agents pass through** — `Explore`, `general-purpose` and any other are unaffected.

The `hooks:` blocks are **stripped from all 15 agent files** as proven-dead weight, and the frontmatter
remains valid (checked: 15/15 retain `name`, `description`, `tools`, and none references `check-domain`).

### A second bug, found on the way and arguably worse

The script derived the project root from `pwd`, so **it failed open whenever it ran from any directory
other than the project root** — printing nothing and exiting 0, silently disabling enforcement. Since a
hook's working directory is not guaranteed, this could have made the hook a no-op even once it fired.
Root is now derived from the script's own location (`<root>/.claude/skills/harness/bin/`), making it
cwd-independent. Verified blocking correctly when invoked from `/tmp`.

**Note the failure shape:** the bug's effect was to *permit* rather than to error. That is the same
fail-open pattern the reviewers, the rules, and now this hook have all been written to hunt — and it
appeared in the enforcement mechanism itself.

### What is still true

`Bash` remains unguarded and all 9 doers hold it. **Serialization plus `isolation: worktree` is still the
write-safety mechanism (DEC-85); this hook is a guardrail.** What has been recovered is the cheap catch of
an *accidental* out-of-domain `Write`/`Edit` and the actionable rejection message — real value, but not the
guarantee. Task 10's `mutates_repo` serialization stays safety-critical.

## DEC-111 — `/harness-init` must write THREE settings entries; the third was missing from its spec

**Caught by the question "does `settings.json` get updated on init with the agent hooks?"** — and the
answer was **no**. BUILD.md §0a's init template listed `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` and
`SubagentStart`, but **not the `PreToolUse` domain hook**, which DEC-110 had just made load-bearing.

A project initialised from that template would have got Expertise injection and **no domain enforcement
at all**, with nothing to report it — fail-open and silent, the failure class this design exists to avoid.

**Two fixes, because documenting it is not enough:**

1. **The §0a template now shows all three**, with a note that `PreToolUse` carries no agent-name matcher
   deliberately — one global registration serves all 15 and the script dispatches on `agent_type`.
2. **`check-state.sh` INV-9 now verifies it**, so an omission is caught at every `/harness` entry rather
   than discovered when an agent writes somewhere it should not. Verified by deleting the entry and
   confirming the violation fires.

**Why this kept happening:** DEC-110 changed *where* the hook lives, and the init spec described *what
init writes*. Those are different documents, and the second did not follow the first — the propagation
defect again, in its fourth appearance (DEC-103, the §0b claim, DEC-109, now this). The pattern is
consistent enough to name: **a decision that relocates a mechanism must be followed to every place that
provisions it**, and the only reliable enforcement is a script that checks the provisioning.

### Also fixed: the propagation checker flagged all 1889 lines of SPEC

DEC-109's prose explains the marker syntax by naming it inline, outside a code fence. The checker
harvested that as an **empty pattern**, which matches every line. Now skips patterns under 4 characters.
Same lesson as DEC-104's fence fix, one level down: **a tool that reads its own documentation as
configuration needs to distinguish the two**, and both times the failure was discovered by running it
rather than by reading it.

---

## DEC-112 — `/harness-init` is built; and an agent that *declines* a write is not evidence the hook works

Task 12 delivered: the flat skill `.claude/skills/harness-init/SKILL.md`, eight distributed templates
under `.claude/skills/harness/templates/`, and three deterministic merge scripts in `bin/`.

### The BRIEF-approval contradiction, resolved against the checker

The task-12 spec said two incompatible things: artifact #4 said init **never marks the brief approved**,
while interview step 3 said the goal is signed before anything runs and the first Done-when required
`check-state.sh` to pass. <!-- stale: "never marks it approved" -->

Run against a fixture, `check-state.sh` exits **1** on a pending brief (`BRIEF.md is NOT approved — halt`)
and **0** on an approved one. So the two lines could not both hold, and the pending reading would have
shipped an onboarding step that leaves every project halted.

**Resolution: init never *self*-approves, but it does write the user's answer.** It asks with
`AskUserQuestion` and writes `## Approval` on an explicit yes. This is not a carve-out — `## Approval` is
**orchestrator-written by design** (SPEC §2.3), and pm is the tier forbidden from touching it precisely
because pm has no user channel. Init runs at the orchestrator tier and does. A deferred approval leaves
the brief pending and init says so plainly.

### Merging is a script, and the fixture found two real defects in it

`.claude/settings.json` and `.gitignore` are **merged by `merge-settings.py` / `merge-gitignore.sh`**,
never hand-edited. Target projects have their own hooks — kaya-ai has five — and a hand-merge into a file
you do not own is exactly where one of the three silent-failure entries goes missing. Both are idempotent
and both take `--check`. Hook presence is matched on **script basename**, not the literal command string,
so a project that registered the same hook via an absolute path is recognised rather than duplicated.

`upgrade-config.py` merges `harness.json` but only **reports** on `team-config.yaml`. Every script in
`bin/` runs with zero third-party dependencies, so there is no YAML library; putting the manifest's
`domain` globs behind a hand-rolled YAML *writer* would place the only write-scope guarantee in the
design behind a line-based regex. It prints the exact new entries and exits 1.

Running it against the fixture caught two defects that reading it did not:

1. `_template`, a template-only marker, was being merged into project state and then popped — so it was
   reported as added while not being added. Now explicitly excluded.
2. `_reason` was re-imposed on a `test_kinds` entry whose `cmd` dev-ops had since verified, pasting
   *"unset — dev-ops has not run detection yet"* next to a working command. **A key's absence can itself
   be the project's decision**, so preserve-on-conflict is not sufficient — some keys must also never be
   *added*.

### The finding worth carrying forward

The first attempt at Done-when #2 spawned `harness-backend-dev` in the fixture and asked it to write
out-of-domain. It **refused** — read the manifest, cited `web/src/**` as frontend-dev's, returned
`VERDICT: BLOCKED`. That reads exactly like a pass. It is not one: the agent never issued the Write, so
**the hook never executed**. Prose in the agent definition was doing the work, and the mechanism under
test produced zero evidence about itself.

Only a probe that forced the tool call proved it — `exit 2`, the full permitted-paths message reaching
the agent, and the file absent from disk afterwards. The in-domain half was confirmed separately.

This is the DEC-108/110 lesson one level up. There, a hook that did not fire looked like a hook that
found nothing to block. Here, an agent's own obedience masked whether the guardrail existed at all.
**A well-behaved agent and a working hook are indistinguishable from the outside — so a test of the hook
must defeat the agent's good behaviour, or it is testing the prose.** The same trap applies to every
remaining guardrail claim: serialization, the qa gate, and the dirty-tree halt.

The technique that finally settled it, after two more agents also self-blocked: **an unconditional trace
as the hook's first statement**, logging `agent_type` from the payload. It answers "did this run at all"
without depending on any agent cooperating — the same instrument DEC-110 used, and the only one that
distinguishes *blocked* from *never invoked*.

### Composing the steps found three things component testing could not

The skill's own workflow was then run headless against a second fixture (steps 1–5, both interview
rounds skipped).

1. **Hooks ARE live in the session that writes them.** Traced: a `harness-dev-ops` subagent spawned
   after a mid-session `merge-settings.py` had its out-of-domain write blocked, `FIRED
   agent=harness-dev-ops` in the log. So the skill's restart warning was **overstated** — it claimed the
   harness agents are not spawnable in-session, which its own steps 4 and 8 contradict by spawning
   three. The restart is only about **agent files written during that session** (DEC-100a); hooks and
   pre-existing agents work immediately. Corrected.
2. **A denied script must be a STOP, not a detour.** With the `bin/` scripts permission-blocked, the run
   hand-replicated the `.gitignore` half, silently skipped the `settings.json` half, and **carried on
   through step 5** — ending with a scaffolded `.harness/`, a seeded manifest, and no domain enforcement
   at all. The subsequent probe write succeeded. Everything looked finished. Step 1 is now an explicit
   hard gate with a `--check` that must pass before step 2, because *a half-installed init is worse than
   a refused one* and it does not announce itself.
3. **The fresh path could recreate the falsehood the upgrade path was just fixed for.** The template
   ships `_reason: "unset — dev-ops has not run detection yet"` on every kind, and nothing told dev-ops
   to delete it when filling a `cmd`. Now stated in both the skill and the template.

Two things worked exactly as designed and are worth recording as such: dev-ops **ran** the project's
`package.json` test script, found it was `echo "1 passing"`, and refused to write a stub as `unit.cmd`;
and step 5's seeding produced fully disjoint dev domains, dropping every glob whose directory did not
exist rather than pointing it somewhere plausible.

---

## DEC-113 — Deploy reconciles instead of copying; agents go global only

Task 13. `/harness-deploy` is rewritten as distribution-only, with the mechanical work in
`bin/deploy.sh` (dry run by default) and the command file reduced to plan → confirm → apply → report.

**The live risk it clears, measured before the rewrite:** `~/.claude/agents/` held five agents — three
of them (`ceo-reviewer`, `eng-reviewer`, `qa-reviewer`) **deleted from this design** and still spawnable
in every project on the machine, pointing at a `.planning/` root that no longer exists. None of the 15
current agents were there. `~/.claude/skills/harness/` was the **April layout** (`personas/`, `rules/`,
`tdd/`, `manifest.json`) — structurally unrelated to the present one. The old deploy was copy-only, so
nothing it ever did could have removed any of that.

### Three decisions, each a deviation worth naming

**1. Agents are distributed GLOBALLY ONLY.** SPEC §3.3 said "skills, agents, templates — to global +
enrolled projects"; §3.3 is now corrected. One copy in `~/.claude/agents/` is visible from every
project, so a per-project copy buys nothing and costs drift: a project holding a stale shadow silently
overrides the fixed agent, and prune cannot see it because prune only walks the sets it knows about.
Skills and templates still go both places — they are read by path, not resolved by name.

**2. Crew overrides live in `.harness/crews/`, not `.claude/skills/harness/crews/`.** Deploy replaces
skill dirs **wholesale**, because they are harness-owned end to end — which means an override placed
inside the tool tree is destroyed by the next routine push. The precedence rule BUILD asked for
("project-local overrides global") only holds if the override sits somewhere deploy never touches.
Recorded in both manifests as `paths.crew_overrides`; the runner (task 10) resolves it first.

**3. `agent_skills` cleanup is REPORTED, not performed.** BUILD's detail block asked deploy to strip
the inert block from enrolled projects' `config.json`. That is writing project state, which the
deploy/init split exists to forbid — and the same list says so two items earlier. The dry run now names
any project whose `agent_skills` points at paths the push removes and leaves it to the user. Second
instance of the DEC-112 shape: **one document holding two requirements that cannot both be satisfied**,
found only by trying to implement both.

### What the fixture caught that reading did not

A fake `HOME` mirroring the real stale global state, plus a live registered project.

1. **`set -u` plus `"${empty_array[@]}"` is an unbound-variable error on macOS's bash 3.2**, not an
   empty loop. It aborted a real `--apply` **after the skills were copied and before agents, registry
   or projects ran** — the half-applied state that is strictly worse than either end. Every
   possibly-empty array now uses `${ARR+"${ARR[@]}"}`.
2. **`printf ... | python3 - <<'PY'` silently discards the pipe.** The heredoc already occupies stdin,
   so the program read nothing and wrote `{"projects": []}` — an **emptied registry** while the
   per-project push visibly succeeded and printed `✓`. Two sources, one stdin, no error anywhere. Data
   now goes via argv.

Both are the DEC-112 lesson again: the output looked right, and only running it against real state
showed it was not. Neither would have been caught by reading the script.

### Safety properties, and why each exists

- **Dry run is the default**, and the wrapper must show the plan and get a yes before `--apply`. This
  reaches outside the repo, into the user's global config and other repositories.
- **A wholesale `replace` names what it deletes.** "~ harness (replace)" hid four April-era subtrees;
  the plan now lists every entry present in the destination and absent from the repo.
- **Every delete target is derived from the repo's own file names**, never from an argument, and is
  re-checked against `harness*` and its expected parent before `rm -rf`. The script refuses outright if
  the computed ship set is empty or contains no flat skill dirs — a push computed from an empty set
  would prune everything.
- **`~/.claude/agents/` is backed up** before any prune.
- **Dead registry entries are dropped**, not warned about forever. That is deploy's own state, not
  project state, and the pre-migration file survives as `.migrated`.

---

## DEC-114 — Cost instrumentation: we compute the dollars, because nothing that knows them can attribute them

Task 3. `cost_model` in the harness.json template, `bin/cost-report.py`, INV-11 in the state check,
and cost wired into `state.yaml` (§11.4), `feature.yaml` (§11.3), the crew schema (§12) and the CEO
briefing (§10.3).

### The build-vs-adopt question, answered by looking

Prompted by "is there an open source solution for this?", which was the right question to ask before
hand-rolling a cost model. Three candidates, checked rather than assumed:

| Source | Native dollars | Per-agent attribution | Infra | Retroactive |
|---|---|---|---|---|
| **Claude Code OTel** — `claude_code.cost.usage` (USD) | **yes** | **no** | needs a collector | no |
| **ccusage** (~4.8k stars, MIT, offline) | no — computes it | no (session/model/day) | npx + node | yes |
| **Transcript + our rate table** | no — computes it | **yes** (`agentType`, `spawnDepth`) | none | yes |

Two findings settled it.

**1. The transcripts carry no cost field.** A full key inventory of `usage` returns
`input_tokens`, `output_tokens`, `cache_creation{_input_tokens}`, `cache_read_input_tokens`,
`speed`, `inference_geo`, `service_tier`, `service_tier`, `iterations` — and nothing denominated in
money. So **ccusage is an estimator too**, computing from its own rate table exactly as we do. It is
not an oracle we are declining to use.

**2. OTel knows the dollars but cannot name the agent.** Its `agent.name` attribute documents that
*"Built-in agent names and agents from official-marketplace plugins appear verbatim. Other
user-defined agent names are replaced with `custom`."* All 15 harness agents are user-defined, so
every one collapses into a single `custom` bucket. `query_source` offers only `main` / `subagent` /
`auxiliary`.

**No option provides native dollars AND per-agent cost.** Per-agent is the axis DEC-99 asks us to
monitor, so computing from tokens is *forced* — the rate table is the price of the attribution, not
a shortcut around a better option. `--cross-check` runs `ccusage` when present and compares totals,
turning rate-table staleness from silent into detected; it is never a dependency (files-only rule).

### Three ways to get this wrong, all found by measuring

**Cache reads are the biggest volume and the smallest cost.** The five token classes differ by 20×
(read 0.1× base input, 5m write 1.25×, 1h write 2×, output 5×) and must never be summed. The
measured dev-ops spawn: 862,903 cache-read tokens, 88,414 write, 14,993 output, 79 input →
**$2.72** on `claude-fable-5`. Price the cache reads at base input and the same run reads as $11.35.

**The cache-write TTL split is nested.** `cache_creation_input_tokens` is the total of both TTLs;
the per-TTL breakdown is in `cache_creation.ephemeral_{5m,1h}_input_tokens`. A 1h write billed at
the 5m rate under-reports by 37%. Where the breakdown is absent we attribute to 5m and **say so** —
the total is then a declared floor, not a quiet guess.

**`speed` and `inference_geo` were nearly missed, and are a silent halving.** Both are recorded per
message. Fast mode bills Opus 5 at **$10/$50 instead of $5/$25**, and it is one `/fast` away in any
session; `inference_geo: "us"` applies 1.1× to every class. Keying spend on model alone would have
reported half the truth with nothing to indicate it. Tokens are now keyed by
`(model, speed, inference_geo)`, and an unrecognised combination — Haiku at fast speed, an unknown
geo, a model with no rate period covering the run date — is reported **UNPRICED with exit 1** rather
than priced at the standard rate. A cost gate that reports a confident wrong number is worse than
one that reports none.

### What the first real numbers say

Across the fixture's probe sessions: **$38.81, which is 78% of the $50/feature budget SC-1 uses as
its kill threshold** — for work that was not a feature at all, just onboarding probes.

More surprising: **the orchestrator's own context is ~80% of it** ($31.17 of $38.81), against $7.64
for all six subagent spawns combined. The design has been treating fan-out as the cost driver and
the thin orchestrator as cheap; on this sample the opposite holds, because the main session carries
a large cached context across every turn while subagents are short-lived. One sample from probe
traffic is not a feature run and must not be over-read — but it is a direct challenge to an
unexamined premise, and task 17 should measure it deliberately rather than assume either way.

**Budgets are bounded like cycles.** `max_cost_usd` sits beside `max_cycles` in the crew schema and
`feature.yaml`: one bounds retries, the other bounds spend, and a fix loop can stay under its cycle
cap while burning the feature budget. Exhausting either takes the same path — stop, `BLOCKED`,
escalate. `budgets.per_feature_usd` defaults to 50, because SC-1 *is* the criterion; inventing a
second number would have meant two thresholds disagreeing about the same thing.

**INV-11** makes the meter non-optional: a run with `status: complete` and no `cost:` block is a
violation, missing `cost_model.rates` is a violation, and rates unverified for over 90 days are a
warning. An unmetered run is indistinguishable from a free one.

---

## DEC-115 — GSD removal is repo-scoped; the global surface is a separate, gated task

Surfaced by a `PostToolUse:Bash` hook error — "Hook JSON output validation failed — (root): Invalid
input" — and the follow-up question of whether the offending hook could just be deleted "since we're
removing GSD anyway."

**It could not, and the premise needed correcting.** DEC-02's removal scope is *this repo* self-hosting
off GSD. All **19** items in the migration map are project-local; **zero** reference a global path, and
neither SPEC, BUILD nor DECISIONS mentions removing GSD from the machine. Meanwhile global GSD is very
much alive and serving the operator's other projects: 33 `gsd-*` agents, 282 files under
`~/.claude/get-shit-done/`, 8 hooks in global settings, the statusline, and 14 GSD-referencing lines in
the global CLAUDE.md. Removing GSD *here* implies nothing about any of that. Recorded as **task 19,
gated on task 17** — the sequencing gate that protects this repo ("never delete the running mechanism
before the replacement is proven") applies with more force globally, where the blast radius is every
project rather than one.

### The bug, and why the obvious fix was the wrong one

`gsd-context-monitor.js` v1.42.3 chose its output event name by guessing the harness from an
environment variable:

```js
hookEventName: process.env.GEMINI_API_KEY ? "AfterTool" : "PostToolUse",
```

With `GEMINI_API_KEY` set — as it was — the hook emitted `hookEventName: "AfterTool"` under Claude
Code, which is not a valid event, so the payload failed schema validation. Reproduced by running the
hook twice with only that variable differing.

**Deleting the script, as first proposed, would have made it worse:** the `settings.json` entry would
still have pointed at it, converting an occasional error on the *warning* path into a missing-command
failure on **every** `Bash|Edit|Write|MultiEdit|Agent|Task` call in every project. The fix was to
remove the settings entry and leave the file inert and restorable — `gsd-check-update.js` runs at every
SessionStart and may re-add the entry.

**And the failure was not cosmetic.** The rejected payload *was* the context warning, so the agent
never received it. A feature that appears to be running, is registered, executes without error, and
silently delivers nothing — the same fail-open class this design keeps encountering, this time in the
tooling around it rather than in it. The correct upstream fix is one line: the input payload already
carries `hook_event_name`, so `data.hook_event_name || "PostToolUse"` needs no guessing.

### Audit of the 8 remaining global hooks — the bug class is contained

Probed the way the context monitor was, plus a source read:

| Property | Finding |
|---|---|
| Harness-detection heuristic (`GEMINI_API_KEY`) | **only** in `gsd-context-monitor.js` — the one removed |
| Emit a `hookEventName` | 6 of 8 — all hardcode the value matching their registered event |
| Runtime probe (realistic payload) | 8 of 8: exit 0, no spurious stdout, no state mutation |
| Opt-in behind `hooks.community: true` | `validate-commit`, `phase-boundary`, `session-state` — inert in this repo, which sets only `context_warnings` |
| Reads `.planning/` by **relative** path | `validate-commit`, `phase-boundary`, `session-state` — cwd-dependent |

The cwd-dependence is the same defect fixed in `check-domain.sh` (§0b), where deriving root from `pwd`
silently disabled enforcement from any other directory. Here it fails *closed* — an opt-in hook that
cannot find its config stays off — so it is latent fragility, not an active bug. Worth knowing before
anyone copies the pattern.

**Two method notes, both mistakes made during this audit.** A hook that is silent on a happy-path
payload proves nothing: the context monitor was silent on its first probe too, and only confessed once
its threshold was forced — so "8 of 8 clean" means clean *on the paths exercised*, not healthy. And two
hypotheses were wrong before the source settled them: `GIT_CMD_LIB` looked like an unset dependency but
is set inline one line above, and a malformed `grep -cl` (mutually exclusive flags) reported every hook
as always-on until it was re-run. Both were caught by reading the file rather than trusting the probe.

---

## DEC-116 — The crew runner works; two spec defects found only by building it

MVP step 3: the flat runner at `.claude/skills/harness-crew/SKILL.md` plus one linear crew
(`crews/smoke.yaml`), proven end-to-end. Gating, loop-back, parallel fan-out and the other three v1
crews remain (task 10 continues).

### The hierarchy assumption is no longer an assumption

Everything downstream of SPEC §10.2 rests on a lead being able to *host* a DAG rather than merely
being spawnable. Confirmed from Claude Code's own spawn records — not from any agent's self-report:

```
depth 1  harness-product-lead       Host smoke crew run
depth 2  harness-pm                 Smoke crew step: write
depth 2  harness-visual-designer    Smoke crew step: read_back
```

The lead spawned both members itself. State passed by file path — step 2 echoed step 1's three lines
character-for-character, diffed independently — no step hit a domain block, and the lead wrote a
`state.yaml` with checkpoints, per-step verdicts and DIGESTs. This matters because the failure mode
is silent: a lead with no `Agent` tool does the work itself and returns something plausible, which is
why the probe crew ships and why it asserts on a verbatim echo rather than on a verdict.

### Defect 1 — as specified, no step could write its own output

§12 said step `outputs:` are "written to the step dir" in the run dir. But the run dir belongs to the
**lead** (`features/*/runs/*-<squad>/**`); no member has write access. Probed before building:
`harness-backend-dev` writing a step output into the eng run dir → `exit 2, BLOCKED`. **The first
dispatch of any crew would have been blocked by the domain hook.**

The fix required no domain changes, because the domains were already right: every member owns a
namespaced artifact path (`notes/research-*`, `notes/review-<persona>-*`, `notes/mockups/**`,
`tests/**`, `src/**`), and cross-writes between them are correctly blocked — verified both
directions. So **§12 was the anomaly, not team-config**: step outputs resolve to the *producing
agent's own domain*, and the run dir is lead-only bookkeeping. That also preserves disjointness under
parallel fan-out, which staging everything in one shared run dir would have quietly destroyed.

### Defect 2 — the host cannot meter the run it hosts

The runner's close-out told the host to run `cost-report.py`. The first real run returned
`cost: unavailable`: leads hold `Read, Glob, Grep, Agent` and **no `Bash`** (§3.4), so they cannot
invoke it — and INV-11, added one commit earlier, fires on every lead-hosted run as a result. Two
correct guards colliding, each fine alone.

Resolved by moving cost to the tier that can do it and already owns it: the lead sets
`cost: pending_orchestrator`, and the **orchestrator** runs the report after the lead returns, having
already owned the `feature.yaml` rollup (§11.3). Same root cause disposes of timestamps — no `Bash`
means no clock, so leads write monotonic ordering markers instead of inventing wall-clock times. The
checkpoint property never needed real time: "dispatched with no matching completion" is decidable
from presence alone.

### Also corrected: the runner's own path, fifth instance of the propagation defect

§12.1 placed the runner at `.claude/skills/harness/crew/SKILL.md` — the nested layout DEC-100 proved
undiscoverable, and the same stale path already corrected once for `harness-init` (DEC-112). It is
flat: `.claude/skills/harness-crew/`. Crew *data* stays at `harness/crews/*.yaml`, which is a data
directory found by path rather than by discovery, so nesting is fine there. The crew-precedence line
was likewise still pre-DEC-113 and now names `.harness/crews/` explicitly.

**A pattern worth naming: every defect in this entry was invisible to reading and obvious to
building.** The domain block, the missing `Bash`, and the undiscoverable path were all present in a
SPEC that had been reviewed repeatedly. The probe crew exists so the next platform shift is caught
the same way.

---

## DEC-117 — Gating and parallel fan-out both work; the loop was destroying its own evidence

Task 10 continues: concrete `on_fail` semantics in the runner, plus two crews — `gate-probe`
(mechanism) and `review-team` (the first real v1 crew). Remaining: `plan-feature`, `ship-feature`,
`debug`.

### Gating — converged in exactly one cycle

`gate-probe` is built so the producer's behaviour is a pure function of whether a review report was
injected: no report → omit the token → reviewer FAILs; report present → add it → PASS. A healthy
runner therefore takes exactly one cycle, and every other outcome names its own defect — 0 cycles
means the gate never checked, hitting `max_cycles` means `feed: [self]` is not arriving.

Ground truth from the spawn records:

```
depth 1  harness-validator-lead   Host gate-probe crew run
depth 2  harness-qa               gate-probe produce#1
depth 2  harness-code-reviewer    gate-probe gate#1          -> FAIL
depth 2  harness-qa               gate-probe produce#2 (loop-back)
depth 2  harness-code-reviewer    gate-probe gate#2          -> PASS
```

`cycles_used: 1`, per-step `cycles: 1`, `feed_path` recorded. The decisive evidence that
`feed: [self]` delivered the *report* rather than merely a path is in the artifact: the producer
quoted the reviewer's reason verbatim into the file, which it could only do by reading it.

### Parallel fan-out — verified by overlap, not by assertion

`review-team` dispatches three reviewers with no interdependencies. The lead reported "one turn";
the transcripts confirm it:

```
code-reviewer      start 03:35:59  end 03:37:48
security-reviewer  start 03:36:04  end 03:37:13
ui-reviewer        start 03:36:08  end 03:36:45
```

The last start precedes the first finish, so the windows genuinely overlap. This check matters
because **serial dispatch is invisible in the output** — the same three verdicts come back either
way, correct and three times slower, with nothing to flag it. The runner now says so explicitly:
serializing out of caution is the most expensive way to be wrong.

The panel also earned its keep on a planted diff: both reviewers found the fail-open `except` and
the token logged in plaintext, and they found two things that were *not* planted — zero real test
coverage behind a green suite, and a module tracing to no REQ. `ui-reviewer` self-scoped out in 37
seconds rather than manufacturing findings. The lead reconciled one severity up and another down
with stated reasons, and rerouted the traceability finding to an open question rather than dropping
it. Panel slice cost ≈ $16 against the crew's `max_cost_usd: 20`.

**The fan-in is not a step.** validator-lead synthesizes in its own consolidated DIGEST; adding a
fourth dispatched step to "synthesize" would be the lead paying a spawn to do its own job.

### The defect: a loop that overwrites the reason it looped

`gate` wrote to a fixed path, so the cycle-2 PASS note **overwrote the cycle-1 FAIL note**. The
record of why a cycle was spent was destroyed by the thing that resolved it, and survived only
incidentally because the producer had quoted it elsewhere.

That is worse than untidy. `cycles_used` bounds the loop (GAP-4/DEC-49) and the reviewer's report is
the evidence for each increment; without it a post-run audit sees a cycle was consumed and cannot
say why. Fixed by resolving `{{cycle}}` in the output paths of anything that re-runs, and by
correcting the §2.3 naming convention to `notes/review-<persona>-<runid>-c<cycle>.md`. The existing
domain globs already permit the suffix — verified before relying on it.

**Third consecutive increment where the defect was invisible to reading and obvious to running.**
The domain block (DEC-116), the lead's missing `Bash` (DEC-116), and now the overwritten report were
all present in a repeatedly-reviewed SPEC. The probe crews ship for that reason.

---

## DEC-118 — A crew is single-squad by construction; multi-squad lifecycles are orchestrator playbooks

Raised by a challenge to MVP step 3's `pm → backend-dev` crew under `lead: eng-lead`: the objection
was that cross-squad work should route lead-to-lead — `pm → product-lead → eng-lead → backend-dev`
— rather than one lead reaching into another squad. The instinct is right and the specific chain is
impossible, for the same reason.

**Depth is capped at 2 and enforced by tool withholding (DEC-102).** A lead spawned by a lead lands
at layer 2, where `Agent` is stripped, and its members would be at layer 3 — unreachable. Confirmed
across every crew run so far: leads only ever at depth 1, members only ever at depth 2. So a lead
cannot reach another squad directly *or* through a peer lead.

The correct route is through the orchestrator, the only tier that can dispatch a second lead:

```
orchestrator
  ├─ product-lead → pm            [run 1]  ─ consolidated DIGEST up
  └─ eng-lead     → backend-dev   [run 2]  ─ dispatched with run 1's artifact path
```

**The model was already correct in SPEC — in one place.** `ship-feature`'s catalog row states it
plainly: "Multi-squad, so the orchestrator sequences the squad segments and each lead runs its own.
No lead ever spawns outside its squad," each segment with its own lead-owned run dir. §14's hard
limit agrees. This decision does not invent the rule; it **propagates it to the two places that
contradicted it**, and states it in §12 where the runner will actually be read.

| Contradicted it | Fix |
|---|---|
| **MVP step 3** — `pm → backend-dev` under `lead: eng-lead` | Corrected in place. `pm` is Product; `eng-lead` leads Engineering. The step predates the three-squad org that **step 2 of the same list** creates |
| **`plan-feature`** — `product-lead` dispatching `eng-lead` and `ui-reviewer(A)` | Re-specified as three orchestrator-sequenced segments. `ui-reviewer` is validator-squad and `eng-lead` is a lead; neither is dispatchable by `product-lead` |

So of the four v1 "crews", **two are not crews**: `plan-feature` and `ship-feature` are orchestrator
playbooks composed of per-squad runs. `debug` and `review-team` are genuine single-squad crews. This
was worth settling before building the remaining three, which would otherwise have been built on a
shape the platform cannot execute.

**`smoke` is deleted.** It was defended as a "permanent shippable health-check crew" — a framing
that conflated a real need (BUILD's Step 0 asks for a re-runnable `harness-selftest`, because the
platform auto-updates and every mechanism fails open) with the wrong container (the crew catalog is
for product-work DAGs, and the filesystem is the registry, so a probe listed there is a non-crew
anyone might run against a feature). The hierarchy it proved is recorded in DEC-116 and re-exercised
by every crew run since; the crew definition itself earned nothing further.

---

## DEC-119 — "team" everywhere, one artifact type per tier, and the two counters get owners

Three terminology and ownership corrections, all from the same review. Earlier decisions keep the
word "crew" as historical record; every live surface now says **team**.

### crew → team

`harness-crew/` → `harness-team/`, `skills/harness/crews/` → `teams/`, `.harness/crews/` →
`.harness/teams/`, the `crew:` digest field → `team:`, and the prose in SPEC, BUILD, the templates,
the agents and the scripts. `review-team.yaml` → `review.yaml`, since "team review-team" was
redundant once the noun changed.

### One artifact type at every tier

`SYNTHESIS.md` is deleted. It appeared in §10.4 and `harness-product-lead.md` and it invented a
second document class for something that was already a digest — which is what made the model hard to
follow. The corrected model, in the operator's words:

> members send a **digest** to leads · leads **collate and assess** their team's digests, including
> sending work back, before reporting **their team's digest** up · the orchestrator assesses across
> teams, routes questions between leads, delegates another cycle, or escalates to a briefing

So the lead's output is a **digest of digests**, written to `<run_dir>/digest.md`. There is nothing
to validate but digests, at every tier — which resolves the naming inconsistency in the validator:
`validate-digest.py` was always right, the second noun was the error.

### The validator was built and never wired in

DEC-101 built `validate-digest.py` precisely because "normative is enforced by one LLM's opinion of
parseability". It was referenced in `harness-handoff` and **nowhere in the runner**, so every digest
across three live runs was accepted by a reader finding it reasonable — the exact enforcement the
validator exists to replace. Measured cost of that gap: the `review` run satisfied **5 of 11**
required §10.4 fields, missing `members:` (which is what preserves per-worker granularity under
hierarchy) and the artifact itself. It is now invoked in the runner's collect step, and a failure
takes the existing `BLOCKED (contract violation)` path.

### The two cycle counters get explicit owners

| Counter | Lives in | Owner |
|---|---|---|
| step `cycles` | run `state.yaml` | **lead** — writes it, reports it |
| `cycles_used` / `max_total_cycles` | `feature.yaml` | **orchestrator** — increments from the lead's report |

This ratifies the operator's ruling and matches file ownership that already existed. It also fixes a
bug introduced in DEC-117: the runner told the lead to "increment `cycles_used` on the *feature*" —
a file the domain hook **blocks** it from writing, verified. Third time the same shape has appeared
(cost in DEC-116, timestamps in DEC-116, cycles here): **an instruction that assumes a capability the
tier's tool and domain grants deny.** Worth a standing check when writing any agent-facing prose —
before telling a tier to do something, confirm its grants permit it.

---

## DEC-120 — The orchestrator becomes a spawned agent; the main session becomes the user channel
<!-- stale: the main session — not an agent -->
<!-- stale: orchestrator = the main session -->
<!-- stale: main-session orchestrator -->
<!-- stale: .harness/STATE.md -->
<!-- stale: One feature in flight at a time -->
<!-- stale: all 15 agents -->
<!-- stale: all 15 personas -->

**Supersedes DEC-102's conclusion** that `depth: 2` "is exactly the harness shape". The shape
changed.
<!-- stale: SPAWN_DEPTH": "2" -->
<!-- stale: SPAWN_DEPTH: "2" -->
<!-- stale: one nesting level -->
<!-- stale: workers are always leaves -->
<!-- stale: session, you are running it flat -->
<!-- stale: Single operator, single session -->

### Why

The operator wants **several flows in flight at once**, seeing only escalations, briefings and
questions that genuinely need a decision. That is impossible while the orchestrator *is* the main
session: one session, one conversation, one orchestrator, and its context is your entire chat —
which DEC-114 measured as the dominant cost line.

Making the orchestrator a spawned agent gives each flow a fresh bounded context and lets N run
concurrently. The accepted cost is an extra round-trip: an orchestrator cannot call
`AskUserQuestion`, so every approval, question and briefing bubbles to the main session, which asks
and re-delegates. That is the existing `open_questions` → ask → `resume_from` mechanism (§2.1),
applied one tier higher — not new machinery.

```
main session — thin. user channel, nothing else.        layer 0
  ├─ harness-orchestrator (FEAT-01)                     layer 1
  │    └─ lead ── members                               layers 2, 3
  └─ harness-orchestrator (FEAT-02)                     layer 1
       └─ lead ── members                               layers 2, 3
```

### What it forces

**Depth 2 → 3 — VERIFIED, not inferred.** Members land at layer 3, and the guarantee that "workers
are always leaves" has to survive the move. Depth semantics have already changed three times across
CLI bands, so this was probed rather than reasoned about: four chained probe agents, each granted
`Agent` in frontmatter and each asked to report whether the tool was actually present, run with
`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH: "3"` on CLI 2.1.220.

```
layer 1  Agent: YES  -> spawned layer 2
layer 2  Agent: YES  -> spawned layer 3
layer 3  Agent: NO   -> chain terminated; layer 4 never ran
```

Layer 3 reported searching its full tool inventory, including the deferred pool via `ToolSearch`,
and finding no spawn tool. So the platform still enforces leaf-ness by **withholding** rather than
erroring, one layer lower than before — exactly the shape the org needs: orchestrator and lead can
delegate, members cannot.

**What this did not test:** the probe used generic agents, not the real roster. It establishes the
platform's behaviour at cap 3, not that an `orchestrator → lead → member` chain of actual harness
agents works end to end. That is the next proving run, and it belongs with the first orchestrator.

**A spawned orchestrator is governed.** `check-domain.sh` exits 0 when the payload carries no
`agent_type`, on the reasoning that the main session "legitimately writes everywhere". Once the
orchestrator is `harness-orchestrator` it has an identity and needs a real domain —
`features/<FEAT>/**`, `logs/`, `notes/answers-*`. The carve-out still applies, but now it protects
the *main session*, which after this change writes almost nothing.

**`STATE.md` moves per-feature.** It is specified single-writer, and N orchestrators would give it N
writers. It becomes `.harness/features/<FEAT>/STATE.md`, owned by that feature's orchestrator, and
the project-level file is dropped. The trade the operator accepted: no single file answers "what is
happening right now" — the main session scans `features/*/STATE.md`, which is cheap because the
index is small. `feature.yaml` needs no change; one orchestrator per feature was already
single-writer.

### Entry — two doors, deliberately

Commands do not distribute (DEC-06), so both are skills.

| Door | Purpose |
|---|---|
| `/harness` | The general door. Bare = list in-flight flows and their pending questions. With a target and goal = spawn an orchestrator for it |
| `/harness-plan` · `/harness-ship` · `/harness-debug` | Verb doors. Each spawns an orchestrator preloaded with that lifecycle playbook |

Both exist because they answer different questions: the verb doors are unambiguous when you know
what you want, and `/harness` is where you go when you do not — or when you just want to know what
is running. This is also the **only** moment the main session learns its role: it has no
frontmatter, so nothing injects a playbook into it. Before this, that level was referenced six times
across SPEC and BUILD ("at every `/harness` entry") and defined nowhere — which is why all three
test runs had orchestration hand-written into the prompt.

### Not yet settled

Whether the multi-squad lifecycles (`plan-feature`, `ship-feature`, DEC-118) are playbooks the
orchestrator *reads*, or a DAG format it *executes* like a team. Deferred until one exists.

---

## DEC-121 — Every digest field is required; `[]` is how you say nothing
<!-- stale: expertise_updated -->

The validator built in DEC-101 skipped absent fields by design — *"presence is the persona's
business; shape is ours"*. Demonstrated against the real `review` run's lead digest, that meant it
caught **1 of 10** problems: the missing `artifact:`, and nothing else. `members:` — the field §10.4
calls *"what preserves `STATE.md` granularity under hierarchy"* — sailed through while the validator
printed "digest ok".

**Now every field is required.** Say nothing with an explicit `[]`, or `none` for a scalar that is
genuinely inapplicable (`branch`, `blocked_on`). Same digest now reports all ten.

The reasoning is that **absence is ambiguous and emptiness is not.** A missing `must_fix` could mean
the lead found nothing blocking or forgot to collate; `must_fix: []` asserts it looked. That
distinction matters most for `open_questions`, which is the mechanism carrying a question all the
way to the operator — silence there is indistinguishable from a dropped question.

Three corrections came with it:

- **The lead schema held 5 of §10.4's 10 fields.** `branch`, `escalations` and `sc_status` were
  absent from the validator entirely, so no amount of presence-checking would have found them.
  Completed.
- **`sc_status` is not a lead's field.** Spotted in review: everything else in the team digest is
  either universal or something the lead itself produces, while `sc_status` originates in **pm's**
  goal-check (§11.6) and merely rides up so the orchestrator can read "is this done" without opening
  member entries. It is now declared on pm at source and on the lead as a passthrough, `[]` in both
  when no goal-check ran.
- **§10.4 never listed `headline`**, yet the validator demanded it of every persona — the spec was
  looser than the thing enforcing it. Added.

`harness-handoff` said `files_touched` and `expertise_update` were "only if" fields, which directly
contradicted the rule; both now read `[]` if none. Note the tension this creates with §5's
*"most tasks teach nothing durable and should produce no update"* — that guidance is unchanged, and
the correct expression of it is now `expertise_update: []` rather than an omitted key.

**Still prose, not enforcement.** A validator nothing runs is a validator that does not exist — the
same trap DEC-119 recorded. The `SubagentStop` hook that makes it mandatory is the next step.

---

## DEC-122 — The digest contract is enforced by a `SubagentStop` hook, mandatory from day one

DEC-121 made every digest field required. That was still prose, and this repo has now learned the
same lesson three times: DEC-19 (prose guarding a safety claim is unenforceable), DEC-110 (domain
enforcement silently absent), DEC-101/119 (a validator built and never wired). `validate-digest.py`
now runs as a **`SubagentStop` hook** — the fourth mandatory `settings.json` prerequisite.

Verified against `code.claude.com/docs/en/hooks`: `SubagentStop` receives `last_assistant_message`
and `agent_type`, and **"exit 2 … prevents the subagent from stopping"**. So a malformed return is
rejected at source and the agent must fix it before it can finish — enforcement, not a request. It
covers all 16 agents including leads, which the runner prose never could, because leads have no
`Bash` to run a validator with.

**Advisory-first was considered and rejected.** An advisory validator is exactly the "looks
enforced, isn't" state that produced DEC-110 and DEC-119. Hedging on it was the wrong instinct.

### Proven live, not just wired

A `harness-qa` agent was instructed to return the single word `done` and to omit the VERDICT,
DIGEST and artifact entirely. It could not:

- the hook's rejection text appears **in the subagent's own transcript**, so stderr reached it as
  actionable feedback;
- it took **4 assistant turns** — attempt, rejection, correction;
- the final return was a complete, contract-satisfying digest, including a legitimate
  `VERDICT: BLOCKED` and a blocking `open_questions` entry explaining that no work had been supplied.

### Three deliberate pass-throughs

The hook is shared by every subagent in the project, so what it declines to govern matters as much
as what it blocks:

| Condition | Why |
|---|---|
| `agent_type` absent or not `harness-*` | `Explore`, `general-purpose` and the rest have no digest contract. Governing them would break every unrelated subagent |
| `stop_hook_active` | Set when we are already re-running after a stop hook blocked. Blocking again is an infinite loop with no operator escape |
| Our own failure — unreadable payload, unknown persona, exception | **Fail open, loudly on stderr.** `check-domain.sh` set this precedent: a hook that blocks on its own bug wedges every agent in every project the moment a payload shape changes. Blocking is for *their* contract violation, never ours |

That last row is a deliberate asymmetry. Everywhere else this design prefers failing closed; here,
the blast radius of our own bug is every subagent everywhere, and the failure is loud rather than
silent — which is the property that actually matters.

<!-- stale: three prerequisites -->
<!-- stale: ALL THREE entries -->
<!-- stale: three platform prerequisites -->

---

## DEC-123 — The lead verdict roll-up is computed, not trusted

SPEC 10.4 states the rule: the team verdict is the worst member verdict,
`BLOCKED > ESCALATE > FAIL > PASS`. `ESCALATE` outranks `FAIL` deliberately — a decision only the
user can make must not be masked by a failure the team could have fixed.

That was prose, with a validator sitting next to it that could check it and did not. Verified live
before fixing: a lead digest reporting `VERDICT: PASS` with a member at `verdict: FAIL` passed the
hook. It is the same shape as DEC-19, DEC-110 and DEC-119, and the most consequential digest error
available — **the orchestrator routes on `VERDICT` and never opens member entries** (SPEC 8), so a
masked `FAIL` ships.

`validate-digest.py` now computes the roll-up and rejects a return that reports better than its
worst member. Reporting **worse** stays legal: a lead may know something its members could not see.
Every member entry therefore needs its own `verdict:`; without one the roll-up is undecidable.

**This is the only part of collation that is arithmetic.** Dedupe across overlapping reviewers,
resolving contradictions, deciding what is blocking, and sending weak work back are judgement, stay
prose, and should not be mechanized.

### The format was unwritable, which is how this surfaced

Making the digest a hard gate (DEC-122) exposed that **both** normative templates — SPEC 10.4's and
the runner's — were rejected by the validator that enforces them. Five defects:

| | |
|---|---|
| `\s*` after the colon matched newlines | `members:` swallowed its own first block line and parsed as a string |
| Keys harvested at every depth | a `must_fix:` nested in one member entry satisfied the top-level roll-up — a false pass on the field the lead digest exists to carry |
| Inline `#` comments parsed as value text | and both templates annotate themselves, so agents copy the comments |
| SPEC packed `team`/`steps_run`/`cycles_used` on one line | not YAML; two required fields vanished silently |
| SPEC omitted `files_touched` | universal per SPEC 8, required of leads too |

Adds `bin/test-validate-digest.py`, 16 cases. Worth having because this validator can now block any
agent in any project: a false negative accepts a malformed digest, a false positive wedges a working
agent, and **both were live**. Neither was noticed because each was only ever exercised by the
example that happened to pass — the same reason DEC-112's false pass went unnoticed.

Both templates are now verified rather than read: extracted from the source files, placeholders
filled, run through the validator. Flipping SPEC's own example to `PASS` gets it blocked.

---

## DEC-124 — Lead collation is proven; the run disproved three things we believed

First time any lead has actually conducted a team: `validator-lead` ran the `review` panel against
a pinned SHA range of this repo's own validator work. **Collation works**, and it produced the thing
a lead exists for — a cross-cutting conclusion no single reviewer had. `code-reviewer` filed "`--hook`
has zero test coverage" as one of fifteen `low`s; the lead re-read the low tier, recognised it as the
**common cause** of the panel's blocking findings, and made it the headline.

Verified from Claude Code's spawn records and from disk, not from the lead's account:

| Claim | Result |
|---|---|
| Lead opens its own run dir, members cannot | ✅ `state.yaml` + `digest.md` in the run dir; all three member artifacts in `notes/` |
| Three members collected and assessed | ✅ merged, ranked, dismissals recorded with reasons |
| Roll-up correct | ✅ `FAIL` over `FAIL`/`PASS`/`PASS` |
| Return satisfies the contract | ✅ hook-enforced at source |
| A reviewer may honestly scope out | ✅ `ui-reviewer` returned PASS with zero findings |

### Three things the run disproved

**1. The lead's own report of its behaviour was false.** It stated "three reviewers dispatched in a
single message (one turn, parallel)". The spawn records show **three separate turns**, 16s and 8s
apart. This is DEC-112's lesson recurring: an agent's account of what it did is not evidence.

**2. But the runner's rationale for that rule is also wrong.** Measuring actual overlap, the three
reviewers ran **concurrently anyway** — last start 24s, first finish 143s — because Claude Code
backgrounds subagents. The runner says single-message dispatch is required "or they run one after
another and the fan-out is lost." That is false as stated. Single-message dispatch remains preferable
because it does not depend on backgrounding behaviour, but the stated reason has to be corrected
rather than repeated.

**3. `<run>/digest.md` is prose, not the contract block.** SPEC 10.4 says the artifact is "same shape
as this block". The lead wrote an excellent human-readable report instead. The **return** carried the
block and the hook checked it; the artifact was never validated by anything. Either SPEC or practice
must move — recorded as open.

### The panel found real defects in DEC-123's own code, all reproduced independently

DEC-123 claimed the roll-up is "computed, not trusted". True only for canonical input:

| Defect | Status |
|---|---|
| `severity_max: [high, low]` → `TypeError` → exit 1 → **only exit 2 blocks, so the gate is disabled** | reproduced; fail-open |
| Quoted `"verdict: PASS on retry"` earlier in a member entry wins the first-match regex | reproduced; masked FAIL ships |
| Multi-line inline `members: [` … `]` parses to `[]`, so the roll-up silently has nothing to check | reproduced |
| `members: []` with `steps_run: 3` — no cross-check | reproduced |
| **`--hook` mode has zero test coverage** — all 16 cases invoke CLI mode | confirmed; the common cause |

A 16/16-green suite that never exercises the only mandatory mode is the same shape as DEC-119.

### Q1 answered by evidence, not preference

The reviewer asked whether to take a real YAML dependency rather than keep hardening a hand-rolled
subset, flagging it as a constraint question. **`python3 -c "import yaml"` fails on this machine.** A
YAML dependency would break the harness on its own development host, so the files-only constraint is
load-bearing rather than stylistic. Harden the parser.
<!-- stale: This one is checked, not trusted -->
<!-- stale: or they run one after another and the fan-out is lost -->

---

## DEC-125 — Nobody was told to create the Expertise file, so nobody ever did

13 of 15 `.harness/expertise/<agent>.md` files did not exist. BUILD task 8 had recorded the symptom
— "`inject-expertise.sh` injects nothing on almost every spawn" — as an Expertise *governance* gap.
It is not. It is one missing sentence.

**The loop was closed:** the file is absent → the hook injects nothing and raises nothing (correct,
by design — a new agent legitimately has none) → the agent sees no Expertise block → the
`harness-expertise` rule only ever described how to **update** a file it opened by asserting "your
Expertise file is **already in your context**" → the agent has nothing to update and no instruction
to create → it does nothing → the file stays absent. Forever. Every agent behaved correctly at every
step.

The two files that existed came from agents improvising past the gap, which is why the failure was
invisible: it looked like adoption starting slowly rather than a mechanism that could never start.

### The diagnosis this replaces, and why that one was wrong

The first diagnosis was that leads have no writer: SPEC 5.3 routes lead and reviewer
`expertise_update` ops to "the orchestrator, which applies it verbatim — a scribe, not an editor",
and `harness-orchestrator` does not exist (task 14). Real, but **not the cause** — **8 of the 9
doers were also missing their file**, and doers hold `Write`, self-apply, and depend on no
orchestrator. A cause that cannot explain two thirds of the instances is not the cause. The simplest
explanation that covers all 13 is that nothing ever said "create it".

**Two genuine defects surfaced on the way and are recorded, not fixed here:**

1. **SPEC 5.3's capability table is factually false.** It splits on "3 leads + 3 reviewers (no
   `Write`/`Edit`)". All six hold `Write` — leads need it for `state.yaml` and `digest.md`,
   reviewers for their findings artifacts. What they lack is `Edit`. `team-config.yaml` already
   grants each `upsert: true` on its own Expertise file, so the manifest and the spec disagree, and
   the manifest is right.
2. **The scribe route therefore has no reason to exist** and points at an agent that does not.
   Leads and reviewers can write their own file, scoped by the domain hook to that one path.

### The fix

`harness-expertise` now says the absence of the block means *you are the first — create it*, gives
the skeleton, and states that with `Write` and no `Edit`, updating is read-modify-write from the
copy already in context. Writing the file from your new entry alone silently deletes every earlier
one, which is the obvious next failure and cheaper to prevent than to detect.

An earlier attempt at this made it worse: it correctly told agents the block may be absent and then
concluded "you have none — proceed without it and do not go looking for it", which states the
deadlock as policy.
<!-- stale: proceed without it and do not go looking for it -->
<!-- stale: Init creating the dir empty is per spec -->

### DEC-125 addendum — the first fix failed, and the reason is the interesting part

Adding "create it if absent" to the top of the rule **did not work.** Retested with `harness-qa`,
which had no Expertise file, a genuine durable lesson, and `.harness/expertise/harness-qa.md`
already granted in its `domain`. It emitted a well-formed `expertise_update` op and **wrote
nothing.**

The instruction to apply it was already there — *"if you hold `Write`, apply your own ops in
place"* — one clause, at the bottom, inside a paragraph about section caps. Above it sat a whole
section headed **"How to propose an update."** The agent did what the dominant framing said. It
proposed.

**Emitting the op feels like completing the task**, because the op is structured, visible, and lands
in the DIGEST where work gets reported. Nothing about that experience signals that the file is
untouched.

Fixed by restructuring rather than by adding more words: the section is now "How to record an
update — **TWO steps, not one**", opening with *the op in your DIGEST is a receipt, not a delivery
mechanism*, and a table stating who writes versus who only reports. Retested with `harness-dev-ops`
from a clean slate: file created with the right skeleton, two real entries with stable IDs, ops also
reported. Both steps.

The general lesson, which is not about Expertise: **a correct instruction placed under a heading that
frames the task differently will lose to the heading.** Burying the operative step at the end of a
section named for the other option is the same defect as prose guarding a safety claim (DEC-19) —
it reads as covered and is not.

### DEC-124 addendum — `digest.md` is prose; the return is the contract

Resolved by the user. SPEC 10.4 said the artifact was "same shape as this block"; the live lead wrote
a prose report instead, and the prose was the better artifact.

**Two readers, two forms.** The return is the machine channel — the orchestrator routes on
`VERDICT` + `DIGEST`, never opens the artifact (SPEC 8), and the `SubagentStop` hook validates the
return at source. `<run_dir>/digest.md` is what a human opens. Requiring the block in the file as
well would put every field in two places with nothing checking the second copy, which is the drift
this project keeps paying for.
<!-- stale: same shape as this block -->


---

## DEC-126 — Group templates centralize where a group has 2+ agents; singletons stay inline

The user's cut, after seeing the 4 dev `## Output` blocks were byte-identical copies: a group of
2+ agents sharing one digest schema shares one canonical template; a schema with exactly one agent
keeps its template inline, because a central file for one reader is pure indirection.

Applied:
- **devs (4, identical)** → new flat skill `harness-digest-dev`, added to the four `skills:` lists;
  agent files carry a pointer, not a copy.
- **leads (3)** → the canonical copy already existed: `harness-team` "Reporting up", preloaded on
  all three since the collation work. The inline blocks written earlier today duplicated it and are
  replaced with a pointer plus each lead's per-role extras (`needs_approval`; `severity_max` +
  `adequacy_notes`).
- **reviewers (3) stay inline, deliberately** — measured first: their blocks share only
  `severity_max/findings/must_fix`; the bulk is role-specific (code: `spec_violations`,
  `review_sha`, `human_commits_in_scope`; security: `threat_model`, `scope_reason`). Centralizing
  five shared lines while keeping large inline extras adds indirection without removing duplication.
- **singletons (pm, qa, visual-designer, documentor, dev-ops) stay inline** per the rule.

Delivery is `skills:` preload — full content at spawn, zero tool calls, proven by this morning's
probe — so the pointer costs nothing at runtime. The canonical dev template validates against the
dev schema; the lead template was already validated when harness-team was fixed.

---

## DEC-127 — The digest gate's own defects, found by a live review panel, are fixed — and enforcement's real shape is now written down

DEC-123 claimed the roll-up guard was "computed, not trusted." A review panel (DEC-124) proved that
true only for canonical input, and traced the common cause: `--hook` — the only mode DEC-122 makes
mandatory — had zero test coverage in a suite that reported 16/16 green. This is the fourth time this
project has learned that a green suite exercising the wrong surface is indistinguishable from no
suite (DEC-101, DEC-110, DEC-119, DEC-124's own re-statement of the shape).

### Fixed, following the panel's fix order exactly

1. **F1 — the roll-up guard, hardened, not rewritten.** Q1 was answered by DEC-124 before this task
   started: `python3 -c "import yaml"` fails on this repo's own host, so the files-only constraint
   (CLAUDE.md) is load-bearing, not stylistic. The parser was hardened instead of replaced with a
   real dependency:
   - Member-entry verdicts are looked up by **key** (`parse_member_entry` + `top_level_colon`), never
     matched as `verdict:` text anywhere in the entry — closes the quote-blind first-match repro,
     where a quoted headline containing the literal text `"verdict: PASS on retry"` won a bare regex
     search before the entry's real (failing) verdict was ever read.
   - `parse_digest` now follows an inline value's unclosed brackets/braces **across lines** instead
     of truncating at the first — closes the multi-line `members: [` repro, which used to silently
     parse to `[]` and made the roll-up guard's `isinstance(..., list)` gate pass over nothing.
   - `split_items` only opens a quote when it starts a token (the preceding character is a delimiter,
     bracket, or whitespace) — closes the unbalanced-apostrophe repro, where a mid-word `'` (e.g.
     `didn't`) used to open an unterminated quote and fuse the rest of the list into one entry.
   - New cross-check: `members: []` beside `steps_run > 0` is now a violation (SPEC 10.4: members is
     NOT optional) — closes the fourth repro, which had no check linking the two fields at all.
   - An inline value whose brackets never balance is a new sentinel (`_UNPARSED`), reported as a
     violation — never silently coerced to an empty list, which was the failure shape underneath
     three of the four repros.
2. **The fail-open crash.** `severity_max: [low, med]` (a list) against a set-typed schema field
   raised an uncaught `TypeError` inside `validate()`; in `--hook` mode that meant exit 1, and only
   exit 2 blocks (DEC-100/DEC-122) — so the digest shipped completely unvalidated with no signal.
   Guarded the membership test on `isinstance(val, list)` (reported as a real violation, not skipped),
   and wrapped `hook_mode()`'s `validate()` call in `try/except` that reports on stderr and returns
   0 — fail OPEN, LOUDLY, on our own bug, matching `check-domain.sh`'s precedent. This was already
   the direction check-domain.sh established for pass-throughs; it just wasn't applied to the one
   call that could actually raise.
3. **Hook-mode test coverage, landed with 1–2, not after.** `test-validate-digest.py` gained a
   `--hook` runner that asserts the **exact** exit code (2 reject / 1 crash / 0 pass are three
   different outcomes — asserting "nonzero == rejected" would let the fail-open crash masquerade as a
   correct rejection, reproducing the exact blind spot this task exists to close) and matches
   rejection text on **stderr** (hook mode writes there, not stdout). Nine hook cases cover all five
   repros plus the three deliberate pass-throughs (non-harness `agent_type`, `stop_hook_active`,
   empty `last_assistant_message`), each verified to fail against a saved pre-fix copy of the
   validator and pass against the fixed one.
4. **Docs corrected last**, after the fixes changed what is true:
   - `harness-team/SKILL.md` §e no longer claims "a member that returned to you at all has already
     been held to the schema: every field present" — false for every one of the panel's repros. It
     now names the three structural pass-throughs (non-harness `agent_type`, `stop_hook_active`, our
     own failure) as the boundary of what the hook actually checked, and says explicitly that a lead
     should not skip reading a return just because it survived the hook.
   - `SPEC.md` §8.3's "the agent must fix it before it can finish" is corrected to "exactly one
     rejection deep" — `stop_hook_active` means an agent that re-emits the identical malformed digest
     on its second stop is accepted. The platform caps this at one wasted turn, not an infinite loop,
     but the old wording claimed a guarantee the mechanism does not make.

### Also fixed (the panel's "fold into the next touch of the file" list)

F4 (`DIGEST:` with a trailing comment — SPEC's own template writes it that way), F5 (standard YAML
block-mapping member entries spanning lines — legal YAML, and SPEC 10.4's own `escalations` example
is written that way), F6 (absent `agent_type` is now loud on stderr, distinguishable from a present
non-harness value which stays silent), F7 (`headline` must be at the DIGEST block's own level, read
from the parsed map — not matched anywhere in the text at any depth), F12 (`str`-typed fields now
have a real type branch; a bare NULLABLE key with nothing under it no longer silently becomes `[]`
where DEC-121 requires the literal `none`), F13 (the `open_questions`-is-a-count check now reads the
parsed top-level value, not a whole-text regex that could false-positive on a nested field of the
same name), F11 (the enum near-miss test now asserts the actual hint text, not a substring that
happens to be vacuously present regardless of whether the hint exists), F14 (CLI mode no longer
crashes with `UnicodeEncodeError` under `LC_ALL=C` — stdout reconfigured to `backslashreplace`,
matching stderr), F15 (the drift-spelling check now iterates the full field set — schema plus
`UNIVERSAL` — not schema alone).

**F10 (duplicate `files_touched:` key in the harness-team template) is found, not fixed.** It still
passes because the hand-rolled parser is last-wins on a repeated key. Not on this task's fold-in
list, and the panel filed it non-blocking; left for the next touch, now backed by the template-
extraction test below that would need a positive assertion updated if it's ever fixed.

**The template-extraction test now exists.** DEC-123 claimed both normative templates were
"extracted from the source files, run through the validator" with no such test on disk. One now
reads SPEC §10.4 and harness-team "Reporting up" directly from their files, fills each `<placeholder>`
mechanically, and runs the result through the validator as a lead digest. Both pass.

### `harness-orchestrator` added to `SCHEMAS`/`ALIAS`, ahead of its own BUILD task

BUILD task 14 (writing `.claude/agents/harness-orchestrator.md`) is running in parallel with this
one. The schema here is the **reconciled** one from that work, not derived independently from SPEC
§10.3/§11.3 (SPEC defines a *briefing artifact* — `.harness/notes/ship-review-<FEAT>-<runid>.md` —
for the orchestrator, not a digest block, so there was nothing to derive without coordinating):

```
"orchestrator": {"feature": str,
                  "status": {"in_progress", "in_review", "shipped", "blocked", "awaiting_user"},
                  "runs": list, "cycles_used": int, "cost_usd": str, "briefing": str}
```

`briefing` is NULLABLE (`none` except when a briefing was written, in which case it is the path).
`cost_usd` is `str`, not numeric — it carries values like `"12.83"` from `cost-report.py` and
`"pending"` mid-run. These are exactly the fields the **main session** routes on when the
orchestrator returns: `status` decides relay-to-user vs. done, `runs`/`cycles_used`/`cost_usd` are
the budget accounting it logs, `briefing` is the path it presents. Everything else about a feature's
execution stays on disk in `feature.yaml` (§11.3), never in the digest.

**Consequence recorded, not silently accepted:** adding `harness-orchestrator` to `SCHEMAS` means the
hook starts governing an agent whose definition file does not exist on disk yet — BUILD task 14 must
land a `harness-orchestrator` that actually emits this shape, or every orchestrator digest is
rejected the moment task 14's agent starts returning.

### Evidence

`test-validate-digest.py`: 16 pre-existing CLI cases unchanged and green; 9 new CLI cases for the
fold-ins; 9 hook-mode cases (5 repros + 3 pass-throughs + F6); 2 template-extraction cases — 36 total,
all green. Every new case verified against a saved pre-fix copy of the validator
(`VALIDATE_DIGEST_BIN` env override): all fail there except the three pass-through cases, which were
never broken and are asserted unchanged. `check-docs.sh` exits 0 after the doc corrections above.

---

## DEC-128 — The orchestrator exists: agent, playbook, and three doors

Task 14's core, built while task 22 hardens the validator in a parallel worktree.

**`.claude/agents/harness-orchestrator.md`** — the sixteenth agent. Layer 1, one per in-flight
feature, `tools: [Read, Glob, Grep, Agent, Write, Bash]`. `Bash` because SPEC §11.3/INV-11 make it
the tier that runs `cost-report.py` — the leads cannot (DEC-116). It preloads the `harness` skill,
so the playbook arrives at spawn the same way the leads get `harness-team` (the DEC-126 mechanism,
proven by the preload probe).

**`.claude/skills/harness/SKILL.md`** — the GSD-era router stub (`.planning/`, `agent_skills`,
`<files_to_read>`, a lifecycle table owned by GSD) replaced by the orchestrator playbook: the §10.1
loop, the routing table for lead returns, both budgets with the exhaustion sequence, the question
round-trip's middle leg, and the §10.3 briefing procedure.

**Three doors, relay protocol central.** `/harness` carries the whole main-session protocol —
gate on `check-state.sh`, approvals, background spawn, the status-routed relay table, `logs/`
appends. `/harness-plan` and `/harness-ship` are thin: read `/harness`, apply a mission and a
terminus (one PLAN+prototype approval; the CEO briefing). Same 2+-agents-share-one-copy rule as
DEC-126. `/harness-debug` deliberately does not exist — debugging is on-demand, not a stage.

**The orchestrator digest schema** (`feature, status, runs, cycles_used, cost_usd, briefing` +
universals) was defined here and sent to the task-22 agent mid-run, so the validator and the agent
file land matching. `briefing` is nullable; `cost_usd` is a string because it carries "pending".

**Unproven, stated plainly:** no flow has run through these files yet. The round-trip's
orchestrator half and the doors' relay loop are specified, not demonstrated — proving them is what
task 17's kaya-ai run (and a smoke flow before it) is for. CLAUDE.md size (DEC-105) remains open
under task 14.

---

## DEC-129 — Feature docs live in the feature's folder; BRIEF states the Problem before the Goal

The first smoke flow wrote `.harness/BRIEF.md` and `.harness/PLAN.md` at the root — where a second
feature would overwrite them. The user's call: **a folder named for the feature holds generically
named files**, not derived filenames at the root. `BRIEF.md`, `PLAN.md` and `DESIGN.md` join
`STATE.md`/`feature.yaml` in `.harness/features/<FEAT>/` — one dir is one feature's whole world,
templates stay generic, and the namespace already existed (DEC-120). "Decisions" needs no file:
`D-NN` is PLAN's `## Decisions` section. `notes/` keeps its FEAT-in-filename convention because runs
prune while notes persist — and it is now **enforced by domain glob** (`research-FEAT-*.md`), since
the smoke's pm promptly wrote `research-verdict-shadowing.md` with no id.

Onboarding's signal moves accordingly: not "BRIEF.md exists" (a fresh project has zero features)
but `harness.json` + `team-config.yaml` exist. INV-1..5 are per-feature now, and INV-4/5 accept
both task formats after the smoke showed heading-style tasks made INV-4 silently vacuous — plus a
guard: T-NN ids present but none parsing is itself a violation, so a third format cannot re-open
the hole.

Also per the user: **`## Problem` precedes `## Goal` in every BRIEF.** What hurts, observed, before
what to build — a brief that cannot state the problem without naming the solution is a solution
looking for a problem, and the goal-check has nothing to anchor against.
<!-- stale: .harness/BRIEF.md -->
<!-- stale: .harness/PLAN.md -->
<!-- stale: .harness/DESIGN.md -->

---

## DEC-130 — Feature notes live in the feature's folder; the path is the id

DEC-129 stopped halfway: it moved BRIEF/PLAN/DESIGN into `features/<FEAT>/` but left feature notes
flat under `.harness/notes/` with the FEAT id encoded in filenames, enforced by glob. The user's
observation: centralize per feature. `features/<FEAT>/notes/` now holds research, reviews, qa
assessments, answers, ship-review, uat, mockups and prototypes. The filename convention and its
glob enforcement retire — **a directory cannot forget its feature id the way a filename did on
pm's first outing.** Retiring a feature is now one directory. `.harness/notes/` remains for
genuinely project-scoped artifacts (cross-feature research, docs sweeps), and pm keeps a
project-level research glob for that.

Also closed on the way: the template manifest never had qa's notes grant at all — live/template
drift caught by asserting every substitution rather than replacing blind (the DEC-129 sweep's own
failure, not repeated).
<!-- stale: .harness/notes/answers- -->
<!-- stale: .harness/notes/ship-review- -->
<!-- stale: .harness/notes/uat- -->

---

## DEC-131 — Interrupting a parent's spawn does not kill the child; INV-12 catches the orphaned work

Platform behaviour, observed live on the FEAT-02 rerun: the orchestrator's product-lead dispatch
returned `[Request interrupted by user for tool use]` — a permission prompt on the nested spawn —
and the orchestrator correctly returned `BLOCKED`, reporting `runs: []`, zero cost, exactly what it
saw. **But the child had already launched and ran on as an orphan**: product-lead → pm completed
BRIEF, PLAN and the research note minutes after the orchestrator died, and the lead's collation was
cut off mid-run (`state.yaml` `status: running`, no `digest.md` — checkpoint-before-dispatch made
the half-state provably in-flight, as designed).

Consequences, each recorded where it acts:

- **The work survives and the money is not wasted** — a resume reconciles rather than redoes.
- **Disk can hold a run no orchestrator records.** Nothing flagged the inverse of INV-8, so
  **INV-12** now warns on any run dir absent from `feature.yaml` — verified firing on the live
  debris before this entry was written.
- The rerun's actual targets all passed: pm produced the DEC-129/130 layout **first try, zero
  domain rejections** — instructed, not rejection-taught — with `## Problem` preceding `## Goal`.

---

## DEC-132 — Success criteria are authored by pm; the spawn prompt carries goal constraints, not SC text

The user noticed the FEAT-02 mission prompt handing pm finished SCs ("may refine wording, not
weaken"). Provenance: the main session wrote them at the door; the orchestrator relayed faithfully.
That reduces pm to a transcriber of criteria and forecloses the derivation — outcome plus `verify:`
method — that is the role's actual product work, checked by the user's signature (harness-brief).

The legitimate form of the same impulse: the CEO may mandate outcomes. Those enter the prompt as
**goal constraints** pm must honor while authoring SC-NN; wording, numbering and verify methods stay
pm's. Recorded at the door (`/harness` step 3), which is where the defect occurred. That pm added
SC-3 unprompted on the first run shows the authorship instinct survives even a bad prompt — the fix
is to stop suppressing it.

**Amended same day, per the user:** adding criteria beyond the user's is not merely permitted — it
is **expected**. The user states what done must include; pm's job includes what done also requires
that nobody said. SCs that merely restate the user's list are under-delivery, and the signature is
where the user prunes over-reach — the gate working, not a reason to hold back.

---

## DEC-133 — Feature ids carry a slug: `FEAT-NN-<kebab-slug>`

Per the user: `FEAT-01`, `FEAT-02` say nothing useful in a directory listing, a log line, or a
briefing. The id becomes `FEAT-NN-<kebab-slug>` (`FEAT-02-verdict-shadowing`) — the number stays
the stable join key, the slug carries the meaning. pm coins the slug at BRIEF time, 2–4 words from
the goal; **immutable once created**, since every recorded reference breaks on rename. No machinery
changes: globs are `features/*/…` and the team YAML's `{{feat}}` is opaque. The two pre-existing
bare-number dirs stay as history — FEAT-02's ship flow was live under that name when this landed.

---

## DEC-134 — Cost budget is informational; cycles stay hard. And every agent pins its model

Per the user, after the first live ship flow BLOCKED at ~$49 of a $40 budget with every gate green
and one $5 step remaining: **crossing `max_cost_usd` never stops work.** It is a visibility
threshold — actual-vs-budget rides every orchestrator return and every briefing, a crossing is
flagged in the headline, wild divergence (multiples, not percents) raises a non-blocking question.
The blocking version protected nothing and cost a goal-check. `max_total_cycles` **stays hard**:
runaway fix loops have no natural end, which is a different failure class than expensive-but-
converging work. (The user said "budget"; scoping it to the cost budget is the recorded reading.)

**Models pinned in frontmatter:** judgment tier — the 3 leads, pm, visual-designer, and the
orchestrator — `model: opus`; the other 10 members `model: sonnet`. The orchestrator was not in the
user's enumeration; grouping it with the judgment tier is the recorded assumption. Context: the
overrun's root cause was every agent inheriting the session's fable-tier model (~$20/lead-run);
pinning makes per-role cost a design property instead of an accident of who spawned the session.
<!-- stale: exhausting either ends the loop -->

---

## DEC-135 — CLAUDE.md cut 79%: the per-spawn tax was mostly a stale artifact

DEC-105 measured CLAUDE.md at ~164k tokens per feature — ~3.7k tokens read by every one of a
feature's ~44 spawns. Eleven of its fifteen kilobytes were the April 2026 GSD-era stack analysis:
not merely oversized but **false** since self-hosting — it described GSD as the backbone, tables of
`agent_skills` mechanics, a `<files_to_read>` convention, none of which exist. Every agent paid to
read a wrong history of the system it runs in.

Deleted outright — briefly archived, then the user asked whether the archive earned its keep and it
did not: git history holds every byte, and a file of stale GSD claims inside check-docs' scan
surface is a standing ok-stale tax, not a resource. CLAUDE.md is now ~0.8k tokens — Project (blurb corrected to the self-hosted reality; the
dead GSD-compatibility constraint marked retired), the Harness section, and two conventions this
session proved the hard way (verify prose claims; check-docs before commit). Per-feature CLAUDE.md
load drops from ~164k to ~35k tokens. Closes the last open item of task 14.

---

## DEC-136 — `.planning/` retired; the GSD dev state is triaged, not dropped (task 16)

The migration map's 19 items were almost all completed incidentally as the harness self-hosted —
rules became flat skills (DEC-63/100), the router became the orchestrator playbook (DEC-128),
CLAUDE.md was rewritten (DEC-135), the manifest/templates/init/deploy chain shipped (DEC-112/113).
What remained of task 16 was the one thing the self-hosting section warned about: retiring
`.planning/` **without silently losing its open items**. The triage, item by item:

| Open item in `.planning/` | Disposition |
|---|---|
| Todo: "architectural scoping gap in discuss-phase" | **Resolved by design.** The harness's plan flow embeds eng-lead architecture review as a segment — it ran twice in FEAT-02 and forced a real loop-back. The gap was a GSD-shape problem; the shape is gone |
| Blocker: "gstack persona prompt surgery needs research" | **Superseded.** Personas were copy-owned and rewritten as the 15 squad agents (DEC-106/107) |
| Blocker: "real project selection needed (500+ LOC, debugging scenario)" | **Tracked as task 17** — kaya-ai |
| Roadmap Phases 1–3 | Delivered as ledger tasks 6, 12–14 (natively, not as GSD integration) |
| Roadmap Phase 4 (validation) | Task 17 |

History stays in git (same call as DEC-135's archive: a directory of stale GSD-shaped state inside
the repo is a standing cost, not a resource). The three surviving `gsd` mentions in live files are
legitimate: deploy's registry-migration code (`~/.gsd/` → `~/.harness/`, functional) and CLAUDE.md's
two historical sentences.

---

## DEC-137 — The codebase map: a third knowledge tier, role-authored, index-preloaded, ship-refreshed

Raised by the user before kaya-ai: agents entering an existing codebase should consult a durable
map instead of combing the code per task — domains, architecture, data flows, stack, LLM patterns —
with pm planning against it and each specialist reading its own view. Design settled by discussion:

**A third tier.** Expertise is per-agent-learned; feature docs are per-feature; the map is
**per-project structural knowledge**, at `.harness/codebase/`: `INDEX.md`, `architecture.md`,
`domains/<module>.md`, `data-flows.md`, `stack.md`, plus role lenses that POINT into the shared
skeleton rather than restate it — one map, role-indexed, because per-role documents would recreate
the template-duplication drift (DEC-126).

**Role-authored** (supersedes SPEC §13's deferred `pm×N → documentor` shape): the consumer authors
its view — data-engineer the schemas/flows, frontend-dev the UI surface, ai-dev the LLM patterns,
security-reviewer the trust boundaries, pm the product surface; documentor consolidates the
skeleton. Multi-squad ⇒ an **orchestrator playbook** (DEC-118), which also exercises matrix A4/D9.

**Index preloaded, details by path.** `INDEX.md` (hard cap ~60 lines) is injected at every spawn by
the existing `SubagentStart` hook alongside Expertise. Decided against pointers-only on the
session's own evidence: every artifact delivered by preload worked on first contact; every artifact
relying on being pointed at failed silently at least once (DEC-125 ×4). Cost ≈ 250 tokens × ~44
spawns ≈ 11k/feature — ~7% of the DEC-135 cut — against 5–20k saved per avoided code-comb. The
rejected hybrid (preload for routers only) reintroduces per-role delivery gaps exactly where the
map matters most (solo debug).

**Truth discipline:** every map claim carries a `file:line` anchor and its section a date; the map
is a hint, code is truth. **Ship-triggered refresh:** after each shipped feature, documentor
updates sections whose domains intersect the team digests' `files_touched` — drift bounded by one
feature. The index refreshes with it.

**Sequencing:** built as task 23; runs as the FIRST act of task 17 — kaya-ai is onboarded, then
mapped, and every subsequent feature plans against the map.

### DEC-137 amendment — authorship is enforced by glob, and the refresh respects it

The user asked how authorship is *ensured*; answering exposed an inconsistency in the entry above.
As written, the ship-refresh had documentor updating specialists' sections — violating
author-is-consumer in exactly the path where the map spends its life.

**Enforcement stack:** (1) each map file is carved to its authoring role in `team-config.yaml` —
`check-domain.sh` makes a wrong-author `Write`/`Edit` mechanically impossible; documentor's grant is
the skeleton only (`INDEX.md`, `architecture.md`); (2) every section header carries provenance
(`author · date · anchors-verified: <sha>`), the audit trail and the refresh dirty-bit; (3) the
playbook routes each view to its squad per DEC-118. Known crack, stated: the DEC-85 Bash bypass —
globs are a strong fence, not a cryptographic one; correct grants up front are what keep agents off
the workaround path.

**Refresh, corrected:** documentor updates the skeleton and *marks* affected role sections
`stale: <FEAT>`; the **owning specialist** rewrites its own stale sections — eagerly, in the same
ship flow, one member spawn per actually-touched domain — so the map is never knowingly stale at
rest and no one ever rewrites a view they don't own.

---

## DEC-138 — GitHub Issues integration: asymmetric truth, orchestrator-executed, full loop (task 24)

kaya-ai tracks milestones and tasks in GitHub Issues, mirroring FEAT→T-NN. The integration, as
decided:

**Mapping.** `FEAT-NN-<slug>` → milestone (DEC-133's slug makes the title readable) · `T-NN` →
issue labeled `harness`, body carrying the task spec, `change_type` and `traces:` · SC-NN → the
milestone description's checklist · `[harness:t-NN]` commits gain `#<issue>` so GitHub auto-links
and `closes #` auto-closes · shipped → milestone closed. Issue numbers are recorded in
`feature.yaml` (`issues: {T-01: <n>}`) at creation — without that, closure is guesswork.

**Asymmetric truth.** Issues are pm's research INPUT at plan time — existing backlog can become
tasks, through pm, under the user's signature. After approval, sync is strictly OUTBOUND. GitHub
is never a write path into PLAN.md: a wiki-editable UI feeding an approval-gated artifact is the
DEC-19 bypass shape, and bidirectional conflict resolution has no machinery here. Inbound edits
re-enter only through a new plan cycle.

**Orchestrator-executed, at its existing checkpoints** — plan approved → create; task commit lands
→ close; shipped → close milestone. Gated per project by `github.sync: true` in `harness.json`
(the standing outward-facing consent, granted once by the user at init). **GitHub is a mirror,
never a gate:** `gh` absent or unauthenticated → the flow succeeds and reports the sync skipped,
per the SPEC §12 precedent for branch/PR operations.

**V1 is the full loop** (intake + outbound + numbers + graceful skip), built before kaya-ai so the
first real feature is mirrored from day one.

### DEC-138 amendment — the structural spec, confirmed

**One source document per GitHub construct.** Milestone ← BRIEF (title `FEAT-NN-<slug>`; description
= Problem + Goal + the SC checklist, so the milestone page IS the definition of done). Issue ← PLAN
`## Tasks`, one per T-NN (body: spec verbatim, `change_type`, `traces:`; labels `harness` + squad).
Issue closes via `closes #<n>` on the `[harness:t-NN]` commit; milestone closes on the user's ship
acceptance.

**Not mirrored, deliberately:** D-NN decisions (approval-gated in PLAN; issues reference them —
a decision as an issue invites drive-by reopening of signed choices), approvals, run dirs/digests,
Expertise, the codebase map. Mirror the work, not the machinery.

**Intake absorbs, never imports 1:1.** Backlog issues are symptoms written by whoever hit them; pm
plans work by its real shape. One T-NN may cover several existing issues — its issue body records
`absorbs: #12, #14, #31` and they close with it, so nothing silently vanishes and every watcher
sees where their item went. Inbound the backlog gets a vote; outbound the plan gets the decision.

**The harness's own design docs (SPEC/DECISIONS/BUILD) do not mirror.** If this repo ever wants
Issues, it eats its own dog food — features through `/harness-plan`, same machinery — not a
BUILD.md scraper.

### DEC-138 amendment 2 — triage: "what should we do next?", and silence on Issues

**The triage route.** "What should we do next?" belongs to no orchestrator — it exists before a
feature does. It is pm's remit through product-lead, and it is **the one sanctioned direct
main-session→lead dispatch**, justified narrowly: no feature exists for an orchestrator to own, and
triage writes no state — it reads (Issues, the codebase map, shipped history) and recommends. pm
returns ranked candidates with rationale; the user picks; the pick seeds `/harness-plan`. Any
dispatch that would WRITE feature state still goes through an orchestrator, no exceptions.

**Silent on Issues in v1.** Agents create, close, and cite absorptions — no agent-authored comments
in the org's repo until the mirror proves itself on a real feature. Division of labour restated:
pm is the mind (reads and interprets the backlog at plan time), the orchestrator is the hand
(mechanical mirror at its checkpoints); they never negotiate about Issues — pm's reading flows into
PLAN, PLAN through the user's signature, the orchestrator mirrors what was signed.

### DEC-138 amendment 3 — issue type labels derive from `change_type`

Per the user: `chore` for scaffolding/infrastructure work, `bug` for bugfixes, and no type label
for feature/enhancement work. Mechanical, because every T-NN already carries `change_type`:
`config`/`scaffolding`/`infra`/`ci` → `chore` · `bugfix` → `bug` · everything else → unlabeled.
`gh-sync.py` applies it at issue creation; no agent judgment involved. (The `harness` provenance
label is orthogonal and stays — it marks agent-created issues, not their type.)
