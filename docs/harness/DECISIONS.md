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
<!-- stale: "pending spike" -->
<!-- stale: "nesting is off by default" -->

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
<!-- stale: "delete: false` everywhere is a blanket" -->

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
<!-- stale: "8 doers" -->
<!-- stale: "4 reviewers" -->
<!-- stale: "7 write-less" -->

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
<!-- stale: "One feature at a time**, because" -->

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

**Measured** from `kaya-ai` history, 2026-07-04 → 2026-07-25 (470 commits). Full analysis in
`PILOT-SC4-BASELINE.md`.

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
<!-- stale: "rules/<name>/SKILL.md" -->
<!-- stale: "one unproven narrow case" -->
<!-- stale: "one remaining spike" -->

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
