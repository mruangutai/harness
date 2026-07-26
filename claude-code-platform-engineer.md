# Harness Review — Claude Code Platform Engineer

> **Reviewer persona:** Claude Code platform engineer / distributed-systems reviewer.
> Mandate: distrust every claim about how a mechanism behaves until checked against current
> documentation; ask what happens on partial failure.
>
> **Scope:** [SPEC.md](SPEC.md), [DECISIONS.md](DECISIONS.md), [BUILD.md](BUILD.md) as of 2026-07-26.
> Platform claims verified against `code.claude.com/docs` (sub-agents.md, hooks.md, env-vars.md,
> settings.md, memory.md) on 2026-07-26.
>
> **Ranking rule:** findings are ordered by the probability that the mechanism does not work as the
> document claims. A confidently-stated mechanism that silently no-ops outranks a
> correctly-identified tradeoff.

---

## 1. Verdict

The architecture is **sound in its state-model core and not sound in its verification layer, and the
second problem contaminates the first**. The single-writer file discipline,
checkpoint-before-dispatch, pinned `review_sha`, feature-level retry budget, and
SC-with-declared-method design are genuinely good and worth keeping. But the document's own
epistemic mechanism — DEC-81/DEC-82 recording platform facts as "verified against the
documentation" — produced at least three confident claims that are not in the documentation at all
(`delete: false`, `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, both concurrency env vars), one of which
(`delete: false`) is presented as a deployed blanket safety rail and is a pure no-op. Since the
design explicitly leans on "verified fact" as a category, every claim in that category is now
suspect until re-cited. Separately, the two mandatory-question areas — orchestrator reliability and
contract enforcement — are structurally unaddressed: an LLM performs ~15 unvalidated bookkeeping
duties per cycle, and the "normative" DIGEST contract has no validator except the same LLM. Build
it, but only after re-running platform verification with per-claim citations and adding a
deterministic invariant checker; as written, the design's safety story is partly built on mechanisms
that don't exist.

---

## 2. Platform-claim verification table

Ranked by probability the mechanism does not work as the document claims.

| # | Claim | SPEC location | Verdict | Evidence |
|---|---|---|---|---|
| 1 | `delete: false` everywhere — "a blanket safety rail" | §2.3, BUILD 0b | **WRONG — field does not exist.** No such option in subagents, hooks, settings, or memory docs. The safety rail is a silent no-op stated with full confidence. | Absent from all fetched doc pages |
| 2 | Nested spawning is "off by default," gated on `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`; `"2"` makes workers mechanically unable to delegate | BUILD 0a, DEC-82 ("Confirmed") | **WRONG / unverifiable.** The env var appears nowhere in env-vars.md. Docs state nesting is supported **up to three layers** with no gating setting mentioned. Consequences: the Step-0a settings prerequisite writes a var that does nothing; "workers are always leaves" is **not** depth-enforced (it *is* enforced by omitting `Agent` from workers' `tools:` — the design survives, the stated mechanism doesn't); DEC-82's "confirmed" and its GSD explanation story are false confidence. | env-vars.md (no entry); sub-agents.md ("up to three layers") |
| 3 | 20 concurrent (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), 200/session (`CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`) | §12, DEC-81 (presented as a doc-verified *correction*) | **WRONG / unverifiable.** Neither var is documented. DEC-81 replaced an old guess (~10) with fabricated specifics and labeled it verification. | env-vars.md (no entries) |
| 4 | `SubagentStart` hook receives agent type, returns `hookSpecificOutput.additionalContext`, injected at spawn | §5.1, DEC-64 | **VERIFIED in essentials** — SubagentStart exists and supports `additionalContext` (it cannot block, which the design doesn't need). **Unverified residue:** matcher-against-`harness-.*` semantics, the exact stdin field name, and whether a settings.json SubagentStart fires for *nested* spawns (lead→worker). If that last one is no, workers get no Expertise in hierarchical mode — silently. | hooks.md |
| 5 | Agent-frontmatter `PreToolUse` hooks fire for that agent's own calls | §4.2 | **VERIFIED.** "Define hooks directly in the subagent's markdown file… only run while that specific subagent is active. All hook events are supported." End-to-end blocking still needs the 0b spike, correctly identified. | sub-agents.md |
| 6 | Only `exit 2` blocks; other non-zero proceeds | §4.2, DEC-81 | **VERIFIED.** "Only exit code 2 blocks actions. Exit code 1 is treated as a non-blocking error and execution proceeds." | hooks.md |
| 7 | Tool input as JSON on stdin; no `$FILE`; three interpolated vars | §4.2, DEC-81 | **VERIFIED** in substance (`.tool_input.file_path` on stdin; no `$FILE`). Minor: docs list more interpolated vars (`${CLAUDE_EFFORT}` etc.) — harmless incompleteness. | hooks.md |
| 8 | `skills:` frontmatter preloads **full skill content** at spawn | §7, DEC-63 | **VERIFIED.** "The full skill content is injected, not only the description." | sub-agents.md |
| 9 | `memory:` auto-enables Read/Write/Edit (rejection rationale) | §4.0, DEC-65 | **VERIFIED** — the rejection was correct. | sub-agents.md, memory.md |
| 10 | `color:` named-only; hex invalid | §4.0, DEC-81 | **VERIFIED.** | sub-agents.md |
| 11 | `isolation: worktree`; `disallowedTools`/`permissionMode`/`maxTurns`/`mcpServers`/`effort`/`background`/`initialPrompt` supported | §4.0 | **VERIFIED** (model also accepts `fable`, omitted). | sub-agents.md |
| 12 | Subagents cannot call `AskUserQuestion` | DEC-42 | **VERIFIED** — explicitly filtered from subagent tool pools. | sub-agents.md |
| 13 | Spawn tool token is `Agent` | DEC-82 | **VERIFIED** — renamed from `Task` in v2.1.63. | sub-agents.md |
| 14 | What a subagent inherits | (never stated in SPEC — an omission) | Docs: fresh context (no parent history), **full CLAUDE.md hierarchy at every spawn**, parent MCP tools. Directly feeds the token-economics finding. | sub-agents.md |

---

## 3. Fatal findings

### FATAL-1 — class WRONG — the design's verification layer is contaminated

From: platform verification. DEC-81 and DEC-82 present fabricated facts (`delete: false`, the
spawn-depth var, both concurrency vars with the numbers 20/200) as corrections "found by verifying
against the documentation." The failure scenario is not any single wrong var — it's that BUILD.md
Step 0 says "verifying the design against the Claude Code documentation **resolved** the two
blocking spikes," downgraded nested spawning from HARD PREREQUISITE to resolved, and instructed
`/harness-init` to write a settings block whose load-bearing line does nothing. A builder following
BUILD.md ships a "safety rail" (`delete: false`) that doesn't exist and a depth guarantee that isn't
one. Specifically: BUILD § 0a, DEC-81, DEC-82, SPEC §2.3/§4.1.

**Instead:** treat every "verified fact"/"confirmed" in all three docs as unverified; re-run
verification requiring a URL + quote per claim (this review covers the platform ones); restore
nested-spawn behavior and concurrency limits to *empirical spike* status alongside 0b; delete
`delete: false` or replace it with something real (a PreToolUse hook matching destructive Bash
patterns, or `permissionMode`).

### FATAL-2 — class FRAGILE — orchestrator reliability

The orchestrator is an LLM that must, per cycle, do all of: re-read BRIEF/PLAN/STATE; run the 8-row
consistency matrix; write `STATE.md`; append rolled-up DIGESTs to `logs/`; prune logs; write
`## Approval` blocks; create the branch before the first mutating step; maintain `feature.yaml`
(status, `review_sha` pinning, `cycles_used` increment, runs list); sequence multi-squad segments in
`ship-feature`; run the question round-trip (ask, write `answers-*.md`, re-delegate with
`resume_from`); validate and apply expertise ops for 7 write-less agents; spawn immediate curation
passes; manage `feedback.md` (write, clear absorbed); assemble the briefing; create the PR; enforce
`max_cycles`; detect malformed returns. That's ~15 duties with **no validator for any of them**.
Checkpoint-before-dispatch protects *crew steps*; the orchestrator's own in-flight actions between
crews (applied 3 of 5 expertise ops; pinned `review_sha` or didn't; incremented `cycles_used` or
didn't) are checkpointed **nowhere** — `STATE.md` is its output, and nothing checks its output.

Failure scenario: it forgets to increment `cycles_used` → the "exactly one bound" on the fix loop
(§11.6) silently stops bounding; it forgets to pin `review_sha` → reviewers diff HEAD, exactly the
GAP-7 failure the design claims closed. The consistency check (§2.2) is executed by the same LLM and
covers a subset.

**Instead:** the design already broke files-only once for `check-domain.sh` because "prose guarding
a safety claim is unenforceable" (DEC-19). The identical argument applies here: ship a second
deterministic script (`bin/check-state.sh`) run at every `/harness` entry that mechanically
validates the invariants — `review_sha` set when a validator run is dispatched, `cycles_used` ≥
count of FAIL runs in `feature.yaml`, every run dir referenced from STATE,
approval-reset-after-replan. The orchestrator's judgment routes; a script audits the bookkeeping.

### FATAL-3 — class ABSENT — contract enforcement

DIGEST schemas are declared "normative" (§8.1); the runner "routes on these exact field names and
enum values." What validates them: nothing but the consuming LLM. §8.3 handles *missing/unparseable*
returns; it cannot handle the dangerous case — a well-formed DIGEST with drifted semantics
(`severity_max: medium` instead of `med`, `must-fix` instead of `must_fix`, a `blocking: "yes"`
string), which an LLM reader will charitably accept, meaning drift is *invisible by construction*:
the system behaves correctly on drifted input right up until one routing decision doesn't. Expertise
ops have the same hole ("the applier validates the op" — the applier is the orchestrator LLM).

Failure scenario: qa emits `matrix_ok: "mostly"`; the host reads it as pass-ish; the hard gate — the
design's central quality mechanism — soft-fails silently.

**Instead:** DIGESTs are YAML; a 40-line validation script (same files-only exception class) checked
at DIGEST-persist time turns drift into the loud `BLOCKED (contract violation)` path §8.3 already
defines. Without it, "normative" is aspiration.

### FATAL-4 — class ABSENT — token economics

Confirmed absent: no budget model exists in any of the three documents. The word "budget" appears
only for retry cycles and the qualitative "context budget" discipline inherited from CLAUDE.md. Now
priced with the verified inheritance fact (every custom subagent loads the **full CLAUDE.md
hierarchy** — user + project — plus full `skills:` content, plus injected Expertise, plus task
context, before doing any work):

- `plan-feature` = 5 spawns (product-lead host, pm, eng-lead-as-reviewer, visual-designer,
  ui-reviewer, + a prototype loop for user-facing features).
- `ship-feature` = ~13–15 (eng-lead + ~2 devs; validator-lead + qa + 3 reviewers; product-lead +
  pm goal-check; documentor; 3 leads for the briefing).
- Each fix cycle = a new eng run **plus** a new validator run ≈ 4–7 spawns; the SPEC's own example
  briefing treats two fix cycles as normal ≈ +8–14.
- Add question round-trips (each answer = re-spawn host + member), immediate-curation
  single-purpose spawns (DEC-68 mandates spawning a closed agent *just to apply a file edit*), and
  expertise-op applications.

Realistic total: **~25–45 spawns per feature**, largely serialized (DAG order + strictly-serial
mutators + DEC-40's serial panels), several of them `model: opus`. Order of magnitude: millions of
tokens and multi-hour wall-clock per feature. For a solo CTO shipping several features a day this is
economically and temporally marginal, and *nothing in the design would tell you* — no cost is
logged, no model-tier policy exists below the per-agent `model:` field, and DEC-68/DEC-71 both
explicitly accept extra spawns as "cheap" without ever defining cheap.

**Instead:** log tokens/spawn-count per run in `state.yaml` (data is available at return time), set
per-crew spawn budgets alongside `max_cycles`, default doers/reviewers to a cheaper model tier, and
revisit DEC-68 (immediate single-purpose curation spawns) and DEC-71 (no orchestrator→worker path
even for trivial tasks) once real numbers exist — those two are the first things the numbers will
kill.

---

## 4. Serious findings

**S-1 — Expertise poisoning has no detection path for the common case.** Lifecycle of a wrong entry:
enters via an `expertise_update` op (quality control is one advisory sentence in a rule skill); is
injected into **every subsequent spawn** of that agent by hook; persists until curation. But
curation triggers only on (a) `expertise_full` overflow or (b) a light briefing pass *that covers
leads only*. A wrong **member** entry below its section cap matches neither trigger — it persists
indefinitely, shaping every run. The **global tier** (`~/.harness/expertise/`) is worse: uncommitted
(no PR visibility, no git rollback), loaded on every spawn in every repo, and **no curator is
assigned to it anywhere in the SPEC** — §5.6 names the risk and assigns no mechanism. Security
angle: expertise entries are derived from repo content, so a hostile file in a reviewed codebase can
plant an instruction that becomes a *durable, hook-injected* prompt injection into all future
spawns. Fix: periodic mandatory curation for *all* agents (not just leads), and either commit-or-kill
the global tier.

**S-2 — Human bottleneck: supervision restructured, not removed — defensible, but the SPEC
overclaims.** Blocking touchpoints per feature: PLAN+prototype approval; every `blocking: true`
open_question (each costing a full re-delegation round-trip); the UAT execution; the briefing ship
decision; the merge. Minimum ~3, realistically 5–8. What the design delivers is supervision batched
at decision boundaries instead of continuous — a real improvement, but "executes reliably at each
stage without constant supervision" should be restated as "without *mid-stage* supervision." The
per-answer cost (DEC-43's accepted tradeoff) makes a chatty feature dramatically more expensive than
a quiet one, which pressures agents toward *not asking* — the opposite of §4.4's intent.

**S-3 — Self-hosting circularity: partially acknowledged, operationally undefined.** SPEC §9.1
honestly flags it ("improved, not resolved"). What it doesn't say: (a) the `eval` test kind requires
a `cmd` — for the harness repo, whose "AI behavior" is markdown personas, **no eval runner exists or
is specified**; the gate is defined but not executable on the one project it's most needed for;
(b) the entire v1 is necessarily built *before* the gates exist, so the harness itself ships ungated
by its own rules — the first system exempted from the harness is the harness; (c) `ai-dev` authors
evals for changes *to ai-dev's own definition*, and validator-lead's adequacy check is a finding,
not a gate. What breaks first: the MVP cutover — BUILD's sequencing gate (items #1–2 delete the
mechanism the harness currently runs on) is a one-way door taken on the strength of an MVP smoke
test. Acceptable as a bootstrap *if* the ungated status of v1 is recorded as an explicit DEC and the
harness's own eval runner is defined before any `ai_behavior` change post-cutover.

**S-4 — SubagentStart in hierarchical mode is a single point of silent failure.** BUILD 0a already
notes missing hook = memoryless agents with no error. Add: unverified whether a settings.json
SubagentStart fires for spawns initiated *inside* a subagent (lead→worker). If it doesn't, exactly
the 12 workers lose Expertise in hierarchical mode while leads keep theirs — a degradation invisible
in output. Add to spike 0b's test list.

**S-5 — Spec bug: doers can't write their own expertise file under the manifest as written.** §5.3
says doers self-apply ("the domain hook scopes it to its own file"), but the example manifest
domains (§3.1) don't include `.harness/expertise/<agent>.md` for any doer — a working hook would
*block* the mechanism §5.3 depends on. One-line fix per member entry; worth catching before 15 agent
files are written.

**S-6 — Multi-developer use breaks the whole state model.** Every guarantee is "single writer" where
writer means *one agent in one session on one machine*. Two developers = two orchestrators = two
writers for `STATE.md`, `feature.yaml`, `logs/`, and committed expertise files that will
merge-conflict. Nothing in any document mentions this. Fine for a solo CTO today; should be a stated
constraint ("single-operator by design") rather than an omission.

**S-7 — Platform drift has no tripwire.** The design depends on ~6 platform behaviors (skills
preload, SubagentStart injection, frontmatter-hook blocking, nesting depth, CLAUDE.md inheritance,
tool filters). Claude Code auto-updates. The state check can verify settings.json *contents*, not
behavior. Cheap mitigation: a `harness-selftest` that re-runs the 0b probe (blocked write + injected
marker) on demand or after CLI updates.

**S-8 — dev-ops's Bash bypass is posed as a choice and never chosen.** §4.2/DEC-58 offer "hook also
matches Bash, or trusted by design" — a security decision left as an either/or in a normative spec.
Pick one before build (recommend: trusted-by-design + user-gated merge, since matching Bash paths is
unwinnable).

**S-9 — The five unrecovered gaps.** BUILD honestly records that five adversarial-pass gaps were
tracked outside the document and are lost. Credit for not inventing them — but the design cannot be
called settled with five known-unknown defects outstanding.

---

## 5. The omissions table

| # | Question | Status | Summary |
|---|---|---|---|
| 1 | Token economics | **Confirmed absent** | No budget model, no cost logging, no model-tier policy. Verified fact makes it worse: every spawn loads the full CLAUDE.md hierarchy + full rules + expertise before work starts. See FATAL-4. |
| 2 | Cost/latency per feature | **Confirmed absent** | ~25–45 spawns/feature with 2 fix cycles, largely serialized. Nothing measures or bounds it. Marginal for many-times-a-day solo use. |
| 3 | Orchestrator reliability | **Confirmed absent** | ~15 unvalidated duties/cycle; orchestrator's own in-flight bookkeeping checkpointed nowhere; consistency check is self-administered and partial. See FATAL-2. |
| 4 | Expertise self-attack | **Partially addressed** | Propose-time reconciliation + curation exist, but under-cap member entries have no scheduled review, and the global tier has a named risk with **zero** assigned mechanism. See S-1. |
| 5 | Human bottleneck | **Partially addressed** | 3–8 blocking touchpoints/feature, batched at boundaries. Real improvement over mid-stage supervision; the "without constant supervision" claim overstates. See S-2. |
| 6 | Contract enforcement | **Confirmed absent** | "Normative" schemas validated only by the consuming LLM; §8.3 catches missing, not wrong. See FATAL-3. |
| 7 | Self-hosting circularity | **Partially addressed** | §9.1 admits it's unresolved; operationally undefined (no eval runner for personas; v1 ships ungated by its own gates). See S-3. |
| 8 | Everything else | **Confirmed absent** | Multi-developer (S-6), platform drift (S-7), security of the agent system itself — prompt-injection persistence via expertise (S-1), repo-shipped hook scripts executing on every Write — observability beyond logs, and no repair path for DEC-52's acknowledged crash-mid-canonical-write. Half-built-feature migration is the one item genuinely covered (resume + `BLOCKED` preservation, DEC-77). |

---

## 6. What is genuinely good — do not break these

- **The state model**: BRIEF/PLAN/STATE separation with STATE bounded by construction (DEC-45);
  declaration vs live state (DEC-47); REQ/FEAT/D/T with the "survives an implementation swap" test
  (DEC-48); computed-not-tracked REQ coverage.
- **The recovery discipline**: checkpoint-before-dispatch, resume-not-reprompt,
  `[harness:<step-id>]` git attribution making side effects derivable (DEC-51) — the strongest
  engineering in the document.
- **`review_sha` pinning** (DEC-50) and **feature-level retry budget** (DEC-49).
- **SC with declared `verify:` methods and pm-as-evidence-collector** (DEC-72/73) — makes "goal met"
  falsifiable, and pm's self-review is correctly reduced to reporting others' evidence.
- **The `memory:` rejection** (DEC-65) — verified correct, and the reasoning (tool-grant side
  effects break load-bearing capability guarantees) is exactly the right kind of paranoia.
- **The exit-2 / stdin-JSON corrections** (DEC-81's middle rows) — verified correct and genuinely
  dangerous to have gotten wrong.
- **Malformed-return → re-prompt once → BLOCKED, never guess** (DEC-30), and the reviewer verdict
  mapping that prevents nit-loops (DEC-31).
- The **append-only decision log itself** — it's what made this review's contamination finding
  legible.

---

## 7. What could not be verified, and how to settle it

1. **Nested-spawn depth semantics** — docs say "up to three layers," no gating var. Settle:
   empirical — spawn agent-with-`Agent` from the main session, have it spawn a worker, have the
   worker attempt a spawn; observe defaults and whether any setting changes them. (Folds into spike
   0b.)
2. **Concurrency/session limits** — undocumented. Settle: empirical fan-out test or the CLI
   changelog; until then size panels conservatively.
3. **SubagentStart specifics** — matcher-vs-agent-name, stdin field name, firing on nested spawns.
   Settle: a logging hook + one hierarchical spawn (add to 0b).
4. **Frontmatter-hook exit-2 blocking end-to-end** — documented, but the design is right to demand
   the 0b spike before trusting parallel safety to it.
5. **Skill-name resolution for nested rule dirs** — whether
   `.claude/skills/harness/rules/<name>/SKILL.md` is discoverable as `harness-<name>` in a `skills:`
   list. Settle: one throwaway agent with one nested rule skill.

---

**Bottom line:** keep the state model, fix the epistemics. Re-cite every "verified fact," add two
small deterministic checkers (state invariants, DIGEST schema), define the global-expertise curator,
and price a feature before committing to DEC-68/DEC-71's spawn-happy defaults.
