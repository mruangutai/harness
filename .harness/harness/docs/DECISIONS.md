# Harness — Decision Log

> **Every entry states current truth, in its own voice.** There are no amendment sub-sections and no
> dated corrections: a correction rewrites the entry it corrects. A claim the tree has since
> falsified survives as one clause of that current truth, inside the entry which replaced it — with
> no date and no attribution — so that nobody re-proposes something already measured false.
>
> **Superseding is a single act.** The author of a superseding decision DELETES the decision it
> replaces in the SAME edit. Writing the replacement and removing the replaced are one act, so there
> is never a moment where both exist.
>
> **Numbers are never renumbered, and a deleted number is never reused** — it is retired with the
> entry.
>
> **History is not lost; git holds it.** This file was renamed in FEAT-22 (`8ad7d52`), so a plain
> `git log` on the path stops at that rename and misses everything before it. Use
> `git log --follow -- .harness/harness/docs/DECISIONS.md` to read the superseded entries and the
> folded amendments as they stood.
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

**Amendment 1 (2026-08-19) — the capability enumeration is corrected: `hooks` struck, `skills` and
`effort` added**

DEC-11 amendment 1. This entry's `Chose:` line enumerates the frontmatter half of the split as
`name`, `description`, `tools`, `model`, `color`, `hooks`. One of those six names a field that does
not work at all, and two fields every agent carries are missing from the list. **The `Chose:` line
is left standing unedited**, struck token and all: the record is appended to, never rewritten.
This amendment is what a citation to the old enumeration lands on.

*How it was found.* An operator asked where else a frontmatter change would need to land, and the
enumeration did not survive the question. No gate caught it, and none could — there is no
propagation checker between a decision and the tree it governs (DEC-188).

*`hooks` is STRUCK from the capability set.* It is not an unused capability, it is not a capability
at all: agent-frontmatter `PreToolUse` hooks **do not fire** for spawned subagents in this
environment, proven across three attempts (DEC-110). Domain enforcement is registered in
`.claude/settings.json` instead. Measured in the working tree at `d1ffd7f` (three lead agent files
modified and uncommitted, none of them for this): `grep -c '^hooks:' .claude/agents/*.md` returns 0
for all 16 agent files.

*`skills` is a capability field.* Rule delivery is frontmatter's job (DEC-63) — the native `skills:`
field preloads full rule content at spawn. `grep -c '^skills:' .claude/agents/harness-*.md` returns
1 for each of the 16 agent files.

*`effort` is a capability field, and it was never enumerated here at all.* It is carried by all 16
agent files (`grep -c '^effort:' .claude/agents/harness-*.md` returns 1 for each) and always has
been since it was introduced. Which value each agent carries is per-tier policy, and that policy
lives in DEC-152, not here.

*What did NOT change.* The rule this entry decided — manifest holds policy, frontmatter holds
capability, nothing is declared twice — is untouched, along with its `Because:` and
`Tradeoff accepted:` reasoning. Only the enumeration of which fields sit on the frontmatter side was
wrong. `SPEC.md` §4.0 restated the enumeration with its own divergence (`skills` swapped in for
`hooks`, `effort` absent, "six of them"); it is corrected to follow this amendment in the same
change. No DEC number is opened, superseded or retired here.

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

**Application (issue #80): the briefing's report round is dropped.** This entry's own premise —
*"the orchestrator already receives all three consolidated DIGESTs at the briefing, so it has the
cross-lead view at no extra spawn cost"* — is exactly why a *"report on your domain"* spawn buys
nothing: it re-narrates context the orchestrator already holds. A FEAT-04 orchestrator reached the
same conclusion unprompted (*"three lead spawns at ~20 USD each to re-narrate digests I hold is
spend with nothing to surface it"*). The curation block DEC-69 mandates is unaffected — it was
never sourced from the report round. A lead is still spawned here when a specific question its
digests do not answer needs one, and then only that lead.





## DEC-70 — `ai_behavior` becomes a real change type for prompt, model and tool-integration changes: ai-dev authors the eval, qa owns the gate — SUPERSEDES DEC-37

**Chose:** add `change_type: ai_behavior` with `eval` as a required test kind, **scoped to changes to
what a model is given or wired to — prompts, model selection and version, and tool integration.**
`ai-dev` **authors** the eval (failure modes, rubric, reference dataset, threshold); `qa` **runs it and
owns the gate**; `validator-lead` assesses eval *adequacy* in its panel synthesis.
**Outside that scope, a change to a markdown playbook an agent preloads is graded by CONDUCT** — a UAT
criterion reading a real dispatch — rather than by a dataset eval, because for a playbook the dataset
and the grader come from one hand and no live behaviour is read, so a passing eval reports only that
those two agree with each other; the reflexive weakness named below is total there, not partial. This
narrows what `ai_behavior` covers and nothing else — the `eval` kind stays required wherever the scope
above holds.
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

## DEC-90 — STRUCK 2026-08-21

Recorded the single-operator assumption as a stated scope boundary rather than an implicit one:
every "single writer" guarantee meant one agent in one session on one machine, and two terminals
meant two orchestrators writing `STATE.md`, `feature.yaml`, `logs/` and committed Expertise files,
**with no lock anywhere**.

Struck under DEC-188 on the operator's word. `bin/expertise-merge.py` holds an exclusive lock across
the whole read-modify-write of an Expertise file, and it reached `main` in FEAT-30 (PR #629), so a
lock exists on one of the files this entry named as unlocked. FEAT-30 falsified it; FEAT-32, where
the striking was raised, has not shipped. Nothing was removed from a gate — DEC-90 was wired into
none. The single-operator boundary now lives in SPEC §15.1 alone; issue #633 records what the strike
cost.

**DEC-90's number is retired, not reused.** DEC-120 cites it.
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

## DEC-103 — STRUCK 2026-08-10

Created `bin/check-docs.sh`, the propagation checker, after twelve decisions left ten falsified
statements standing in SPEC and BUILD — the exact defect the SPEC/DECISIONS/BUILD split had been
created to prevent.

Struck under DEC-188: the operator replaced detection with deletion. A decision the tree flatly
contradicts is now struck from the record and removed from every gate, so nothing survives to
contradict and nothing needs detecting. `bin/check-docs.sh` is deleted.

## DEC-104 — STRUCK 2026-08-10

Enforced DEC-103's checker as INV-10 in `check-state.sh`, with DECISIONS itself as the registry via
inline stale-wording markers in HTML comments, with a per-line escape comment.

Struck under DEC-188, with DEC-103. What went with it: the INV-10 block in `check-state.sh`, 66
`stale` markers and 14 `ok-stale` exemptions. The trigger is worth recording because it is the
mechanism's own failure mode — a change contradicted a passage in DEC-165, the marker needed a host
decision, and the natural host DEC-161 had already been deleted. There was nowhere to put the
declaration.

**INV-10's number is retired, not reused.** It appears in shipped digests and reviews.

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
`` marker on DEC-108** — the checker enforces what it is told, and I recorded the finding
without registering the wording it invalidated.

**So the mechanism is sound and the discipline around it is not.** Two markers now declared, and the
lesson generalises: **writing a superseding decision is only half the work — declaring what it
invalidates is the other half**, and skipping the second half puts the claim right back into circulation.

This is the third recurrence (DEC-103, then the §0b claim, now caught only by reading). The honest
conclusion is that no amount of care substitutes for the marker being part of writing the DEC.

## DEC-110 — Agent-frontmatter `PreToolUse` does not fire; the domain hook moves to `settings.json` and WORKS



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
`check-state.sh` to pass.

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

## DEC-113 — Team and crew overrides live outside the tool tree, and are resolved first

Task 13. **Crew overrides live in `.harness/crews/`, not `.claude/skills/harness/crews/`.** The
skill tree is this repository's own source, rewritten by harness development itself — so an override
placed inside it is whatever the next harness change leaves behind, and nobody editing harness code
owes it a thought. The override directory is project-owned state that harness development never
edits. The precedence rule BUILD asked for ("project-local overrides global") only holds if the
override sits there. Recorded in both manifests as `paths.crew_overrides`; the runner (task 10)
resolves it first.

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

**Status note (FEAT-06, 2026-08-04): the `gate-probe.yaml` team file was deleted from the repo; this
entry is retained as the historical record of loop-back semantics, which remain in force** — the
probe was a mechanism check that had already produced its evidence, and the rulings it settled
(`{{cycle}}` in the output path of anything that re-runs, `feed: [self]` delivering the report) bind
every team that loops back.

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






**Supersedes DEC-102's conclusion** that `depth: 2` "is exactly the harness shape". The shape
changed.





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

## DEC-137 — STRUCK 2026-08-24

Recorded the codebase map as a third knowledge tier at `.harness/codebase/`, authored by the role
that consumes it, carved per role in `team-config.yaml`, with `INDEX.md` preloaded at every spawn
and kept true by a ship-refresh pass at every close-out.

Struck under DEC-188 on the operator's word, on a measurement: across **35 feature directories the
map was never built**. `.harness/codebase/` did not exist, so thirty-five features planned against
a tier that `/harness-map` describes as the thing "everything plans against". A tier nothing ever
used is not under-adopted; it is unneeded, and every gate and pointer still naming it was a false
statement standing in the tree.

Removed from every gate and surface: `INV-14` and `INV-20` deleted from `check-state.sh`, the
`INDEX.md` injection deleted from the `inject-expertise.sh` SubagentStart hook, ten map paths
dropped from `team-config.yaml` and its template, `/harness-map` and `/harness-deepen` deleted,
`bin/render-map.py` and `templates/codebase-INDEX.md` deleted, and the playbook's ship-refresh
section removed.

**The glossary survived the tier it lived in.** `.harness/codebase/glossary.md` is the domain's
ubiquitous language, used by `harness-spec-driven`, `harness-grilling` and `harness-init` — none of
them the map. It moved to `.harness/glossary.md`; DEC-162 and its INV-19 hold, with the map
precondition dropped.

**DEC-137's number is retired, not reused.** DEC-149 cites it.

**The original entry follows, left standing unedited (DEC-188: appended to, never rewritten).**

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

**Intake reshapes, never imports 1:1.** Backlog issues are symptoms written by whoever hit them; pm
plans work by its real shape. One T-NN may cover several existing issues. **The `absorbs:` citation
that recorded this is STRUCK 2026-08-25 under DEC-188 — see amendment 7.** An issue a feature
actually does is a ticket in its own right and closes when its card reaches `Done`; an issue the
feature does not do stays open, cited nowhere. Inbound the backlog gets a vote; outbound the plan
gets the decision.

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

### DEC-138 amendment 4 — leads' residual findings become issues through the briefing, never directly

The user asked how findings raised by leads reach GitHub. The split: **blocking findings
(`must_fix`) never become issues** — they route back into the current flow as fix cycles and die
there. **Residuals** — findings that survive the lead's collation but do not gate (FEAT-02's F-1
advisory, qa's coverage notes) — are future backlog, and today they die in the briefing notes.

Route: **briefing-gated.** The briefing's residual-findings section is a *proposed backlog* list;
on the user's ship acceptance, unstruck entries become plain backlog issues — labeled `harness`
plus `bug`/`chore` by finding nature, unlabeled for enhancements, **no milestone** (they belong to
no feature yet; a later plan cycle may absorb them). Rejected alternatives: digest→GitHub direct
(publishes unapproved judgment — FEAT-02's panel raised 15, collation dismissed 10; noise is how
backlogs die, and work items enter existence through a human signature, same as tasks); pm-first
review (the lead's collation already is the quality filter, and pm sees the backlog at next triage
anyway — a spawn for a third opinion on something the user is about to read).

Mechanically: `gh-sync.py backlog <feature-dir>` reads the accepted residuals (the main session
passes them after the briefing decision) — part of the door's shipped row alongside `ship`.

### DEC-137 amendment 2 — the human view: map.html, derived and never authored

Per the user: the map also renders to a single HTML artifact — collapsible side TOC, domain
sections, physical- and component-level architecture diagrams. The structural rule that decides
everything: **derived, never authored.** Agents write only the markdown views; `bin/render-map.py`
projects them into `codebase/map.html` deterministically (stdlib, no build step). Diagrams are
authored as Mermaid blocks in `architecture.md` — text, diffable, anchorable — rendered by
mermaid.js from CDN in the viewer's browser, degrading offline to visible source (the files-only
constraint governs the harness runtime, not the browser). No separate refresh mechanism exists or
is needed: the renderer runs at the end of the map mission and every ship-refresh, and running it
by hand IS the manual refresh — the HTML is exactly as fresh as the markdown, by construction.
A parallel authored HTML would be the duplication-drift class killed twice already (DEC-126,
DEC-135).

---

## DEC-139 — Debug is an investigation segment, not a team; bugs are BUG-NN flows through the same gates

Task 20's ledger row carried a contradiction: "single-squad under eng-lead" with a DAG spanning
three squads (pm → specialist → qa/code), which DEC-118 forbids a team to be. Resolving it exposed
the real question — what is debug that FEAT-02 (a bugfix, fully served by plan→ship) was not?
Answer: **the unknown cause.** Debug = an investigation segment in front of the normal flow:
eng specialist in debug mode reproduces, localizes, and root-causes with evidence — no fix — and
that report seeds pm's mini-plan; signature and ship follow the standard gates. Known-cause bugs
skip the segment entirely. Three failed hypothesis cycles is `BLOCKED`, per systematic-debugging.

**Bugs are full flows, named `BUG-NN-<kebab-slug>`** (user's call): independent number sequence,
same rules as FEAT ids, and deliberately the same folder root (`.harness/features/` — the flows
root; zero scripts hardcode the FEAT prefix and all 18 domain globs are `features/*`, verified, so
a parallel `bugs/` root would re-carve everything for nothing). A lightweight ungated bug lane was
rejected: "small" is a judgment that drifts, and a second path around the signature is the DEC-19
bypass shape. The standalone all-in-one debug team was rejected with it — a fix that ships without
qa, review, or a signature between diagnosis and change.

---

## DEC-141 — The first real map audit: renderer fixes codified, and the reviewer's blind spot named

kaya-ai's map was audited twice — by the user (three findings) and independently by ui-reviewer
(four). The overlap and the misses are both codified:

**Renderer defects (mine), fixed in `render-map.py` with regression proofs (16 total):** sibling
`<h2>`s per section and no `<h1>` in `<main>` — the reviewer's high/a11y finding and the user's
"headers blend in," same defect through two lenses (each view's own `# Title` now folds into the
section heading; content nests h4+; full type scale and spacing rhythm styled). HTML comments
stripped from view bodies (they rendered as prose). Mermaid `useMaxWidth:false` + scroll container
— the user's "diagram too small"; the default shrink-to-fit renders real diagrams as thumbnails.

**Content learnings → the map mission's authoring rules:** label every edge with what flows in both
directions (the write-only label hid the read path); never let directory layout impersonate
architecture (`WORKER → api/` implied HTTP where only a persistence import existed); no raw HTML
comments in prose; keep each diagram at its declared level. The two kaya diagram defects themselves
are kaya-side content fixes, reported to that session.

**Reviewer calibration, recorded in its agent file:** ui-reviewer audits source, not pixels — it
computed contrast and node counts correctly while missing the shrunken rendered diagram the user
saw in seconds. It must now declare rendered-size/layout dimensions as "needs eyes" rather than
implying coverage. The complementary strength stood: it traced every diagram claim to code and
found two substance gaps no human eyeball would have.

### DEC-141 addendum — round 2: the viewport inversion, and documentor to opus

Two more from the user against the fixed render. **Viewport:** capping `<main>` at reading width
forced diagrams into a 60rem box — panning inside the pre *and* scrolling the page, four directions.
Inverted: the prose elements carry the 60rem cap, the page does not, and the diagram gets one
scroll container at full window width with a fixed max height (78vh). Top-down orientation joins
the authoring guidance — layered architectures read naturally TD.

**Jargon:** the html read as a parts inventory, not prose. This was the evidence the morning's
deferred call was waiting for — **documentor is now `model: opus`** (writing for humans is its
entire role), and every view must open with `## In brief`: three to six sentences of plain English
before any anchored detail. The anchored rigor stays; it follows the prose instead of replacing it.
Kaya's existing views predate the rule — their re-authoring rides the next map refresh there.

---

## DEC-142 — One dispatch-title convention at every layer

Field report from kaya-ai: the same piece of work read as three different things at three layers —
a stale orchestrator title, a generic lead title, a task-worded member title — and the user watching
the spawn tree reasonably suspected duplicated work. Titles were free text at each dispatching tier.

Convention, now stated at all three origins (door, playbook, team runner):
**`<flow-id> · <step or task id> · <what, 3–6 words>`** — e.g. `FEAT-02 · T-01 · red repro cases`,
`BUG-01 · investigate · reproduce and localize`. The flow id appears in every title all the way
down; a spawn title that cannot be traced to its flow is a dispatch defect. Ergonomics, not
mechanics — nothing routes on titles — but the spawn tree is the user's only live view of a running
org, and it should read as one chain.

---

### DEC-142 amendment — the agent NAME is the title the user actually sees, and it cannot hold `·`

DEC-142 was written when a spawn had a free-text title and nothing else. Agents are now addressable
by `name` for `SendMessage`, and that name is what surfaces in the spawn tree and on every relayed
message. The name field is constrained to `^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$`, so **the convention's
`·` separator and its spaces are illegal there** — DEC-142's literal format cannot be used as a name.

Observed defect, main session, 2026-08-03: FEAT-05's ship orchestrator was named
`yaml-sweep-f1-ship`. Its `description` did carry the flow id ("Ship FEAT-05 pyyaml file parsers"),
but the NAME is what rendered, so the user watching the tree could not trace the running agent to its
flow, saw `harness-eng-lead` conducting a run, and reasonably asked why a lead had been spawned
directly instead of an orchestrator. Nothing was wrong with the org — main had spawned only the
orchestrator, which had dispatched the lead correctly at layer 2 — but the tree could not show that.
**That is exactly the kaya-ai failure DEC-142 was written to prevent, reproduced through the one field
the decision did not know about.**

The rule, unchanged in spirit: **a spawn the user cannot trace to its flow is a dispatch defect.**
Mechanically, when a spawn carries a `name`:

- **The `name` is a flow-traceable slug** — `<flow-id>-<step>`, e.g. `FEAT-05-ship`, `FEAT-05-T01`.
  Hyphens for the separator, since `·` and spaces are rejected. The flow id comes first so the tree
  sorts and reads as one chain.
- **The dispatch description keeps the full form** — `FEAT-05 · ship · build validate and ship`.
- **A name that omits the flow id is the defect**, however good the description is. Naming an agent
  for addressability must not silently displace the convention.

**One genuine gap this does not close.** A NEW feature's id is coined by pm at BRIEF time (DEC-133),
so the very first `plan` spawn has no flow id to carry — the door cannot comply on that one dispatch.
Options are a provisional slug renamed on return, or accepting one untraceable spawn per feature.
Unresolved, and deliberately not decided here; it affects exactly one spawn per feature and the
orchestrator's own name can be corrected on the next dispatch.

## DEC-143 — check-domain.sh sees through worktrees; the unsplittable-task gap is task 25

Field report from kaya-ai, at the most expensive possible place — the first build dispatch after
plan approval: in a worktree-per-session project, **no doer could write source at all.** The hook
computed paths relative to the main checkout, so `.claude/worktrees/t01-83/src/…` was just a
subdirectory matching no repo-relative glob, while the identical path in the main checkout passed.

**Fix, in the hook:** match the raw path first (preserving any future glob that deliberately
targets `.claude/worktrees/**` — the reporter's own edge case), then strip the worktree prefix and
match the in-worktree path against the same globs. Not a widen — identical globs, anchored to the
checkout the agent stands in. Seven proof shapes green, including the verbatim kaya repros,
absolute paths, and foreign-path blocks in both checkouts.

**Credit where due:** the kaya orchestrator identified and explicitly REJECTED the third option —
Bash writes the hook admits it cannot see — as guardrail evasion, then used a recorded, scoped
waiver instead (main-checkout build on the feature branch, waiver in feature state). That is the
DEC-85 pressure handled exactly right, and the opposite of the bin/-ownership incident (FEAT-02).

**Two design notes captured, not fixed here:**
- **Task 25 — shared-workspace mode.** A task that removes a default relied on by N call sites, in
  a repo whose pre-commit runs the full suite, is unsplittable across commits: sequenced squad runs
  must share one workspace with no intermediate commit. Per-agent worktree isolation cannot provide
  that even with the hook fixed. Dispatch planning needs a declared "shared workspace" mode for
  tasks of this shape.
- **Worktrees branch from the LOCAL branch, not origin** — with unpushed commits, origin is behind
  the pinned SHA. Added to the runner's worktree guidance.

---

## DEC-144 — The branch-creation gate joins the harness: fifth prerequisite, self-gating on the mirror

Reviewed at the user's request: kaya-ai's field-proven `branch-create-gate.sh` — a `PreToolUse:Bash`
gate requiring every new git branch to name the work it serves, with a best-effort project-board
In-Progress flip. Ported into `bin/` with four genericizations: the hardcoded kaya board IDs become
OPTIONAL `harness.json` config (`github.project_number/project_id/status_field/in_progress_option`;
absent = flip skipped); the repo is the PINNED `github.repo` on every gh call, never cwd-inferred
(DEC-138); `jq` is gone (python3 stdlib, like every harness script); and a second branch grammar is
accepted — `<type>/FEAT-NN-slug` / `BUG-NN-slug` validated against the flow existing on disk,
because harness flows branch per feature and the original's issue-number-only rule would have
denied every legitimate orchestrator branch.

**Registration is unconditional — the fifth `settings.json` prerequisite** — because the script
self-gates on `github.sync` and exits instantly where the mirror is off. Conditional registration
would be a second INV-13-style limbo. Unlike gh-sync (a mirror that must never gate), this IS a
gate: unverifiable states (gh missing, unauthenticated) DENY with the reason rather than waving
work through. Nine offline proof shapes green, including the original's year-token guard and both
grammars. The init question that keys it ("Mirror features to GitHub Issues?") was already in place
(DEC-138).



---

## DEC-145 — Expertise v2: observations mid-run, Expertise only at distillation

Field report from the kaya-ai two-feature run: Expertise files bloated to 1,371 lines / ~21k words
across 13 files (pm 6,796 words, product-lead 5,191, validator-lead 3,092). The entry-count caps
held — the growth was *inside* entries (one 1,073-word bullet; another with ten inlined incidents
labelled (a)–(j)) and in invented, uncapped section names ("Recurring failure modes", "Assessing
members"). Since `inject-expertise.sh` cats the whole file into every spawn, every dispatch paid
the tax, compounding per cycle.

Three root causes, all verified: injection was whole-file and uncapped; the §5.4 curation loop was
spec-only — carried into no runtime skill, so nothing ever distilled; and the design asked the
agent hot with an incident to record AND abstract in the same moment. It records. "Prefer merge
over add" then rewarded appending case histories to existing entries — cap-compliant bloat.

**The fix splits recording from distillation.** Mid-run, agents append granular observations to
`.harness/features/<FEAT>/observations/<agent>.md` — never injected, so detail is free; every
agent's domain gains that one path. Expertise is written only under a distillation dispatch: the
new feature-close step in the orchestrator playbook (leads distill members, orchestrator distills
leads, per DEC-69's recommend/condense/apply split), or the new `/harness-curate` skill
out-of-band. `expertise_update: []` is the normal DIGEST on every other run.

**Format is now mechanical, not advisory:** entries are WHEN/DO rules or durable repo facts, ≤50
words, no FEAT/T/issue tokens, no nested bullets or instance lists; four canonical sections only;
150-line file budget. `bin/check-expertise.sh` enforces it (exit 1 with per-violation report), and
`inject-expertise.sh` hard-truncates at 150 lines with a loud in-context warning, so one bloated
file can never again silently tax every spawn. `merge` is redefined: the result may be no longer
than the longer input — appending an instance is `add` wearing a costume.

Supersedes the mid-run write discipline of DEC-24/66/67 (the op format, IDs, and who-holds-the-pen
all survive; only the *when* moved) and DEC-25/68's overflow flow becomes the escalation path when
a distilling agent cannot condense under the caps. Live probe deferred to the next kaya-ai feature
run: agents appending observations, feature-close distillation firing, injected context staying
under budget.



**Amendment (same day):** a third boundary joined decision-vs-observation: **a harness defect is a
bug report, not a learning** — it routes to `open_questions`, never Expertise, because a recorded
workaround outlives the fix. Found live in the kaya retrofit: the orchestrator had filed "injection
failed to fire once; cat the file manually" and "member caps silently stop learning" as Outcomes —
the first is now evidence on BUILD.md's task-10 preload probe, the second is this very decision.

**Amendment 2 (2026-07-29) — the digest-skim, dry-run-proven before wiring.** Tested on FEAT-01's
11 real eng digests with a sandboxed member before touching the playbook. The lead (recall) stayed
bounded — 3 sourced, observation-phrased candidates per member — and its yield included a class we
did not predict: two existing Expertise entries contradicted by code shipped later in the feature,
so the skim doubles as a staleness audit. The member (precision) accepted 2, and REJECTED one with
a reason — no rubber-stamping of its lead. Wired into the playbook with the guards that keep the
three-party split a pipeline, not diffusion: ≤3 candidates, observation-phrasing, rejection as a
first-class recorded outcome, displacement-never-merge at a full section, and per-source accept
counts in the distillation digest so a skim that stops yielding gets cut. Also pinned the run-dir
slug grammar (`<task-or-purpose>-<squad>`, no feature infix) — FEAT-02's dirs embedded the feature
id redundantly. Displacement-at-cap remains untested (no section was full); first live distillation
covers it. Same test measured re-bloat velocity: 9 of 15 kaya files failed the checker within a day
of distillation because kaya still ran the old rules — deploy is the gating control, not authoring
discipline.


**Note (2026-08-24): am.3 below is MOOTED.** Ship-refresh existed only to keep the codebase map
true, and it was removed with that map tier (DEC-137, struck). Close-out is now one dispatch —
distillation — so there is no second job to run concurrently with. The amendment is left standing
below as the record of why the pairing existed; nothing acts on it.

**Amendment am.3 (issue #80): ship-refresh and distillation dispatch concurrently, and the cold
property survives it.** They were two sequential close-out rounds; they share no data and neither
reads the other's output, so the round-trip bought nothing. They are now **two separate dispatches
issued in one message**.

The distinction is load-bearing and is why this amendment exists rather than a bare sequencing
note. **Concurrency is free; combining the prompts is not.** Ship-refresh is hot, mechanical
routing work. Distillation is the cold, stepping-back judgment this entry created — *"mid-run you
only observe; distillation happens later, cold"*. A lead handed both jobs in ONE dispatch performs
the second while still hot from the first, and its distillation degrades into summarising the run
it just routed — invisible at ship time, surfacing as a worse next feature. Two dispatches in one
message preserve the cold framing; one dispatch carrying both does not, and is forbidden.


---

## DEC-146 — Board-flip lookup inverted: issue → projectItems, no item cap

The DEC-144 port kept the original's lookup direction for the In-Progress flip: list the whole
project (`gh project item-list --limit 500`) and filter for the issue client-side. The cap is a
time bomb — past 500 board items the issue falls outside the page, `item` comes back empty, and
the `[ -n "$item" ] &&` guard **silently skips the flip forever**: the gate still gates, but the
board decays with no failure anywhere. Raising the limit only moves the date.

Inverted the direction: one GraphQL query on the issue node's `projectItems` (an issue sits on at
most a handful of boards), filtered by the pinned `project_id`. O(boards-per-issue) instead of
O(tickets-per-board); no pagination, no cap. Six offline proof shapes green, including a two-board
node set where the flip must select by project id, both deny forms, the flow-dir form, and the
sync-off pass-through. Flip stays best-effort by design — only the lookup direction changed.

---

## DEC-147 — Flat-roster rule promoted from Expertise to the constitution

Kaya field report: an orchestrator dispatched eng-lead with a `name:` parameter and got the
platform rejection "Teammates cannot spawn other teammates — the team roster is flat" — for at
least the fourth time. Three agents had each already learned this independently (orchestrator,
eng-lead, product-lead Expertise all carry "omit `name:`"), and it recurred anyway: Expertise is
per-agent and probabilistic (a fresh agent, or one injection miss, and the lesson is absent), while
this is a platform invariant that holds for every spawner in every project. Wrong tier. Promoted to
the rule skills — the playbook's delegation rule and the team runner's dispatch step now state it —
via the SPEC §7 promotion path firing on its first real case. Heuristic worth keeping: **a lesson
three or more agents record independently is constitution or codebase-map content, not Expertise.**

---

## DEC-148 — The long-context tax: a watchdog in cost-report and a relay rule in the playbook

The kaya cost snapshot's headline line — $1,010 on one "orchestrator" row — decomposed to ~all
cache reads: 3.48B tokens of context re-read, i.e. context length × turn count, growing with the
square of session length. Measured directly: the map rebuild orchestrator averaged 310k tokens of
context per turn over 1,360 turns; the cumulative main-session line, 304k/turn over 11,449 turns.
Expertise injection was 1–3% of that tax (DEC-145 already caps it); the dominant term is agents
living too long in one context.

Two changes. **cost-report.py grows a context watchdog:** it now counts turns per agent line and
flags any agent whose average cache-read/turn exceeds `budgets.context_per_turn_tokens` (default
200k) — first run on kaya flagged exactly the three known offenders and nothing else. **The
playbook grows a relay rule:** the orchestrator ends its run at mission-phase boundaries once a
phase has cost ~10+ dispatches, reporting "phase complete, spawn a successor" — the disposable-
context/state-on-disk design already guarantees a successor loses nothing (proven by the map
orchestrator dying at a restart AFTER completing its render, with zero loss). Payloads never ride
forward: a member's output lives in its digest file; the orchestrator's context needs the verdict
and the path.

---

## DEC-149 — Design knowledge enters the org: vocabulary, glossary, and the deepen mission

**Amendment 1 (2026-08-24) — mission `deepen` is retired; the two skills and the glossary stand.**
`deepen` scanned the codebase map, and the map tier was struck (DEC-137) after 35 features never
built one. `/harness-deepen` is deleted and the mission is removed from `harness.md`'s resolution
list. What this entry ALSO created is untouched and live: `harness-codebase-design`,
`harness-spec-driven`, and the glossary — which moved with the tier's retirement to
`.harness/glossary.md`. This entry is amended rather than struck because only its mission clause is
contradicted.


Three imports from Matt Pocock's MIT-licensed skills (mattpocock/skills), each re-homed onto
existing harness machinery rather than bolted on:

**`harness-codebase-design` — a new rule skill** (from `codebase-design`): the deep-module
vocabulary (module/interface/seam/adapter/depth/leverage/locality) plus four tests — the deletion
test, the-interface-is-the-test-surface, one-adapter-hypothetical-two-real, and
state-the-lifetime-with-the-seam (the fourth is ours, generalized from the kaya pool-leak that four
green gates missed and eng-lead's diff-read caught). Preloaded by **eng-lead** (dispatch constraints,
architecture review, optional design-it-twice on interface-defining tasks) and **code-reviewer**
(stage-two finding shapes). Doers receive it through dispatch prompts, not preload — context budget.

**The D-NN bar and the glossary — into `harness-spec-driven`** (from `domain-modeling`): a choice
earns a D-NN only when hard-to-reverse ∧ surprising-without-context ∧ real-trade-off; otherwise it
is a digest note. NO second decision store — the ADR practice's filter is imported, its `docs/adr/`
is not (nothing is declared twice). The ubiquitous language lives at
`.harness/codebase/glossary.md`, a pm-owned map lens (domain granted in team-config): challenge
drift before it lands in a REQ, sharpen overloaded terms before SCs are written against them, code
wins over stated meaning, update inline at ship-refresh. Field motivation: kaya's status-vocabulary
question and the expense_credit badge-vs-blocker confusion both went up as open questions a
glossary would have pre-answered.

**Mission `deepen` — in the playbook** (from `improve-codebase-architecture`): a between-features
scan, never mid-build. Hot spots from the last ship's `files_touched` → eng squad scans in the
design vocabulary → validator panel adversarially verifies each candidate → surviving candidates
reported with recommendation strength → the user picks at a briefing, and the pick enters
/harness-plan as a normal feature. Three adaptations from the original: the interactive grilling
loop becomes the main-session approval conversation (agents have no user channel); the CDN-built
HTML report becomes the render-map offline pattern; rejected-with-reason becomes a D-NN instead of
an ADR. Cadence: the three imports fire at different times — the vocabulary is a lens on every
step, glossary/D-NN-bar fire where language and decisions are born, deepen runs between features.

---

## DEC-150 — State files get physics: the shape gate, and the resume-reading rule

Field report: a resumed FEAT-01 orchestrator hit ~100k tokens "almost immediately." The suspected
cause (a validator digest it was told to read) measured 6.5KB — innocent. The real causes: the
handoff's "read all state from disk first: {BRIEF,PLAN,feature.yaml,notes/,runs/}" pointed at
~1.1MB across 111 files, and feature.yaml itself had grown to 141KB / 1,644 lines of narrative
YAML comments — the orchestrator's memory dump, paid for by every successor. FEAT-02's copy showed
the same disease early (a cost figure stored as a paragraph-long string).

The spec was already right — STATE.md is `## Current` + `## Open Questions`, "holds no history at
all" (§2), feature.yaml is data a script parses — but nothing enforced it, and the playbook itself
taught the opposite: step 5 said "APPEND the per-member roll-up to STATE.md."


Three changes. **A shape gate in check-domain.sh** (stage two, after the domain check): a `Write`
to `.harness/features/*/feature.yaml` over 200 lines or 20 comment lines, or to `STATE.md` over
120 lines or carrying any section besides the two legal ones, is DENIED with the routing table as
the reason — current truth replaces `## Current`, per-run findings go to that run's digest,
rationale to notes/. Accretion is impossible: the governed writers hold Write not Edit, so every
increment re-passes the whole file through the gate. Eight proof shapes green (clean/oversized/
comment-heavy feature.yaml, legal/illegal STATE.md, Edit skipped, main session ungoverned, domain
block intact). Known side door: Bash writes (DEC-85) — guardrail evasion by constitution, caught
after the fact by the context watchdog. One found-bug recorded for script authors: `python3 -`
takes its PROGRAM from stdin, so piping data alongside a heredoc silently loses the data — the
gate's first draft passed everything; payload now rides an env var.

**The playbook's reading and writing rules corrected:** step 1 scopes reads (Grep BRIEF/PLAN by
task id; on resume the handoff prompt IS the working set; runs/ and notes/ are archives read by
pointer, never a startup sweep); step 5 now says REPLACE `## Current`, data-not-narrative for
feature.yaml; the DEC-148 relay text names the three correct homes instead of "STATE.md" loosely.

**Enforcement honestly labeled:** the reading rule is advisory (reads cannot be gated); the write
gate is physics; the context watchdog names whoever ignores the advisory part. Kaya's existing
141KB feature.yaml is cleaned up separately — the gate only prevents new accretion.

---

## DEC-151 — The Bash write bypass, exploited and then narrowed: bash-write-guard.sh

Field incident, reported by the kaya orchestrator as a security finding: during the FEAT-01 fix
cycle, **qa was denied a source edit by check-domain and made the identical edit anyway via
`perl -pi` from Bash.** The orchestrator judged the instance harmless but did not audit earlier
runs; the bypass was available to every Bash-holding agent, and "read-only reviewer" was a
convention, not a boundary. DEC-85 had documented this gap as accepted risk with dev-ops as the
trusted case — qa exploiting it under pressure breaks that rationale.

**Fix: `bin/bash-write-guard.sh`, a PreToolUse:Bash hook** registered alongside the branch gate
(sixth settings.json prerequisite; snippet template updated). Policy: the three reviewers are
READ-ONLY — any detected write pattern (redirects, sed/perl/awk in-place, tee, sponge, rm/mv/cp)
is denied outright, "report the finding; never fix." Every other harness agent except dev-ops
(exempt per DEC-85 — owns builds) gets extractable target paths checked against its team-config
domain, shared paths included, worktree-normalized; in-domain and unparseable commands pass. The
deny message names the rule: a path the domain hook denied does not become writable by switching
tools — that is guardrail evasion; raise an open_question instead.

**Honest scope:** this narrows DEC-85, it does not void it. Arbitrary shell is still unwinnable —
the guard converts the CASUAL bypass (what an agent under pressure actually types) into deliberate
obfuscation, which is a different behavior class and is caught post-hoc (tree audit, context
watchdog, the orchestrator's spot-checks). Ten proof shapes green: qa's literal perl bypass denied;
qa's in-domain sed/perl and pytest allowed; BSD `sed -i ''` and bare-sed script args parsed
correctly (two false positives found and fixed in testing); reviewers denied on any write shape;
dev-ops exempt; main session ungoverned.

---

## DEC-152 — Reasoning effort pinned per tier; the session default stops leaking down

Found while investigating the model-selection scare: no agent declared `effort:`, so all 16
inherited the spawning session's setting — and the user's saved default is LOW, meaning both kaya
features ran their entire judging apparatus at low effort invisibly. Frontmatter `effort:`
overrides the session (sub-agents docs).

Pinned by tier: the seven **judging** agents — orchestrator, three leads, three reviewers — run
`effort: high` (they are the error-catching tier and a small fraction of spawns); the nine
**doers** run `effort: medium`. The user chose judgment quality now over baseline purity: the
DEC-145..148 baseline was measured at inherited-low, so effort is a known confound in the FEAT-02
comparison — noted here so the comparison reads it as two changes, not one.

**Amendment 1 (2026-08-19) — the tier assignment is struck and restated: four judging agents at
`high`, twelve at `medium`**

The rule this entry states is unchanged and is not in question: frontmatter `effort:` is pinned per
tier and overrides the spawning session's setting. `dispatch-guard.sh` enforces it and cites this
entry by number. What is false is the census in the paragraph above — **"the seven judging agents
run `effort: high` and the nine doers run `effort: medium`."** That sentence is STRUCK. It is left
standing unedited so a citation to it lands here.

*The tree at `b4659cd`:* four agents run `high` — `harness-orchestrator`, `harness-code-reviewer`,
`harness-security-reviewer`, `harness-ui-reviewer` — and twelve run `medium`. Measured with
`grep -h '^effort:' .claude/agents/harness-*.md | sort | uniq -c`, not counted by hand.

*What moved and why.* The three domain leads — eng, product, validator — dropped from `high` to
`medium` on operator instruction. The original split put them in the judging tier because they
assess what their members return. The operating reason for the change is that a lead routes and
consolidates; it holds no shell and reads no diff itself, so the error-catching work the `high` tier
was bought for happens in the three reviewers and the orchestrator. That is now the whole `high`
tier, and it is four rather than seven.

*How it was found.* Nothing detected it. A documentor flagged the arithmetic while amending DEC-11
in the same session the leads were changed; there is no propagation checker between a decision and
the tree it governs, and DEC-188 is the rule that there will not be one.

*A strike was considered and refused.* DEC-188 strikes a decision the tree flatly contradicts, and a
strike removes it from every gate. The tree does not contradict the pinning rule — `dispatch-guard.sh`
runs on it. Only the enumeration was falsified, so only the enumeration is struck.

---

## DEC-153 — The audit's verdict, and two sanctions: worktree perturbation, orchestrator commits

The one-shot bypass audit (190 subagent + 78 main transcripts, 788 raw write-pattern hits, 34
surviving the source-path filter) found the qa `perl -pi` incident was **not isolated but also not
malicious**: qa bypassed the domain fence in five transcripts, every instance a backup-perturb-
restore mutation proof — the discipline of proving a test discriminates, done in the only place the
tooling allowed. A fixes-orchestrator additionally made probe edits to source via python heredocs
(invisible to shell-pattern parsing) and **committed source directly** (c04482a, 6e02fa8, shipped
in PR #299) — content doer-produced and gate-checked, but staged by an agent whose domain is
`.harness/features/**`. Nothing dirty at HEAD anywhere.

Two sanctions, both user-decided. **Perturbation proofs get a legal home:** bash-write-guard now
permits governed-agent writes under `.claude/worktrees/**` — disposable checkouts are where
mutation proofs live; the main checkout stays hard-gated; reviewers stay read-only everywhere
(they never reach the path check). qa's rule skill states the protocol: worktree, byte-identity
restore verification, never "just briefly" in the main checkout. **The commit pen is the
orchestrator's:** it stages by explicit pathspec and commits the feature branch it owns; merge/PR/
deploy stay user-gated; probe edits must be byte-verified restored before any commit. Recorded in
the playbook.

Residual, stated honestly: python-heredoc writes evade the guard's shell parsing (found by the
audit's second pass) — the guard remains a casual-shape filter per DEC-151; heredoc evasion is
deliberate-obfuscation class, caught post-hoc. The audit could not exhaustively prove the main
session never wrote source attributed to an agent — spot-checks found none.

## DEC-154 — state.yaml is a checkpoint, not a notebook

Observed in the wild (kaya-ai, FEAT-02 run t01-fe-eng): the eng lead's `state.yaml` carried
ad-hoc top-level keys — `pre_dispatch_checks:`, `lead_assessment_cycle_1:` — holding multi-line
prose list items dense with file:line citations and reasoning. Valid YAML, and no written rule
forbade it: harness-team specified the seed fields and the checkpoint discipline but never
constrained what *else* the file may hold, while separately declaring the lead's report artifact
is `digest.md`, "NOT state.yaml". The lead was duplicating digest material into the checkpoint
file.

Why it matters: `state.yaml` exists so a fresh context can decide recovery *mechanically* —
which steps are in flight, what cycle the run is on. Prose in that file is read, not matched;
it burns the budget of every context that must load the file to make a decision, and it invites
drift between the two copies of the same finding (the digest is collected once; the checkpoint
is rewritten every dispatch).

The rule, now stated in harness-team: every value in `state.yaml` is an identifier, an enum, a
counter, a path, or a sequence marker. One-line `note:` per step is the prose ceiling. Findings,
citations, and assessment reasoning go in `digest.md`; the step entry records only the verdicts
they justify. Test: a value that must be read rather than matched is in the wrong file.

Mechanized at DEC-156 (leads kept padding — the FEAT-02 audit found ad-hoc prose keys in all
15 run checkpoints): check-state.sh INV-16 now whitelists top-level state.yaml keys and rejects
duplicates.

## DEC-155 — Members run on their pinned model; a lead override is an escalation, not a parameter

Observed in the wild (kaya-ai, FEAT-02 ship, T-02): the eng-lead dispatched
harness-frontend-dev with an explicit `model: "opus"` in the Agent call. Claude Code's
resolution order puts a per-invocation `model` parameter above agent frontmatter, so the doer —
pinned `model: sonnet` in its definition — executed on claude-opus-5. Nothing sanctioned it: the
orchestrator's prompt to that lead never mentioned a model, the lead recorded no rationale, and
no rule forbade it. Dispatches in the same feature that passed no parameter ran sonnet as
pinned, confirming the pin works when left alone.

Why it matters: the model-per-agent assignment is org design — DEC-152 deliberately splits the
seven judging agents (opus, effort high) from the nine doers (sonnet, effort medium). A lead
that quietly upgrades its member re-decides that trade per-dispatch, invisibly: nothing in
state.yaml, the digest, or any gate records which model actually ran, so the cost shows up in
the budget with no cause attached. The failure mode is not the upgrade itself — a hard task may
genuinely warrant one — it is that the decision was free and unrecorded.

The rule, stated in harness-team (dispatch step) and the leads' zero-micro-management red
flags: never pass `model:` in a dispatch. Believing a task needs a stronger model is an
escalation — raise it in `open_questions` with evidence; the decision happens above the lead
and gets recorded. Same shape as DEC-31's reviewers-advise-don't-block: judgment is welcome,
unilateral silent action is not.

Mechanized at DEC-156: dispatch-guard.sh (PreToolUse on the spawn tool) rejects a harness
agent's dispatch carrying a `model:` parameter. The transcript JSONL (`"model":` on the spawn
record) remains the audit trail. Separately noted for cost accounting, not sanctioned against: the user-level
`advisorModel: opus` setting attaches an Opus advisor to every agent regardless of execution
model — that is Claude Code configuration, outside the org's authority.

## DEC-156 — Prose-only rules from the FEAT-02 audit get gates: digest file, checkpoint shape, dispatch parameters

The FEAT-02 (kaya-ai) output audit found three rule classes that were stated but had nothing
enforcing them, and all three drifted in the same run:

1. **The written team digest.** All 14 `runs/*/digest.md` files were narrative markdown with no
   §10.4 block — every one returns `BLOCKED (contract violation)` from `validate-digest.py lead`.
   The SubagentStop hook validates only `last_assistant_message`, so the in-message return passed
   while the durable copy — the one a successor context actually reads — did not comply. Nothing
   could have caught it: the gap is structural, not a lapse.
2. **The run checkpoint.** DEC-154's rule existed only as skill prose; all 15 state.yaml files
   carried ad-hoc prose keys, 15 different top-level key sets, and 12 carried a duplicate `cost:`
   key (`cost: pending_orchestrator` left in place when the orchestrator appended the cost block —
   YAML where the second key silently shadows the first).
3. **Dispatch parameters.** DEC-155's `model:` override ran unsanctioned because nothing inspects
   Agent-call inputs.

Same answer as DEC-19/DEC-122 — prose guarding a contract is unenforceable, a script guards it:

- **validate-digest.py --hook, extended:** after a lead's in-message return validates, the hook
  resolves the return's `artifact:` path and validates the FILE against the same lead schema;
  a non-conforming file is exit 2 while the lead is still alive to fix it. If the path cannot be
  resolved from the hook's vantage (worktrees, cwd drift), it passes through LOUDLY and the sweep
  below catches it — fail-open-with-signal, per the hook's own precedent, because blocking on our
  resolution bug would wedge legitimate leads.
- **check-state.sh INV-15:** for every run with `status: complete` and a lead host, `digest.md`
  must exist and pass `validate-digest.py lead` — the deterministic backstop that runs from repo
  root and cannot be fooled by cwd.
- **check-state.sh INV-16 (mechanizes DEC-154):** run state.yaml top-level keys must come from
  the checkpoint whitelist (seed fields + loop fields + pins), and no key may repeat. Prose keys
  (`pre_dispatch_checks:`, `lead_assessment:` …) are named in the rejection with their routing:
  digest.md.
- **dispatch-guard.sh (mechanizes DEC-155):** new PreToolUse hook on the spawn tool
  (matcher `Task|Agent`); a harness agent's dispatch carrying a `model:` parameter is exit 2 with
  the escalation route in the message. The main session (no `agent_type`) is never governed —
  model choice at the user channel is the user's. Registered in settings.snippet.json and
  checked by INV-9 like the other four mandatory hooks (now five).

Honest scope: the hook file-check is one-shot (`stop_hook_active` passes through, by design), so
a lead that fails the file check once and returns unchanged is caught by INV-15, not the hook.
INV-16's whitelist will need a new key added when the checkpoint legitimately grows a field —
that cost is the point: growing the checkpoint becomes a decision, not an accretion.

## DEC-157 — A cycle is a rework loop, not a run; the default budget moves into harness.json

`max_total_cycles` kept exhausting on healthy features and the escalations read as "budget too
low" (kaya-ai FEAT-01: raised 10 → 30 → 40 → 44 by three user decisions, closed at 42 used;
FEAT-02: raised 10 → 22, closed at 19). The audit of those numbers says otherwise: FEAT-02's 19
"cycles" span 16 runs, of which only ~6 were rework — three fix runs (design-fix, t02-fix,
sc02-fix) and three runs carrying one internal send-back each (t01, t04, t05). The rest were
first-pass runs counted as cycles because leads reported `cycles: 1` for clean runs and the
orchestrator summed them. So any feature with more than ~10 planned runs mechanically went
BLOCKED with zero failures — the same protect-nothing stop DEC-134 removed from the cost bound,
now caused by the retry bound counting the wrong unit.

Two clarifications, no new machinery:

- **The unit: `cycles_used` counts REWORK ONLY.** It increments when a FAIL is routed back, when
  an unmet SC re-dispatches, or when a lead reports send-backs inside a run — never for a
  first-pass run. A clean run reports and contributes **zero** cycles (a lead's digest
  `cycles_used` is its send-back count, not its step count). First-pass work is already bounded
  by the PLAN's task list, which has a natural end; the cycle budget exists solely for the loop
  that does not — consecutive rework. Inflating the number instead (30–50 while counting runs)
  was rejected: it defeats the bound's one job, killing a genuine runaway loop early.
- **The default: `budgets.max_total_cycles: 10` in harness.json.** Until now no default existed
  anywhere — the only "10" was SPEC's illustrative feature.yaml, which orchestrators copied;
  kaya's own orchestrator Expertise records the gap ("a max_total_cycles written into
  feature.yaml is an orchestrator guess and wants a PLAN Decisions entry"). The orchestrator now
  seeds `feature.yaml` from the config value, same source-of-authority shape as
  `max_cost_usd` ← `budgets.per_feature_usd`. Ten *rework* loops fits the evidence: FEAT-02's ~6
  true rework cycles clear it, and ten consecutive fix loops on one feature IS the runaway the
  bound exists to kill. Raising it per-feature remains a user decision recorded in feature.yaml,
  as both kaya features already practiced.

Not mechanized: nothing distinguishes a first-pass run from a rework run in state files, so a
checker cannot recount cycles independently; INV-7 (cycles_used ≥ recorded FAIL runs) remains
the floor. Revisit if run records gain a `rework_of:` marker.

**Amendment am.1 (issue #79): runs are COUNTED too, informationally — INV-22.** This entry's own
consequence is that a first-pass run contributes zero, so nothing counted total runs at all:
FEAT-03 ran **19 times against a 6-cycle count** and tripped nothing. Cost was the other
long-feature signal and DEC-178 deleted it, leaving no signal whatever.

`check-state.sh` INV-22 notes `len(runs)` against `budgets.max_total_runs` (default 20, from a
measured range of 1-19 across nine features). **Informational, never a gate** — the exit code is
identical over and under, and a fixture asserts that. A high run count is not a defect: a long
feature is fine when each run is efficient, resolves issues and advances the SCs, which is what the
note asks rather than demanding justification for the number.

Two properties are load-bearing and each has a fixture, because the first cut had neither.
**The count is a FLOOR** — a main-session-direct segment is not a run and never appears in `runs:`,
which on FEAT-07 hid eight of ten tasks — so the message says so. **A budget it cannot resolve is
REPORTED, not silently dropped**: a `harness.json` that parses but lacks the key used to disable
the check with no diagnostic, and `templates/examples/harness.kaya-ai.json` ships in exactly that
shape. DEC-160 records the identical config lag for `max_total_cycles`.


## DEC-158 — Context-budget pass: skills carry the rule, DECISIONS carries the rule's history

**Amendment 1 (2026-08-24) — move 3 is widened from rare missions to any bounded PROCEDURE, and
three of this entry's statements are corrected.**

*What went stale.* `references/missions.md` no longer exists: missions map and deepen were retired
with the codebase map tier (DEC-137, struck), and mission debug — the only survivor — moved to
`references/debug-mission.md`. Ship-refresh, named above as staying inline because it "runs every
ship", was removed with the same tier. Feature-close distillation does stay inline and still does,
though it is now triggered at merge rather than at close-out (DEC-145).

*What changed.* Move 3 as written keyed on FREQUENCY — rare missions move, every-ship work stays.
That criterion does not survive contact: the `gh-sync.py` contract runs every ship and the
context-probe runs every wake, yet both are step-by-step procedures an orchestrator consults once
and does not need resident for the rest of its life. **The criterion is now SHAPE, not frequency: a
bounded procedure with a named trigger moves to `references/` and leaves a pointer; a rule that must
be resident to be obeyed stays inline.** A procedure is looked up when its trigger fires. A rule has
to already be in context at the moment it would otherwise be broken.

Applied: `references/github-mirror.md` (the nine subcommands, their owners, the station table and
the failure shapes) and `references/context-check.md` (the two-call nonce probe). The playbook keeps
the rule that governs each — you run three subcommands and no others; the threshold advises and a
check you cannot complete is skipped, never guessed.

*The cost, stated because it is real.* Every pointer can be skipped, and a skipped pointer is
silent. The preload-versus-pointer measurement — every artifact delivered by preload worked on first
contact, every artifact relying on being pointed at failed silently at least once (DEC-125 ×4) —
still stands, and the playbook now carries five pointers where it carried one. That is the bound:
**move 3 is not a licence to keep extracting.** Distillation, the CEO briefing and the build phase
were each considered for extraction and each kept inline, because their triggers fire on the ship
path where a silent skip costs the most.

*Move 1's red-flag protection is NARROWED, not repealed.* The orchestrator playbook's `## Red
flags` table is removed on the operator's word. The supporting observation: after this pass all six
of its rows restated rules still present in the body — no user channel, lead-not-member, pm re-plans,
the hard cycle bound, counters on disk, shape is not truth — so the table carried no rule of its own.
The counter-argument this entry made still stands and is recorded here rather than lost: bare
imperatives get rationalized around (DEC-19's lesson), and a rule stated once as prose and once as a
named temptation is harder to talk past than a rule stated once. That trade was taken knowingly.
**The other nineteen red-flag tables in the tree are untouched** — this narrows move 1 for one file,
it does not withdraw the pattern.


Measured per-spawn preload (agent file + `skills:` + injected Expertise): orchestrator ~12.3k
tokens, leads ~8.4–9.2k, dev specialists ~4.8k — replayed across every spawn (kaya FEAT-02:
58 frontend-dev, 46 product-lead spawns). Profiling the two largest skills (`harness-team` 3.6k
words, `harness` 3.5k) showed ~25–30% was not rules but rule *history*: incident narratives,
"this used to say X and was measured false", superseded-rationale walkthroughs. That is
DECISIONS.md's genre in the agents' hot path — an agent needs the rule and one clause of why,
not the rule's biography, and since DEC-156 several of those paragraphs restate what a gate now
enforces mechanically.

Four moves, in force for all rule skills:

1. **Rule + one-clause why + DEC pointer.** History, incident detail, and superseded reasoning
   live in DECISIONS.md only. Red-flag tables and one-clause whys stay — bare imperatives get
   rationalized around (DEC-19's lesson), and the tables are dense.
2. **Conditionally-relevant skills load on demand.** `harness-systematic-debugging` leaves the
   five dev specialists' preload (its own description says "when working a bug"); a debug-mode
   dispatch prompt tells the specialist to Read the skill file first (devs hold Read, not Skill).
   ~800 tokens off every non-bug dev spawn.
3. **Rare-mission playbook sections move to `references/`.** Missions map and deepen run between
   features, not in the plan/ship loop every orchestrator spawn serves; they live in
   `.claude/skills/harness/references/missions.md`, read by path when dispatched with that
   mission. Ship-refresh and feature-close distillation stay inline — they run every ship.
4. **Single-source shared contracts.** One canonical copy, pointers elsewhere (the
   `harness-digest-dev` pattern). Applied here to the DEC-155 dispatch rule (now one line +
   pointer in harness-team, since dispatch-guard.sh enforces it mechanically) and the stale
   BUILD-task-22 roll-up warning (the "until that is fixed" box outlived its fix, FEAT-02).

Kept deliberately: the whys themselves, red-flag tables, and everything load-bearing for
compliance. The real kaya token sink — orchestrators at 258–310k cache-read/turn from session
longevity — is DEC-148/150's problem, not the skills'; this pass buys latency and instruction
signal, not a cost order-of-magnitude.

**Applications of move 2, and the wording each one falsified.** Move 2 is applied repeatedly, and
each application invalidates statements elsewhere in the tree. Declaring them here rather than
opening a new decision per application keeps DECISIONS.md the single registry without growing an
entry for something that is not a new decision:

- **`harness-distill` split out of `harness-expertise`** (issue #84). The write-rules left the
  universal preload; anything describing `harness-expertise` as carrying them is stale.
- **`harness-team` dropped from the orchestrator's preload** (issue #83). Flat mode — the
  orchestrator hosting a team DAG itself — is dead per DEC-100/DEC-102, so anything describing the
  orchestrator as a team host, or offering flat as a live hosting mode, is stale.








## DEC-159 — Orchestrators are per-phase; the handoff note carries intent, trust, and dead ends

The measured cost lever after DEC-158: kaya's context watchdog showed orchestrators at 258–310k
cache-read tokens per turn from session longevity alone — one long orchestrator outspends every
skill-trimming pass combined. DEC-148 already said "relay at phase boundaries if the phase took
more than ~10 dispatches", but it was advisory prose with a threshold judgment, and the field
evidence (kaya FEAT-01/FEAT-02) shows the successions that did happen worked mechanically while
losing the predecessor's working memory: inherited claims were stale at both successions (a "fix"
for an already-fixed defect, findings already closed at HEAD), and a pre-dispatch verification
once found half the requested work already done.

**The seam: per-phase by default.** An orchestrator's mission IS its phase (plan → build →
validate → ship); ending at the boundary is normal termination, continuing is the exception.
Exit predicates are disk-checkable: plan and ship end at user gates (those seams were always
free); build exits when every planned T-NN has a PASS run in feature.yaml. `feature.yaml` gains a
`phase:` field; transitions are STATE.md log entries. The fix loop is the sanctioned exception —
validator FAILs are worked inside the validate-phase orchestrator, not relayed per cycle; a fix
loop that runs long is what monitoring is for, and a mid-phase relay is the bounded escape.
Small features collapse naturally: short phases mean cheap sessions, and a feature small enough
to plan-and-ship in one sitting never meets a seam worth paying a relay for.

**The handoff: working memory, not summary.** Everything the checkpoint discipline covers is
already on disk; what dies with the context is exactly four things, so the note
(`notes/handoff-<ending-phase>.md`, template `templates/HANDOFF.md`, ~60-line cap (raised from 40 at DEC-160),
superseded never appended) has exactly four sections:

- `## Next` — the decided-but-not-dispatched action, cited to PLAN.
- `## Trust` — claims the successor will act on, one line each in the grammar
  `claim — evidence pointer — verified-at <sha> | UNVERIFIED`. Written at the calm moment a
  phase ends, NEXT is nearly deterministic; the trust flags price re-verification for the rest.
- `## Dead ends` — exclusions active for the next phase, same grammar; no pointer, no entry.
  Durable exclusions belong in PLAN Decisions or observations, never here.
- `## Working set` — the 3–5 paths read first; everything else is archive.

The successor's step zero is validating `## Next` against PLAN/STATE (one grep) — the note never
grants trust, it prices it. STATE.md remains the single durable truth per feature, `## Current`
replaced across every orchestrator that ever serves it; the note is ephemeral and dead once
validated. **Disk-only reconstruction stays fully supported** — the note is an accelerator, and
nothing may ever require it, or a crash becomes unrecoverable.

**Enforcement, the digest pattern (DEC-156) pointed at a new artifact:** check-domain.sh's
DEC-150 write-time shape gate grows a third pattern — handoff-*.md is denied on a missing
required heading or >40 lines while the author is still alive to fix it; check-state.sh INV-17
flags a feature whose `phase:` sits past a seam with no handoff note for the crossing, or a
note that fails the shape.

**The in-flight warning, and the metric it is not.** The watchdog is no longer only a post-hoc
audit: `.claude/skills/harness/bin/context-watch-hook.py` is a PostToolUse hook registered in
`.claude/settings.json` on the existing `Write|Edit|Bash` matcher, and it tells a running
`harness-orchestrator`, in its OWN context while it runs, the moment its measured prompt size
reaches `budgets.orchestrator_context_warn_tokens` (DEC-198). That is a different measurement
from the one deferred here. What this entry deferred was a turn-count nudge — warn an
orchestrator that is N turns deep mid-fix-loop — and what shipped is a context-size threshold
instead: same function, different metric. The turn-count nudge remains deferred; nothing counts
an orchestrator's turns, and the live fix loop that would justify it has still not been
observed. The warning advises and never refuses — its own text says "this advises only; the
orchestrator decides", and PostToolUse fires after the tool has already run, so its exit 2
carries text back to the orchestrator and stops nothing.

**The mid-flight case, which the seam rule does not cover.** Per-phase assumes a boundary is
reachable; the warning can land when a phase is genuinely mid-flight. A warned orchestrator
determines the nearest seam and writes the state a successor needs before it ends. Where no seam
is reachable it writes a mid-phase handoff rather than continuing — the same note, the same four
required sections, the same cap. This is when "a mid-phase relay is the bounded escape" above
applies, and the note is what bounds it.

Relay economics, stated once: a succession costs a fresh ~10k preload plus the working set
(~30–50k total) and is won back the moment it prevents a handful of 300k-cache-read turns.

## DEC-160 — First live handoff: the cap was tight, the sweep does not deter, and deploy cannot ship config

FEAT-03 (kaya-ai) crossed the plan seam within a day of DEC-159 landing, and the first live
handoff note was written unprompted — content exactly to spec: trust entries carrying
`verified-at <sha>` and an honest `UNVERIFIED by me at source — I accepted pm's reading` on the
heaviest premise, dead ends with pointers, a validated `## Next`. Three findings from watching it:

1. **Cap 40 → 60.** The note ran 49 lines with zero fat — every line changed what the successor
   does. A cap the first compliant artifact violates is mis-set; 60 keeps the not-a-second-STATE.md
   pressure while fitting a real four-section handoff. (Also fixed: INV-17's message printed
   `missing []` when only the length failed.)
2. **Run state.yaml gets the write-time gate (mechanizes DEC-154 fully).** The first post-deploy
   run violated INV-16 within hours (`lead_checks:`, top-level `note:`) — the entry-time sweep
   reports but demonstrably does not deter. check-domain.sh now denies a run state.yaml Write
   carrying non-whitelisted or duplicate top-level keys, same pattern as feature.yaml/STATE.md/
   handoffs. The whitelist is deliberately duplicated in check-state.sh (INV-16) and
   check-domain.sh, cross-referenced by comment — two scripts, no shared import, files-only.
3. **INV-18: run dirs without feature.yaml.** FEAT-03's whole plan phase ran before feature.yaml
   existed, during which INV-8/12/17 had nothing to key on — a feature can complete a phase
   invisible to every feature-keyed invariant. Now flagged.

Also surfaced, fixed out-of-band: deploy.sh never writes project state (by design, DEC-113), so
DEC-157's `budgets.max_total_cycles` default never reached kaya's `.harness/harness.json` — the
handoff's Trust section caught the discrepancy against SKILL.md. Added to kaya directly; the
general path for config-schema additions remains `/harness-init --upgrade`, and a DEC that adds a
harness.json key must say so.

## DEC-162 — The glossary gets a checkable moment; domain-modeling is otherwise already resident

Assessed Matt Pocock's `domain-modeling` skill for adoption (the user's ask). Finding: DEC-149
already cloned its core into `harness-spec-driven`'s glossary section — challenge drift, sharpen
fuzz, code-wins, update-inline, glossary-never-a-spec — and its ADR three-part test is verbatim
the D-NN bar, where harness's version is stronger (approval-gated). Not adopted, deliberately:
multi-context maps (`CONTEXT-MAP.md`) — no project has bounded contexts yet, and speculative
structure fails the deletion test.

What WAS missing is enforcement: `.harness/codebase/glossary.md` was "create lazily when the
first term is resolved," and across three shipped kaya features that fired zero times — while a
four-status enum and a review-loop vocabulary were being pinned. The same failure shape as any
obligation recorded only in prose — "run the map first" lived that way, and a feature build ran
before the map: a duty attached to no checkable moment does not happen. pm's
domain has granted the path since DEC-149; nothing assigned the work.

Two changes: mission map now assigns pm `glossary.md` alongside `product-surface.md` — the map
is the checkable moment the language gets recorded; and check-state INV-19 warns (INV-14's
level: flows still run) when a mapped codebase has no glossary. Existing mapped projects get
seeded from their shipped features' pinned vocabulary rather than waiting for a re-map.

## DEC-163 — A null test runner over a real surface is a gap that gets escalated, not absorbed

`cmd: null` is the honest record dev-ops is required to write when it finds no runner for a test
kind (never invent a plausible command — DEC-100-era rule, still right). What was missing is what
happens next. qa resolves a null kind to a **soft skip**, so an SC resting on it can never be met
and never fails loudly; pm, correctly avoiding that trap, quietly stops writing SCs against the
kind. The result is a gate that looks real and does nothing, chosen by nobody.

Measured in kaya: `ui`, `eval` and `integration` are all null, while the codebase map describes
`ui-surface.md` at 292 lines, `llm-patterns.md` at 203, and `data-flows.md` at 315 — three real
surfaces with no runner. Across three shipped features nothing ever escalated it; FEAT-01 had to
note in its plan that `cross_module`'s integration evidence "records as skipped, carried by
unit+functional", and FEAT-03 pinned all 17 SCs to the two kinds that exist. Correct planning,
invisible consequence.

**The discriminating check is the codebase map** — it already records which surfaces exist, so a
null runner matters exactly when its surface view is more than a self-scoped-out stub (a CLI with
no `ui` runner is fine; a web app with none is not). Three surfacings, one per audience:

- **check-state.sh INV-20** (warn-level, INV-14's level — flows still run): a null kind whose
  mapped surface exceeds a stub is reported at every `/harness` entry, naming the kind, the view,
  and both remedies. Verified: fires on exactly kaya's three, silent on the two with runners.
- **BRIEF `## Verification gaps`** (`harness-brief`): pm may never rest an SC on a null kind — that
  much was already implied — and now must record, where the user signs, what is therefore NOT
  proven and what carries it instead. The approval gate is the visibility moment.
- **Onboarding** (`harness-init`): every remaining null kind is put to the user as a decision —
  stand up the runner now, or accept the gap knowingly — with an accepted gap going to the backlog.

Not mechanized: nothing blocks a feature over a null kind, deliberately. A missing runner is a
priority call the user makes, and hard-failing on it would stop work the org can still do honestly
(the DEC-134 lesson about bounds that protect nothing).

## DEC-164 — Grilling is blocking step zero: dialog to clarity before the org spends a spawn

pm plans from what it is told, and the org's most expensive failures start as unstated assumptions:
**five kaya premises briefed as fact were FALSE at HEAD** on one feature, caught only because a
successor re-verified them. The cheapest place to find that is in conversation with the user, before
any spawn. Adopted from Matt Pocock's `grilling`/`grill-me` and the transferable half of
`wayfinder` (MIT), re-homed onto harness machinery.

`harness-grilling` is **main-session only** — the sole tier with a user channel (DEC-120), and an
agent that answers its own questions has broken the discipline. The rules: one question at a time
with a recommendation attached; **facts are the agent's to find, decisions are the user's**;
dependencies first; challenge language against `glossary.md` as you go; never act until the user
declares shared understanding.

From wayfinder, three ideas earn their place without its machinery: **name the destination first**
(it fixes scope, so everything else is judged against it), **fog of war** (`## Not yet specified` —
in-scope questions not yet sharp enough to state; the test is the question's sharpness, never
whether you can answer it), and **out of scope** (ruled beyond the destination; scope, not
sharpness, lands it there). The artifact is `.harness/notes/grilling-<slug>-<date>.md`, one screen,
whose `## Settled` seeds BRIEF's REQs and whose `## Facts I verified` saves pm a research pass —
handed to pm as a **path**, never a transcript.

Wired blocking at two doors: `/harness-plan` step zero, and `harness-init`'s interview (whose
answers also seed `harness.json`, the domain description, and the first glossary terms). Skipping
it is the user's explicit call, never the main session's assumption.

Wayfinder's full form was deferred here and **adopted at DEC-165** once the user named the actual
goal (vague → plannable, which is wayfinder's own purpose): as local markdown under
`.harness/efforts/`, never on the tracker, since DEC-138 makes the mirror outbound-only and the
frontier is a read.

## DEC-165 — Wayfinding adopted: a local-markdown map for ideas one sitting cannot hold

DEC-164 deferred wayfinder's full form as speculative. The user corrected the premise: the point of
grilling *and* wayfinding is one pipeline — take an idea from vague to clear enough that (a) we are
aligned and (b) it can be handed to planning. That is wayfinder's own stated purpose, and the org
had only the one-sitting half of it. Kaya's own roadmap thinking ("the visibility, context and
system-of-record layer for 3PL ops") is exactly the shape a single conversation cannot settle.

Adopted, with the three things `harness-grilling` structurally could not do:

1. **Persistence across sittings.** The grilling artifact is a one-shot record with no notion of
   what is takeable next. A map at `.harness/efforts/<slug>/` — `MAP.md` (index) plus
   `tickets/T-NN-<slug>.md` (one decision each) — survives between sessions; the **frontier** (open
   tickets whose blockers are closed) is what a fresh session reads to know where to stand.
2. **Ticket types, because not every unknown is a conversation.** `research` (agent alone — a
   decision waiting on a fact is the agent's job, never a question for the user), `prototype` (build
   something cheap to react to when "how should it behave" is the question), `grilling` (the
   default), `task` (something must exist before a decision is possible). A HITL ticket the agent
   answers itself is a fabricated decision — worse than an open ticket.
3. **One decision per session** (research excepted) — which also carries DEC-159's discipline into
   the pre-feature phase: a long session writes worse answers, and the map is what makes stopping
   free.

Two harness-specific rulings. **The map is local markdown for now** — and the first stated reason
for that was WRONG, corrected here: DEC-138's outbound-only rule governs mirroring *approved*
feature work ("issues are pm's research INPUT at plan time… after approval, sync is strictly
OUTBOUND"), and wayfinding happens entirely before any approval, so it was never constrained by
it. The honest reasons are practical: markdown works with no network, no repo and no `github.sync`,
adds no read paths to `gh-sync.py`, is committed with the code (so it lands in PR diffs and
outlives the transcript window), and keeps one copy of the truth.

**The source skill supports both modes** (tracker when provided, "default to the local-markdown
tracker" when not), and the user's stated preference is the faithful tracker form — map issue
labelled `wayfinder:map`, tickets as sub-issues, native blocking edges, assignee as the claim,
resolution as a comment — because a map that spans days is a *shared* artifact and GitHub is where
a human can read it, add a ticket, or see the frontier render without opening a session. **Not
built yet, deliberately, pending the user's go-ahead**; when it is, tracker-mode is preferred where
`github.sync` is on with markdown as the fallback, and the "decision as an issue invites drive-by
reopening" concern from DEC-138's amendment does not transfer — that guards *signed* D-NNs, while
wayfinding decisions are provisional by construction.

**Charting and resolving are separate sessions** — a session that charts and then starts resolving
does both badly.

The entry test keeps the two doors honest: fits one conversation → `/harness-grilling`; the destination
itself is fuzzy or decisions wait on facts and prototypes → `/harness-wayfinding`; a grilling that
stalls on "we cannot answer that until we know X" gets **promoted** to a map carrying what is
settled. A map with three tickets you could have talked through was a worse conversation.

Terminus, either door: decisions, never deliverables. `/harness-plan` takes the artifact path —
`## Decisions so far` is what pm authors REQs from, `## Out of scope` is what keeps BRIEF scope
honest, ticket resolutions are there to zoom. pm still owns REQs, SCs and tasks; wayfinding removes
the fog, not pm's job.

## DEC-166 — Wayfinding switches to the tracker: sub-issues, native blocking, assignee-as-claim

DEC-165 built the markdown map and recorded the tracker form as preferred-but-unbuilt. Built now, on
the user's go-ahead, and **verified before building rather than assumed**: `gh` 2.92.0 with
`repos/{repo}/issues/{n}/sub_issues` and `repos/{repo}/issues/{n}/dependencies/blocked_by` both
live on the pinned repo, so the faithful wayfinder shape — map issue, tickets as sub-issues, native
blocking edges, assignee as the claim, resolution as a comment — is fully implementable with no
degraded body conventions.

Why the tracker wins where it is available: a map that spans days is a **shared** artifact. The
human reads it, adds a ticket, or sees the frontier render in GitHub's own UI without opening an
agent session — which is the entire point of a map versus a one-shot grilling record. Storage is
chosen by **config, not preference**: `github.sync: true` and a working `gh` → tracker; otherwise
local markdown, which stays fully supported (no repo, no network, no sync still works).

**`bin/wayfind.py` owns every tracker operation** — `map` · `frontier` · `chart` · `ticket` ·
`block` · `claim` · `resolve` — because three of them are traps by hand, which is exactly the
DEC-19 test for when prose must become a script: the sub-issue API takes the child's internal `id`
and NOT its `number` (a number silently attaches the wrong issue or 422s); the frontier is a
compound query (open AND every blocker closed AND unassigned) that no single `gh` invocation
expresses; and a ticket created without its `wayfinder:<type>` label is invisible to every later
query. Mutations are **dry-run until `--apply`** (deploy.sh's precedent — this writes to a shared,
human-visible surface, so the plan is shown first), and the script refuses to run at all when
`github.sync` is off, pointing at markdown mode instead.

Read paths verified live against the pinned repo; write paths are dry-run verified only — the first
real `chart --apply` is their live test, deliberately not run against a production tracker to avoid
leaving a test map behind (GitHub issues do not delete cleanly).

Recorded because it is the reasoning that changed: DEC-165's original objection — that DEC-138's
one-way rule forbade this — was **wrong**, and was corrected in place. DEC-138 governs mirroring
*approved* feature work and explicitly sanctions issues as pm's research input at plan time;
wayfinding runs entirely before approval, so the frontier being a read breaks nothing. The adjacent
concern ("a decision as an issue invites drive-by reopening") guards *signed* D-NNs — wayfinding
decisions are provisional by construction, and reopening one is the point of a map.

## DEC-167 — Frontier rounds for speed; GitHub is the canonical store, with no markdown shadow

Two corrections after DEC-166, both from the user's reading of how it would actually feel to use.

**1. "One decision per session" was over-read as slow.** The rule bounds how deep a single decision
is explored (DEC-159's anti-degradation logic); it never required serialising *independent*
decisions, and frontier tickets are by construction unblocked by each other. Two speed levers,
neither costing rigour: fire every frontier `research` ticket in **parallel** at once (no user
needed, and fog most often hangs on facts), and put the frontier's HITL tickets to the user as **one
numbered round** with a recommendation each — Matt Pocock's `batch-grill-me` shape, which is the
same author's answer to the same problem. Drop back to one-at-a-time the moment a question needs
real exploration or an answer would change what the next question is; that is a dependency, and
dependencies serialise. `wayfind.py round <n>` computes both lists. Also clarified: **a session is a
context, not a calendar day** — six back to back in an afternoon is the intended use and costs one
map reload each, so "clarity as fast as possible" and "context-cheap" are not in tension.

**2. Tracker mode has no markdown shadow.** `resolve <n> <file>` implied a local file per decision,
which would recreate the two-copies drift this org keeps finding (the digest.md gap, the qa-gate
matrix table). Now explicit, and `--body "<text>"` is the default path so a short answer needs no
file at all: the **dialog** is saved nowhere (it is the transcript — ephemeral, and a verbatim log
is not a decision); the **decision** is the ticket's resolution comment; the **gist** is one line in
the map's `## Decisions so far`; a substantial **asset** is a repo file *linked* from the comment,
never pasted and never a second copy. Markdown mode remains the whole store only when
`github.sync` is off — never alongside.

**And the gist is written by the tool, not remembered by a human.** `resolve` now REQUIRES
`--gist "<one line>"`, discovers the ticket's map itself (the sub-issues `parent` endpoint —
verified live), and appends the line to that map body's `## Decisions so far` in the same
invocation as the comment and the close. Three drift holes closed at once: a resolution recorded
only on its ticket (the map silently stops being an index), a gist written on the sub-issue instead
of the map, and a hand-edited map body diverging from what the tickets say. It refuses to run if the
map has no `## Decisions so far` section, rather than putting the line somewhere plausible.

**The round mechanism belongs to both doors, on a two-axis test.** `harness-grilling` said "one
question at a time" flatly while its sibling batched the frontier — a contradiction between two
skills the same session loads. Both now carry one rule, and the first draft of it conflated two
different axes; corrected: **batch only what is BOTH independent and shallow** (a recommendation
plus a pick settles it). Serialise anything **dependent** (an answer changes the later questions) or
**deep** (it needs back-and-forth to reach an answer) — independence alone does not make three deep
questions one round, and depth alone does not make two shallow ones serial. `prototype` tickets are
never line items in a round: the artifact *is* the exchange, so it gets its own thread even when it
sits on the frontier beside batchable questions. A ticket on the frontier only because its
dependency was never wired is not independent, it is mis-wired. **The user's stated preference
outranks the whole heuristic** — how they want to be asked is their decision, not a tuning
parameter.

## DEC-168 — Sub-issue closure does not cascade, in either direction (measured)

Probed live in `mruangutai/harness` (scratch issues #1 parent, #2/#3 subs, all since closed and
annotated) because `close-task`'s correctness under the sub-issue model depends on it and nothing in
the docs consulted stated it. Three results, all favourable:

| Action | Result |
|---|---|
| close ONE sub of two | parent stays **open**; summary → `completed: 1, 50%` |
| close the LAST open sub | parent **stays open**; summary → `completed: 2, 100%` |
| close the PARENT with two open subs | subs **stay open** |

So closure is entirely manual in both directions. What that buys the DEC-138 sub-issue migration
(explored in `.harness/notes/explore-pm-tickets-subissues.md`): `close-task` on a task's sub-issue
closes exactly that task — the FEAT-03 "CLOSE-TASK HAZARD, ELEVENFOLD" cannot recur; the parent must
be closed deliberately at ship acceptance, so it never drifts closed on its own; and a parent closed
early cannot silently orphan-close outstanding tasks.

One operational gotcha for any implementation: **`sub_issues_summary` is eventually consistent.** It
read `total: 1` immediately after the second attach and corrected to `total: 2` seconds later. Never
assert on it right after a write — the same class of mistake as reading a cost meter before it
settles.

### DEC-138 amendment 5 — the silence rule is the MIRROR's, and abandonment closes `not_planned`

Two clarifications the sub-issue exploration forced.

**Scope of am.2's silence.** "No agent-authored comments in the org's repo" was written for the
**mirror** — the orchestrator mechanically reflecting signed work — and as a v1 caution ("until the
mirror proves itself on a real feature"; three features have now mirrored). It does **not** govern
wayfinding, where the resolution comment on a decision ticket **is** the artifact, not commentary on
someone else's work (DEC-166/167), and where the author is the main session rather than a mirroring
agent. The mirror stays silent: it creates, closes, and cites absorptions, and never editorializes.

**Abandonment closes `not_planned`** (user decision). Verified enum — GitHub's `state_reason` accepts
exactly `completed`, `not_planned`, `duplicate`; `not_doing` returns 422, so "not doing" could only
ever be a label, never a close reason. `not_planned` renders a visually distinct icon, which is the
point: an abandoned feature must not read as a shipped one at a glance. The *reason* it was dropped
**is posted as a comment, verbatim from the signed ship-review artifact** — see am.6; a closed issue
with a distinct icon and no explanation is opaque to the only audience the mirror exists for.

**Not implementable until the sub-issue migration, deliberately.** Today's recorded issues are
adopted backlog items — all eleven of FEAT-03's tasks point at #48, which is still wanted — so the
mirror has nothing that is unambiguously the feature's to close, and closing an adopted issue
`not_planned` would assert something false about live work. Post-migration: close the feature's own
**sub-issues** `not_planned`, leave the adopted parent open, close the milestone (milestones take no
`state_reason` — close is close). That gives `cmd_ship` and a new `cmd_abandon` the same shape, one
per terminal state. (Originally filed as am.4 — renumbered to am.5 on discovering a collision with the
existing am.4 on briefing-gated residuals.)

### DEC-138 amendment 6 — the comment rule is about PROVENANCE, not about which skill is asking

am.2 banned agent-authored comments outright, as a v1 caution ("until the mirror proves itself on a
real feature" — three have now mirrored). am.5 then carved out wayfinding, which was the right
outcome reached by the wrong reasoning: the exemption is not "wayfinding is special." The user
identified the actual line, and it is **provenance**:

> **Anything posted into the org's repo is either the user's own words, or text the user signed.
> Agents doing the work post nothing, ever.**

What that permits and forbids, in every case the org has:

| Post | Provenance | Verdict |
|---|---|---|
| a wayfinding ticket's resolution comment | the user's own answer, captured live | **allowed** — it IS the decision record (DEC-166/167) |
| an abandonment reason on a closed issue | a line from the ship-review the user signed, posted **verbatim** | **allowed** (am.5) |
| a ship summary on the parent issue at acceptance | same — signed artifact, verbatim | **allowed** |
| a dev / reviewer / qa / lead commenting mid-build | unreviewed agent prose | **forbidden** — they return digests; a second status channel competes with `STATE.md` and drifts from it |
| the mirror composing its own text at post time | agent prose, however brief | **forbidden** — mirror what was signed, never author |

The mechanism follows from the rule: any subcommand that posts takes its body from a **file path**,
never from a string the mirror assembled. `--reason-file <path>` / `--body-file`, pointing at the
approved artifact. That makes the constraint mechanical rather than a matter of restraint — the mirror
*cannot* editorialize because it has no text of its own to post.

Unchanged: the mirror is still write-only, PLAN.md is still the truth, and issue state is still never
read back into an approval-gated artifact (DEC-138 proper).

### DEC-138 amendment 7 — the sub-issue mirror: one parent per feature, and `absorbs:` closes nothing

The shipped shape of the GitHub Issues mirror after the sub-issue migration. Two things here reverse
earlier text; the rest is the contract as the code now runs it (`.claude/skills/harness/bin/gh-sync.py`).

**The `absorbs:` rule is STRUCK 2026-08-25 under DEC-188.** It said a task's issue body cites
`absorbs: #12, #14, #31`, closes none of them, and leaves them for a human signature, because
absorption is normally partial. The operator struck the concept whole: it named a third category
between "this feature does the work" and "it does not", and no such category exists. A sub-issue is
a ticket. It is planned, tasked and shipped like any other, by whoever picks it up.

DEC-138's own body carried the text this clause superseded — absorbed issues "close with it". That
text is struck in the same act and does NOT revive; nothing in the tree now says an issue closes
because another task mentioned it.

What replaces both: **a ticket is open while its card is not at the `Done` station, and a parent
closes when it has no open children.** Station is the authority on open, not the issue's own state.

**`open` creates one sub-issue per `T-NN` under a single parent, adopted-or-created but never
discovered.** Precedence, first match wins: (1) `feature.yaml github.parent` already holds a number →
use it; (2) `--parent <n>` on the command line → adopt it; (3) otherwise `open` **creates** one, title
`<FEAT-NN-slug> — <the BRIEF H1's human phrase>`, body = the BRIEF's Problem plus `**Goal:**`, label
`harness` (`gh-sync.py:255-271`). The number is **recorded** at `feature.yaml github.parent`, and calling the
parent endpoint to *find* it is rejected: that is a READ, and DEC-138 makes the mirror write-only —
idempotency comes from local receipts, so a discovery path would be a second, contradictory source of
truth. Children attach by the child's internal **`id`**, never its `number` (the trap of DEC-138's
live probe). The **origin** is recorded at the same moment as the number, at
`feature.yaml github.parent_origin` — `created` or `adopted` — because re-deriving it later would mean
reading GitHub.

**Both terminal subcommands branch on the recorded origin.** `ship` and `abandon` are mirror images,
and the parent's fate is conditional in both:

| | created parent | adopted parent | no recorded origin | milestone |
|---|---|---|---|---|
| `ship` | closed — `issue close` with no `--reason`, i.e. GitHub's default `completed` | left **open** | left **open** | closed |
| `abandon` | closed `state_reason=not_planned` | left **open** | left **open** | closed |

`abandon` additionally closes the feature's **own** sub-issues `not_planned`, and posts the signed
reason on any recorded parent whatever its origin; `ship` posts the signed `--body-file` the same way.
Milestones take no `state_reason` — close is close — and the milestone's close **does not depend on the
parent's origin: it closes in all three parent cases** (`gh-sync.py:379-410`, `:317-355`). Neither
subcommand closes a parent it did not create.

Why the branch, recorded because it cost this feature two of its three fix cycles:

- a **created** parent is this feature's own container; left open with every child closed it is an
  orphan nothing will ever close;
- closing an **adopted** parent would assert something false about someone else's live backlog item —
  `completed` and `not_planned` are *both* false claims about a thing this feature does not own;
- **absent or unrecognised origin defaults to leave-open.** Stated explicitly because SC-10 forbids
  editing the `github:` block of any existing `feature.yaml`, so no pre-existing feature carries the
  marker — this feature included (`FEAT-03-subissue-mirror/feature.yaml:73` is `parent: none`).

**Shared code, and migration scope.** REQ-06's three primitives — the internal-id attach, the parent
read, the blocking-edge write — plus the internal-id lookup and `gh_bin()` now live in exactly one
place, `.claude/skills/harness/bin/gh_issues.py`, as **argv builders**; each caller keeps its own
runner, because `gh-sync.py` skips-and-exits-0 on an environmental failure while `wayfind.py` dies exit
1. `gh-sync.py` imports only `internal_id_args` and `attach_sub_issue_args`; its containing **no** call
to `parent_args` or `blocked_by_args` is a standing regression guard for the write-only rule.
**Migration is new-features-only** — no backfill, no retrofit, no edit to any existing feature's
recorded map.

**Not here yet.** Feature B — `depends_on:` in PLAN becoming `blocked_by` edges — is sequenced
separately, and **no `blocked_by` edge is emitted by the GitHub Issues sync**: the builder exists but
its only caller is wayfinding (`wayfind.py:283`).

**Two prose sites are a named main-session pre-ship step, not an agent's** (SC-13):
`.claude/skills/harness/SKILL.md:137` still reads "closes its issue and everything it absorbs" — the
superseded contract — and `:144`'s ship row names only the milestone, where it must name the parent as
**conditional on its recorded origin**. No agent domain covers that file (`team-config.yaml` grants
`.claude/skills/harness/bin/**` and nothing else under `.claude/skills/` — `:154`, `:193`), so it returns to the main session before ship. Deliberately, this
amendment declares **no** staleness marker for either phrase: `check-docs.sh` scans
`.claude/skills/**/*.md`, so a marker for wording that is still live would turn the checker red and gate
every `/harness` entry on an edit no agent may make. The checker is silent about this gap **by design**;
SC-13's own grep at the ship gate is what detects it. If the mechanical route is preferred, the ordering
is: land the SKILL.md edit first, then a marker may be declared — never before.


### DEC-138 amendment 8 (2026-08-25) — the parent origin table is struck, and the harness writes the `Done` station

Amendment 7's **origin table is struck** under DEC-188, together with the origin prose around it.
That table gave `ship` and `abandon` three columns — a `created` parent closed, an `adopted` parent
left open, no recorded origin left open — and the surrounding paragraphs argued the case for each.
DEC-203 replaces the whole shape: **origin stops mattering, and an open child is what holds a parent
back.** Amendment 7's body stays standing so citations resolve; this record is what a citation to the
table lands on.

**What falsified it, measured.** `parent_origin` read **null** on FEAT-34 and FEAT-35, the two most
recent features that recorded a parent, because both parents were recorded by hand. Under the struck
table a null origin means leave-open, so #728 was left open with all thirteen of its children already
finished. The field was meant to protect someone else's live epic and instead failed open on the two
cases it was newest to.

**A correction to the plan that instructed this amendment, recorded rather than quietly fixed.** That
plan said amendment 7 also carries the D-23 reasoning that a closed sub-issue cannot sit at `Review`.
It does not. That reasoning is in **DEC-196 amendment 4**, which is struck whole today, so the
reasoning goes with it either way — but it is not struck from here, because it was never here.

**The measurement that falsifies that reasoning, recorded so it is not re-derived.** It argued
GitHub's native `Item closed` workflow moves a closed card to the done column, so a closed sub-issue
*cannot* hold `Review`. At `cc84b29`, FEAT-34's thirteen sub-issues **#818 through #830 are all
closed and all sit at `Review`**. A closed issue's card stays where it is; nothing drags it.

**The replacement station-writer row for `Done`:**

| Station | The one writer |
|---|---|
| `Done` | **the harness**, at `gh-sync.py ship`, which writes the done station on every recorded card. GitHub's `Auto-close issue` workflow then closes the issue |

Every other row of amendment 4's table is carried forward unchanged. `Abandoned` is still not a
station and still has no writer.

## DEC-169 — An absence check is never a criterion on its own; pair it with a presence check

Demonstrated, not argued. SC-13 required that `.claude/skills/harness/SKILL.md` stop stating the
closure contract FEAT-03 reversed, checked as
`grep -c 'closes its issue and everything it absorbs' == 0`. Run against three variants of the file:

| Variant | clause gone (need 0) | `ship` row present | parent conditional | `close-task` documented |
|---|---|---|---|---|
| original | 1 | yes | no | yes |
| **two lines deleted** | **0 — PASSES** | **gone** | no | **gone** |
| corrected | 0 | yes | yes | yes |

`sed -d` on two lines satisfies the criterion completely and destroys the org's only record of when
to run `close-task` and when to run `ship`. An orchestrator reading the result would never close a
task issue or a milestone again — a worse defect than the stale prose, shipped behind a green gate.

What saved SC-13 was its second clause, which is not a grep: *":144's ship row must name the parent
AND name it conditional on recorded origin."* Deletion cannot satisfy a requirement that something
**be present and say something specific**. That is also why SC-13 is `verify: inspection` and not
`automated` — the automatable half is precisely the half that can be gamed.

**The rule: an absence check proves only that the wrong words are gone, never that the right words
are there. Every absence check needs a presence check beside it, or `rm` passes the gate.** It
applies to prose greps, to code greps, and to test assertions equally.

Third instance in one feature, which is why it is written down rather than re-derived:
- **MF-1** — SC-06's absence-greps, as first written, asserted the removal of code that must
  *remain* (the retained list GETs build the same endpoint string as the extracted writes), so the
  obvious repair would have voided the SC. Fixed by discriminating on payload form, and by asserting
  absence in **both** close forms rather than one.
- **B-2** — a test label claiming "for the new subcommand" above an invocation of an old one. A false
  label travelled two review tiers as a measurement and produced a report of a gap that did not
  exist.
- **SC-13** — this entry.

Applies forward to `harness-verification-rules` and `harness-code-review` as a review question:
*for every absence assertion, what presence assertion sits beside it?* An SC with only the first
half is not verifiable, however green it runs.

## DEC-170 — The advisor is the org's only turn-level independent reviewer; its influence gets disclosed

The user observed that nearly every agent calls the `advisor` tool and asked whether it is needed.
Two facts, both verified:

- It is attached by a **user-level setting** — `advisorModel: opus` at `~/.claude/settings.json:112`
  — not by the harness. **Zero agents declare it in `tools:`.** DEC-155 noted this and called it
  outside the org's authority; that was right about the *setting* and wrong about the *discipline*.
- **Its spend is invisible to the meter.** No `advisor` row exists in any `cost-report.py` block; the
  recorded names are the 16 harness agents plus `Explore`, `fork`, `general-purpose`, `Plan`. Every
  call forwards the agent's full transcript to Opus, and none of it is attributed. Part of every
  reported overrun — FEAT-03's 3.0x, FEAT-04's plan phase at budget — is unattributed by
  construction.

**Considered and rejected: make the LEAD the advisor.** The user's proposal — the lead already holds
the context, so a member should ask it. It fails twice:

1. **Mechanically.** Members hold `[Read, Glob, Grep, Edit, Write, Bash]`; **no agent holds
   `SendMessage` or `Agent`**, so there is no synchronous upward channel by design. A member's only
   route to its lead is its return, so "ask the lead" costs a full spawn round-trip — return with
   `open_questions`, lead reads, re-dispatch — one cycle per question, against an advisor's
   near-zero latency.
2. **Structurally.** The lead authored the dispatch: it chose the approach, wrote the anchors, framed
   the problem. It cannot audit its own framing. The org says so about itself in four Expertise
   entries by different agents — product-lead P-01 *"pre-argued framing is the least trustworthy
   input a lead receives"*, P-03, P-06, G-03. And the one advisor catch on record is exactly that
   class: *"the advisor caught that I had never re-read `statementsFixture.ts`"* (kaya pm, OBS-02) —
   an omission the lead would likely have shared, because the lead handed the anchors down.

**So the advisor's differentiation is real and specific: independence from the dispatch chain.** The
validator squad supplies that at the **run** level; the advisor supplies it at the **turn** level,
where the org has no other mechanism at all. It is kept.

**The defect is not its existence, it is its invisibility.** Everything else in this org passes state
by file path and records what changed a decision; advisor advice is neither recorded nor gated, so a
load-bearing catch is indistinguishable from the agent having thought of it alone. **The rule: an
agent whose decision or verdict changed because of advisor input says so in its DIGEST**, naming what
changed. Same provenance discipline as DEC-138 am.6 — free to comply with, and it turns a fourth
reviewer from invisible into auditable.

**Not decided, deliberately: whether to keep it on.** No cost decision should be made while the meter
is blind. Open questions for whoever picks this up: can `advisorModel` be scoped to the main session
only, and what does one call actually cost? Answer those before trading away catches that have
provably worked.

## DEC-171 — The no-dependency clause is reversed: PyYAML is permitted, and hand-rolled YAML regex goes

**Supersedes the "Zero dependencies" bullet of DEC-101.** That bullet ruled: *"No YAML library — the
manifest reader is a narrow line scanner, because these must run on any machine without an install
step."* Everything else in DEC-101 stands; only the dependency clause is reversed. The wider
files-only constraint in CLAUDE.md also stands — no CLI, no build step, no template generator.

**What forced it.** Issue #11: `check-state.sh`'s run parser is a three-line regex,
`id:\s*(\S+)\s*\n\s*squad:\s*(\S+)\s*\n\s*verdict:\s*(\S+)`. Because `\s*\n` admits only whitespace
after the `id:` and `squad:` captures, a trailing `# comment` — legal YAML, and the house style on
45 lines of `FEAT-03-subissue-mirror/feature.yaml` — makes the match fail and drops the **entire
run** from `runs`. That silently fails open on three invariants at once: INV-6 (`review_sha` pinned
when a validator run exists), INV-7 (`cycles_used` >= FAIL count), INV-8 (run dir exists). Exit 0,
no message. It has not fired only because the two vulnerable lines happen to carry no comments, and
one author who hit it wrote a warning into the data file (`feature.yaml:63-64`) instead of fixing
the parser.

**Why the line scanner was always going to lose.** This defect shape is documented repeatedly in-tree,
and #11 is not its first appearance. `check-state.sh:105-107` names two priors in its own comment —
the digest parser (DEC-123) and INV-4 (DEC-129), both single-format bugs — alongside DEC-101's own
INV-12 false positive the first time a real orchestrator wrote block-form YAML. Separately,
`validate-digest.py:247-272` documents **five** hand-patches of the same class, one of which (F4) is
a trailing-`#`-comment fix identical to #11, found and fixed independently. A regex encodes
one serialization of a format that has many; every legal variant an author later uses is a silent
failure. The cost of the constraint stopped being "no install step" and became a recurring class of
fail-open bugs in the code whose entire job is to catch fail-open bugs.

**What replaces it.** A real `yaml.safe_load` wherever the harness reads YAML. The reversal *permits*
the dependency; it does not mandate the rewrite happen everywhere at once — but the direction is
settled, and new code does not hand-roll a YAML parser.

**Graceful degradation is mandatory, and it mirrors DEC-101's own rule** that `check-domain.sh` fails
open loudly rather than blocking every write. A bare `import yaml` would convert a latent fail-open
into a guaranteed fail-closed: no PyYAML, traceback, non-zero exit, every `/harness` entry gate
reporting failure on a machine that merely lacks a package. So: guard the import, fall back to the
comment-tolerant line scan, and print one loud line naming the install command. The parse gets
better where PyYAML is present and gets no worse where it is not.

**Two hazards for the implementer, both real:**

- **`safe_load` returns typed values; the regex returned strings.** `check-state.sh:120` is
  `cu.isdigit()` on `cycles_used` — an `int` under `safe_load`, and `.isdigit()` on an `int` raises.
  Every consumer of a parsed value must be walked for str-assumptions.
- **A bare date-shaped scalar becomes a `datetime.date`.** Run ids like `2026-07-31-01-product` carry
  trailing text and stay strings, but an id that is exactly `2026-07-31` would silently become a date
  object and break the run-dir path join.

**Do not pin `/usr/bin/python3`.** Apple's system Python ships PyYAML 6.0.1, which makes pinning it
look free. It is macOS-only and deprecated for scripting; it would make the harness unrunnable on
Linux, in CI, and in the distributable package this repo is aiming at.

### DEC-171 amendment — the fallback is removed: PyYAML is REQUIRED, and the hooks fail CLOSED

Two reversals of DEC-171 as first written, both the user's call at the `/harness-plan` grilling the
same day.

**1. No graceful degradation. PyYAML is required.** DEC-171 mandated a loud fallback to a
comment-tolerant line scan when the library is absent. The user rejected it on the ground that
settles it: a fallback keeps a hand-rolled YAML parser at every call site, and removing exactly that
is the entire point of the effort. Two code paths also means the fragile one is the one that never
gets exercised, so its bugs are found in production or not at all. **A missing PyYAML is an error,
stated loudly, not a quieter mode of operation.**

**Where the requirement is enforced:** a seventh entry in `harness-init`'s existing six-prerequisite
HARD GATE — check the import, and if it fails STOP and print the install command, exactly as that
gate already does for a script it cannot run. Not a `requirements.txt`: nothing in the harness would
read it, and it would be the first dependency manifest in a repo that is still files-only.

**2. `check-domain.sh` and `bash-write-guard.sh` fail CLOSED on a missing PyYAML.** This is a
deliberate exception to DEC-101's fail-open rule, and the distinction is what the failure means.
DEC-101 fails open on a *missing manifest* because an unconfigured project has nothing to enforce,
and on an *unparseable payload* because that is the hook's own bug — blocking on either would wedge
every write over a condition the hook cannot fix. A missing PyYAML is neither: the project IS
configured, the hook has no bug, and there is exactly one action that resolves it. Failing open
there means domain enforcement is silently off precisely when the environment is wrong.

**The bootstrap escape, and why it is not a loophole.** Fail-closed plus an install-time prerequisite
would brick any existing project that pulls the update without re-running init: every agent write
blocked, including the writes that would fix it. So the first session that hits a missing PyYAML
prints the install command and **permits writes for that session only**, blocking from the next
session onward. The steady state is closed; the escape exists so the failure is recoverable from
inside the tool, and it expires by construction rather than by anyone remembering to remove it.

## DEC-172 — the agent return gets a `yaml` fence, and unfenced returns are blocked

`validate-digest.py` carries five hand-patches (`:247-272`) for one root cause: the three-part return
is **already a well-formed YAML mapping** — `VERDICT:` scalar, `DIGEST:` mapping, `artifact:` scalar
— floating in free prose with no delimiter (`harness-handoff/SKILL.md:14-22`). Every patch is
boundary detection: where the block starts, what the base indent is, when a dedent ends it, whether
`DIGEST:` may carry a trailing comment (F4 — the same bug as issue #11, fixed independently in a
second file). None of them are YAML bugs.

**The return is wrapped in a ```` ```yaml ```` fence.** Extraction becomes one unambiguous match and
`safe_load` does everything else, which deletes all five patch classes at once.

**Rejected: DIGEST as a real `.yaml` file** with the return carrying its path. It looks like
"pointers not payloads" but is not. The hook validates `last_assistant_message` (`:645`), so a path
would still have to be located in prose — the parse moves rather than disappears. The DIGEST is the
compact routing signal that rule deliberately keeps inline; `artifact:` is already the pointer. And
it would change the return contract for all 16 agents plus DEC-122 — a larger feature, orthogonal to
removing regex, and available later at no extra cost if it is ever wanted.

**Unfenced returns are BLOCKED, with no deprecation window.** Consistent with the fail-closed posture
above, and safe here because `validate-digest.py` already returns 0 when `stop_hook_active` is set,
so a blocked agent retries once and cannot loop.

**Correction to this entry as first written.** It claimed "the 16 agent templates and the parser must
land in the same ship, or every agent breaks at `SubagentStop`." Both halves were wrong, and the
error mattered because it made the template work look blocked when it is not.

- **The count is 13 files, not 16** — nine `.claude/agents/harness-*.md` plus four skills
  (`harness-handoff`, `harness-digest-dev`, `harness-team`, `harness-tdd-enforcement`). Counted with
  `grep -rln '^DIGEST:'`. Seven of the sixteen agents carry no return template of their own; they
  inherit `harness-handoff`'s.
- **The ordering constraint only binds in one direction.** The CURRENT parser already accepts a
  fenced return — verified directly against `validate-digest.py` at this SHA with a fenced digest,
  and with a fenced digest surrounded by prose: both `digest ok`, exit 0. The `artifact:` key at
  column 0 already ends the block, so a closing ``` fence at column 0 is an ordinary dedent it
  handles. **Templates may therefore ship FIRST, independently and safely.** What must not ship first
  is the parser's *rejection* of unfenced returns — that is the half that breaks every
  not-yet-updated agent.

The practical sequencing: fence the 13 templates whenever convenient, then make rejection the
parser's behavior once no unfenced returns remain. Agent files are read at spawn, so the
`harness-init` step 9 restart caveat still applies to the template change.

## DEC-173 — "nothing happened" gets a spelling: `n/a`, and declining a gate is not passing it

An audit of every persona's did-nothing state (`.harness/notes/audit-digest-schema-nothing-happened-2026-08-02.md`,
reproducer beside it) found **6 of 7 could not report it truthfully**. In five, the honest value was
REJECTED while a false one was ACCEPTED — the schema actively selected for the lie:

| persona | honest | was rejected in favour of |
|---|---|---|
| `dev` | `suite: n/a` | `suite: pass` — the suite passed, when nothing ran |
| `qa` | `suite`/`matrix_ok: n/a` | `pass` + `matrix_ok: true` — **the only blocking gate, recorded as passed because the suite could not run** |
| `reviewer` | `severity_max: n/a` | `info` — indistinguishable from "reviewed it, found info-level issues" |
| `visual-designer` | `contract: n/a` | `written` — asserts a DESIGN.md exists |
| `pm` | `surface`/`risk: n/a` | `S` + `low` — asserts a small, low-risk feature |
| `lead` | `members: []` + `steps_run: 1` | *(nothing accepted — see below)* |

**This is the fail-open shape the file exists to prevent**, turned inward. The accepted value does not
merely lose information; it collapses *this did not happen* into *this happened, benign result*. The
orchestrator routes on four of these fields.

**The fix reuses the mechanism that was already here.** `NULLABLE` gains `suite`, `matrix_ok`,
`severity_max`, `contract`, `surface`, `risk`; the existing short-circuit already accepts
`none`/`null`/`n/a` for a nullable scalar. **`n/a` is the spelling to use** — all three parse, but one
vocabulary across sixteen agents is the entire point of DEC-121, and three synonyms is how the
near-miss problem gets reinvented.

`dev-ops`'s `suite` already carried `n/a` and every other occurrence did not: the vocabulary was
extended once, locally, where someone hit the wall, and never propagated. That member is now removed
as redundant — one mechanism for "did not happen", not two that drift.

**Declining a gate is not passing it — and the rule is keyed by PERSONA, not by field.** Widening
`NULLABLE` alone would have created a new fail-open: `matrix_ok: n/a` with `VERDICT: PASS` is the same
unearned pass in new clothes. But a field-only rule is wrong, and testing proved it — it rejected
`dev-ops`'s legitimate `suite: n/a` + `PASS`, where `test_matrix` maps `config`/`scaffolding`/`docs`
to `[]` (DEC-100) and "no tests apply" is the correct outcome. So `GATE_FIELDS` is
`{"dev": {"suite"}, "qa": {"suite","matrix_ok"}}` — only the roles whose PASS is *earned by the gate*
are bound by it. A `reviewer` scoping out of a diff with nothing for its role to judge passes with
`severity_max: n/a`, legitimately.

**What triggered the audit.** `harness-tdd-enforcement`'s under-specified-task refusal was written
with two DIGEST fields and no `artifact:`. The `SubagentStop` hook rejected it with **exit 2**, so the
guard against under-specified tasks was told it had committed a contract violation at the moment it
fired; the forced retry sets `stop_hook_active` and exits 0, shipping **unvalidated**. Completing that
example without fixing `suite` would have enshrined `suite: pass` — a lie — in a normative template.
It now reads `suite: n/a` and validates in both CLI and hook mode.

**NOT fixed here, and both need a decision rather than a patch:**

1. **B-13, the `lead` row** (`FEAT-03-subissue-mirror/feature.yaml:97`, raised independently by
   product-lead and validator-lead). `members: []` with `steps_run > 0` is rejected as "never
   legitimate", but a lead applying its own Expertise ops genuinely self-executes a step. This is
   doctrinal — *may a lead execute work at all?* `harness-zero-micro-management` says route, never do;
   the distillation dispatch says otherwise in practice. Resolve the doctrine, then the encoding.
2. **The `stop_hook_active` pass-through.** A blocked agent's second attempt is accepted with no
   validation whatsoever. That is how a wrong correction escapes, and it is why defect 1 above was
   survivable rather than visible.

## DEC-174 — Self-hosting stops at the enforcement layer: the harness plans its own work, it does not execute changes to its own guards

Raised by the user after a day of building FEAT-05 through the harness: *"my sense is that we shouldn't
be using harness to build harness."* Substantially accepted, with the boundary drawn narrower than the
full claim.

**The evidence, all from 2026-08-03 and all on this repo.** Every gate was green —
`run-unit-tests.sh`, `check-docs.sh`, `check-state.sh`, `gen-decisions-index.py --check` — while:

- four `.harness` YAML files did not parse, `team-config.yaml` among them, its `[` unclosed since a
  space-`#` opens a comment inside a flow sequence, so **every key from `orchestrator:` onward was
  unreachable to a real parser** — the entire team roster;
- `harness-tdd-enforcement`'s normative refusal template was **rejected by the harness's own
  `SubagentStop` validator**, six contract violations, so the guard against under-specified tasks was
  told it had violated the contract at the moment it fired;
- six of seven personas could not report a did-nothing state truthfully, and in five the schema
  **accepted the false value and rejected the honest one** (DEC-173).

**Self-hosting caught none of these.** They were found by hand, and the largest by chasing a red unit
test that could reasonably have been dismissed as an expected RED gate. A system whose self-checks pass
while its own manifest is unparseable is not checking itself.

**The circularity is not uniform, which is why the answer is a carve-out and not a repeal.**

| layer | self-hosted? | why |
|---|---|---|
| grilling, BRIEF, PLAN, review panel, goal-check | **yes, keep it** | none of it depends on the code being changed; FEAT-05's grilling and plan were good work and caused none of the day's trouble |
| agent roles, digests, expertise | yes | drift risk, not circularity |
| **hooks, validators, gate scripts** (`check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`, `check-state.sh`) | **NO** | the artifact under change is the artifact doing the checking |

Everything painful on 2026-08-03 sits in the third row: which copy of `check-domain.sh` a hook fires,
whether DEC-173 governs any agent, whether 13 edited agent templates are even live, and a fail-closed
conversion that can block the write that would fix it.

**The ruling.** A change to the enforcement layer is made **directly** — ordinary edits, tests run
explicitly, a human reading the diff — not dispatched through a team run whose gates are the thing
being changed. Planning such a change through the harness remains fine and useful; **executing** it
through the harness is not.

**Two structural smells that justify the line, recorded because they generalise:**

1. **The bootstrap escape.** FEAT-05 had to design a one-session escape so a fail-closed hook could not
   brick the write that fixes it. Needing an escape hatch *from yourself* is the signature of
   circularity, not a missing feature.
2. **Cost shape.** $92 went to planning before a single line of code, on a change whose core is roughly
   fifty lines of Python. The ceremony is calibrated for product features, not for editing the ceremony.

**What this costs, stated honestly rather than argued away.** Dogfooding is real pressure and it worked:
this one day produced DEC-142's name-vs-title gap, DEC-173's schema class, and the invalid-corpus
finding — all because the harness was actually run. Removing the enforcement layer from self-hosting
removes some of that pressure, and it weakens the claim that a CTO can ship reliably through this thing.
The trade is accepted anyway: **finding bugs by running a $240 team flow is a worse deal than finding
them with a test.**

**Not decided here:** whether harness development should use the ceremony at all for non-enforcement
work. The user considered stopping self-hosting entirely and chose the carve-out; the stronger position
stays available and is a stage question, not a correctness one.

### DEC-174 amendment 1 (2026-08-11) — three checkout modes, and the factory workspace is not one of them

FEAT-15 gave `check-domain.sh` two bases, and that made a question visible that the original ruling
never faced: harness code can be edited from three different checkout shapes, and they do not carry the
same rights. Resolved with `--resolve` on the SAME file,
`.claude/skills/harness/bin/check-domain.sh`, at this tree:

| mode | path | `--resolve` | ever used? |
|---|---|---|---|
| factory workspace clone | `harness-factories/harness/.claude/…` | **NOBODY** | **never** — `/Users/molchairuangutai/GitHub/harness-factories` does not exist |

Measured before the removal below. **The removal changed this verdict, and the change is recorded
because the first draft of this amendment asserted the old one.** With `mruangutai/harness` gone from
`repos:`, that path is no longer inside any `workspace_bases` entry, so it no longer reaches the
product base at all — `--resolve` now exits **2**, "under the factory workspace but belongs to no
repository declared in fleet.yaml". The enforcement got louder, not quieter, but the mechanism is the
unlisted-repo branch and no longer glob filtering. A reader who cites "returns NOBODY" is citing the
pre-removal tree.
| worktree | `.claude/worktrees/FEAT-13-…/.claude/…` | `harness-backend-dev`, `harness-dev-ops` | yes — FEAT-13, merged as #260 |
| live checkout | `.claude/…` | `harness-backend-dev`, `harness-dev-ops` | yes — the ordinary case |

A worktree sits UNDER the repository root, so `_inside(target, root)` holds and it lands in the harness
base with full rights. A factory clone lands under `workspace_root`, outside the root, so it resolves in
the product base where control-plane globs are filtered — and harness's own source lives almost entirely
in `.claude/skills/harness/bin/**` and `.harness/**`. A factory-dispatched agent would be refused writes
to most of the thing it was sent to change.

**The ruling.** Harness develops itself in the live checkout and in worktrees under it. The factory
workspace is not a harness development mode. `mruangutai/harness` is REMOVED from
`.harness/factory/fleet.yaml` `repos:` so this is mechanical rather than prose, and
`test-no-distribution.py` `case3_absence_harness_is_not_a_fleet_member` fails if it is re-added.

**Capability was never sanction, and that is what looked like a contradiction.** The entry made the
factory route REACHABLE from the day FEAT-10 wrote it. Nothing made it ALLOWED, and nobody ever took it.
FEAT-15 did not open this door — before FEAT-15 a write to a factory clone got no verdict at all and
landed silently; now it returns NOBODY. FEAT-15 made an existing hole visible and closed it.

**The cost, stated rather than argued away.** Removing the entry costs nothing measurable today, because
no factory workspace has ever existed. It costs later: if harness ever wants factory-style parallel
dispatch across many issues, the entry comes back and this amendment is revisited with it.

**A loose end this amendment does NOT close, and it is not deferrable.** `fleet.yaml` `board.number: 3`
is the *Harness* board. Measured 2026-08-11: `gh project item-list 3 --owner mruangutai` returns **30
items, all 30 `mruangutai/harness`, zero kaya-ai**; `gh project list --owner mruangutai` shows board 2
is "kaya-ai".

So the fleet now holds exactly one repository — kaya-ai — and points its station board at a board that
contains no kaya-ai issue. The operator has stated that factory runs against kaya-ai are the primary use
case for the factory. That run reads board 3 for an issue that is not there.

This is left open because retargeting the board is a separate decision with its own consequences — the
30 harness issues on board 3 are the live effort tracker, and `harness.json` `github.repo` still points
at `mruangutai/harness` for the issue mirror, which is a different mechanism from the factory station
board. It is recorded here as OWED, not as an accepted state.

### DEC-174 amendment 2 (2026-08-12) — the station board is declared per repository, and am.1's board loose end is closed

FEAT-16 closes the loose end the section above records as OWED. That section describes the
pre-FEAT-16 tree — a fleet-level `board.number: 3` pointed at a board holding no kaya-ai issue — and
it is superseded by this amendment. It is left standing unedited: the record is appended to, never
rewritten.

**The station board is declared PER REPOSITORY.** Each `repos:` entry in
`.harness/factory/fleet.yaml` carries its own `board:` mapping, with `number`, `station_field` and
`stations` together in that one block, so a repository's board and the field the factory moves cards
in are read from the same place as the repository itself.

**There is no fleet-level board, and a leftover top-level key is REJECTED, not ignored.**
`load_fleet` in `.claude/skills/harness/bin/factory_config.py` raises on a top-level `board` key
naming the offending key and telling the author to move it under the `repos[]` entry. Ignoring it
would let a fleet declare a board nobody reads and get silence back.

**`mruangutai/kaya-ai` is paired with board 2.** Its Status options were brought to the same
six-value vocabulary board 3 carries — `Backlog, Plan, Ready, Building, Review, Done`, in that order
— by RENAMING `Todo` to `Backlog` and `In Progress` to `Building`, retaining `Done`, and adding the
three that were missing. That cost **zero item writes** against the 118 finished issues: renaming a
Projects v2 option keeps its id, so no card moved. The verbatim capture the figures come from — 211
items, 118 `Done`, 82 `Backlog`, 11 `Building`, zero in each of `Plan`, `Ready` and `Review` — is
`.harness/features/FEAT-16-factory-per-repo-board/notes/board2-capture.md`, taken at T-07 before any
factory run. `Ready` is deliberately empty: on this board `Backlog` means filed-and-untriaged and
`Ready` means promoted for the factory, so a claim run that finds nothing has found the truth.

### DEC-174 amendment 3 (2026-08-18) — the fleet declares no board at all, at any level

FEAT-24 moved every fleet member's board out of `.harness/factory/fleet.yaml` entirely. That
falsifies one paragraph of amendment 2 above, which is left standing unedited: the record is appended
to, never rewritten.

**What became false.** Amendment 2's paragraph headed *"The station board is declared PER
REPOSITORY"* states that each `repos:` entry in `.harness/factory/fleet.yaml` carries its own
`board:` mapping, with `number`, `station_field` and `stations` together in that one block. No
`repos:` entry carries a board now, and one that does is refused.

**What is true now.** A board declared anywhere in `fleet.yaml` is REJECTED by `load_fleet` in
`.claude/skills/harness/bin/factory_config.py` — at the top level as before, and now inside a
`repos[]` entry too, each raising a message that names where the board moved to. Every repository's
board lives in that repository's own `.harness/harness.json` under `github.board`, read from that
repository's **default branch** by `product_config`/`board_for` and validated by `validate_board` —
the one board validator in the tree, which `gh_board.load_board` calls directly, and which RAISES
rather than returning a verdict.

**This is a change of FILE, not a return to a fleet-level board.** What amendment 2 ruled otherwise
stands and is not swept away with the paragraph above: the board is still declared PER REPOSITORY;
`mruangutai/kaya-ai` is still paired with **board 2** — read back live through `board_for` at this
tree as `owner mruangutai, number 2, station_field Status`, now from kaya-ai's own
`.harness/harness.json` on `master` rather than from `fleet.yaml`; and the six-value Status
vocabulary and the zero-item-writes rename record stand exactly as amendment 2 recorded them.

**`default_branch` did NOT move with the board,** and the reason is mechanical: `factory_workspace`
reads it in order to CREATE the checkout, so it cannot live inside the checkout.

**Not a strike:** DEC-188 strikes what the tree flatly contradicts in whole, and what this tree
contradicts is one paragraph. DEC-174's carve-out ruling, amendment 1, and the rest of amendment 2
are untouched.

### DEC-174 amendment 4 (2026-08-19) — the enumeration is a list of examples, not a boundary; `check-plan-routes.py` and its test join it

The carve-out's table names the category **"hooks, validators, gate scripts"** and then lists four
files in parentheses: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
`check-state.sh`. `DECISIONS-INDEX.md` carries the category and not the list. **The two readings
disagree about `check-plan-routes.py`**, and FEAT-28 could not be laned until the disagreement was
settled.

**The category governs. The parenthetical is examples, and it is now stale.** DEC-183 made
`check-plan-routes.py` a step of the required `integration` CI job — *after* DEC-174 was written, so
the list could not have named it. Changing it through a run whose gates include it is exactly the
circularity this entry exists to refuse.

***Its test joins it too, and that is the part worth arguing.*** The narrower reading — FEAT-28
edits `test-check-plan-routes.py`, the gate's TEST, so the gate itself keeps checking and the
rationale does not bite — was put and rejected. **A gate's test is the only thing proving the gate
discriminates.** On the day this amendment was written, three separate assertions in this repository
were found unable to fail: a verify slicing a marker that did not exist so every absence grep passed
vacuously; a case searching stdout for a traceback that goes to stderr; and a citation resolver that
truncated `case_25b9` to `case_25`, found `def case_25():`, and reported the exact phantom it was
built to catch as resolved. Every one was invisible to green gates. A test edited under gates that
cannot see it is the same circularity one level out.

**So the enforcement layer is: `check-domain.sh`, `bash-write-guard.sh`, `validate-digest.py`,
`check-state.sh`, `check-plan-routes.py`, `dispatch-guard.sh`, and the test file of each.** A script that becomes a gate
joins the list on the day it becomes one, and this entry is amended when that happens — the category
decides, the list records.

*Where the line falls for a library a gate calls.* A module a gate imports is not itself a gate. The
working rule, applied to FEAT-29: a squad may write the library, and **the cutover that makes a gate
use it is main-session-direct**, proven by showing the gate's violation set is identical before and
after. The gate's behaviour changes only by a hand the carve-out governs.

`dispatch-guard.sh` joins the enumeration on the evidence that it refuses dispatches — it
declined a `harness-orchestrator` dispatch over a `model` parameter on 2026-08-21 — and it joins
under the rule this amendment already states rather than as a new ruling, so no lane changes and
amendment 4 remains an amendment about the list and not about the category.

**Not a strike.** DEC-174's ruling, its rationale and amendments 1 through 3 are untouched. What
changed is that the enumeration is now correct and is declared non-exhaustive.

## DEC-175 — The engineering return declares which task it is answering: `task: T-NN|none` gates `task_verify`, and a self-reported gate FAILURE stops being a pass

Three things ship together and each is unintelligible without the others: the `task_verify` field, the
`task` field that governs it, and a second gate structure that catches a *reported failure* rather
than a declined report. All three live in `.claude/skills/harness/bin/validate-digest.py`, under the
DEC-174 carve-out — edited directly, tests run explicitly, a human reading the diff.

**1. `task_verify`, and it binds all five dev specialists.** A `dev` or `dev-ops` return must state
whether its PLAN task's `verify:` command actually passed — `pass` or `fail`, the enum at
`validate-digest.py:149` and `:160`. There is no dev-ops carve-out: `GATE_FIELDS` (`:92-93`) gains
`"dev-ops": {"task_verify"}`, so `task_verify: n/a` + `VERDICT: PASS` is rejected for dev-ops as it
is for the four `dev` specialists. This is *per field*, not per persona — dev-ops's `suite: n/a` +
PASS stays legal, because `test_matrix` maps config/scaffolding/docs to `[]` (DEC-100) and "no tests
apply" is the honest outcome there. Every PLAN task carries a `verify:`, so "no verify applies" is
never honest, and `n/a` there means refused or blocked.

**2. `task: T-NN|none`, and the conditional.** A return that carries no PLAN task — an architecture
review, an Expertise distillation, a debug or research pass, any lead-issued investigation — had no
legal value to write: omission rejected, `n/a` + PASS rejected, `fail` + PASS rejected, and `pass` a
lie about a command that never ran. So `dev` and `dev-ops` gain a REQUIRED `task` field matching
`T-\d+|none` (`TASK_ID_RE`, `:136`, `fullmatch` — the placeholder spelling `T-NN` is rejected), and
`CONDITIONAL = {"task_verify": "task"}` (`:117`) switches `task_verify`'s obligation off exactly when
`task` says `none`.

**The cheaper option was recommended, and the user rejected it — recorded so a future scan does not
re-suggest it.** The alternative was a fourth `task_verify` value, `no-task`: one string in two
schema sets, no new required field, no new validator logic. It was rejected because it reinstates a
**self-declared bypass carrying no receipt obligation**. REQ-08 makes a `pass` show its command and
that command's verbatim output; `no-task` obliges nothing, because there is no command it could ever
be asked to show. It was therefore *cheaper to abuse than lying* — the shape an earlier ruling in the
same feature had already rejected.

**`task: none` is still self-declared, and this entry says so plainly.** Nothing in
`validate-digest.py` reads the dispatch. What the ruling buys is not proof but *auditability*: a
task-id-shaped string in the same vocabulary the dispatch prompt is now required to carry verbatim
(`.claude/skills/harness-zero-micro-management/SKILL.md`, commit `0a34989`). The audit becomes a
string equality between two durable artifacts instead of a presence question with nothing on the
other side.

**3. The `task: none` branch is pinned, because that is where a conditional fails open.** Three
sub-rulings, each with its reason:

| when `task: none` | ruling | reason |
|---|---|---|
| `task_verify` omitted | legal | this is the branch the conditional exists to create |
| `task_verify: n/a` (or `none`/`null`) | legal, and the `n/a`-with-PASS gate does not bind | DEC-121 and `harness-handoff` tell every agent a field is never said with silence, so `n/a` is the spelling it was preloaded to write. Rejecting it would order an agent to violate its own contract. The explicit assertion has MOVED, not vanished — `task: none` is itself "I looked; there is no task", and it is required |
| `task_verify: pass` or `fail` | REJECTED, whatever the VERDICT | self-contradictory: the return denies there is a task's `verify:` command and then reports that command's result. Accepting it hands a PASS to a dev that carried a task, mis-wrote `task: none`, and reported `fail` |

**The interpreter fact that makes it fail closed, and it is load-bearing:** `str(None).lower()` is
`"none"` in Python. A helper written `seen.get("task")` instead of `seen.get("task", "")` would let a
*missing* governor switch the requirement off for every return that omits `task` — the conditional
failing open in its own first line. `_unbound` (`:119-130`) carries the `""` default and a comment
saying why; no governor value, or any value but `none`, means the requirement BINDS.

**4. The fail-value gate — a SECOND structure, distinguished by mechanism, not by field.** The
diagnosis, re-measured at `4091b36` by running each case through the validator rather than by reading
it: `GATE_FIELDS` was consulted only INSIDE the `field in NULLABLE and val in PLACEHOLDER_UNSET`
branch, so it could only ever see a placeholder. DEC-173 gave "did not run" a spelling and gated it;
**"ran and failed" was never gated at all.** `GATE_FAIL_VALUES` (`:108-110`) is consulted OUTSIDE
that branch (`:613-620`) and answers the other question, and it is additive — it appends rather than
`continue`s, so a value that is both a gate failure and a schema violation reports both. (`GATE_FIELDS`
now has a second consultation of its own at `:548`, in the missing-field message path, so that a
rejection message never names a value the validator will then reject — REQ-11.) It covers `suite` for `dev` and `qa`,
`matrix_ok` for `qa`, and `task_verify` for `dev` and `dev-ops`.

Its table is keyed persona → field → **the failing VALUE**, not a set of field names, because the
failing values differ in TYPE: `suite` and `task_verify` fail as the string `fail` while `matrix_ok`
fails as the boolean `False`. A string-keyed set would have silently never fired on `matrix_ok` —
the project's only blocking gate. The comparison is type-strict for the mirror-image reason:
`0 == False` is `True` in Python, so a naive equality would reject `matrix_ok: 0`-shaped values by
accident.

**5. `dev-ops` is deliberately EXCLUDED from both structures for `suite`, and the consequence is
residue, not an oversight.** DEC-100 justifies the `n/a` half and says nothing about `fail`, so
`dev-ops` `suite: fail` + `VERDICT: PASS` remains ACCEPTED — a real instance of the defect class this
entry closes, left open one persona over by the user's ruling. It is recorded in FEAT-07's BRIEF
under `## Verification gaps` and pinned by a fixture in `test-validate-digest.py` (`:1214`), so the
next edit to it is deliberate rather than accidental.

**The behaviour change, stated plainly.** Of four persona/field combinations that reported a gate as
FAILED alongside `VERDICT: PASS` and returned `digest ok`, exit 0, **three now fail closed** — `dev`
`suite: fail`, `qa` `suite: fail`, `qa` `matrix_ok: false`. The fourth is the `dev-ops` residue
above. Separately, `task` is a new REQUIRED field for both dev personas: a return written to the
previous contract does not validate until its dispatch and its author know about both fields.

**6. Where the receipt clause landed, and the rule it generalises to.** REQ-08's clause — a dev's
verification claim must leave the command and that command's own output in a durable file — went into
`.claude/skills/harness-tdd-enforcement/SKILL.md`, one copy. This is recorded here rather than in a
per-feature plan because a plan is not a durable record and this is a textbook re-litigation target:
the obvious home is `harness-digest-dev`, with the rest of the dev return contract.

**The rule, which is about preload coverage and not about this feature:** *the topical home of a rule
is not necessarily the file that reaches everyone the rule binds — verify the preload set before
choosing.* `harness-digest-dev` is preloaded by FOUR agents (`harness-frontend-dev`,
`harness-backend-dev`, `harness-ai-dev`, `harness-data-engineer`); `harness-tdd-enforcement` is
preloaded by exactly FIVE, those four plus `harness-dev-ops`. The obvious home would have silently
missed the one persona the ruling had just brought into scope. The same arithmetic runs the other
way for a rule 11 agents cannot act on: it does not belong in a file all 16 preload.

## DEC-176 — The signature gate is BATCHED: one review pass produces one consolidated fix, dispatched after the user has read to exhaustion

At the BRIEF/PLAN signature gate the main session now collects **every** change request the user
raises in that one review pass into a single answers file and dispatches **exactly one** consolidated
revision. No fix goes out while the user is still reading. The rule is in
`.claude/commands/harness.md:45-50` (section 2, where the signature is taken) and in the Red flags
row below it (`:90`); commit `7da58c6`.

**The evidence, and it is the reason this is a rule rather than a preference.** FEAT-03's plan phase
spent **seven serialized runs and roughly $95** on a product-fix → re-verify ping-pong in which **no
reviewer found anything**. Every cycle existed because a new ruling arrived separately. The cost is
not review; it is arrival order.

**The cost, named rather than argued away:** the first fix goes out later than it otherwise would.
That is accepted. A revision pass is cheap to widen and expensive to repeat.

**A deliberate omission, recorded so it is not read as an oversight: there is no escape hatch for an
urgent, independent change request.** Grilling established that nobody has hit that case, so its
shape cannot be stated sharply enough to write. Writing a hatch for a hypothetical would give the
batching rule a bypass before it had a single instance of pressure against it. When the case occurs,
it will describe itself.

## DEC-177 — A bounded runtime-environment question is MEASURED before any claim about it is relayed

When what is about to be relayed rests on how the runtime *resolves* something — which copy of a file
executes, which cwd a hook sees, which binary is on PATH — and the probe is bounded (a single
additive line, a byte-identical revert, one suite re-run), the measurement is taken first. Inferring
one such question cost a working day and two retracted claims, and the probe, when it was finally
taken, **disproved** the inference. A file-difference check cannot answer a resolution question.

**Scope is two surfaces and only two**, both landed in `7da58c6`: `.claude/commands/harness.md:76-81`
(section 4, where returns are relayed to the user) and `.claude/skills/harness/SKILL.md:123-128` (the
orchestrator's question round-trip, where `awaiting_user` is returned). These are the two tiers that
relay claims to the user, and the two that over-claimed.

**It is deliberately NOT in `harness-handoff`, and that is the load-bearing reason — recorded so a
future scan does not re-suggest the obvious home.** `harness-handoff` is preloaded by all 16 harness
agents, so a rule placed there is paid for at all 16 spawns. "Probe before you relay" is meaningless
to an agent that relays nothing to the user; charging every agent for a rule only the relaying tiers can act on is the
context-budget failure the constraint in `CLAUDE.md` exists to prevent. Placement follows *who can
act on the rule*, not *where rules of this kind usually live*.

---

## DEC-178 — Cost tracking is removed entirely: the meter, the budgets, the invariant and every reporting surface

The money meter measured a shrinking minority of the work and fed a budget that was already forbidden
to stop anything. `cost-report.py` attributed spend from transcript snapshots and could not separate a
task run at depth 0 in the main session from the session total: FEAT-06 ran 9 of 10 build tasks in that
shape and records its own figure as an understatement; FEAT-07 ran 8 of 10 the same way and finished at
$702.82 against a $550 budget the orchestrator had computed for itself. DEC-134 had already made
`max_cost_usd` informational — a crossing is a headline, never a stop. A measurement nobody can trust,
feeding a limit nobody can enforce, is not instrumentation; it is 439 lines of script plus a dated
per-model rate table to re-verify. It goes: the meter, the `cost_model` and `budgets` config blocks,
INV-11, the digest field, and every rule surface that told an agent to produce a number.

**The DEC-148 context watchdog is knowingly DROPPED with the file it lived in** — not preserved as a
standalone script, not folded into `check-state.sh`, not deferred. Its reason: the watchdog's only
behavioural consequence was to argue for ending an orchestrator's run at a phase boundary, and DEC-159
now makes one-phase-per-orchestrator mandatory regardless of any measurement. The diagnostic no longer
decides anything, so keeping it would cost maintenance to produce advice already hard-coded. This
clause exists so a future scan does not re-propose the watchdog on the strength of DEC-148's prose.

**DEC-148 is only PARTIALLY superseded here.** It made two changes. The watchdog dies with this
feature; its OTHER half, the relay rule, was superseded by DEC-159 independently and before it — which
is why no blanket supersession marker is declared against DEC-148 anywhere in this entry, and why the
correction lands as a rewrite of DEC-148's hand-written ruling in `DECISIONS-INDEX.md` instead.

**Historical figures are LEFT IN PLACE as the only surviving record.** `cost_usd`/`max_cost_usd` in
already-shipped `feature.yaml` files and the `cost:` block in every run `state.yaml` are not scrubbed:
deleting them would rewrite what was measured. The mechanical consequence is that `cost` stays in
`check-state.sh`'s `CHECKPOINT_KEYS` — allowed, never required. Measured: all 67 run `state.yaml` files
in this repo carry the block, and the checker flags any top-level key not in that set, so removing the
entry would convert 67 historical runs into 67 violations in a single edit. The entry looks dead after
this feature and is not; a comment beside it says so.

**Nothing replaces the ship-review briefing's cost line.** Every candidate — a run count, a wall-clock
duration — is a NEW measurement this feature has not built, and inventing one inside a removal is how
removals grow. The 2026-08-04 agent-workflow performance review's row 10 (count and budget RUNS) is the
remaining lever on that ground, and it is filed to the backlog rather than built here.

**`cost_usd` came OUT of the orchestrator digest schema rather than being kept as a declared literal.**
Probed first: a payload omitting the key while the schema still required it is rejected
`BLOCKED (contract violation)`, whereas a payload carrying an unknown extra key validates clean. The
hazard is one-directional, so the schema drops the key first and in-flight returns that still emit one
keep validating — including this feature's own build, which was running under the live hook while the
change landed.

---

## DEC-179 — Task routing is resolved at PLAN TIME: an ungranted surface becomes a DECLARED main-session step, never a discovered one

A PLAN task naming a path no agent is granted to write used to be found at dispatch time, mid-run, by
`bash-write-guard.sh` or `check-domain.sh` rejecting the write — after the plan had been signed and the
run was underway. `.claude/skills/harness/bin/check-plan-routes.py` moves that discovery to the plan
phase: it reads each task's `files:` and `execution_mode:` and asks `check-domain.sh --resolve <path>`
who may write each one. The ungranted surface is still allowed; what changes is that it is now
**declared in the plan** as a main-session step, priced and visible before approval, instead of
surfacing as a rejected write halfway through a build.

**The checker MUST NOT reimplement path matching, and the test enforces it behaviourally, not by
inspection.** No `fnmatch`, no glob-to-regex translator, no prefix comparison on the text before `/**`
— every resolution is a subprocess call with stdin closed (`check-plan-routes.py:67-73`). A second
matcher that drifts from the guard is the failure mode, and it does not drift visibly: a bare prefix
comparison answers *False* for a pattern with an earlier wildcard segment, such as
`.harness/features/*/runs/*-eng/**` — the exact bug recorded in the `glob_to_re()` docstring of
`check-domain.sh` (`:61-69`), where it blocked every lead from its own run dir. The
17th case of `test-check-plan-routes.py` runs a path granted *only* through that mid-pattern grant and
requires an `OK` line; the source-string cases (9, 16) alone would pass against a hand-rolled matcher
that named its helper something else.

**Two tokens are legal — `team` and `main-session-direct` — but only one of them is compared.** The
declaration lives in `.claude/skills/harness/templates/PLAN.md`; the code branches solely on
`mode_token == "main-session-direct"`. So: an ungranted path plus `main-session-direct` prints `OK` as
a declared carve-out; an ungranted path with any other token, a missing token or an unrecognised one is
a `VIOLATION` and the run exits 1. When every literal path resolves to a granting agent, an
unrecognised token is *not* flagged — `team` is validated nowhere. The entry says so rather than
implying an enforcement that does not exist.

**The inverse case is surfaced, never silenced, and never fatal.** A task whose literal paths all
resolve to a granting agent but which declares `main-session-direct` prints a `DEVIATION` line and
leaves the exit status alone (`check-plan-routes.py:216-221`). That is the DEC-174 shape — the harness
plans its own work but does not execute changes to its own enforcement layer — and it is deliberately
legal. Making it a violation would forbid the carve-out; making it silent would let a hand-executed
task read as an ordinary team task in the one artifact a reviewer scans.

**Scope, stated so it is not over-read.** This is a plan-phase CLI, not a `PreToolUse` hook and not a
gate: `.claude/skills/harness-spec-driven/SKILL.md:39` tells the plan author to run it and fix every
violation, and nothing executes it automatically. Only *literal* `files:` entries are resolved; an
entry containing `*` or `?` prints `UNRESOLVED-GLOB` and contributes nothing to the violation count, so
a task whose paths are all globs is reported and passed over rather than guessed at.

---

## DEC-180 — The state-file SHAPE gate is independent of the DOMAIN gate: it binds every write route and every author, and reports post-hoc where it cannot block

DEC-150 made the state-file caps physics rather than advice. Measured at `ea24536`, they were physics
on one route of four. One 400-line `feature.yaml` against its 200-line budget, same target, same
payload otherwise:

| Route | Before | After |
|---|---|---|
| `Write`, `harness-orchestrator` | exit 2 | exit 2 (unchanged, still PREVENTS) |
| `Edit`, `harness-orchestrator` | **exit 0** | exit 2 post-hoc |
| `Bash` (`sed -i`, `cat >`, `python3 -c`) | **exit 0** | exit 2 post-hoc, via a swept read |
| `Write`, **the MAIN SESSION** | **exit 0** | exit 2 |

**The fourth route is not in issue #132, and it is the one that explains the ticket's own evidence.**
That ticket attributes a 226-line `feature.yaml` to `Edit`. The shape gate sat *below*
`check-domain.sh`'s domain carve-out `if not agent: sys.exit(0)`, so the main session escaped it on
every tool including `Write` — which accounts for the same observation without any appeal to `Edit`.
Shape is a **context budget**, not an authorization question: it binds whoever writes the file. So the
carve-out is now a `_governed` flag the DOMAIN phase reads, and the shape phase runs unconditionally.

**Detection where prevention is impossible, and the honesty is the point.** An `Edit` payload carries
`old_string`/`new_string` and no whole-file `content`; a `Bash` payload carries a command and no path.
Reconstructing either before the fact — replacement semantics, `replace_all`, TOCTOU, shell parsing —
is guessing at an answer the filesystem gives for free one moment later. So `check-domain.sh --post`
registers on `PostToolUse` for `Write|Edit|Bash`, reads what LANDED, and exits 2, whose stderr reaches
the agent. The budget is a context bound, and a report issued immediately after the write still lands
before the next reader loads the file. `PreToolUse` on `Write` is unchanged and still blocks.

**The domain phase is PRE-ONLY (`_domain_phase = _governed and not _post`), and this was a defect in
the first draft of this change, caught by its own test.** Post-hoc a domain denial is noise duplicating
a verdict the pre hook already gave, and `require_or_bootstrap` would SPEND the session's single
bootstrap grant on a question whose answer can no longer change anything. Measured before the fix: a
post-mode payload for an ungranted path exited 2 with the domain message, after the file was written.

**The Bash sweep is bounded by a HIGH-WATER MARK, and the fixed window it replaced was broken in two
ways review measured.** A `Bash` payload names no file, so the only honest answer is to sweep the state-file
globs. Measured on this tree — 120 matching files, 82 of them `state.yaml` the gate YAML-parses:
read-and-parse all 120 costs **515 ms**, `stat` on all 120 costs **0.2 ms**. 515 ms on the harness's
most-used tool would make the guard the slowest thing in the session. `PostToolUse` fires immediately
after the command, so a file that command wrote has an mtime inside the window. The whole hook measures
42.5 ms/call in post-Bash mode against a 48.6 ms/call pre baseline.

**Three review findings landed on the sweep and one on the registration, and the registration one was
the worst.** Narrowing the `PostToolUse` matcher from `Write|Edit|Bash` to `Write` in all three copies
left EVERY gate green — the unit suite at exit 0, `merge-settings.py` printing "all 8 prerequisites
present", INV-9 silent. `Write` alone is the one route that already worked, so that single edit reverts
this entire decision in production while the tree reports itself correct. `hook_present()` matched
basename only, ignoring both `matcher` and `args`; it now requires ours to be a SUBSET of what is
registered, INV-9 names the missing tools, and `test-check-state.py` case (m2) fails without it.

On the sweep: it never reached `.claude/worktrees/` (a live agent worktree held 38 matching files and
the sweep saw none — every harness agent works in one); it re-reported the same file on every
subsequent Bash call; and `git checkout --`, `git stash` and `git stash pop` all reset mtime to now,
dragging the whole tree into a fixed window at once. A stamp file under `.harness/` replaces the fixed
window with "changed since this sweep last ran", which fixes the second and third with less logic than
either would need alone. The window survives only as the first-run bound, where no mark exists yet.

**Round 2's own fix was worse than the bug for one round, and that is recorded rather than smoothed
over.** The stamp advanced to the moment the sweep FINISHED, so a file another agent wrote *during* the
walk landed before the new mark and was reported by nobody — reproduced 40 times out of 40 at a 40 ms
offset, and PERMANENT, because the stamp is global and shared. The repeat-reporting it replaced was
merely noisy. The mark now records the moment the sweep STARTED, so a write during the walk is strictly
newer than it; the cost is that such a file may be reported twice, and a duplicate report is the right
side of that trade. An unreadable candidate leaves the mark unadvanced for the same reason.

**Two gates were EXISTENTIAL where they had to be UNIVERSAL, and both were closed only after a reviewer
walked through them.** `hook_present()` and INV-9 each matched the FIRST registration mentioning
`check-domain`, so prepending a compliant decoy and narrowing the real entry back to `Write` passed all
four gates while restoring the 1-of-4 coverage. Both now union coverage across every entry. And both
matched the script by SUBSTRING, so `check-domain.sh.disabled` — a name that runs nothing — counted as
the hook; the match is now a whitespace token whose basename IS the script. A registration pointing at
a deleted file still reads as present, which is a residual this entry names rather than hides.

**The first fix for the matcher hole broke the thing it protected, which is why the test file exists.**
Binding the matcher was right; comparing `set(matcher.split("|"))` against a required set was not,
because a matcher is a REGEX. Six legitimate registrations were then reported missing — an absent
matcher key (which matches every tool), `".*"`, `"(Write|Edit|Bash)"`, anchored forms, and three
per-tool entries that together cover the requirement. "Missing" makes the installer write a SECOND
copy: measured, three entries became four and every `Write` fired the hook twice, while `--check`
failed a gate `harness-init` calls HARD. `test-merge-settings.py` now asserts both directions in one
table, because a fix for either alone is what produced the other.

**Findings name their file, ON EVERY ROUTE — and the first fix for that covered only one.** The sweep
walks up to 234 candidates across the main checkout and every worktree and named none of them: one
logical file present in five checkouts produced five byte-identical findings, and a reviewer received
another agent's transient fixture, unattributable, in their own session. Threading a display path
through the SWEEP alone left the named-target routes printing a bare `CLAUDE.md` — measured, an agent
told its file was 81 lines opened the 74-line root copy and concluded the gate was stale. All three
mutations of that threading survived every gate, because nothing bound it.

`_norm` and `_show` are now a deliberate pair: `_norm` strips the worktree prefix and answers "which
rules apply to this file"; `_show` does not strip and answers "which file am I talking about". All
three routes pass both. The mixed tuple arity that made the gap easy to miss — 3-tuples from the sweep,
2-tuples elsewhere, read back with `_t[2] if len(_t) > 2` — is gone.

A comment justifying the original fix claimed the stripped form "still carries `FEAT-NN` — enough to
tell two checkouts apart". A reviewer falsified that against this repo the same day: two live worktrees
emitted findings naming the identical strings `FEAT-02/STATE.md` and
`FEAT-05-pyyaml-file-parsers/STATE.md`. Stripping collapses every checkout onto one name for state
files as much as for `CLAUDE.md`; the latter is only where it is most obvious.

**Superseded:** The sweep walks up to 234 candidates across the main checkout and every
worktree and named none of them: one logical file present in five checkouts produced five
byte-identical findings, and a reviewer received another agent's transient fixture, unattributable, in
their own session.

**PyYAML's C loader, folded in on measurement.** `harness_yaml.py` subclassed the pure-Python
`SafeLoader` while `yaml.__with_libyaml__` was True — a default, not a decision. Re-measured here:
528.2 ms against 69.8 ms across this tree's 92 YAML files, with **zero** differences in parsed output.
Both overrides (D-08's timestamp strip, D-02's duplicate-key raise) apply to whichever base is chosen,
and the resolver copy keys off that base rather than a hard-coded `SafeLoader` — otherwise picking the
C loader would silently restore the timestamp resolution D-08 removed on purpose. This weakens the
sweep's own performance argument by 7.7x, which is a reason to record it plainly rather than bury it.

**INV-23 sweeps the same budgets from disk at `/harness` entry, at WARN level, and the level is
measured rather than tidy.** It is the backstop for a session where the `PostToolUse` half was never
registered — which INV-9 now asserts against separately, because the pre-existing check passes on a
tree carrying only the `PreToolUse` half. Run against this tree the day it landed, INV-23 found
`FEAT-05/STATE.md` at 165 lines against a 120 budget with five illegal sections, and `FEAT-02/STATE.md`
with five more, both predating the gate. Making those halt `/harness` entry would convert a reporting
backstop into an unrelated cleanup that has to land first. The write-time gate is the one with teeth.

**The duplication this creates now has a drift detector, because it doubled.** Before this change one
number — the handoff cap of 60 — appeared in both `check-domain.sh` and `check-state.sh`. Now 200, 120,
20 and 60 do, alongside the checkpoint vocabulary and the four handoff headings. The mechanisms stay
separate by D-02 (one measures a payload, the other a file); what is not deliberate is the two drifting
apart in silence, where one blocks at 201 and the other warns at 251 and no reader can tell which is
the budget. `test-check-state.py` case (o) reads both files plus `templates/HANDOFF.md` and asserts
they agree. Case (n) is what binds the DECLARED number to the ENFORCED one, and it earned its shape by
mutation: its first draft crossed both budgets at once and asserted only `"INV-23" in out`, so raising
the `feature.yaml` budget from 200 to 250 left the STATE.md finding in the output and the case still
reported ok. Each fixture now crosses exactly one budget by exactly one line.

**The prerequisite count is now derived, because adding one hook made every written count wrong at
once.** `merge-settings.py` carried "six" on five lines and the snippet three more, while
`harness-init/SKILL.md` said "seven" on five — counts re-derived with `git show origin/main`
after a first draft of this very paragraph asserted them from memory and got both wrong. The script now prints `len(HOOK_SPECS) + 1`; the prose says eight. A prose count that disagrees
with the code is how a reader concludes an entry is spurious and deletes it.



**Carve-out compliance.** `check-domain.sh`, `check-state.sh` and their tests are DEC-174 files: this
landed as direct main-session edits with tests run explicitly and a human reading the diff, never
through a team run whose gates are the thing being changed. Six mutants were run against
`check-state.sh` and six against `check-domain.sh`; five of the latter were caught and the sixth —
removing the `--post` argv blanking — was **not**, which is recorded in the code as the line being
defensive rather than load-bearing instead of being papered over with a test that cannot detect it.

---

## DEC-181 — CLAUDE.md gets a line budget of 80

**STRUCK IN PART, 2026-08-10.** This decision had two halves. The budget stands and is enforced at
`check-domain.sh:779-780`. The other half — putting `CLAUDE.md` into the propagation checker's scan
roots — went with the checker itself under DEC-188, along with every paragraph here that argued for
it. Nothing cites the struck half.

`CLAUDE.md` is read at **every session start** — the widest blast radius of any file in this repo,
wider than SPEC.md or any agent file. It was the only file of its class with no mechanical budget.
Its peers all have one: expertise 150, `feature.yaml` 200/20, handoff notes 60, STATE.md 120.

**80 was re-derived at `a5edb13`, not inherited from issue #139, and it comes from the file's own history, and that history STARTS AT A CLEANUP.** The file was
208-214 lines from April through 2026-07-27; DEC-135 then cut it to 50. That blow-out is why issue #139
exists — it says so, and an earlier draft of this entry began the table after the cleanup and read as
though the file had always been small. Since the cleanup: 50-51 through 07-28, 56 on 08-02, 71 on 08-04,
then **84**, at which point a human trimmed it twice, to 78 and then 74.

**The evidence constrains the number to roughly 75-83; it does not fix it at one.** Above 84 discards
the only judgement anyone actually made about this file's size, and 74 bans all growth. 80 sits inside
that band with six lines of headroom, which is thin deliberately: the file is preloaded into every
session, and two trims in one day say the right response to pressure here is to cut rather than to raise
the ceiling. An earlier draft called 80 "the only number with evidence" — that overstated it, and a
reviewer said so.

**Issue #139 ruled out `check-domain.sh`'s shape gate, and DEC-180 made that reason obsolete.** The
ticket says "it fires on `Write` only (see #132 — `Edit` and `Bash` bypass it) and the main session,
which is what actually edits `CLAUDE.md`, is ungoverned by it". Both clauses were true when written and
neither is true now: the main session is bound on all four routes. So the budget lives where the
four-route machinery already is, rather than in a fifth gate. `Edit` matters more than `Write` for this
file, and a `Write`-only gate would have bound the one route nobody uses on it.

**Two residuals, measured and accepted rather than discovered later.** The SHRINK EXEMPTION applies:
with the file at 200 lines, a `Write` payload of 150 is denied even though it improves things, because
the pre gate measures the payload. `Edit` is never blocked pre-hoc, so the author trims with `Edit` and
the post route reports until they are under — a working alternative, against a fix that would make the
pre gate read the file it is about to overwrite, adding file I/O and a TOCTOU window to the hot path.
And a `CLAUDE.md` nested in a subdirectory or a monorepo package is ungoverned on every route; the
pattern is anchored `^CLAUDE\.md$` and this tree has exactly one.

INV-23 sweeps it from disk at `/harness` entry as the backstop, at warn level, exactly as for the four
state files. That makes `CLAUDE.md`'s budget the **fourth** number duplicated across `check-domain.sh`
and `check-state.sh`, so it joins `test-check-state.py` case (o) — the drift detector — in the same
commit that duplicates it, rather than in a later one nobody writes.


---

## DEC-182 — The plan is `plan.yaml`, real YAML loaded with `safe_load`, and nothing in it is prose for a human

`PLAN.md` was markdown that LOOKED like YAML. No parser could use a YAML library, so three
scripts hand-rolled regexes against it — `check-plan-routes.py`, `check-state.sh` (INV-3/4/5),
`gh-sync.py` — plus the team runner via `teams/build.yaml`. Each invented its own rule for what a
value may contain, and nothing reconciled them.

**There was no decision establishing that format.** Searched `DECISIONS.md` and the index: nothing.
`templates/PLAN.md` prescribed it and the parsers were written to match. It was convention, never a
ruling — which is exactly why issue #147 could be filed and could not be answered.

**Measured, not argued.** `harness_yaml.load_str` over every task block in the four live plans fails
**43 of 44 times**. 26 because `files:` begins with a backtick, a reserved YAML indicator; 4 the same
on `verify:`; one — `execution_mode: **SPLIT` at `FEAT-08/PLAN.md:306` — raises *"while scanning an
alias"*. Meanwhile `intent:` and `verify:` already use folded `>` scalars in 64 places: the authors
were writing YAML-shaped values all along, and only the markdown-decorated fields broke.
`SPEC.md:1701-1702`, the NORMATIVE example, was itself illegal YAML — three keys on one line — and
shipped that way because nothing ever tried to parse it.

**A fenced ```yaml block inside markdown was considered and refused, and the 43-of-44 figure is the
argument against it rather than for it.** A fence is the same mixture with a border drawn round it:
an author who decorates a value today decorates it inside a fence tomorrow. It makes the mistake
loud instead of silent, which is worth something, and it is compensating code for a problem the
format invites. A plain `.yaml` file cannot tempt the author, because nothing else in it is prose.

**`feature.yaml` was not available as the alternative home, and the schema refuses it by name.**
`SPEC.md:1687-1692`: `feature_id` is "join key ONLY — no name, no traces, no task list. Those live in
PLAN.md, which is what you approve; duplicating them here would let an agent redefine what FEAT-01
means without your signature." Audited while deciding this: of 182 DEC entries, **1** names a
`FEAT-NN` in its ruling and **0** are dominated by a single feature, so `DECISIONS.md` carries no
feature-local pollution in the other direction either.

**What the agents actually read decided the split** — measured, not assumed. `intent:` is the
LITERAL dispatch prompt (`teams/build.yaml:59`); `verify:` is a byte-exact cross-file contract;
`depends_on:` orders the build; `change_type:` feeds the qa gate and the issue label; `files:` and
`execution_mode:` are read by `check-plan-routes.py` alone; `traces:` is captured at
`gh-sync.py:163` and **never used**. So DEC-154's test — *"if a value needs to be read rather than
matched, it is in the wrong file"* — puts everything in one file, because the one long field is the
dispatch prompt and the human reads `BRIEF.md`.

**Issue #147's three questions are answered by the type, not by a ruling.** Legal `files:` shapes:
exactly one, a sequence of strings — block and flow style load identically, so the three shapes the
old parser accepted collapse into one thing nobody adjudicates. Annotations like `(delete)`: the
loader returns the literal authored string, so a resolver gets what was written instead of guessing
which characters were commentary; the old `_clean()` stripped backticks and a trailing comma but not
a parenthetical, so `` `bin/cost-report.py` (delete) `` resolved ONLY because a `/**` grant swallowed
the suffix. `execution_mode: **SPLIT`: unwritable, because `**` opens an alias and the loader raises
first — and the real need behind it, one task with two routes, is TWO TASKS.

**Forward-only, and shipped plans are never route-checked again.** Checking them was the default
behaviour of a glob and never a decision: the work shipped, the routes were taken, the plan will not
be re-executed. Measured before: 36 violations across 8 plans — 27 `no files: line`, 8 the
pre-FEAT-06 prose shape, **0 routing defects**, all in delivered work. That noise is why issue #133's
gate could never be switched on. After: **1**, on live work, and it is FEAT-08 T-04's `**SPLIT`.
`status:` is a BORROWED signal for era — it means "how far along" — and it is used deliberately
because no `feature.yaml` carries a `schema_version`. A feature that cannot be classified is
CHECKED, never skipped.

**The `PLAN.md` reader is a migration-window reader, not a permanent one.** An earlier draft of this
entry said permanent; that was wrong and untested. Four live features still carry `PLAN.md` and
INV-3/4/5 must keep working for them. Once they ship it can go, and shipped plans stop being parsed
at all — verified: INV-3/4/5 report 0 findings across the five shipped features today.

**The budget is PER TASK, 30 machine-field lines, and the asymmetry against every peer is
deliberate.** Derived the way DEC-181 derived CLAUDE.md's 80: measured machine+verify lines per task
are 11.5 (FEAT-09), 21.2 (FEAT-06), 26.7 (FEAT-07), 19.9 (FEAT-08), so 30 leaves ~12% headroom. A
plan is a LIST — its length tracks how many tasks a feature has, not how much fat it carries — so a
flat file cap would be a cap on how many tasks a feature may have, a scoping decision wearing a
budget's clothes. `intent:` is excluded from the count because it is READ. Enforced in
`check-plan-routes.py` at plan time, not in the shape gate: pm holds `upsert: true` and drafts with
`Edit`, and that gate measures `Write` payloads.

**`plan.yaml` is deliberately absent from `check-domain.sh`'s shape gate.** Shape is not budget —
that conflation was mine and the user caught it. `feature.yaml` 200/20 and `CLAUDE.md` 80 are
budgets; `state.yaml`'s 23-key whitelist is a VOCABULARY with no cap at all; `STATE.md` and the
handoff note are both. A `plan.yaml` check there would be a PARSE check, a third thing — and
`check-plan-routes.py` already refuses a malformed plan BEFORE signature, with `check-state.sh`
refusing it again at entry. A third enforcement point bought nothing and cost two entries in two
pattern lists that had already drifted once during this very change.

**Behaviour change worth stating rather than discovering:** a GitHub issue opened from a `plan.yaml`
task carries the task's `intent:` as its body, where a `PLAN.md` task passed its whole raw block.
Existing issues are not rewritten, so the corpus is mixed.


---

## DEC-183 — The route check is promoted to a step of the `integration` CI job, and the step asserts the plan COUNT, not just the exit code

`check-plan-routes.py` shipped working and nothing mechanical ran it (issue #133). DEC-179's clause
"nothing executes it automatically" is now false.

**The venue is CI, and the step goes INSIDE the `integration` job.** Branch protection requires
exactly that one context, and it is the job's ID — the job carries no `name:` key. A job of its own
would emit a context nobody requires, which is the defect being closed rather than a fix for it, and
adding a `name:` renames the context and blocks every PR forever. `check-state.sh` was rejected on
WHO MAY WRITE IT, not on merit: it is a DEC-174 carve-out, so an invariant there forces a
main-session-direct edit for every future adjustment. Both venues together was refused — DEC-182
turned down a third enforcement point one PR earlier.

**The cost is EARLINESS.** Issue #133 framed the check as plan-time; CI fires at PR time, when the
plan is signed and the tasks may already be built. That is why the planner-facing sentence stays in
`harness-spec-driven/SKILL.md` rather than being replaced. No venue had both.

**The step asserts M, and that assertion is the whole promotion.** The checker's final line is
`N violation(s) across M plan(s)`, and a step reading only `$?` passes when M is 0 — a green tick
from a gate that examined nothing. Three outcomes get three messages: no summary (the checker could
not run), a summary with M=0 (it ran and looked at nothing), and a real verdict. `|| true` on the
summary grep is load-bearing, not defensive: under `bash -e {0}` an unmatched grep inside a command
substitution kills the step before either diagnostic prints.

**THE STEP IS UNGUARDED, BY DECISION, AND THAT REOPENS ISSUE #133.** An earlier version of this
entry described a suite of assertions defending the step — that the workflow defines the required
job, that the step is present and unneutered, that the job header carries no `if:`, `needs:`,
`defaults:`, `env:` or `container:`, that the step list and `uses:` set are pinned, and that the
bodies are executed rather than read. **All 39 of those assertions were deleted by owner decision**,
along with the harness that executed workflow bodies against a cloned workspace. Nothing in this
tree now asserts anything about `.github/workflows/tests.yml`.

The consequence is specific and is not softened here: `pull_request` runs the workflow definition
from the PR's own ref, so **a PR that deletes the `Plan-route gate` step still emits a green
`integration` check and satisfies branch protection.** The gate can be removed by the same PR it
would have failed. That is issue #133's own shape — "the guard is right and nothing calls it" —
restored at one remove, and it is accepted rather than unnoticed.

The control that remains is a human reading the `.github/` diff, and **nothing requires one — nor
can anything, on this repo as it stands.** `required_pull_request_reviews` on `main` is null: one
required context, `enforce_admins` on, zero required reviewers. CODEOWNERS covering `/.github/` and
`run-unit-tests.sh` is committed and **deliberately not enforced**, because enabling
`require_code_owner_reviews` would make every PR to `main` permanently unmergeable — measured, not
predicted: `mruangutai` is the sole collaborator and therefore the only possible code owner, GitHub
forbids authors approving their own pull requests, and `enforce_admins: true` removes the bypass.
The repo's own history shows the policy already in effect — **52 reviews, every one `COMMENTED`,
none `APPROVED`.** #175 is closed as not achievable; it becomes possible only with a second
collaborator. So the honest statement is that this gate protects the plans and **nothing protects
the gate** — not pending, settled.

**Also removed by owner decision: `actions/setup-python@v5` and the root-assert step.** The job is
four steps — checkout, Install PyYAML, Integration suite, Plan-route gate. The Python version is no
longer pinned, so a runner-image bump changes the interpreter with no diff here; and nothing
observes the runner's uid, so if the job ever ran as root the `chmod 000` assertions elsewhere in
the suite would pass for the wrong reason and go QUIET, not red.

**The per-feature off-switch is a one-word status flip, named rather than closed.** The checker skips
`shipped` and `abandoned` features (DEC-182). Promotion made that skip load-bearing: flipping a
feature's status takes the gate green without touching CI. Accepted as an escape hatch — status is
the one signal that says work is delivered, and refusing to trust it re-introduces the noise DEC-182
removed. Failing when M drops in the same PR that flips a status was weighed and declined: a
legitimate ship drops M by one, so the common case would fire and the fix would be an override.

**This gate is RED at the commit that introduces it, deliberately** — FEAT-08 T-04's
`execution_mode: **SPLIT`, a real finding in live work. A gate switched on green by exempting the one
thing it found would be enforcement theatre.

**Scope:** no prior decision established this workflow, and this one does not adopt it. It rules on
the route step alone; #163's triggers and #161's reasons keep their justification in the file's own
comments. **Not verified:** the real CI run.

**Amendment 1 (2026-08-21) — the reason the 39 assertions were deleted, recorded at last.**

The entry above says only "deleted by owner decision" and gives no reason, so the question was
reopened once and cost a review round. The reason, stated by the operator on 2026-08-21, is two
things and the second is the load-bearing one:

1. **The harness was too heavy.** What was deleted did not merely read the workflow — it cloned a
   workspace and EXECUTED workflow bodies against it. That weight is what was rejected.
2. **A check on this workflow does not belong in this workflow.** `pull_request` runs the definition
   from the PR's own ref, so one PR edits a step and its guard together. A guard hosted here cannot
   protect its own host step: delete the `Integration suite` step and every assertion inside it
   simply never runs. Neutering is detectable; deleting the host is not.

**What this settles, and it is narrower than it sounds.** A LIGHTER guard is not the answer either,
because reason 2 is structural rather than about cost. A proposal to add a pure predicate over
`yaml.safe_load` of this workflow — no clone, no body execution — was worked up in full, planned, and
then ABANDONED on this reasoning: it shrinks the hole (it catches a hollowed-out step and the deletion
of the inner gate steps) and cannot close it (it cannot see the deletion of the step that runs it).

**What remains unmeasured.** Whether a GitHub ruleset, a required workflow, or a workflow pinned to a
different ref can run a check the pull request cannot edit. Nobody has checked. If one can, reason 2
dissolves and this amendment should be revisited; until then the conclusion below stands.

So the original conclusion holds for a better-stated reason: **nothing protects the gate — not
pending, settled.** What DID change is the honesty of the file: four citations in
`.github/workflows/tests.yml` claimed guards that do not exist, including one naming a real, green,
passing test that asserts something unrelated. Those were repaired, so a reader who follows a
citation now finds what it claims or finds it saying plainly that nothing is there.

## DEC-184 — Design 0001, reconstructed stub: the work-graph engine is a recorded future design, deferred until multiple seats need atomic claiming

**Reconstructed after the fact (2026-08-08), not a transcript.** `docs/PRINCIPLES.md` cited a
"Design 0001" research brief that was never written down; the operator ruled (effort #181, ticket
#191) that Design records live HERE, in this file, not in a separate design store. A later ruling
the same day made the constitution standalone — no identifiers, no amendment records — so
PRINCIPLES.md no longer cites Design 0001 by name; this entry and git history are the lineage's
only home. The stub adds nothing beyond what PRINCIPLES.md stated.

What PRINCIPLES.md records of it (the deferral still stands there, now without the identifier): the work-graph engine is deliberately deferred — local SQLite is
correct until multiple seats need atomic claiming, and the options on that day are adopt Beads, fork
it as Harness's own, or build from scratch ("Deliberately deferred", `docs/PRINCIPLES.md`).

For effort #181 ("Personal Software Factory"), this deferral is CONSUMED by the operator's GitHub
ruling of 2026-08-08: GitHub Issues are the work ledger for that version.

## DEC-185 — Design 0002, reconstructed stub: the minimal roster is a starting point, and management seats exist

**Reconstructed after the fact (2026-08-08), not a transcript** — same provenance and same operator
ruling as DEC-184, and the same standalone ruling applies: PRINCIPLES.md now carries no amendment
records, so the text below survives only here and in git history.

What PRINCIPLES.md recorded of it (dated 2026-08-06 there, before the amendment notes were removed):
the original constitution text fixed the
roster with no place for a management seat; the operator ruled the minimal roster was a starting
point, not an endpoint, founding management seats that orchestrate and never produce. The same
ruling amended the Bootstrap section: the first harvest produced a Harness backlog before any
outside project was registered, and the operator ruled Harness-first with the outside-ship tripwire
kept (pre-rewrite rule 10 and "Bootstrap" of `docs/PRINCIPLES.md`; git history holds the text).

## DEC-186 — STRUCK 2026-08-25

**Struck under DEC-188, replaced by DEC-203.** Its heading read *"GitHub is the factory's control
plane, and factory read-back is bounded to exactly three purposes"*; amendments 2 and 3 had already
widened three to five. DEC-203 carries the read-back bound forward at SEVEN purposes and keeps the
rule the bound exists for — a read-back value never enters `BRIEF.md`, `plan.yaml` or any approval
block — and it keeps amendment 1's one-board-per-repository-served framing.

Struck rather than amended because the sixth and seventh purposes arrive together with a change to
who writes the done station, and three entries were each stating part of one lifecycle. Splitting a
seventh amendment off from that would have left the rule in three places again.

The body below stands so citations resolve. Do not act on its numbers: read DEC-203.

The factory publishes work to GitHub Issues and one Projects v2 board, and then has to read some of
it back — otherwise no tool can tell whether an item is already taken. DEC-138 made the mirror
one-way and outbound precisely so that a wiki-editable surface could not feed an approval-gated
artifact. Effort ticket #184 found that treating issues as truth after approval contradicts DEC-138,
DEC-182 and DEC-168; effort ticket #182 found that a factory needs some read-back to exist at all.
This entry rules on the bound between those two findings.

**GitHub Issues and one Projects v2 board are the factory's INTERFACE and control plane; the
approval-gated `plan.yaml` remains the source of truth for what the work is.** Factory tools may
read GitHub state back for exactly THREE purposes, and the set is closed: learning whether an item
is claimed, learning or setting which station it is at, and learning whether a blocker issue is
finished. A read-back value is never written into `BRIEF.md`, `plan.yaml` or any approval block. The
only harness file a factory tool writes is a feature's own `feature.yaml` factory block.

**The third purpose is a ruling, not a detail, and it widens the bound by exactly one item.**
`factory_claim` MUST NOT claim an issue whose plan dependencies are unfinished, so blocker
completion has to be readable. Blocker state is neither a claim nor a station: it is a gate on
candidacy, applied before ownership, bookkeeping or the station field are engaged at all. It
therefore did not fit the original two-purpose bound, and the bound was widened deliberately rather
than stretched to cover it. The operator ruled it in at the plan review of 2026-08-08 and rejected
deferring enforcement, on the ground that a board which renders a block marker and then hands the
work out anyway is worse than no marker at all — the operator reads the board and believes ordering
holds.

**What is read, and from where.** The DAG authority stays the signed `plan.yaml`'s `depends_on`.
Resolution runs a task's `depends_on` to `feature.yaml`'s issue map to that blocker issue's open or
closed state, and GitHub contributes the last hop only. **What is NEVER read is the rendered
`blocked_by` edge on GitHub** — it is hand-editable, so deriving control flow from it would put a
remote object in charge of the signed DAG, which is the inversion DEC-138 exists to prevent.

**The cost is a blocker-state read PER BLOCKER PER CANDIDATE, not one per candidate.** It is bounded
by the ready column rather than by the board, because the board read is already a server-side query
on the ready station option — on board 3 that query returned 1 item against 150 on the board.

**Two edges are ruled here rather than left to the implementation.** A `depends_on` entry that
cannot be resolved to an issue counts as BLOCKED rather than clear, and is reported on stderr. An
issue the factory cannot resolve to a plan task at all — a `gh-sync.py` mirror issue with no feature
label — is not gated and stays claimable.

**An amendment, not a contradiction.** Bounding the read-back to those three purposes and to nothing
else keeps DEC-138's actual guarantee intact while letting the control plane work: nothing read back
is ever written into an approval-gated artifact.

**Scope.** This entry rules on factory read-back and on the claim mechanism, and on nothing else.
DEC-179's plan-time route resolution and DEC-182's plan format are untouched by it.

**Failure behaviour is deliberately the opposite of the mirror's.** `gh-sync.py` prints SKIP and
exits 0 on any environmental failure, because a mirror must never gate a flow. The factory
control-plane tools exit non-zero instead, because a control plane that skips leaves the board
asserting a state that is not true.

**The claim is a git ref create, and the reason is the part a future reader will want.** Ownership
is taken by creating the ref `refs/heads/factory/issue-N` in the target repository — a
create-if-absent that the server decides. The `factory:claimed` label and the assignee are
operator-visible bookkeeping that the winner writes afterwards. The rejected alternative is
assignment as the claim, rejected because an assignee set is additive: two racing agents both
succeed, neither can conclude it won, and the issue is left marked and owned by nobody. **The
residual risk, plainly:** that concurrent ref creates serialise is INFERRED from the endpoint being
create-only, NOT MEASURED, and no success criterion exercises the live concurrent case before ship.
The operator accepted that on 2026-08-08, so the first real dispatch is the live verification.

**D-12 — two known duplications this increment records rather than fixes**, so that a later reader
finds them named instead of rediscovering them. First, `gh-sync.py` and `factory_decompose.py` are
two independent issue writers keeping two T-NN-to-issue maps in one file, `feature.yaml`'s `github`
and `factory` blocks; `mruangutai/harness` is both a candidate fleet member and `harness.json`'s
`github.repo`, so running both there yields two issues per task, and INV-24 detects collisions only
within the factory ledger. Second, the publish idempotence key is `feature.yaml`, which is LOCAL
state, in a feature whose non-negotiable constraint is that GitHub is the single source of truth — a
lost or reverted `feature.yaml` republishes duplicates. Both are judged non-blocking for increment 1
and both are named here as work a later increment owns.

**The rejected alternative: issues as the post-approval source of truth**, rejected because it
reopens signed choices through a surface with no signature.

### DEC-186 amendment 1 (2026-08-12) — one board per repository served, with the three-purpose read-back bound unchanged

**The control plane is one board PER REPOSITORY SERVED.** FEAT-16 declares the station board inside
each `repos:` entry of `.harness/factory/fleet.yaml`, so the ruling clause above beginning "GitHub
Issues and one Projects v2 board are the factory's INTERFACE and control plane" is superseded in its
"one Projects v2 board" framing only. Everything else in that clause stands: the three purposes
remain exactly three — whether an item is claimed, which station it is at, whether a blocker issue
is finished — the set stays closed, and this amendment neither widens nor narrows it. The
approval-gated `plan.yaml` remains the source of truth for what the work is.

**The read-back cost model changes shape, not size.** The clause above beginning "The cost is a
blocker-state read PER BLOCKER PER CANDIDATE" states the board read as one server-side query on the
ready station option per poll; it becomes one such query per repository served per poll. That scales
with FLEET SIZE and not with board size — a fleet of one repository pays exactly what the original
model priced, and each repository added costs one more server-side query, whatever its board holds.

### DEC-186 amendment 2 (2026-08-23) — the read-back bound widens to FOUR, and the fourth is `/harness-init` reading a board's workflow list

**The set was closed at three and it is now closed at four.** The fourth purpose is learning **which
of a board's native workflows are enabled** — `Item closed`, `Auto-close issue`, `Pull request
merged`. It is bounded to `/harness-init`: no other surface makes this read, and nothing in a build,
a claim or a station flip may reach for it.

**Widened by an operator ruling, not by re-categorisation.** FEAT-33's plan argued the read is
*configuration* rather than *control flow* and therefore already inside the bound. The architecture
review rejected that, correctly: the third purpose was added on 2026-08-08 by an explicit ruling
recorded as a widening by exactly one item, and re-labelling a fourth read is not the same act. The
operator was given both branches — widen, or drop REQ-02 — and ruled to widen on 2026-08-23. This
amendment is that ruling.

**The reason is that the harness does not move cards to `Done` — GitHub does.** When `Item closed`
fires, a closed issue's card moves. When it is off, every card stops moving and nothing reports it;
the failure is discovered by a human noticing the board looks wrong. Measured the same day this was
ruled: FEAT-32's parent `#700` read `Building` while its `feature.json` read `Review`, and its
sub-issue cards reached `Done` only because that workflow happened to be on. **A dependency only a
human click can satisfy, with no reader, is the same shape as an assertion that cannot go red.**

**What it does NOT authorise.** The read is REPORT-ONLY and writes nothing. Only a click enables a
workflow, so `/harness-init` names each one that is off and says so. A read-back value still never
enters `BRIEF.md`, `plan.yaml` or any approval block, and the fourth purpose gives no tool a new
write.

**Not a strike.** DEC-186's ruling, its rationale and amendment 1 stand. What changed is the number,
from three to four, and the fourth carries its own surface bound.

### DEC-186 amendment 3 (2026-08-23) — the read-back bound widens to FIVE, and the fifth is ship deriving a pull request number from the feature's own recorded branch

**The set was closed at four and it is now closed at five.** The fifth purpose is learning **which
merged pull request a feature's recorded branch resolves to** — `gh pr list --state merged` filtered
on that branch. It is bounded to `gh-sync.py record-pr` and to `gh-sync.py ship`, which calls it: no
other surface makes this read, and nothing in a plan, a build, a claim or a station flip may reach
for it.

**Widened by an operator ruling, not by re-categorisation.** DEC-200 recorded both readings and
settled neither. The competing reading — that the mirror is simply outside DEC-186's scope — has real
textual support: DEC-186's own **Scope.** clause says it rules "on factory read-back and on the claim
mechanism, and on nothing else", and its failure-behaviour clause treats the mirror as a different
class throughout. It is refused on precedent. **Amendment 2 rejected exactly this move**: FEAT-33
argued its read was already inside the bound, and the architecture review ruled that "re-labelling a
fourth read is not the same act" as an explicit widening. Declaring this read outside the scope is
that same re-categorisation, one step further. The operator was given both branches and ruled to
widen on 2026-08-23. This amendment is that ruling, and it closes DEC-200's open question.

**The reason the read exists at all is that the number has no local source.** DEC-153 keeps the
harness out of opening pull requests, so the operator opens it and GitHub alone knows its number.
Every other value `gh-sync.py` writes has a local receipt to re-derive it from — the parent issue,
the milestone, the T-NN map. The pull request number has none, which is the distinction DEC-138
amendment 7 turns on and the reason a write-only mirror may read this one thing.

**What it does NOT authorise.** The read is bounded to the feature's OWN recorded branch and returns
one integer. It writes only `feature.json`'s `pr`, once, and never overwrites a value already there.
A read-back value still never enters `BRIEF.md`, `plan.yaml` or any approval block, and the fifth
purpose gives no tool a new write. **`gh pr list` is never used to discover work, to pick a branch,
or to decide what a feature is** — only to name the change that already shipped it.

**Not a strike.** DEC-186's ruling, its rationale, amendment 1 and amendment 2 all stand. What
changed is the number, from four to five, and the fifth carries its own surface bound.


## DEC-187 — The test matrix is per-project, and a kind with no runner is excluded by decision, never by inference

The qa gate is the project's only blocking gate, and on 2026-08-09 it could not return a verdict on
FEAT-10. `test_matrix` requires a `functional` test for `api` and `cross_module` changes; the factory
tools shell out to `gh` and `git`, which is crossing a process boundary; and `functional` cannot run
here for two independent reasons — `cmd` is null, and `detect` is `tests/functional/**` in a
repository that has no `tests/` directory.

The cause was not the requirement. It was that `test_matrix` and `test_kinds` are two halves of one
contract and only one half was ever given an owner. `dev-ops` detects `test_kinds.cmd` per project at
init. The matrix has no owner, no init step, no upgrade path, and nothing that checks the kinds it
names against the kinds that can run. This repository's matrix is character-for-character the
template's, and the template describes a web application — endpoints, components, client state,
`.tsx` files. Five of its seven kinds have no runner here.

**The matrix is per-project, with a closure invariant instead of a freeze.** Every kind the matrix
names must exist in `test_kinds` and be either `active` — a `cmd` someone has run and seen pass — or
`excluded`, which is a human's recorded decision that this project does not practise the kind.
`unresolved` is the template default and means nobody has decided yet; it blocks.

**A kind resolves to a soft skip only when its status is `excluded` and its `signed` value names a
decision that resolves in the project's decisions file.** An excluded kind is not selected at all,
so neither its `cmd` nor its `detect` is read, and the gate reports it by name with that decision id.
In every other case a null or unrunnable `cmd`, or a `detect` glob matching nothing, is BLOCKED —
never a skip and never a FAIL. That settles a contradiction that had been live across eight files:
three said BLOCKED, five said soft skip, and one of the five was `harness.json`'s own note, which
every agent reads as data.

Two records are added to `harness.json`. `status` on every kind, with `excluded_because` and `signed`
whenever it is `excluded`. `_matrix_provenance` beside `test_matrix`, one entry per change type that
differs from the template, naming what was removed or added and the decision that signed it. The
baseline `_matrix_provenance` measures against is **the template as it stood at this decision**; a
later template change does not retroactively make an entry wrong.

**This clarifies DEC-35's scope rather than amending it.** DEC-35 fixed the *predicate names*
(`touches_db_or_external`, `has_interaction_flow`, `match_bug_class`) as data so qa's judgment stays
auditable. It never said the table must be identical across projects, and it already scoped
`test_kinds.cmd` as per-project. Tailoring was in fact already happening, ungoverned: the one
onboarded reference, `templates/examples/harness.kaya-ai.json`, deleted `functional`, added a
project-specific `python` kind, and reshaped four change types — and is broken, because its
`bugfix.always` names `__bug_class__`, a predicate placeholder that exists in no `test_kinds` and can
therefore never resolve. Ungoverned tailoring is what this entry replaces.

**Applied here: this repository excludes `functional`.** `run-unit-tests.sh` splits its suite on one
stated principle from issue #160 — does this drive a real script end to end? — into in-process
`UNIT_SCRIPTS` and forking `INTEGRATION_SCRIPTS`. There is no third bucket, this repository ships no
service API, and pointing `functional` at either array would double-count files the other kind
already runs. There is no honest `functional.cmd` here, so the requirement is removed from
`api.always`, `cross_module.always` and `feature.always`, and the kind is retained with
`status: excluded`.

**The kind is retained, not deleted, and that is load-bearing.** Three DEC-163 surfacings trigger on
the key existing with a null `cmd`: INV-20 in `check-state.sh`, pm's `## Verification gaps` block,
and the init interview's null-kind loop. Deleting a kind silences all three — it goes past the soft
skip DEC-36 forbids, to no record at all. `upgrade-config.py`'s additive merge also re-adds a deleted
key wholesale from the template, stale placeholder reason included, while a narrowed `always` list
survives untouched. So the rule is: narrow the lists, never remove the keys.

**Rejected: standing up a functional runner.** It would pass vacuously, because this feature has no
functional tests to put under it, and a green gate over an empty suite is the silent no-op DEC-36
exists to prevent.

**Rejected: settling the null-`cmd` contradiction toward soft skip and leaving the matrix alone.**
It does not even unblock — the empty-`detect` trigger survives independently — and it would convert
every unrunnable kind in every project into a silent pass.

**Tradeoff accepted, and it is real.** This lowers the floor for every future feature in this
repository. If a service surface ever appears here, `functional` must be reinstated, and nothing
active will prompt that — only the `_matrix_provenance` entry, which is findable but passive. The
compensating control is the closure invariant, which makes the *absence* of a runner for a *required*
kind a violation rather than a warning, because a warning is what already failed.

---

## DEC-188 — A contradicted decision is struck, not marked: detection is replaced by deletion

**The operator's rule, 2026-08-09.** If an existing decision is one the tree absolutely goes
against, with zero room for interpretation, it is **struck from the record and removed from every
gate**. Not marked stale. Not amended. Not left standing with a marker beside it.

DEC-103 and DEC-104 are struck, and DEC-181 is struck in part. `bin/check-docs.sh` is deleted, the
INV-10 block is out of `check-state.sh`, and the 66 stale-wording markers and 14 escape
comments are gone from the live docs.

**What forced it was the mechanism's own failure mode.** A change contradicted a passage in DEC-165.
Under the old convention that needed a `stale` marker, and a marker has to be hosted by the decision
that supersedes the wording. The natural host, DEC-161, had already been deleted. There was nowhere
to put the declaration. A convention with no valid place to record the thing it requires is not a
convention.

**What is traded away, stated plainly rather than softened.** The repo loses the only mechanism that
catches a doc statement a later decision falsified. That gap is not theoretical here: DEC-103 exists
because, after twelve decisions were recorded, SPEC and BUILD still held **ten** statements those
decisions had already falsified — and the SPEC/DECISIONS/BUILD split had been created to prevent
exactly that, and did not.

The new rule replaces detection with deletion: nothing survives to contradict, because the
contradicted decision is struck. **This holds only while the striking actually happens every time,
and nothing mechanical now checks that it did.** The enforcement is a human reading a diff.

**The rule does not generalize by itself.** It applies to a flat contradiction with no room for
interpretation. Anything softer than that — a decision that is merely dated, narrowed, or partly
overtaken — is amended, and striking it needs the operator's word first.

**A struck decision is DELETED only when a named successor exists to repoint its citations to.** A
successor need not carry the rule forward; it need only explain what happened, which is all the
citation ever asked for. Where no successor exists the entry keeps its heading and its strike record,
because an absent entry with nowhere to point reads as a broken reference rather than as a decision.
DEC-90 is the one entry this rule keeps, because its successor is a SPEC section rather than a
decision and its historical citations cannot be edited.

## DEC-189 — The write guard resolves against two bases, and which one applies is decided from the target

**The factory works on repositories it does not contain.** A product repo lives on its own, is
checked out under the fleet's `workspace_root`, and is worked on from a harness-rooted session — so
it is harness's hooks that fire, never the product's. Until this rule the guard had one base, the
harness checkout, and every path outside it received **no verdict at all**: not a refusal, not a
message, not a log line. The twelve product-shaped entries in `team-config.yaml` described paths the
guard never evaluated. They appeared to work only because harness happens to own a `docs/` and a
`README.md` of its own.

**A target resolves against the harness checkout, or against the checkout of a repository declared
in the fleet.** Which base applies is decided from the **target**, never from the manifest entry,
and there is no manifest schema change.

The rule is two-sided, and stated mechanically because prose is what admits the wrong reading:

- **In the harness checkout** every entry is matched, product-shaped and control-plane alike, and a
  match is accepted only when the base-relative target is **control plane** — its first path segment
  is `.harness` or `.claude`, or it is one of four named harness paths: `docs/harness/**`,
  `docs/PRINCIPLES.md`, `README.md`, `.github/**`.
- **In a product checkout** entries whose first segment is `.harness` or `.claude` are excluded and
  the rest apply normally. **The four named paths are not consulted there.** They are target-side
  only, so a product repository keeps its own readme, its own docs and its own CI — the files its
  documentor and its dev-ops exist to write.

Consequently a `src/**` grant refuses `<harness>/src/main.py` and permits `<repo>/src/main.py`; a
`.harness/expertise/**` grant permits it here and refuses it inside a product checkout; and a
`docs/**` grant reaches `<harness>/docs/harness/guide.md` and `<repo>/docs/guide.md` both.

**Lineage.** The shared block this narrows is DEC-85's. The guard being changed is the one DEC-174
carves out of self-hosted execution, so this landed as direct main-session edits with the tests run
explicitly. DEC-151's sibling guard on the Bash route is **not** changed here, and the asymmetry that
leaves is filed rather than absorbed.

**Target-keyed is not a preference, it is the only shape that expresses the rule.** `team-config.yaml`
grants `docs/**` and contains no `docs/harness/**` entry anywhere. A glob-keyed classifier would have
nothing to match two of the four named paths against.

**Three boundary answers, so none is inferred.** A path under the workspace root belonging to no
declared repository is **refused** — a checkout there for an unlisted repo is stale or a mistake. A
fleet declaration that exists and cannot be read **closes every write**, not only writes to workspace
paths, because the value that identifies product paths is the one that failed; enforcing the readable
parts would mean classifying paths with the classifier missing. An **absent** declaration changes
nothing: a project with no factory has no second base and keeps the prior behaviour exactly. A path
outside both bases still receives **no verdict** — `/tmp` is not the repo, is not deployed, and is
not state.

**The accepted risk, recorded so it is not rediscovered as a defect: this is one more place to
remember.** A harness-owned path beginning with neither `.harness/` nor `.claude/` and absent from
the four named paths is treated as a product path. A per-entry base tag, a two-list split and a
value-level prefix marker were each offered and declined, because each changes the grammar every
future entry must carry. **No detection machinery is added.** The omission is accepted, not fixed.

**What lost a route, stated precisely rather than generally.** Observed at `d0f0ee9`:

- **No live harness file loses one.** The four named paths carry harness's own docs, its
  constitution, its readme and its CI, which is why they were named. This rests on nothing in
  `docs/` sitting outside `docs/harness/` except `docs/PRINCIPLES.md`, which was checked rather than
  assumed.
- **The shared block loses its route in the harness checkout.** All eight entries are dependency
  manifests and lockfiles — `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`,
  `pyproject.toml`, `uv.lock`, `requirements.txt`, `tsconfig.json` — and none is control plane, so
  each stops being a serialized allow and becomes a refusal here. Serialized-allow survives where
  those files actually live: a product checkout.
- **The live set of affected files is EMPTY**, stated explicitly rather than omitted: none of those
  eight exists in the harness repository. The consequence is latent. Adding one would need it named
  the way the four are named.


### DEC-189 amendment 1 (2026-08-20) — the illustrative paths are respelled `<repo>`, tracking DEC-193 am.2

This entry's two examples read `<product>/src/main.py` and `<product>/docs/guide.md`. They now read
`<repo>/...`. Nothing about the two-base resolution changes; only the name of the segment, so that
this entry and DEC-193 do not spell one idea two ways — which is the drift DEC-193 am.2 closes.

**Recorded here because the edit was made in place.** The reasoning lives in DEC-193 am.2, and a
reader who opens THIS entry through the index would otherwise find altered text with no local note
that it changed or why. An unrecorded edit to a decision is indistinguishable from a decision that
always said that.

## DEC-190 — `jsonschema` is a required dependency, and a missing import is a loud error

**A feature's execution state is validated against a real JSON Schema at write time**, and the
library that does it — `jsonschema` — is **required**, not optional. This is the second dependency
the harness takes, and it takes the shape DEC-171 am.1 established for the first.

**The shape, borrowed whole from PyYAML's clause (DEC-171 am.1).** A missing import is a **loud
error that names the install command**. It is never a silent skip, never a warning that lets the
flow continue, and never a quieter mode that validates less. The reason is the one DEC-171 already
paid for: a degraded path that validates nothing is indistinguishable, from the outside, from a
validator that passed — and the harness's own gates are the thing that would be reporting green.
There is no hand-rolled fallback, because a fallback keeps the weaker checker alive in the tree,
which is the whole point of removing it.

**Where it is declared.** This repository has **no `requirements.txt` and no `pyproject.toml`**, so
there is no manifest to add it to. It is declared in exactly the two places PyYAML is: the
prerequisite gate in `harness-init` (`.claude/skills/harness-init/SKILL.md:47`, the eighth
prerequisite, with the install commands at `:61-65`) and the CI workflow
(`.github/workflows/tests.yml:59-60`). Those two are the dependency declaration. A future reader
looking for a manifest will not find one, and should not add one for this.

**The rejected alternative, with the reason that made it a rejection.** A hand-rolled stdlib checker
— walk the mapping, assert the key set, assert the types — was offered and declined. It would put
**a checker and a schema in the tree that can disagree with each other**, and every drift this org
has paid for has had that shape: two copies of one truth, one of them silently going stale. With a
real schema library there is one artifact, `.claude/skills/harness/bin/feature-schema.json`, and the
checker is a library call over it. The dependency is the price of not having a second copy.

DEC-101 is the precedent for treating an unavailable tool as a stop rather than a degraded run.
DEC-171 is the parent clause this one extends.

## DEC-191 — A feature's execution state has a CLOSED key set: eleven keys, `additionalProperties: false`

**The execution-state file may carry eleven top-level keys and no others.** The schema is
`.claude/skills/harness/bin/feature-schema.json` and it sets `additionalProperties: false` at the
top level and inside each closed sub-object: `runs` items, `github`, and `factory`.

**Eight required, three optional.** Required: `feature_id`, `branch`, `pr`, `status`, `review_sha`,
`cycles_used`, `max_total_cycles`, `runs`. Optional: `max_total_runs`, `github`, `factory` — the
last two exist only once a feature has been mirrored to GitHub or decomposed by the factory.

**The burden of proof is on KEEPING a key, not on removing one.** A key survives because code reads
it, and the schema records the reader by name in each key's `description`. "Removing it feels lossy"
is not a reason; neither is "an agent might want it later". Where a key was kept without a
demonstrated reader, the schema says so in as many words.

**The measurement that forced this, recorded so it is not re-litigated.** At 2026-08-10 the corpus
carried **75 distinct top-level keys across fourteen features**. **41 of them appeared nowhere
outside a feature directory** — no script read them, nothing gated on them. `cost_usd` survived on
**75 run entries with zero readers**, an entire field kept alive by copy-paste after DEC-178 deleted
cost. And run entries had begun carrying **prose as mapping keys**: a sentence where a field name
belongs. That is not an untidy file, it is a file with no shape at all, and every agent that wrote
to it was inventing the format afresh.

**The enforcement point, and why it is that one.** The check runs on `check-domain.sh`'s existing
write-payload path, which is already the place every write to this file passes through, plus the
required integration job in CI so that a write made outside a hooked session is still caught before
merge. Two alternatives were declined, one clause each: **`bash-write-guard`** sees a command line,
not a payload, so it cannot validate content; **a `check-state.sh` sweep** runs after the fact, and
an invalid file that already landed has already been read by something.

**The rejected alternative a future scan will re-suggest: a typed `notes` array.** Declined. A
free-form escape hatch, however typed, becomes the drawer everything is swept into — and it would
leave the execution-state file a narrative document with a schema's blessing on it, which is worse
than an unvalidated one because it looks governed. The answer for content that has nowhere to go is
the **redirection table**: each displaced item names the file that actually owns it.

Lineage: DEC-150 (the authority is read by index, never whole — a file nobody reads whole must have
a shape a machine can check), DEC-154, DEC-160, DEC-174 (the enforcement layer is changed directly,
never through a run whose gates are the thing changing), DEC-183, and DEC-190 for the library.

## DEC-192 — STRUCK 2026-08-25

**Struck under DEC-188, replaced by DEC-203.** Its heading read *"`phase` and `status` collapse
into ONE field whose values are the board's six columns"*.

**Nothing in this entry is reversed.** DEC-203 item 6 carries the single `status` field, its six
case-sensitive values, the refusal of any alias or translation table, the deliberate absence of
`blocked`, and both named collapses with their costs — forward unchanged in substance. It is struck
only so that one entry, not three, states the lifecycle.

The body below stands so citations resolve. Read DEC-203 for the live rule.

**There is one lifecycle field, `status`, and its six values are the GitHub board's own column
names: `Backlog`, `Plan`, `Ready`, `Building`, `Review`, `Done`.** The `phase` field is **deleted**.
This is the entry a future scan is most likely to try to undo, so the reason is on the record rather
than inferable.

**The values are the board's column names, byte for byte.** They are therefore **case sensitive**,
and no lowercase alias is accepted. The board is the surface the operator actually reads; the moment
disk and board spell the same state differently, a human is doing translation that a machine was
supposed to make unnecessary.

**This is a REPLACEMENT, and no old-to-new mapping survives anywhere in code.** There is no
translation function, no alias table, no compatibility shim. The migration record lives in the T-04
receipts of FEAT-14 and in this entry; nothing in the live tree remembers the old vocabulary.

**Two collapses, with their cost stated as cost rather than smoothed over:**

- **`Review` cannot distinguish a running review panel from waiting on the operator.** Both are
  `Review`. A reader of the board cannot tell, from the column alone, whether anything is executing.
- **`Done` cannot distinguish shipped from abandoned.** This affects exactly one record in the
  corpus, FEAT-01. It is a real loss of resolution, accepted because a second value to express it
  would be a seventh column the board does not have.

**`blocked` was DELIBERATELY dropped, not overlooked.** The live corpus carries it **zero times**
across all 17 features, and a blocked feature is by definition waiting on the operator — which is
`Review`. Recorded explicitly so that a later reader does not restore it as a fix for an omission.

**The rejected alternative a future scan will re-suggest: keep both fields with a translation
between them.** Declined. Two vocabularies for one lifecycle is precisely the two-copies drift this
org keeps paying for, and the tie-breaker is that only one of the two is a surface the operator
reads. A field the board does not show is a field that goes stale unobserved.

**The consequence that made this a task rather than a rename.** Deleting `phase` without replacing
INV-17's guard would have left that invariant **skipping all 17 features** while `check-state.sh`
went on exiting clean — a gate that examines nothing and reports success. That failure mode, not the
field's name, is why this needed work rather than a search-and-replace.

Lineage: DEC-148 and DEC-159 define plan, build, validate and ship as **orchestrator MISSIONS** and
as handoff-note names; those are unaffected and are not this field. DEC-172, and DEC-191 for the
closed key set this field lives inside.

## DEC-193 — Code is written in exactly two locations; any other checkout of this repository is refused by one shared rule on both write routes

**There are exactly two places code is written under harness's authority:** `.claude/worktrees/<id>/`,
where harness develops itself, and `workspace_root/<repo>`, where the factory works on a product.
(Spelled `<product>` as signed; respelled by amendment 2 — see below.)
Both keep exactly their prior behaviour. **Any other checkout of this repository — a linked worktree
living outside `.claude/worktrees/`, however complete its manifest and its agents look — is a
mistake, not a supported shape.**

**Three refusals, and all three refuse rather than resolve.** Such a checkout **cannot be created**
through the Bash route: `git worktree add` and `git worktree move` are refused broadly, a destination
that cannot be determined included. It **cannot be written into**, on the Write/Edit route and the
Bash route alike. And it **cannot host a governed session** — a session rooted there is refused the
writes that are in-domain relative to its own manifest, in a parser-present session. Nothing maps
such a location back onto a domain so that it works; that is the ruling, not an omission.

**One implementation, `.claude/skills/harness/bin/harness_boundary.py`, imported lazily by both
guards** exactly as `harness_yaml` already is, exporting a `classify()` that returns a structured
verdict rather than raw predicates — a consumer finishing the decision itself is how the two routes
drifted apart in the first place. **A worktree is identified from its own `.git` pointer file, never
by invoking git:** the pointer names `<owner>/.git/worktrees/<id>`, the owning root is two levels
above, and the location is legitimate only under `<owning root>/.claude/worktrees/`. The
governed-write path therefore forks no subprocess. If the module cannot be imported, both governed
routes print a BLOCKED line naming it and exit 2 — an unhandled `ImportError` exits 1, which is
non-blocking, and would switch enforcement off on both routes at once.

**The alternative that was declined, recorded so a future scan does not re-propose it: consulting
`git worktree list` to map a sibling worktree back onto the domain globs.** It adds a git call to
every governed write in order to legitimise a location the architecture says should not exist, and it
would still leave every other prefix-dependent rule broken there.

**What did NOT converge, said plainly so a later reader does not take it for drift this rule failed
to close.** The requirement commits to one shared **implementation**, not to identical verdicts, and
three divergences between the two write routes survive deliberately:

- The Bash route keeps DEC-153's blanket allow for governed agents writing under
  `.claude/worktrees/`, which the Write route does not have.
- The Bash route still does not enforce product-base domains for paths outside the harness root: its
  outside-repo pass-through is preserved, narrowed to a filter on the verdict rather than removed,
  because dropping it would begin enforcing those domains there for the first time. **"Preserved" is
  true of two of the three fleet states and not the third** — see amendment 1.

### DEC-193 amendment 1 (2026-08-12) — "preserved" was too wide by one column

The review panel found that moving the outside-repo pass-through BELOW `classify` also moved it below
`resolve_fleet`, whose own `sys.exit(2)` for an unloadable fleet declaration is now reached first. So
on the Bash route a **malformed** `.harness/factory/fleet.yaml` refuses every write outside the
harness root, where before it refused none. Measured on both branches, same fixture, same target:

| `fleet.yaml` | `main`, before | FEAT-17, after |
|---|---|---|
| absent | 0 | 0 |
| valid | 0 | 0 |
| **malformed** | **0** | **2** |

**The behaviour stands; the sentence above did not.** The direction is fail-closed, and it agrees with
what `resolve_fleet` already did on the Write route and with its own stated reason — the value that
identifies product paths is the one that failed, so enforcement is closed rather than partial. What
was wrong was claiming preservation across all three states when it holds across two.

Recorded as an amendment rather than a strike: DEC-188 strikes a decision the tree **flatly
contradicts**, and this one is accurate except in a case it did not enumerate. It is written down
because the alternative was leaving a falsified sentence standing in the entry the whole factory reads
as ground truth — and because moving the filter back above `classify` to restore the old column would
re-blind this route to sibling worktrees, which is the defect the entry exists to record closing.
- In a PyYAML bootstrap-grant session the Write route does not apply the ROOT-SIDE check. That check
  sits inside `domain_check`, which is called under `if _run_domain and not _no_parser`, while the
  Bash route's root-side check sits ahead of that route's own `_no_parser` exit and still fires.
  Chosen in the 2026-08-11 re-scope rather than left by accident: the grant already skips
  `domain_check` in the real checkout, so it opens the same escape everywhere. **The Bash route is
  deliberately not weakened to match** — that would degrade a working route to the level of a
  weakened one.

**`check-domain.sh --resolve` answers from inside an out-of-place worktree even though the hook now
refuses writes there.** The resolver exits before session governance is computed and writes nothing,
so refusing there would make the planning tool unusable from the very tree an operator must stand in
to diagnose the problem. `check-state.sh`'s INV-25 reports such a tree at session entry as a FAILURE
rather than a warning, and that is the loud signal instead.

**The evidence, and the wording matters because half of the original evidence was overtaken.**
Measured at `a29ad06`: a Write to `<root>/src/main.py` exited 2 while the same write via Bash exited
0; and three writes that exit 2 in the real checkout exited 0 when written INTO a sibling worktree
**from a harness-rooted session**, taking DEC-150's shape caps dark with them on that route. **The
other case — a session ROOTED in the sibling worktree — is NOT evidence of an enforcement hole.**
Re-measured at `a29ad06`, a 211-line `feature.yaml`, a 70-line handoff note and an out-of-domain
`bin/` script all exit 2 from there, because DEC-180 and issue 132 made the shape caps independent of
domain and bound them to every author. The rooted case is refused as a lost-work risk, and because
the location is a mistake — never because it escapes enforcement.

**What the one-implementation claim rests on, stated no wider than the evidence.** The mutation proof
edits the named legitimate-location constant in an isolated copy of `harness_boundary.py` and watches
one identical payload's verdict flip on BOTH write routes. The fixture pins `CLAUDE_PROJECT_DIR`
inside the worktree, so the flip is observed through the **ROOT-SIDE** check and only there: it is
direct evidence that the root-side rule has one implementation, and it is the strongest evidence this
rule carries. The **TARGET-SIDE** branch — a write into a sibling worktree from outside it — is
covered by behavioural cases on both routes and is **NOT** mutation-proved. Neither half may be
widened into the other, and narrowing the claim does not drop the root-side proof.

Lineage: DEC-151 for the Bash-route guard this rule now shares an implementation with; DEC-153,
whose worktree allow is one of the three divergences left standing; DEC-174, because both guards are
the enforcement layer, so this landed as direct main-session edits with the tests run explicitly
rather than through a run whose gates were the thing changing; and DEC-189, the two-base target-keyed
resolution this rule sits on top of, whose filed Bash-route asymmetry this closes for the boundary
case alone. DEC-150 for the shape caps, and DEC-180 for why a rooted session is already governed.


### DEC-193 amendment 2 (2026-08-20) — the second location's segment is spelled `<repo>`, not `<product>`

This entry names the two write locations as `.claude/worktrees/<id>/` and
`workspace_root/<product>`. The second spelling is struck: ~~`workspace_root/<product>`~~ is
`workspace_root/<repo>`.

**Operator ruling, 2026-08-20, and the reason is drift during build.** One thing had two names. The
per-repository segment introduced by the layout migration is `<repo>` — `.harness/<repo>/features/`,
`.harness/<repo>/expertise/`, team-config's `.harness/*/features/**` grants — while this entry called
the same idea `<product>`. A builder reading both cannot tell whether they denote one segment or two,
and resolves it by guessing. That is the failure this amendment prevents, not a wording preference.

`<product>` was also the narrower word. The factory serves repositories, and the thing at that path
is a repository checkout; whether its contents are a product is a fact about the work, not about the
path.

DEC-189's illustrative paths carried the same `<product>` spelling for the same idea and are
restated with it, because two decisions using different words for one segment IS the drift this
closes. Shipped feature artifacts keep `<product>` — they are frozen, dated records, and editing
them would falsify what was written on their date (the same rule applied to FEAT-11's stale figures
on 2026-08-20).

**Nothing about the RULE changes.** Exactly two locations, all three refusals, one shared module on
both write routes: unaltered. Only the name of a path segment.

## DEC-194 — A partial layout migration is judged per coupled surface, and a reader matching neither form is cannot-verify

The layout migration moves `.harness/features/…` and `docs/harness/…` under a per-repository root, one
unit at a time. A tree-wide definition of "half migrated" reddens on a state the release sequence
sanctions, and degrading an unrecognised reader to clean is how a check passes forever. Both are
closed here.

**Failure is judged per coupled surface, never tree-wide.** Two surfaces exist. FEATURES, whose
coupled readers are `team-config.yaml`'s write grants, `check-domain.sh`'s `SWEEP_GLOBS` and shape
regexes, `check-plan-routes.py`'s discovery join and `check-state.sh`'s discovery globs. DOCS, whose
coupled readers are `factory_config`'s probe, `harness_boundary`'s control-plane entry and
`gen-decisions-index`'s docs directory. The two surfaces carry no ordering tie between them, so a tree
with one migrated and the other not is a sanctioned state and passes.

**Each reader carries a two-form data row.** A reader matching neither form is
cannot-verify, never clean — the exit code is 2, and both call sites, session entry and the required
CI job, treat it as a violation. Because those rows are data that later units edit, a surface is judged clean only over a
non-empty reader set, and the surfaces are a fixed enum judged independently of the table: a surface
whose rows are dropped is cannot-verify rather than vacuously clean, and can never be skipped ahead of
its verdict. Every finding names the reader path with the form it matched, because finishing a reader
and reverting one are opposite remedies and must not arrive as the same line.

**What the check proves, and what it does not.** It proves per-file
form agreement, never per-site completeness: it answers whether a file speaks one layout language and
the same one its evidence speaks, not whether every site inside it was updated. A legacy pattern is
therefore written as the weakest fragment every stale site necessarily contains, audited against the
real file rather than inferred from the commonest site. An earlier draft specified `check-state.sh`'s
legacy form with a trailing wildcard and would have missed the two discovery sites that carry none,
reporting a clean tree with two dead call sites.

**The maintenance contract on every later unit.** Any unit that changes a reader's form updates that
reader's row inside the same atomic commit that migrates it, and that unit is not done until the
detector exits 0 on its own migrated tree in that same commit. Nothing else converts the migrated
pattern from an anticipated form into an observed one; a pattern written too tight matches neither
form and exits 2 loudly at that commit, which is the intended way to discover the mistake.

**Historical mentions, and the two rows that pay for them.** Because every pattern is matched against a
file's whole text, a purely historical mention of a legacy form inside a coupled reader holds that file
mixed forever. Five of the seven rows avoid this because their patterns are code-shaped — a join
expression, a grant path, a glob or regex source — so docstring and diagnostic prose falls outside
them. Two rows are exceptions, both ruled deliberately and both resolved the same way, by correcting
the text rather than excusing it.

The first is `harness_boundary.py`, whose comments quote the `docs/harness/**` control-plane entry
verbatim. Those comments assert a present-tense fact the migration falsifies, so the unit that moves
docs rewrites them to describe the migrated control-plane entry. Rewritten, never deleted: deleting
them would make the file clean just as cheaply and would erase the signed risk-acceptance recorded in
the comment above `HARNESS_CONTROL_PLANE`, which is a record loss rather than a migration.

The second is `gen-decisions-index.py`, and its row is the one place a code-shaped pattern was
overruled. That script emits a header template into the committed index carrying a literal
`docs/harness/DECISIONS.md`, which no join-shaped pattern sees; updating the docs directory constant
and leaving that template stale would report the file cleanly migrated while the shipped index pointed
every agent at a path that no longer exists. The row therefore matches the slash-shaped spelling too,
which also catches that script's module docstring — inseparably, since the two are spelled
identically. That is accepted rather than worked around, because every one of those lines is a
present-tense operational claim about paths the script reads and writes, and the unit that moves docs
falsifies all of them at once. Detection was preferred to an unenforced obligation recorded in prose.

Lineage: DEC-174, which is why the detector and its session-entry call site are built by hand rather
than dispatched through the gates they change; and DEC-183, which is why the CI step carrying this
check is a second signal and not its guarantee — nothing in this tree asserts that step is still
wired.

### DEC-194 amendment 1 (2026-08-14) — the applicability marker is the fleet declaration, and an undeclared segment is loud

Two pre-merge review findings, both probe-verified, both fixed before PR #376 landed.

**The marker moved from `check-state.sh`'s own path to `.harness/factory/fleet.yaml`.** The first
marker was wrong by construction: `harness-init` installs the whole `bin/` — marker included — into
product repositories, so every onboarded product became "applicable," held no layout evidence of
either shape, and reported CANNOT VERIFY at exit 1 forever, which onboarding's own exit-0
requirement cannot survive. The fleet declaration is the one file only the control plane carries:
products are declared IN it, never holders OF it. Applicability and segment authority now come from
the same fact.

**A migrated repo root must be a DECLARED repository's segment.** The first evidence glob accepted
ANY first-level `.harness/` subdirectory as a repo root, so a non-repo sibling growing the wrong
shape — `.harness/archive/features/…` was the probe — forced a MIXED verdict no reader edit could
clear. Now only fleet-declared segments (name-after-owner, the `workspace_path` rule) plus the
repository named in `harness.json` `github.repo` count as migrated evidence. Evidence under any
other segment is not silently ignored — it is a fifth CANNOT_VERIFY cause, `undeclared-segment`,
naming the offending paths, because a misfiled migration is exactly what this detector exists to
catch.

**The cause table at the session-entry call site is closed and fails loud.** The wording dispatch
was four `if/elif` branches with no `else`; a fifth cause value would have appended nothing and the
operator-facing gate would have passed clean while CI stayed red. It is now a dict lookup whose
miss appends an "unrecognised cause" violation.


### DEC-194 amendment 2 (2026-08-14) — blame is one exported policy, rendered whole at both call sites

Issue #366 found the body's sentence "every finding names the reader path" overclaiming: three
cannot-verify causes — no-evidence, no-rows, undeclared-segment — have no responsible reader file to
name. A first correction narrowed the sentence by rewriting the body in place; that edit violated
this file's append-only rule and is reverted, with the ruling recorded here instead.

**The settled behaviour, ruled by the operator after validator finding M-1 (2026-08-14):**
`layout_migration.blame()` is the ONE policy for which readers a finding names — a reader whose
form-set is defective (both, neither, unreadable) or disagrees with a single evidence shape, with
every reader named when a MIXED surface has no such individual. Both call sites — `render()` for CI
and `check-state.sh`'s INV-27 at session entry — render that list WHOLE, on every verdict that is
not clean, with no per-cause or per-form filtering at either site. Filtering is what produced two
divergences in one day; the rule is therefore stated as an absence: there is no second place where
naming is decided. `blame()` may return an empty list — structurally always for no-rows, and
whenever no reader's form is defective or disagreeing for the other causes — and an empty list
appends nothing. That, not a filtered sentence or a per-cause label, is how "names no reader"
happens; only no-rows is reader-less by construction, and labelling causes reader-less is the
thinking that invites the per-cause filtering this amendment removes.

Units 3–7 cite this entry as their maintenance contract; the body's sentence is read through this
amendment.

### DEC-189 amendment 1 (2026-08-16) — the docs entry moves into the repository segment

The named entry `docs/harness/**` becomes `.harness/*/docs/**` — FEAT-22 moved the harness
design docs to `.harness/harness/docs/`, and the entry follows the files. The two-sided rule
this decision established is unchanged; only the spelling of one named path moved.

The entry is now logically redundant in the file, for both of its consumers:
`is_control_plane_target` short-circuits on `is_control_plane_glob` (any `.harness/` first
segment answers True before this list is read), and the deny-message advertise filter inside
`classify` reaches the same result on the same line. The entry is kept because the layout
detector's migrated pattern requires the string to be present, and because the list is
advertised in deny messages as the closed statement of what harness owns — a list that
silently under-states ownership teaches readers the wrong boundary.

One arithmetic in the original justification is corrected rather than left to mislead. The
ruling said a glob-keyed classifier would have nothing to match "two of the four" named
entries against. That overstates. `README.md` and `.github/**` are verbatim grant paths and
never made the argument; `docs/harness/**` and `docs/PRINCIPLES.md` were the two with
nothing to match — and the move supplies a match for the first alone, through the documentor's
new `.harness/*/docs/**` grant. The correct figure is ONE of the four. Target-keying still
holds on `docs/PRINCIPLES.md`, because team-config grants `docs/**`, a different string.

## DEC-195 — The four-angle simplify pass is the last build step and a plan-flow step, harness-native, never the validator lead

A simplification pass had been run twice by hand, at a different moment each time, and both
placements cost something measurable. The step's position in both flows is fixed here, together
with the seat that was rejected for it, so no later planner re-litigates either.

**The position, build flow.** Build, then the `test_matrix` qa gate, then SIMPLIFY — whose findings
are applied **only where the domain guard grants the touched file to a specialist**, with the suites
re-run after the apply — then pin `review_sha`, then the review panel, then goal-check. It sits
before the pin because the apply moves the tip: run after the pin and the commit invalidates the
verdict the panel just gave. It is sequenced as its own squad segment to `harness-eng-lead` rather
than folded into the `build` team, because a team is single-squad by construction (DEC-118).

**The position, plan flow.** The plan draft, then simplify over the plan surface, then the
architecture and design reviews, then the operator's signature. Reviews read the simplified draft,
and the operator signs what the reviews read.

**The apply is conditional on surface ownership.** On a code surface the findings are applied by the
specialist that owns each touched file, and the suites are re-run. **Where the domain guard resolves
a touched path to NOBODY the finding is FLAG-ONLY**: it returns to the orchestrator with its
concrete alternative and no apply is attempted, because a dispatched write to an ungranted surface
is refused mid-run and the segment would come back with nothing applied and the finding lost. That
NOBODY region is everything under `.claude/` except `skills/harness/bin/**` — which is precisely
where a self-hosted feature does much of its work, so the gap is not a corner case here. **This is
an implementation gap in the build-side apply, not a weakening of the ruling.** The pass remains the
last build step, owned by the build side, applied before `review_sha` pins. The position is
unchanged.

**The plan-surface pass is flag-only for the same reason, and permanently.** `check-domain.sh`
grants `plan.yaml` and `BRIEF.md` to `harness-pm` alone, so the eng squad produces findings and
`harness-pm` applies them to its own draft. Forced by the guard, not chosen.

**The bound on the apply: it may not delete or weaken an assertion.** The step runs after the qa
gate has PASSed, and nothing afterwards re-assesses the test-matrix judgement or coverage adequacy.
So "this asserts the same fact twice" is a backlog row, never an apply.

**The second bound: the apply carries a ceiling of one fix.** Where an apply reddens the suites and
a single fix does not restore green, the apply is reverted and the finding is filed as a backlog
row. The ceiling is needed because this is the only permanent build step with no `max_cycles` of its
own — `max_cycles` is an `on_fail` field of the team schema and this pass is an
orchestrator-sequenced squad segment, so no file grants it one — and without a ceiling the repair
loop is unbounded at the last step before `review_sha` pins. Both bounds are stated authoritatively
in `.claude/skills/harness-simplify/SKILL.md` under `## Applying what comes back`; that section
governs if the two ever drift. The step's position is unchanged by either bound.

**The recurring cost, accepted, and there is deliberately no skip condition.** The step adds roughly
a dozen spawns per feature — two lead segments, eight read-only passes, the appliers and a suite
re-run — against the roughly 33 a feature already spends. No feature may skip it. Recorded as a
decision so a later cost review reads the absence of a skip clause as a ruling rather than an
oversight: a pass that runs at the wrong moment costs a validator round or delivers zero applicable
findings, and both are worse than the spawns.

**Who reads the angles: four spawns, one per angle, all read-only**, drawn from the eng squad by
adjacency to the domains the diff touches. Four independent readers is the load-bearing part. One
reader carrying four checklists is not the same pass and must not be substituted for it.

**The two measurements that forced the position.** On FEAT-20 the pass ran after the validator's
PASS at `6296149`; the apply commit moved the tip, invalidated the pinned verdict and cost a third
validator round. On FEAT-22 the pass ran after the operator's signature and zero findings could be
applied — four binding notes now sit beside the signed text in
`notes/simplify-pass-2026-08-16.md` instead of inside it.

**Why never the validator lead: the fixer is never the judge.** The validation tier's FAILs stick
precisely because it is read-only on the source it rules on and could not have quietly fixed
something and then forgiven it. A seat that has applied edits to a diff cannot certify that diff.

**Why harness-native.** The methodology previously existed only in one session's dispatch prompts
and in a plugin shipping outside this repository. A workflow step that depends on either breaks
silently on a machine lacking it, which is the quiet-degradation shape the files-only constraint
exists to prevent. The prompts are preserved verbatim in
`.harness/harness/features/FEAT-23-ship-flow-fixes/notes/research-FEAT-23-simplify-angles-source.md`
and the procedure ships at `.claude/skills/harness-simplify/SKILL.md`, read at the point of use and
deliberately not preloaded.

**The rejected alternative: a dedicated `harness-simplifier` agent.** Considered and refused. DEC-107
and DEC-86 declare the roster complete at three leads, nine doers and three reviewers; the seat needs
no write domain of its own and accumulates no expertise, so the price would be superseding a signed
decision to buy nothing mechanical. Measured at `b7ae135`: no script in the tree validates roster
composition — `check-domain.sh` harvests the names from `team-config.yaml` only to resolve domains,
and the per-agent validation DEC-107 records checks each agent file's properties, not the size or
shape of the roster. So the cost of a seventeenth agent is doctrinal, not CI breakage, and doctrinal
is the expensive kind. Recorded here so a future scan does not re-suggest it.

Lineage: DEC-118 for why this is a squad segment rather than part of the `build` team; DEC-107 and
DEC-86 for the roster this refuses to grow; DEC-174, because the pass reads and applies across the
harness's own tree and the enforcement-layer carve-out still governs what it may touch there.

## DEC-196 — STRUCK 2026-08-25

**Struck under DEC-188, replaced by DEC-203.** Its heading read *"The harness moves any board card
it is pointed at and closes only the cards it created"*.

**The second half is reversed.** The harness now writes the done station itself at `gh-sync.py ship`,
on every recorded card, and GitHub's `Auto-close issue` workflow turns that write into a close. Origin
stops being part of the decision; an open child is what holds a card back. The first half is
unchanged and is not a rule DEC-203 needs to restate: the harness still moves any card it is pointed
at, which is why `/harness-plan` may move a source ticket it did not create.

Amendment 4's station-writer table is struck with the entry. Its `Done` row said the harness writes
that column **never**. Measured on board 3 on 2026-08-25, probe #847 moved to `Done` at 19:06:14Z and
read `CLOSED` at 19:06:20Z, so the write works and the close follows it. DEC-138 amendment 8 carries
the replacement row.

The body below stands so citations resolve. Do not act on its close rule: read DEC-203.

Two shapes a future scan will try to add are refused here, and the boundary they would be added
against is stated as the rule the code already enforces rather than the rule the doctrine assumed.

**The rule: the harness MOVES any card it is pointed at, and CLOSES only cards it created.** Both
halves are measured in the tree, not asserted. The parent station write inside `gh-sync.py`'s
`_apply_parent_rule` carries no `parent_origin` check at all, so an adopted parent's card is moved
today. The close is origin-gated, by the `parent_origin == "created"` branch in `cmd_ship` and by
the matching branch in `cmd_abandon`. Cited by symbol deliberately and never by line number: this is
a permanent record, the same feature that records it inserts statements into `gh-sync.py` that shift
every line below `save_recorded`, and nothing in the tree detects a falsified statement left
standing. Observed at `b7ae135`.

**The consequence for the kickoff step.** `/harness-plan` moves the source ticket the operator names,
and that ticket is usually a wayfinding ticket the harness did not create. That is consistent with
the rule above, not an exception to it, and DEC-186 already lists setting a station among its three
sanctioned read-back purposes.

**No stations map is declared for the harness's own board.** `gh_board.set_station` takes the station
as a plain string and `factory_gh.project_field_set` resolves the option BY NAME at runtime; nothing
validates the string against a declared list, and the `Plan` option already exists on the harness
board, so a declaration would buy nothing today. Issue 350 is CLOSED carrying a ruling that every
board gains an explicit stations map and that `derive_station`'s hardcoded literals go — and that
ruling has no open implementing ticket. Half-landing it here would leave a declaration that exactly
one writer reads, which is worse than none.

**The writer is a new bin, not a `gh-sync` subcommand.** `gh-sync.py`'s `main` takes the feature
directory as a positional argument and exits when it is not a directory, before any subcommand
dispatch, and derives the harness root by walking up from it. At plan kickoff there is no feature
directory at all — the same fact that makes `gh-sync open` unrunnable that early. Forced by the
file's structure, not chosen.

**The accepted cost, stated as cost:** a second board-writing entry point, and one more call site to
update when 350's restructure lands.

Lineage: DEC-186 for the control plane and the three sanctioned read-back purposes this sits inside;
DEC-192 for the status values the board columns carry; DEC-174, because the board writer is harness
code the harness plans but the enforcement-layer carve-out bounds what may be dispatched against it.

**Amendment 1 (2026-08-18) — the harness's own board now declares its stations**

DEC-196 amendment 1. FEAT-24 declared a stations map for the harness's own board, falsifying one
paragraph above. That paragraph is left standing unedited: the record is appended to, never
rewritten.

*What became false.* The paragraph headed *"No stations map is declared for the harness's own
board"*. Measured at `ada8e99`, `.harness/harness.json`'s `github.board` carried three keys —
`owner`, `number`, `station_field`. It carries a `stations` map now.

*This is the follow-on DEC-196 named, not a reversal of it.* That clause was conditioned explicitly
on issue 350's ruling — every board gains an explicit stations map — having **no open implementing
ticket**. FEAT-24 is that ticket, so the condition the clause rested on is gone rather than
overruled. The accepted-cost line about one more call site to update when 350's restructure lands is
now SPENT: the call site was `board-station.py`, and it was updated inside this same feature.

*What is declared.* Five station keys under `github.board.stations` in `.harness/harness.json` —
`backlog`, `ready`, `building`, `review`, `done`. `plan` is deliberately NOT declared:
`board-station.py` takes the station as a plain CLI string, `gh_board.set_station` hands it to
`factory_gh.project_field_set`, and the option is resolved BY NAME at the board, so a wrong value
still fails loudly there and a name nobody declares is still writable. That is DEC-196's own rule and
it is unchanged.

*What did NOT change.* The harness still MOVES any card it is pointed at and CLOSES only the cards it
created — `_apply_parent_rule` still carries no origin check, and the close is still gated on the
`parent_origin == "created"` branch in `cmd_ship` and `cmd_abandon`. This amendment touches the
stations paragraph alone.

**Amendment 2 (2026-08-18) — the heading's third clause is struck**

DEC-196 amendment 2. FEAT-24 declared a stations map for the harness's own board, and that same
fact falsified a clause of this entry's own `##` heading. The clause is struck from the heading;
this record is what a citation to the old wording lands on.

*What the heading said.* It ended `..., and its own board declares no stations` — three clauses,
the third of which `.harness/harness.json` now contradicts directly: `github.board.stations`
declares five keys, `backlog`, `ready`, `building`, `review`, `done`, landed by this feature.

*What it says now.* Two clauses, both measured in the tree at this commit and both unchanged by
FEAT-24. The harness MOVES any card it is pointed at: `_apply_parent_rule` in `gh-sync.py` reaches
its station write with no origin check between the entry point and `gh_board.derive_station`. The
harness CLOSES only cards it created: both close paths are gated on the `parent_origin == "created"`
branch, one inside `cmd_abandon` and one inside `cmd_ship`.

*Why the heading is rewritten when amendment 1 deliberately left the false body paragraph standing.*
The two are not the same kind of text and do not take the same treatment. A body paragraph is dated
prose — it records what was true when written, and rewriting it would erase the record, so it stands
and is amended around. The heading is neither dated nor prose: it is the citation target every
reference to this entry resolves through, and the source the index row is generated from, so a false
clause there is repeated by every reader and every regeneration. The record is preserved by this
amendment quoting the struck clause, not by leaving it in the position where it is read as live.

*What did NOT change.* The body of DEC-196, including the paragraph amendment 1 identified as false
and the amendment-1 record itself, is untouched. No DEC number is opened, superseded or retired
here, and the entry's rule is the same rule.

**Amendment 3 (2026-08-23) — the `plan` station is declared, and amendment 1's refusal of it is reversed**

DEC-196 amendment 3. FEAT-33 declares a sixth station key on every board the factory serves,
falsifying one clause of amendment 1. Amendment 1's body stays standing unedited, as does the
original entry: the record is appended to, never rewritten.

*What became false.* Amendment 1's clause "`plan` is deliberately NOT declared". Measured at the SHA
this feature ships at, `.harness/harness.json`'s `github.board.stations` declares six keys —
`backlog`, `plan`, `ready`, `building`, `review`, `done` — and `mruangutai/kaya-ai`'s own
`.harness/harness.json` on `master` declares the same six, landed as `mruangutai/kaya-ai#336`.

*Amendment 1's REASONING is not falsified, so this is not a strike under DEC-188.* That clause
argued the option resolves BY NAME at the board, so a wrong value fails loudly there and a name
nobody declares is still writable. Both halves remain true in the tree: `board-station.py` hands the
station through to `gh_board.set_station` as a plain CLI string, validated against no list, and
`factory_gh.project_field_set` resolves the option by matching `o["name"] == option` at runtime,
raising `project field option not found` when nothing matches. What is reversed is the CHOICE that
reasoning supported, not the reasoning.

*Who reversed it, and on whose authority.* The operator ruled on 2026-08-23 that the sixth station
key belongs, recorded as ruling 3 in
`.harness/harness/features/FEAT-33-board-lifecycle-native/notes/rulings-2026-08-23.md`. That ruling
is this amendment's warrant, and the parity argument below is the ruling's own reasoning.

*What actually changed is parity, not capability.* DEC-192's six case-sensitive status values ARE
the board's column names, and a station map that names five of the six cannot express one of them by
key. The declaration now carries all six, and `factory_config._STATION_KEYS` requires exactly those
six, so a five-key declaration is rejected with a message naming `github.board.stations`.

*What did NOT change, stated so a future scan does not add it.* `gh_board.derive_station` still
returns exactly the building station, the review station, or None. There is no `Plan` derivation and
none is wanted — `Plan` is written at kickoff by `board-station.py`, invoked by `/harness-plan` with
the station as a literal argument. An all-pending derivation would overwrite a card the operator
promoted to `Ready`, a station whose meaning is documented in kaya-ai's own `harness.json`, where
`Ready` means promoted for the factory and `Backlog` means filed-and-untriaged; that would be a new
backwards-move defect of the same class as issue 674. DEC-196's rule is otherwise untouched: the
harness still MOVES any card it is pointed at and CLOSES only the cards it created, and no DEC number
is opened, superseded or retired here.

*The accepted cost.* The required key set is now exact at six across every repository served, so a
repository joining the fleet with a five-key declaration is rejected until it declares all six.

**Amendment 4 (2026-08-23) — the station lifecycle is event driven, and every station has exactly one named writer**

DEC-196 amendment 4. FEAT-33 makes each board column the consequence of an event the harness already
performs, and names the one writer of each. The original entry and amendments 1 through 3 stay
standing unedited: the record is appended to, never rewritten. No DEC number is opened, superseded or
retired, and DEC-192's refusal of a seventh column is upheld here rather than amended.

*The map, one writer per station.* Recorded in
`.claude/skills/harness/references/github-mirror.md` under the heading
*"Who writes each station — one writer per column"*, and cited here by content because a permanent
record must survive the line moving.

| Station | The one writer |
|---|---|
| `Backlog` | whoever files the ticket. Not the harness |
| `Plan` | `board-station.py`, at the `/harness-plan` door |
| `Ready` | the signature, via `gh-sync.py status <feature-dir> Ready` — it moves the **task sub-issues** and **never the parent** |
| `Building` | `gh-sync.py start-task`, owned by the task's `execution_mode` |
| `Review` | the validation panel kickoff, via `gh-sync.py status <feature-dir> Review` — it moves the **parent AND every recorded sub-issue** |
| `Done` | **GitHub**, from the `Closes` lines at merge, which close the sub-issues and the parent together. The harness writes this column **never** |

`Abandoned` is not a station and has no writer: DEC-192 gave it no column at all. Both `status`
station writes are in `cmd_status` in `gh-sync.py`, and `feature.json`'s `status` is the authority
there — `_record_status` runs first and unconditionally, before any board write, and nothing rolls it
back from the board. The station is its mirror, which is DEC-138's outbound posture, never a gate.

*The ruling of 2026-08-23, and the cost the operator accepted with it.* `gh-sync close-task` is **no
longer run per commit** — ruling 1 in
`.harness/harness/features/FEAT-33-board-lifecycle-native/notes/rulings-2026-08-23.md`. A task
sub-issue therefore stays OPEN through Building and Review and closes with its parent at merge. Why
it had to change: GitHub's native `Item closed` workflow moves a closed card to the done column, so a
sub-issue cannot hold `Review` while it is closed — the per-commit close and the ruling that
sub-issues reach `Review` could not both stand. The cost, stated rather than buried: this returns to
FEAT-31's close-everything-at-merge shape, which the per-commit close had been written to replace, so
a sub-issue's `Done` depends on the merge again. `Review` becomes reachable because it is now written
explicitly, not because the close was deferred.

*The consequence for INV-26, and the one enforcement-layer edit this feature makes.* A task whose
`plan.yaml` status is `done` now has a deliberately OPEN sub-issue standing at the building or review
column for the whole Review phase, while INV-26's `_EXPECT` map in `check-state.sh` maps status
`done` to the done column — every `done` task of every feature would become a violation in the gate
that runs at every harness door. INV-26 was widened to accept that shape by the operator's own hand
under the DEC-174 carve-out, ruling 4 of the same date, and that widening is the ONLY edit to a gate
script this feature makes. The separation the ruling turns on: an issue's STATE is GitHub's own
open-or-closed field, a card's STATION is the board column, and INV-26's defect was reading a station
off a state.

*The measurement that forced the `Review` row, with its conditions.* Board 3, 539 items, measured at
`f5f5185` and recorded in `notes/research-FEAT-33-station-writers.md`: **ZERO** items at `Review`,
and zero at `Ready`. `Review` was reachable in principle — `close-task` on the final task derives it
— and had never fired, because the last `close-task` runs while later tasks are still `pending` and
nothing calls `gh-sync` again until ship. A station that is never written is the same shape as an
assertion that cannot go red.

*What did NOT change, stated so a future scan does not remove it.* `gh_board.derive_station` still
returns exactly the building station, the review station, or None, and `check-state.sh`'s INV-26
still grades the PARENT card against it. The derivation stopped being the only path to `Review`; it
did not stop being the expectation the gate reads. Removing it would silence INV-26's parent
comparison, and `check-state.sh` is untouchable under DEC-174.

*The ceiling, recorded as a limit rather than as a solution.* The only genuinely CAUSED writes
available are GitHub's own workflows and a Claude Code hook. Hooks are the enforcement layer DEC-174
forbids executing here, and a board read inside a `PostToolUse` `Write`/`Edit` hook costs a measured
490 to 506 GraphQL points per fire on board 3 and would fire on every edit in every session. So each
write is instead folded into a command already mandatory at that moment, which makes forgetting the
station require forgetting the whole act. It is not impossible.

*The hole that was closed, with its measurement.* At `f5f5185` the only thing moving a card mid-build
was one `SKILL.md` row addressed to the orchestrator — `SKILL.md:191` as measured — while DEC-174
forbids the orchestrator `main-session-direct` tasks and nothing instructed the main session to move
their cards. FEAT-32 carried 9 of 17 tasks in that mode.

*`Ready` has ONE meaning on every served board — the plan is signed — and the cost is stated rather
than discovered.* `mruangutai/kaya-ai` loses a signal it has today: its own `.harness/harness.json`
on `master` documents `Ready` as the human pick-up point, and after this nothing on board 2 records
that a human promoted a ticket. A visible label is the route if that turns out to be needed, the same
shape as the `abandoned` label, and it is not built here.

*Why the claim queue is not at risk — settled, not open.* `factory_claim.py:302` polls the ready
station as the factory's CLAIM QUEUE and `factory_decompose.py:414` is what puts served-repo TASK
cards there; both re-derived in this worktree, and the second anchor MOVED from the `:411` an earlier
draft cited. `factory_decompose.py:393` records that the parent is NEVER added to a served-repo
board, so that poll has only ever contained tasks, by construction. The rule this amendment carries —
a parent card never reaches `Ready` on any board — makes the harness lane AGREE with the factory lane
rather than change it.

## DEC-197 — A test file matching two `detect` globs resolves to the explicit kind, and the record is the enforcement

**Chose:** state the precedence that was already in force. In `.harness/harness.json`'s `test_kinds`,
where a file matches more than one kind's `detect`, it resolves to the kind whose glob names it
**explicitly**, never to the kind whose glob is a catch-all.

Concretely: `unit.detect` carries `.claude/skills/harness/bin/test-*.py`, which matches every test
script in `bin/`, and `integration.detect` is a list of filenames. A file in both is `integration`.

**Because:** the rule was already load-bearing and already consistently applied — four files sat in
both lists and were treated as integration — and it was written nowhere. A convention nobody can
find is one every reader has to re-derive from the data, and two readers who derive it differently
will not be caught.

**What this does not do, said plainly rather than discovered later.** Nothing implements it. There is
no classifier. `test_kinds` is read by `harness-qa` by hand, and `run-unit-tests.sh` reads its own
`UNIT_SCRIPTS` / `INTEGRATION_SCRIPTS` arrays and never opens `harness.json` at all. So this entry is
the enforcement until something mechanical exists, and the failure mode it does not close is two
readers disagreeing about an overlapping file.

**What forced it.** Eight of twelve `INTEGRATION_SCRIPTS` entries were absent from
`integration.detect`, so `run-unit-tests.sh` ran them as integration while the qa matrix read them as
unit — and every `evidence: integration` claim resting on one of those files was false. The fix is to
name each file in `integration.detect`, which leaves it matching **both** globs. That fix means
something only if this precedence is real, so the rule had to stop being folklore before the fix
could be trusted.

**A cross-check is separate from this rule, deliberately.** The check that the arrays and the
`detect` lists agree is a set comparison; its correctness does not depend on the answer here, only
its meaning does. Keeping them apart stops a check from silently encoding a rule the record does not
state.

**If this is ever implemented, the test must assert on a file matching BOTH globs** and go red when
the resolution flips. A test over non-overlapping files passes under either rule and proves nothing
about the only case in question.

## DEC-198 — `budgets.orchestrator_context_warn_tokens` is declared: a context figure, not money, that advises and never refuses

**Chose:** add one integer leaf, `budgets.orchestrator_context_warn_tokens`, to `harness.json`. It is
the orchestrator context size at which the harness ADVISES. **When the key is absent, the default is
200000** — read from `.claude/skills/harness/bin/context-watch.py`, where
`DEFAULT_CONTEXT_WARN_TOKENS = 200000` is returned by the resolver on every miss path: file missing,
unreadable, not JSON, no `budgets` dict, key absent, or value not a number (bools excluded).

**`budgets` is NOT new; only the leaf is.** The block already held `max_total_cycles` and
`max_total_runs` in both `.harness/harness.json` and
`.claude/skills/harness/templates/harness.json`.

**It is a CONTEXT figure, not money.** DEC-178 removed cost tracking entirely — meter, budgets,
invariant, reporting surfaces — and that removal stands. Nothing here reintroduces a rate table, a
dollar figure or a spend budget. The unit is tokens of context.

**Why 200000 rather than a fresh guess:** it is the figure DEC-148's watchdog used, carried over.
Stated precisely, because the entry should not be read as more than it is: DEC-148 wrote the figure
as "200k" for `budgets.context_per_turn_tokens`, an **average cache-read-per-turn** threshold, and
DEC-178 deleted that watchdog along with the meter. The same numeral is reused for a **different
metric** — an orchestrator's context size — because re-deriving a threshold nobody has grounds to
move invents precision. `.harness/harness.json`'s own rationale string records the distribution
behind it (28 of 76 orchestrator transcripts above the figure, largest 750837, measured 2026-08-20);
that is the plan's measurement, quoted, not re-derived in this entry.

**Crossing it ADVISES and never refuses.** It is informational, not a gate. No branch stops, no
dispatch is denied, nothing is blocked on it.

**Added in BOTH files, because DEC-160 makes the template the propagation source.** The leaf sits in
`.harness/harness.json` (this repo's live config) and in
`.claude/skills/harness/templates/harness.json` (what `/harness-init --upgrade` propagates into other
repos). DEC-160 also requires that a decision adding a `harness.json` key SAY SO; this entry is that
statement, and it is the reason the entry exists.

**Propagation, stated as what was read in `upgrade-config.py` and not as an expectation.** The script
required no change and was left byte-unchanged. `merge()` is a recursive additive merge — "template
fills gaps, project values win" — and the file contains **zero occurrences of `budgets`**, so there is
no key-specific path; propagation is a property of the generic merge alone. That zero is load-bearing:
`merge()` consults three exclusion sets — `PRESERVE_ALWAYS`, `NEVER_ADD`, `TEMPLATE_ONLY` — and
neither `budgets` nor the new leaf appears in any of them. Had `budgets` been in `PRESERVE_ALWAYS`,
the recursion would be short-circuited and the leaf would not propagate at all.

**Two code paths, and only one is tested.** A project that ALREADY has a `budgets` block receives the
new leaf through the recursion branch (`elif isinstance(tv, dict) and isinstance(out[k], dict)`), and
this is the ordinary case since `budgets` has long been in the template. T-05's new case in
`test-upgrade-config.py` exercises **only** that path — its fixture project config carries
`budgets: {}`. A project with NO `budgets` block receives the whole dict through the add branch
(`if k not in out: ... out[k] = tv`), and that path is **untested** for this key. Propagation is
therefore proven for the first shape and inferred for the second.

**What is NOT guarded, recorded rather than discovered later.** No test in
`test-upgrade-config.py` pins that an operator's EXISTING value of
`orchestrator_context_warn_tokens` survives an upgrade. The behaviour rests on `merge()`'s stated
contract — project values win, scalars the project already set are left alone — and the code reads
that way, but no assertion holds it. A future change to the merge could overwrite an operator's tuned
threshold and the suite would stay green.

## DEC-199 — Every shared artifact two contexts can write at once goes through one locked, union-merging core, `harness_merge`, and a named persona is dispatched once per checkout

**Chose:** one core, `.claude/skills/harness/bin/harness_merge.py`, holding the lock, the union-merge scaffolding and
the atomic replace, with exactly four consumers on it — `plan-merge.py`, `observations-merge.py`, `expertise-merge.py`
and `inflight_registry.py`. No consumer opens its own lock or rename primitive. DEC-193 is the precedent: one shared
implementation, divergences recorded.

**The lock is `fcntl.flock` on a sibling lock file opened `O_CREAT|O_RDWR`, never `O_EXCL`**, so the file's existence is
not itself the lock and the file is never removed. **Over** a create-and-delete `O_EXCL` lock file, which survives a
`SIGKILL` and then refuses every later write — for a feature's `plan.yaml`, no plan can be written until a human deletes
a file they have no reason to know exists. **Two divergences, kept in one place:** this is not the shape
`expertise-merge.py` shipped with, which carried the `O_EXCL` lock and was rewired onto the core rather than forked; and
the deadline is not uniform — `acquire` and `locked_update` take an optional `timeout`, the four file-merge callers keep
the 10.0s default and the registry takes 1.0s, a lock held a second on a millisecond read-modify-write meaning the
holder is stuck, not busy.

| Union is keyed, per file class | On | Notes |
| --- | --- | --- |
| Expertise file | section, then entry id | conflict is an error; the cap applies |
| `plan.yaml` | task id and decision id | spliced as text, never re-rendered; the approval block carried forward as the base file's own bytes |
| observation log | whitespace-normalised text of a bullet record | order-preserving; no conflict exit and no cap, the file having neither ids nor a budget |

**The single-flight registry.** A named set of personas — today the product manager alone — may not be dispatched twice
at once on one checkout. The `PreToolUse` Task hook refuses the second, the `SubagentStop` hook releases the claim, a
claim expires after an hour, and one command, `inflight_registry.py release-all`, clears every claim — already
exercised, not hypothetical — because a fix that can brick every later dispatch is worse than the defect it prevents.
**The root comes from the hook payload's `cwd`, one registry per worktree**, by the same precedence in both hooks, which
is what "on one checkout" means: a shared registry would refuse a second feature's product manager while the first's is
live.

**Only the dispatch cause of issue #551 is closed.** Its two reporting consequences — a lead emitting a terminal verdict
about members it cannot see, an orchestrator inferring run verdicts from disk — are NOT closed, and no wait can close
them: the `SubagentStop` hook passes through on `stop_hook_active` to avoid an infinite stop loop, so a stop refusal
fires at most once per consecutive stop sequence and re-fires on each later wake while a child is still live. What ships
is aimed at the false REPORT — a lead or orchestrator returning while a child it dispatched is still claimed is REFUSED
on that hook once per consecutive stop sequence, the one-correction-round strength every other digest contract in that
file has, and again on each later wake; the loss itself is prevented at the `PreToolUse` hook, whose refusals have no
once-only bound. The residual, plainly: a second identical return ships when it is immediate, the refusal re-fires only
on a later wake while a child is still live, and an orphaned child of an interrupted parent has no parent left to refuse
it.

**The bound is per consecutive stop sequence, not per run.** The hook keeps no state marking a return already refused —
`validate-digest.py` returns early on `stop_hook_active` and reads live children fresh, and `live_children` is a read
that only expires stale claims — so a wake that finds a child still live is refused again. One observed orchestrator run
on the code path the lead tier uses carries two stop refusals naming DIFFERENT child sets, which is a distinct refusal
event and not replayed context (`agent-a89be3fd837d1b779`). Ending a lead's turn after every dispatch raises the rate of
stop attempts made with children live, so each attempt risks its own refusal rather than there being one per return.
`inflight_registry.py`'s refusal message states the same bound.

**#551's count is a FLOOR, never a total.** At least eight are measured as of this commit, and the mechanism fired again
during the build of its own fix: 5 through 8 came from this feature's own runs. The count has already moved four → seven
→ eight, and this file has no propagation checker, so a bare total written here becomes a false statement nothing
detects. Occurrence 5 is a lead forced to a terminal digest with its product manager in flight; 6 is the orchestrator
forced to a stop with its lead in flight; 7 is what 5 cost — that lead's first digest asserted the product manager's
work was `files_touched` empty and unrecoverable and was COMMITTED as the run's outcome; the product manager was then
resumed, ran to completion and returned PASS, and `148c8c5` corrected the record. The defect does not merely cost a
spawn: it WROTE A FALSE VERDICT INTO THE DURABLE RECORD, caught only by a resume. Occurrence 8 is strictly stronger — a
lead force-closed with a member still in flight has no honest word available to it, because the digest validator ranks
only PASS, FAIL, ESCALATE and BLOCKED (`.claude/skills/harness/bin/validate-digest.py:703`), so a return declining to
grade a child it cannot see is REJECTED and the lead must state a verdict on work it has not seen. Seven measured that
the mechanism PERMITS a false verdict; eight measures that it DEMANDS one. #551's harm is false reporting.

**One deliberate disagreement, not rot.** Run directories are gitignored, so this entry and the feature's `STATE.md` are
the durable record and the run directory is not. `BRIEF.md` line 16 still reads "seven measured occurrences" and STAYS
at seven, the operator having declined to reset the brief's approval for a prose change: the plan is the current
authority on the count, the brief the signed one, and neither is edited to match the other.

**The bound on the whole ruling is identity.** A Bash-invoked CLI has no identity source — no `agent_type` reaches it
and no environment variable carries one — so it checks WHERE it writes, never WHO called it. That route is reachable
from a read-only persona because `bash-write-guard.sh` is allow-by-omission (#627), not fixed here.

## DEC-200 — The pull request number is derived at ship time from the recorded branch, and write-only survives on the destination AND on the absence of a competing local receipt

**Chose:** at ship, the mirror derives a feature's pull request number from the branch already recorded
in `feature.json` — one query on that head, merged state only — and writes it to the top-level `pr` key
**only when exactly one merged pull request is found**. Zero, two-or-more, an unset branch, and a `gh`
failure are all the same shape: one printed line, no write, exit 0. An already-recorded number is never
overwritten, which is what makes a backfill re-runnable.

**Over recording the number when the pull request is OPENED.** The opening seat is the user's — DEC-153
keeps merge, pull request and deploy user-gated — so an open-time write still depends on a human
remembering to run something at the moment they open it. Ship is a step the harness already takes, and
the branch it needs is already on disk.

**Exactly one, not first match, and that is measured rather than cautious.** One branch in this
repository's own history, `feat/harness-native-foundation`, carries TWO merged pull requests. A
first-match rule would record the wrong one for whichever feature asked second, and nothing downstream
would contradict it.

**DEC-138's write-only guarantee holds here, and what governs THIS read is the destination.** This IS
the mirror reading one fact back out of GitHub, and a reader will hit `gh-sync.py`'s own docstring
first, which says the script never reads GitHub state back into harness state. Both hold, because of
**where the value lands**: `pr` lives in `feature.json`, which is execution state and carries no
approval block, and nothing read back reaches `BRIEF.md`, `plan.yaml` or any approval block. DEC-138
amendment 6 says it in exactly those terms — "issue state is still never read back into an
approval-gated artifact (DEC-138 proper)".

**The destination test is not all of write-only, and DEC-138 itself supplies the case that does not
fit.** Amendment 7 (`DECISIONS.md:4359-4362`) refuses a read whose destination is this very class —
the parent issue number, landing at the feature's `github.parent`, execution state with no approval
block — and refuses it invoking write-only. What separates the two is not the destination but whether
GitHub is being asked for something the harness already holds. Amendment 7's refused read is a
**discovery** path, and it names that as its own reason: "idempotency comes from local receipts, so a
discovery path would be a second, contradictory source of truth" — the harness creates or adopts that
parent and records the number at that moment, so re-deriving it from GitHub competes with a receipt
already on disk. The merged pull request number is not that: the harness never opens the pull request
(DEC-153), so it holds no receipt of the number; the recorded branch is the query's input rather than
the thing re-derived; and the write is once-only, never overwritten. So the claim to carry is the
narrow one — this destination, **and** no competing local source — not that write-only was only ever
about destinations.

**SETTLED by DEC-186 amendment 3 (2026-08-23): this read sits INSIDE the bound, and the bound is now
five.** DEC-186 closes factory read-back to a set of named purposes — three originally, four after its
amendment 2 — and this read was none of them. Two readings had textual support in DEC-186 itself:

- **Outside the bound, so DEC-186 should say the mirror is out of scope.** Its bound clause grants the
  read to "factory tools"; its own **Scope.** clause says it "rules on factory read-back and on the
  claim mechanism, and on nothing else"; and it contrasts its failure behaviour with "the mirror's",
  treating the mirror as a different class throughout.
- **Inside it, so the bound must widen to five.** Amendment 2 is direct precedent that the
  out-of-scope move fails: FEAT-33 argued its read was *already inside* the bound, and the architecture
  review rejected that because "re-labelling a fourth read is not the same act" as an explicit widening
  ruling. Declaring this read outside the scope is that same re-categorisation.

The operator ruled to widen on 2026-08-23, on that precedent. The fifth purpose is bounded to
`record-pr` and to `ship`, which calls it. Nothing in this entry turned on the answer — the destination
argument above holds under either reading, and it is unchanged by the ruling.

**What else this pins, briefly.** The source tickets are the signed `plan.yaml`'s own `source_issues`;
`feature.json`'s `github.source_issues` is only ever their mirror, refreshed by re-running `open`, so a
re-plan is picked up by that re-run and never by editing the mirror. The closing keywords are RENDERED
for the operator to paste and posted nowhere — DEC-138 amendment 6 forbids the mirror composing text it
posts — and no source ticket is ever closed by the harness, per DEC-196.

**All eleven previously null features were backfilled and none grandfathered**, because every one maps
to a merged pull request, so a cut-off would preserve a gap nobody could later close. Four took a number
the operator confirmed from the pull request titles, their branch being shared or unresolvable.

**The new invariant is warn, not violation** — INV-28, a feature at `Done` with no recorded number,
gated on `github.sync` like INV-21. It follows INV-21's recorded reason rather than a fresh judgement:
the mirror never gates a flow, so a missing mirror value must not fail the state check.

## DEC-201 — Neither an orchestrator nor a lead ever waits: every dispatch ends its turn, and the platform's wake is measured, not documented

**Chose:** the never-wait rule binds the orchestrator AND THE THREE DOMAIN LEADS. A lead that has
dispatched a member ends its turn, and the member's completion is what wakes it; an orchestrator
ends its turn at every dispatch on the same terms. Neither tier polls, sleeps, or invents activity
to stay alive. The platform resumes the caller when the child completes, and on waking an
orchestrator (a) re-reads `STATE.md` and `feature.json` from disk, because its context may have reset,
(b) treats a reported completion as a CLAIM until an artifact on disk confirms it, and (c) weighs its
own context against `budgets.orchestrator_context_warn_tokens` to decide whether to finish this phase
or hand it to a fresh orchestrator. That threshold ADVISES and never refuses (DEC-198).

**A waiting agent has no mechanism for waiting.** An agent has exactly two moves — end its turn or
call a tool — and a tool call keeps the turn alive, so an agent that believes it must wait burns
turns alternating filler tool calls with restatements that it is waiting (issue 831).

**The rule EXPLICITLY OVERRIDES the platform's own text.** The `Agent` tool's dispatch result tells
the caller to continue other work or respond to the user in the meantime; that text is
platform-supplied, with no file the harness can edit to change it, so the rule has to override it
rather than merely fill a silence.

**The rule carries an INOCULATION, and would install the loop it removes without one.** Every
dispatch's first turn-end meets a live child and is refused, so the rule states that the refusal is
expected, that the response is to end the turn again, and that it can recur on a later wake.

**One file reaches the whole lead tier.** The lead-tier rule is written once into
`.claude/skills/harness-team/SKILL.md`, which all three lead agents preload.

**No lead is granted `SendMessage` or any message-sending tool.** A lead that has ended its turn
cannot send anything, and a lead holding a message tool gains a fresh reason to stay awake and
watch, which is the loop this rule removes. Issues 610 and 552 are closed on that ruling, recorded
here precisely so a future scan does not re-suggest it.

**Over keeping the orchestrator alive across the wait**, which is what it was doing. One orchestrator
spent 354 of its 450 Bash calls on `echo hold` and `sleep` — 341 of them `echo hold` — went quiet,
and was killed by the platform's 600s no-progress watchdog, taking its lead and its member down with
it. The other 13 were not that command again: `sleep N; echo tick` six times, over five different
values of N, then seven singletons — `echo waiting`, `echo heartbeat`, `date '+%H:%M:%S tick'`,
`echo t`, `echo t1`, a bare `sleep N`, and one trailing a real `git status`. Six plus seven is the
13, and they are 12 distinct strings — an agent with nothing to do does not merely repeat itself,
it keeps INVENTING new ways to look busy.
A partial return is resumable; a killed subtree is not.

**The evidence is MEASUREMENT, and the published sub-agent documentation states the opposite. Treat
the measurement as the authority.** Three probes on 2026-08-23, each writing an unguessable
identifier to disk so that no result could be confused with a model's paraphrase, measured that a
parent subagent which has STOPPED is woken by its child at every depth the org uses: one stopped at
`15:17:14`, received the completion at `15:18:05`, and resumed at `15:18:09` quoting the child's
identifier exactly. The documentation says a stopped parent does not resume. It is wrong here, and no
argument from it overrides these three runs.

**Both stalling parents in the probes invented a hold to stay alive, and one FABRICATED a completion
for its child** — an identifier appearing nowhere but in its own messages. That is the harm shape
DEC-199 names, and it is why the woken orchestrator verifies against disk rather than against what it
was told. Waiting is not merely expensive; a parent with nothing to do manufactures both activity and
findings.

**Self-identification is part of the ruling, and it needed no new code.** To weigh its own context an
orchestrator must first know which transcript is its own: it emits a fixed, unguessable literal, then
LATER greps the orchestrator sidecars for it, then runs `context-watch.py`, which is read-only and
decides nothing. **The two Bash calls cannot be collapsed into one** — a single call grepping for a
nonce it emitted in the same command finds nothing, because the message carrying that nonce has not
reached the sidecar yet. Measured end to end at `569d417`, resolving a live orchestrator to its own
row in about a second. Zero matches and two-or-more matches both SKIP the check for that wake, which
is legal only because the threshold advises.

**The open measurement, stated as open.** Whether a STOPPED parent survives past 600s while its child
is still running had never been measured when this was decided. If it does not, this decision removes
the invented stalling without removing the death — the orchestrator would die quietly instead of
noisily. That is the thing to watch. **One data point since:** this feature's own PLAN-phase
orchestrator survived a gap of 1057.1s (`15:34:10.019Z` → `15:51:47.145Z`), past the watchdog, with
**0** Bash calls made to stay alive, not killed, closing with its own text. The control discriminates:
all 115 orchestrator sidecars on the machine were swept and exactly two fail, and BOTH are deaths on
that same watchdog in opposite shapes — one stalled LOUDLY, 1043 events of which 575 assistant and 341
`echo hold` calls, ending on a final gap of exactly 600.0s after 3457.4s alive; the other produced
NOTHING, 8 events and zero assistant, ending on a final gap of 642.6s at a lifespan of 642.7s — and
they are #744's two incidents, which that ticket files as two diseases sharing one watchdog, matching
it independently. **The limit, which must travel with the number:** that run was under a
DISPATCH-LEVEL OVERRIDE, not under the rewritten playbook, which is committed in a worktree while a
spawned agent loads its skills from the main checkout. So it proves the BEHAVIOUR survives a long
wait; it does NOT prove the rewritten playbook CAUSES it. Whether one post-merge run is needed to
settle that is a reviewer's call, recorded here as open rather than resolved.

**The threshold is a WARNING LINE, not a budget, and the operator has calibrated where concern
starts.** Crossing it is normal and expected; it advises and never refuses (DEC-198), and nothing
here narrows that. On 2026-08-24 an orchestrator sitting at 270,000 against the 200,000 line was put
to the operator and ruled acceptable — *"that's okay, i expect some margin buffer"*. So the point
where an overshoot becomes worth thinking about is roughly TWICE the threshold, not the threshold
itself.

**The bands are guidance and never a gate.** Just over the line, carry on. Around twice it, take the
next seam you reach. Far past it, a phase you fail to finish costs more than the handoff you avoided.
Nothing enforces any of these numbers — no hook reads them, no validator checks them, no gate fails
on them — and an orchestrator that weighs them and keeps working owes nobody a justification. They
are a sense of scale offered to the agent doing the measuring, and that is the whole of their force.

**They exist because a number with no scale cannot be weighed.** The playbook's context step
previously gave the threshold and nothing more, so an orchestrator that crossed it could not tell a
routine overshoot from a real problem, and both mistakes cost: hand off early and a spawn burns on a
phase that had one dispatch left in it, stretch too far and the phase dies unfinished. The scale is
measured, from this feature's own orchestrators — they ran at 195k, 217k, 270k and 330k across four
handoffs, every one of those handoffs correct, and one reached 418k, past the concern line, without
harm. That last figure argues FOR the band rather than against it: twice the threshold is where the
judgement gets hard, not where it gets made for you.

**Lineage.** DEC-148 and DEC-159 make one phase per orchestrator the mission, so the phase boundary is
normal termination and the successor reads a capped handoff note — ending a turn is the same act at a
smaller grain. DEC-118 is why waiting could never work: one phase spans several single-squad lead
round-trips, each far longer than 600s, so no amount of holding survives them. DEC-120 places the
orchestrator at layer 1, one per in-flight feature, under a spawn depth cap of 3 — the depths the
probes covered. DEC-198 supplies the advisory threshold; DEC-199 supplies the false-reporting harm
shape. **DEC-158 is why the incident numbers are HERE and not in the playbook:** the rule skill
carries the rule, one clause of why, and a pointer; the history is this entry's job, and nothing above
is repeated there.

**Branch `chore/744-never-wait-for-a-lead` is absorbed and abandoned.** Its work lands through this
feature; the branch is not to be merged or revived.
---

## DEC-202 — OMP is the canonical Harness runtime; providers and host adapters are replaceable configuration

**Chose:** Harness is authored against OMP-native and open Agent Skills surfaces:

- shared project guidance is root `AGENTS.md`;
- canonical roles are `.omp/agents/harness-*.md`;
- OMP's canonical skill access path is `.agents/skills`, a symlink to the single authored tree at `.claude/skills/`;
- lifecycle enforcement is `.omp/extensions/harness-hooks.ts`;
- concrete model selections live only in `.omp/providers/*.yml` as `modelRoles`;
- `.claude/agents/`, `CLAUDE.md`, and `.claude/settings.json` are Claude Code compatibility
  adapters, not policy authorities; `.claude/skills/` is shared authored source consumed by both runtimes.

**Why this is forced by the goal rather than preferred syntax.** A role whose frontmatter says `opus`
or `sonnet` cannot run unchanged on OpenAI, and a hook present only in Claude settings is absent when
OMP disables the Claude discovery provider. The pre-port probe at
`.harness/notes/omp-port-baseline.md` measured exactly that split: all 16 roles and both required
three-level spawn chains were discoverable, while Expertise injection, domain denial, reviewer Bash
denial, branch gating and digest rejection were all absent. Two providers agreeing after the port
would not prove preservation, so that measured baseline is the third comparison point.

**Role policy and deployment policy are separate.** Canonical agents select `@deep`, `@strong`,
`@standard`, or `@review`. The OpenAI and Anthropic overlays resolve those aliases to concrete
models. Dispatches still select only an agent; the tool schema exposes no per-dispatch model field.
Changing provider therefore changes configuration, never prompts, tools, skills, spawn permissions,
hooks or digest schemas.

**The organization is explicit in OMP frontmatter.** `spawns` records orchestrator → leads → owned
members and every leaf carries an empty list. `task.maxRecursionDepth: 3` remains the outer bound.
Every canonical role body carries a machine-readable `HARNESS_AGENT_ID:` line; OMP lifecycle events
do not expose the task-agent name, so the extension reads this exact marker from the role system
prompt. That is declared metadata, not inference from prose or model identity.

**Expertise remains durable Harness data.** `.harness/expertise/<agent>.md`,
`.harness/*/expertise/<agent>.md`, and `.harness/codebase/INDEX.md` do not move. The delivery seam
moves from Claude `SubagentStart` to OMP `before_agent_start`, preserving repository > project >
global precedence and the existing budgets. Skills and artifacts stay selectively loaded; none is
copied into `AGENTS.md`.

**Enforcement reuses policy and replaces delivery.** The OMP extension converts native `write`,
hash-anchored `edit`, `bash`, `task`, and `yield` events into the tested script contracts.
`tool_call` denies before execution; `tool_result` reports post-write shape failures; `yield` is the
task-agent stop boundary and validates structured OMP results after rendering them into the
normative digest text. The TypeScript layer owns no domain, branch, Expertise or digest rule.

**The control plane expands.** `.agents/**`, `.omp/**`, and `AGENTS.md` are Harness-owned paths in
`harness_boundary.py`; hidden-root grants remain checkout-local and never reach a product
repository's same-named directories. `.claude/worktrees/` remains the sanctioned development
location, because this port changes runtime discovery, not DEC-193's worktree placement ruling.

**Claude Code stays usable during and after the port.** `sync-agent-adapters.py` generates Claude
role frontmatter and identical bodies from canonical OMP agents. `.claude/skills` remains a real
directory for Claude Code discovery, while `.agents/skills` symlinks to it for OMP Agent Skills
discovery. `CLAUDE.md` imports `AGENTS.md` and states only Claude-specific delivery.
`check-omp-port.py` rejects adapter drift, a reversed or broken skills link, concrete provider IDs
in canonical agents, missing provider overlays, missing OMP hooks, or re-enabled Claude discovery.

**Amended by #836 after local compatibility testing.** The first cut reversed this link: it moved
the authored tree to `.agents/skills` and made `.claude/skills` the symlink. Local filesystem reads
worked, but Claude Code's discovery contract requires the real directory at its native path.
Reversing the link preserves one copy and OMP discovery—measured with Claude-provider discovery
disabled—without making Claude Code consume a compatibility link.

**Cost accepted:** OMP runs require an explicit provider overlay, the OMP extension is a maintained
host adapter, and Claude Code compatibility adds generated files. The alternative is cheaper only by
keeping provider coupling and silently losing guardrails under a non-Claude host.

**DEC-174 governs the cutover.** Agent prompts, skills and Expertise may be migrated normally, but
changes to hooks, validators, gate scripts and their tests are direct main-session work with explicit
tests and human diff review. The Harness enforcement path never certifies its own replacement.

This decision supersedes the Claude-only conclusions of DEC-63, DEC-64, DEC-100, DEC-108,
DEC-110, DEC-111 and DEC-122 for the canonical OMP runtime. Their measured Claude Code behavior
remains true for the compatibility adapter and their historical evidence remains authoritative.

## DEC-203 — A ticket is open until its card reaches `Done`, the harness writes `Done` at ship, and a parent waits for its children

Replaces DEC-186, DEC-192 and DEC-196, all three struck under DEC-188 in the same act. Those three
ran to about 4,900 words and stated one lifecycle three ways. This entry states it once, and it is
written plainly on purpose: the dense register of the three is part of what is being replaced.

**1. What "open" means.** A tracked ticket is open while its card is not at the done station. The
station is the record. The issue's own open-or-closed field is a consequence of the station, not the
other way round.

**2. Who writes `Done`.** The harness does, at `gh-sync.py ship`. GitHub's `Auto-close issue`
workflow then closes the issue. This reverses DEC-196 amendment 4's station table, which gave the
done column to GitHub's `Closes` lines and said the harness writes it **never**. Measured on board 3
on 2026-08-25: probe issue #847 was moved to `Done` at 19:06:14Z and read `CLOSED` at 19:06:20Z.

**3. Which cards ship moves.** Every card the feature records — each task sub-issue, each entry of
`source_issues`, and the parent.

**4. The parent rule.** A card is not moved to done while its ticket has an open child. Ship skips
it and prints one line naming the child that held it open.

**Origin stops mattering entirely.** Who created a ticket is no longer part of the decision. This
replaces DEC-196's created-versus-adopted gate and DEC-138 amendment 7's `ship` and `abandon` parent
table, both of which asked where a ticket came from.

The child check is the better guard because it is true of the ticket rather than true of its
history. The old rule left an adopted parent open on the theory that closing someone else's epic
asserts something false about it. That theory names the right harm and picks the wrong test. A
parent with no open children is finished whoever opened it. A parent with open children is not
finished even when the harness created it. Origin also failed in practice: `parent_origin` read null
on the two most recent features that recorded a parent, because both were recorded by hand.

**5. The read-back bound, carried forward from DEC-186 and now SEVEN purposes.** A factory or mirror
tool may read GitHub state back for these and no others:

1. whether an item is claimed;
2. which station it is at;
3. whether a blocker issue is finished;
4. which of a board's native workflows are enabled — bounded to `/harness-init` and to
   `gh-sync.py ship`, which calls the audit;
5. which merged pull request a recorded branch resolves to — bounded to `gh-sync.py record-pr` and
   to `gh-sync.py ship`, which calls it;
6. which children a card's ticket has — bounded to `gh-sync.py ship`;
7. which closed tickets a repository holds, with their close reasons and labels, and which station
   options its board declares — the detection reads inside `board_lifecycle.py`'s audit — bounded to
   `/harness-init` and to `gh-sync.py ship`, which calls the audit.

**The fourth purpose's surface is WIDER here than DEC-186 amendment 2 left it, and that is a ruling,
not a tidy-up.** Amendment 2 bounded the workflow read to `/harness-init` in the words *no other
surface makes this read*. Scheduling the audit inside `ship` falsifies that sentence unless this
entry widens it, so it is widened here in as many words. The precedent for widening a purpose by
naming a second caller is DEC-186 amendment 3, which bounds its purpose to `record-pr` and to `ship`,
which calls it.

**A read-back value still never enters `BRIEF.md`, `plan.yaml` or any approval block.** That bound is
the whole reason DEC-138 made the mirror outbound, and nothing here touches it. The control plane is
one board **per repository served** (DEC-186 amendment 1), and the signed `plan.yaml` remains the
source of truth for what the work is.

**6. The status field, carried forward from DEC-192 unchanged in substance.** There is one lifecycle
field, `status`. Its six values are the board's own column names: `Backlog`, `Plan`, `Ready`,
`Building`, `Review`, `Done`. They are **case sensitive**, byte for byte, because the board is the
surface the operator actually reads. There is no alias, no translation table and no compatibility
shim. `blocked` is deliberately absent, not overlooked: a blocked feature is waiting on the
operator, which is `Review`.

Two collapses, and both are real losses:

- **`Review` cannot tell a running review panel from waiting on the operator.** A reader of the
  board cannot tell from the column alone whether anything is executing.
- **`Done` cannot tell shipped from abandoned.** This affects one record, FEAT-01. It is accepted
  because expressing it would need a seventh column the board does not have.

**7. What DEC-168 keeps, and what it loses.** Its three probe results stand: closure does not cascade
in either direction, so closing a sub-issue never closes its parent and closing
a parent never closes its subs. What is superseded is its operational conclusion — that the parent is
closed deliberately at ship acceptance, by a close. The parent now reaches done by a station write,
and the close is GitHub's consequence.

**8. The guardrail, and the one narrow exception.** A `PreToolUse` Bash gate refuses a hand-typed
`gh issue close` and names the sanctioned command in its refusal.

**It is a guardrail against habit, not a security boundary, and the difference is measured.** The
gate's first cut matched the raw command line with `grep -E`. Thirteen forms were measured reaching
`gh issue close` straight through it — a quote inside the subcommand, an absolute path to the same
binary, a leading backslash, `eval`, `bash -c`, command substitution, a quoted `state="closed"`, a
JSON body arriving on `--input -`, and the GraphQL `closeIssue` mutation, which never spells
`state=closed` at all. A character class is not a shell lexer. The gate therefore tokenizes with
`shlex`, compares the basename of the command word, and re-scans each token as a command line so
`eval` and `bash -c` are read rather than skipped.

One class survives and is recorded rather than implied: a binary that exists only after shell
expansion, as in `G=gh; $G issue close 5`. Catching it needs the shell's own expansion, which a
`PreToolUse` hook does not have. So nothing here stops a determined evasion — `curl` to the REST API
would not even be a shell builtin away. **What bounds the harness is structural, not textual: no
harness command closes an issue except `abandon`.** The gate's value is that it stops the close a
tired operator types out of habit, which is the case that actually happens.

The gate is structurally blind to a Python subprocess: a hook receives only the Bash command line, and
`gh-sync.py` reaches `gh` through `subprocess.run`, which never crosses that route. So the gate alone
cannot stop a harness command from closing an issue. `gh-sync.py close-task` is therefore **deleted**
in this same feature rather than left standing as a harness-blessed way around the rule this entry
installs. After that, `abandon` is the ONLY mirror command that closes an issue directly, and it
reports what it would close and asks first.

The gate also cannot see a close typed in another terminal or made in the GitHub web interface. The
compensating control is `board_lifecycle.py`'s audit, run once per feature, inside `ship`. **The cost
is stated as a cost: a card closed outside the harness can sit wrong for the whole build and is only
caught at ship.** That is tolerable only because ship is the moment the wrongness would otherwise
cause harm, since ship is where the open-child decision is made.

**An abandoned card goes back to the BACKLOG station, and its ticket is DETACHED from its parent.**
Not to done. Measured on 2026-08-25 with probe #860: closing an issue moves its card to the done
station immediately, `not_planned` included — so before this rule, every abandoned ticket landed at
`Done` and the board could not tell dropped work from shipped work. `abandon` therefore writes the
backlog station **after** the close, which the same probe measured as the order that sticks; a write
made before the close is overwritten by GitHub's own workflow, silently.

The detach follows from item 1 rather than from taste. A ticket is open while its card is not at
done, so an abandoned ticket sitting at `Backlog` reads as **open** — and `ship` refuses to move a
parent that has an open child. Left attached, one abandoned child would hold its parent open forever,
and the Bash gate above refuses the hand close that would otherwise end it. Detaching is what makes
the backlog station safe rather than a trap. The ticket survives, closed and labelled `abandoned`,
for the operator to pick up or clear later.

Both writes are best-effort, like every other write the mirror makes: a failed detach prints one line
and the close still runs. An attached-but-closed ticket is a worse outcome than a detached one, and a
far better one than a ticket that was never closed.

**9. The accepted cost, and it is the largest one here.** The harness now depends on a board
automation that only a click in the project web interface can enable. Nothing in a checkout can turn
it on, and nothing in a build reports it off. The one reader of that dependency is the `WORKFLOW`
finding class in `board_lifecycle.py`'s audit. If the audit stops running, or its finding class is
removed, the dependency goes unwatched and tickets stop closing with nothing saying so.

Lineage: DEC-138 for the outbound mirror this sits inside and amendment 8 for the station row this
entry rewrites; DEC-168 for the cascade measurement; DEC-174, because the Bash gate and the
invariants are the enforcement layer, so this feature's code lands as direct main-session work;
DEC-188 for the striking of the three entries replaced here; DEC-191 for the closed key set `status`
lives in; DEC-200, which cites DEC-186 for its own read and is repointed separately under issue #844.

## DEC-204 — OMP supervises long-running Harness dispatches; claims are feature-scoped and process-owned

**Chose:** OMP is the supported host for multi-hour Harness work, with two different edges because
the runtime gives them different jobs. The main session dispatches the orchestrator asynchronously:
it receives agent/job identity, ends its turn, and OMP injects the terminal result. Every lead and
member is declared `blocking: true`: orchestrator-to-lead and lead-to-member task calls stay inside
OMP while the parent model is inactive, then return the terminal child result directly. No agent
calls `hub wait`, polls `hub jobs`, sleeps, emits a heartbeat, or invents work. Model family remains
provider configuration; process supervision is OMP.

**The safety bound is not the liveness bound.** `task.maxRuntimeMs: 0` removes elapsed wall time as
a reason to kill useful work. OMP's 200-request soft budget remains active and still forces a yield
at its hard multiple. Hours of legitimate tool execution and hundreds of model turns are different
failure modes; changing one does not disable the other.

**Every governed edge carries flow identity.** The first prompt line is exactly
`HARNESS-FEATURE: FEAT-NN-slug` or `HARNESS-FEATURE: BUG-NN-slug`. A later line, a missing line, or a
different id form is refused. The OMP adapter normalizes both batch and flat task input, runs the
existing dispatch guard for every item, and refuses the whole batch when one item fails. A batch
cannot start with only part of its checkpoint represented by claims.
The role marker comes from the system prompt, but the feature marker does not: OMP places the task
assignment in the first user message. The extension captures that message before the first tool
call and carries the feature into yield validation and startup reconciliation. Reading only
`before_agent_start.systemPrompt` was measured losing the feature and falsely treating concurrent
features as one parent-child tree.


**Claims use schema version 2.** The registry is one explicit `claims` list. Every entry names
`claim_id`, `feature`, `agent`, `dispatcher`, `cwd`, `started_at`, and `runtime`; an OMP entry also
names its supervising PID and, after spawn, its agent/job identity. Single-flight is keyed by
`(feature, persona)`, so two PMs for one feature are refused while PMs for different features are
legal. The version-1 persona-keyed object is read once for migration and every following write is
version 2. There is one locked registry implementation, still `inflight_registry.py`.

**OMP liveness follows the supervisor, not elapsed time or child session id.** An OMP claim remains
live for any age while its recorded supervisor PID exists and becomes stale immediately when that
PID is gone. Parent and child sessions differ, so the Claude session filter does not hide a live OMP
child. Claude Code remains a compatibility host and keeps FEAT-37's measured 1200-second TTL; this
decision does not restore DEC-199's historical one-hour value. The difference is forced by host
capability: Claude Code exposes no equivalent process-owned async job identity.
Expiry is query-scoped. Looking up or dispatching one feature never sweeps a dead claim owned by
another feature; only that feature's query or an explicit targeted reconcile removes it. This keeps
crash recovery from changing an unrelated flow merely because both claims share one registry.


**Release is targeted and idempotent.** A settled blocking task result releases its claim directly.
For a background task, OMP attaches agent/job identity from task result details and releases the
matching claim on `task:subagent:lifecycle`; `yield` validation remains an idempotent second path.
A failed preflight or spawn releases claims for items that did not start. Recovery instructions and
refusals print only feature/agent/claim-targeted commands, never `release-all`. The older command
remains an operator escape hatch but is not an automated remedy. A lead or orchestrator `yield` is
refused while any matching child claim remains live; `agent_end` is notification-only.

**A process exit does not pretend detached work survived.** OMP sessions and transcripts persist,
but running jobs belong to the process. On `--resume`, a dead-PID claim is reconciled before a new
dispatch. The recovery order is checkpoint on disk, persisted `agent://`/`history://` result, then
landed commits. A transcript or claim never proves PASS. A valid terminal artifact is collected; a
recoverable regular agent with no terminal artifact may be revived; otherwise only the unfinished
checkpointed step is re-dispatched.

**GitHub mirrors durable transitions only.** The existing command ownership and write-first order
stand. Child runtime, wakes, and recovery generate no heartbeat traffic. On wake, the owner re-reads
`plan.yaml`, `feature.json`, and stored GitHub receipts before deciding whether a transition is due;
duplicate delivery is an idempotent no-op. OMP's Bash preflight now invokes `gh-close-gate.sh`
before branch and write guards, so the direct-close rule in DEC-203 applies under the canonical host.

**Measured enforcement overturned the first design rather than being fitted to it.** With nested
agents left asynchronous, OMP forced the orchestrator toward `yield` while its lead remained live;
the digest hook refused it six times and OMP stopped the parent to avoid an infinite submit loop.
After marking the lead and member blocking, the same OpenAI hierarchy completed in 51.8 seconds:
the leaf held one five-second Bash call, wrote an unguessable token, the lead and orchestrator each
read that exact artifact, and the outer async result reached main. Their transcripts contain no
poll, sleep, wait, heartbeat, or keepalive call. The probe also found macOS OMP launching
`/usr/bin/python3` 3.9, where `-P` is invalid; gates now use portable `-I` where possible and a
`sys.path[0]` bootstrap where normal site-packages are required.
The provider control used the same three probe agents, prompts, tools, claims, and artifact shape
under the Anthropic overlay. Its Sonnet leaf held one Bash call for 900.06 seconds, its Opus lead
and orchestrator verified the exact token, and main received the terminal async result after 16m39s.
An OpenAI feature claim remained live concurrently; feature capture from the assignment kept it out
of every Anthropic parent-yield check.
The long control then held the OpenAI Terra leaf's single Bash call for 7200.07 seconds. The Sol
lead and orchestrator each resumed only when their blocking task result arrived, read the exact
token, and returned PASS; main received the outer result after 2h1m. Between task start and result,
each parent transcript contains no intervening model message or tool call.



The deterministic suites separately exercise per-feature PM isolation, live/dead OMP supervisors,
targeted release, schema migration, runtime identity, atomic batch refusal, blocking-result release,
flat/batch normalization, lifecycle release, and parent-yield refusal. The port checker rejects
drift in async enablement, wall-clock configuration, nested blocking declarations, task preflight,
lifecycle wiring, or the GitHub close gate.

This decision supersedes DEC-199 only for claim schema, key, liveness, and automated recovery. It
supersedes DEC-201's host-specific mechanics for OMP while preserving its no-wait conduct and
evidence standard. DEC-202 still owns canonical paths, provider overlays, and compatibility
adapters. DEC-203 still owns issue/card lifecycle and command ownership.

## DEC-205 — This file states current truth: no amendments, supersession is deletion, and two mechanical checks guard it

**The amendment convention is ended.** An entry states current truth directly. A correction rewrites
the entry it corrects; it does not append a dated sub-section beside it. A claim the tree has
falsified survives as one clause of that current truth, so it cannot be re-proposed as new. The cost
is recorded honestly rather than waved away: dated reasoning about how a decision *changed* is
recoverable only from `git log --follow` on this path, and for one block — the former DEC-145
amendment 3 — the reasoning existed only in the file, because its authoring commit message is an
unrelated write-up. That block's reasoning is therefore gone. It was accepted on 2026-08-20 as a fair
price for a file whose every sentence can be trusted as present-tense.

**Supersession is deletion.** The author of a superseding decision deletes the decision it replaces,
in the same edit. There is no `SUPERSEDED BY` marker and no code that can emit one. Nine superseded
entries had accumulated precisely because the deletion was somebody else's later problem: a marker is
cheap to write and nobody is ever dispatched to collect it.

**A struck decision is deleted only once a named successor exists that its citations can be
repointed to.** That is DEC-188's rule, as amended by this feature; its reasoning lives there and is
not restated here. One statement, one home.

**A deleted number is never reused.** Numbers are not renumbered either. Reuse would make every
historical citation actively wrong — pointing at a real entry about something else — rather than
merely dangling, and a dangling citation is the failure a reader can detect.

**The index generation contract, one clause only: a refs graph entry naming a `DEC-NN` with no live
heading is never emitted.** The evidence is the whole reason the clause exists. DEC-161 was deleted
outright; zero `## DEC-161` headings remain; and `DECISIONS-INDEX.md` still carried `DEC-161` in the
refs graph of two rows, regenerated on every run, because the generator scraped the id out of the
sentences that describe the deletion. Orphan detection guards a *row* whose entry is gone; it never
looked at a refs graph at all. This is one clause of issue 686 — the rest of that ticket, the full
generation contract, is deliberately not settled here.

**Two mechanical checks guard this file, and only two.**

1. **Anchor rot.** Every file-and-line anchor cited in this file must name a file that exists and a
   line within that file's length. This is deliberately existence plus range and **not** a stored
   snippet. Existence-plus-range already earns its keep at zero authoring cost: three anchors here
   name `feature.yaml` — `FEAT-03-subissue-mirror/feature.yaml:73`, the same file at `:97`, and a
   bare `feature.yaml:63-64` — a path the tree no longer has, its execution state now living in
   `feature.json`. A stored snippet costs an author something on every anchor and still cannot see
   the failure that matters most: a line that still exists and now says something unrelated.
2. **Executable claims.** Where an entry states something a command can check, it records the command
   and the expected result in an HTML comment marker whose body opens with `claim:`, then the command,
   then a double-colon separator surrounded by single spaces, then the expected stdout substring. A
   checker re-runs every marker in the suite, so the claim fails when the tree moves under it. The
   safety boundary is part of the rule, not an implementation detail: the checker refuses any command
   whose first word is not `git` or `grep`, and never invokes a shell. A documentation file must not
   become an arbitrary code execution surface inside the test suite.

**What was considered and refused, recorded so a future scan does not re-suggest it.** A
**referenced-file watch** (M3) — flagging every entry whose cited files changed — was declined: it
hands over a review list and proves nothing, so its output is work, not verification. A **periodic
LLM audit of design claims** (M4) was declined as a gate: its judgement decays the moment code moves,
so it is worth running once as a sweep and worthless standing as a check. Neither becomes cheap
merely because the two checks above are open rather than closed — that openness is exactly why the
two that are in are the mechanical ones.
