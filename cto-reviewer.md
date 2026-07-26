# Harness Design Review — CTO Reviewer

> **Reviewer persona:** engineering leader who has run multi-agent systems at real cost.
> **Scope:** `docs/harness/SPEC.md` (1694 lines), `DECISIONS.md` (DEC-01…DEC-82), `BUILD.md`, plus
> repo state and measured file sizes as of 2026-07-26.
> **Mandate:** quantify spawns/tokens/dollars/minutes; test against the null hypothesis; answer the
> eight omission questions; rank findings by expected waste and abandonment probability.

---

## 1. Verdict

**Not sound enough to build as written.** The control-plane engineering — checkpoint-before-dispatch,
pinned `review_sha`, feature-level cycle budgets, the VERDICT enum, SC-with-evidence — is genuinely
careful work. But it is bolted onto an org shape whose economics were never computed: 15 stateless
agents, mandatory lead intermediation on every task (DEC-71), a happy path of ~19 spawns and a
realistic path of 30–45 spawns per feature, each spawn reloading ~12–17k tokens of baseline context,
with 4–6 blocking human touchpoints per feature. The spec contains exactly zero numbers about tokens,
dollars, or minutes — grep confirms the only "budgets" in all three documents are retry-cycle
counters. The system's stated value ("Claude executes reliably at each stage without constant
supervision") is contradicted by its own design: it delivers supervision restructured into approvals,
UAT scripts, round-trips, and briefings. **Build the state artifacts and gates; do not build the
org.**

---

## 2. Fatal findings

Ranked by expected waste (time, tokens, money) × probability a single busy CTO abandons the system
within a month.

### F1 — ABSENT · cost engineering · No token/cost/latency model anywhere

- **Ref:** entire SPEC; the closest thing is §10.2 "*Cost accepted:* one extra spawn for trivial
  single-task work" and §7 "rules must stay short."
- **Scenario:** You run `plan-feature` + `ship-feature` on your third feature of the day and discover
  each feature costs hours and tens of dollars, with no dial to turn because cost was never a design
  axis. A *one-line UI tweak* under DEC-71 costs a minimum of 3 spawns (orchestrator turn → eng-lead
  → frontend-dev → assessment back up), each loading the CLAUDE.md hierarchy (~5k tokens measured
  today: 5.4KB user + 14.4KB project), rules, Expertise, and BRIEF/PLAN/STATE before doing any work.
- **Instead:** Give every crew a token/latency budget field the way it already has `max_cycles`. Add
  a direct orchestrator→worker path for single-task work (delete DEC-71's "no exception" rule). Make
  lead intermediation opt-in above a size threshold.

### F2 — WRONG · security/systems · Domain enforcement is bypassed by the tool every doer holds

- **Ref:** SPEC §4.2, §2.3; roster §3.4.
- **Scenario:** §4.2 hooks only `matcher: "Write|Edit"` and names `dev-ops` as "the sharp edge"
  because it holds Bash. But per §3.4, **all eight doers hold Bash** — pm, qa, documentor,
  visual-designer, and all five eng specialists. Any of them writing a file via `sed -i`, `cat >`, or
  a build script bypasses `check-domain.sh` entirely, silently. The "disjoint writers, therefore safe
  to fan out" claim (§2.3) — described as "the entire justification for running agents in parallel" —
  rests on a hook the agents' most-used tool ignores. Not malice; ordinary drift: models reach for
  shell redirection constantly.
- **Aggravating irony:** §8.5 already forces repo-mutators strictly serial on one branch. So the
  elaborate hook apparatus (spike 0b, generic script, per-agent frontmatter) protects mostly a case
  the design serializes anyway — maximum machinery, minimum protected surface.
- **Instead:** Accept serialization as the real mechanism (it already is), use `isolation: worktree`
  for the rare true parallel-mutate case, and demote the domain hook to a nice-to-have guard rather
  than a load-bearing guarantee.

### F3 — FRAGILE · distributed-systems · The orchestrator is an unchecked single writer with ~15 duties and no self-checkpoint

- **Ref:** SPEC §2.3, §5.3, §10, §11.3. Full enumeration in omissions Q3.
- **Scenario:** An LLM following a prose playbook must, per cycle, correctly do state-consistency
  checking, branch creation, `feature.yaml` writes, `STATE.md` appends, daily-log appends,
  Expertise-op application for 7 write-less agents, `## Approval` writes, `review_sha` pinning,
  cycle-budget accounting, answers-file writes, `feedback.md` clearing, PR creation, and pruning.
  Workers get checkpoint-before-dispatch and re-prompt-once contracts; **the orchestrator's own
  mid-cycle progress is checkpointed nowhere** except `feature.yaml`/`digest_ref` (which covers
  Expertise-op replay only, §5.3). A skipped log append or unapplied op is silent; a corrupted
  `STATE.md` poisons the file every agent loads at spawn. The state-consistency matrix (§2.2)
  catches structural inconsistencies, not omissions.
- **Instead:** Shrink the duty list (fewer files, fewer tiers) rather than trying to validate an
  LLM's conformance to 15 duties. If you keep it, make each cycle idempotent and add a mechanical
  post-cycle check (a script, like `check-domain.sh` — the one deliberate exception already exists as
  precedent).

### F4 — FRAGILE · product · The human bottleneck contradicts the stated value

- **Ref:** SPEC §2.1, §10.3, §11.6, §13.1; DEC-43 ("Tradeoff accepted: every human interaction costs
  a full re-delegation").
- **Scenario:** 4–6 blocking touchpoints per feature (count in omissions Q5), several of which (UAT,
  briefing, PLAN+prototype approval) cannot be batched. Each question round-trip re-spawns the lead
  host with `resume_from`. For a solo CTO running features "many times a day," you become the
  scheduler of a system that idles between your responses. The predictable outcome within a month:
  you start approving without reading (which deletes the value of every gate) or you bypass
  `/harness` for anything urgent (which deletes the system).
- **Instead:** Collapse PLAN approval, prototype approval, and open questions into one batched
  checkpoint per feature; make the CEO briefing + UAT the only other one. Two touchpoints, both
  batched, is survivable.

### F5 — FRAGILE · AI-systems · Expertise has an ingress path and no truth-verification path

- **Ref:** SPEC §5.2–§5.6; DEC-24, DEC-27. Full lifecycle trace in omissions Q4.
- **Scenario:** The spec itself writes the finding for the global tier: "**Risk to accept:** a wrong
  global entry silently misleads every project at once" — accepted with no detection mechanism
  attached.
- **Instead:** Provenance + decay: every entry carries the run that produced it; entries not
  re-confirmed within N runs get flagged for the curation pass; global-tier writes require your
  explicit sign-off (they currently don't — promotion is "deliberate" but agent-judged).

---

## 3. Serious findings

Real problems that need solving but don't invalidate the approach.

1. **No mechanical contract validation** (§8.1/§8.3) — see omissions Q6. The "normative" schemas are
   enforced by an LLM's opinion of parseability.
2. **`skills:` preload is unconditional and unbounded** (§7). "Rules must stay short" is prose;
   nothing measures them. Today's rule files are 2–3KB each (measured), fine — but three of the seven
   rules don't exist yet, and nothing stops `handoff` + `expertise` + a role rule from growing to 5k
   tokens × every spawn × 30–45 spawns/feature.
3. **Platform-behavior dependency without version pinning.** The design load-bears on:
   `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `SubagentStart` `additionalContext` injection, frontmatter
   `PreToolUse` with exit-2-blocks semantics, `skills:` full-content preload, and 20/200 spawn caps.
   BUILD.md §0a admits both settings "degrade silently" if missing and has the state check verify
   them — good — but a Claude Code release changing hook payload shape or exit semantics fails open
   with no canary. Add a self-test crew that asserts each mechanism (BUILD.md's verification list is
   close; make it re-runnable, not one-time).
4. **Five unrecovered gaps** — BUILD.md's own "Open items" says GAP 1, 2, 5, 6 and "the five
   remaining gaps" were tracked outside the document and are lost. The design ships with admitted
   unknown unknowns. Recover them before calling the design settled; that's the document's own
   instruction.
5. **BRIEF/PLAN/STATE read by every persona at spawn** (§2) means plan bloat multiplies by spawn
   count. A 20KB PLAN.md costs ~5k tokens × 40 spawns ≈ 200k tokens per feature just re-reading the
   plan. No excerpting mechanism exists.
6. **Multi-squad `ship-feature` splits run-dir ownership** — §13 says "the orchestrator owns the run
   dir, branch and cycle budget across segments" while §11.4 makes each squad lead own its
   `state.yaml`. Reconcilable but currently ambiguous, and it's the highest-traffic crew.
7. **Single-user assumption** — see omissions Q8. Two terminals = two orchestrators = two writers for
   every "single-writer" file. No locking anywhere.

---

## 4. The omissions table

| # | Question | Status |
|---|---|---|
| 1 | Token economics | **CONFIRMED ABSENT** |
| 2 | Cost & latency per feature | **CONFIRMED ABSENT** |
| 3 | Orchestrator reliability | **PARTIALLY ADDRESSED** |
| 4 | Expertise as attack surface | **CONFIRMED ABSENT** (no verification stage) |
| 5 | Human bottleneck | **CONFIRMED** — supervision recreated under new names |
| 6 | Contract enforcement | **PARTIALLY ADDRESSED** |
| 7 | Self-hosting circularity | **PARTIALLY ADDRESSED** — acknowledged, not resolved |
| 8 | Other omissions | see below |

### Q1 — Token economics: CONFIRMED ABSENT

Grep across all three docs: every "budget" is a retry counter (`max_cycles`, `max_total_cycles`,
`node_repair_budget`). Qualitative discipline only ("state by file path", "rules stay short",
"bounded DIGEST"). Expertise caps are *entry counts* (15/15/10/5), not token caps — entries have no
length limit.

**Per-spawn baseline, measured + estimated:**

| Component | Tokens | Basis |
|---|---|---|
| CLAUDE.md hierarchy | ~5k | measured: 5.4KB user + 14.4KB project = ~20KB |
| System prompt + tool defs | ~3k | estimate |
| 2–3 preloaded rule skills | ~1.5–2.5k | measured: current rules 2–3KB each |
| Injected Expertise (project + global) | ~1.5–2.5k | 45-entry cap × ~25–40 tok/entry |
| BRIEF + PLAN + STATE at spawn | ~2–5k | grows with project |
| **Baseline before any work** | **~12–17k** | |

Then 20–150k more accumulated over the agent's working turns. It "stops fitting" when PLAN.md +
Expertise + rules grow — and nothing measures any of them.

### Q2 — Cost & latency per feature: CONFIRMED ABSENT

**Spawn count for one interactive user-facing feature.** Assumptions (argue with these): hierarchical
mode; 2 eng specialists (UI + API); 2 fix cycles — the SPEC's own briefing example (§10.3) shows 2;
2 question round-trips; 1 curation event.

| Segment | Spawns |
|---|---|
| `plan-feature`: product-lead + pm + eng-lead(arch review) + visual-designer(+prototype) + ui-reviewer(A) | 5 |
| `ship-feature` happy path: eng-lead + 2 devs + validator-lead + qa + 3 reviewers + product-lead + pm(goal-check) + documentor + 3 leads (CEO briefing) | 14 |
| Fix cycles ×2: each = new eng run (lead+dev) + new validator run (lead + qa ± re-panel) ≈ 5–7 | +10–14 |
| Question round-trips ×2 (re-spawn host + member) | +4 |
| Single-purpose curation spawns | +1–3 |
| **Total** | **~19 floor · 34–40 realistic** |

- **Tokens:** ~12–17k baseline × spawns + working context ≈ **1.5–4M tokens processed per feature**.
- **Dollars** (educated guess — verify against current pricing: Sonnet ~$3/$15 per Mtok, Opus ~5×,
  cache reads ~10%): **~$15–50/feature all-Sonnet; $60–250 with Opus leads+devs** as the §4.0 example
  specifies. Treat as ±2×.
- **Wall clock:** mutators serial (§8.5), squad segments sequenced, round-trips block on the human →
  ~25–35 mostly-serial stages × 2–6 min = **1.5–4 hours machine time per feature**, plus your
  response latency.

**Not economically usable many times a day by one person.** Even the zero-defect floor is ~19 spawns
and >1 hour.

### Q3 — Orchestrator reliability: PARTIALLY ADDRESSED

Per cycle the orchestrator must: re-read BRIEF/PLAN/STATE; run the §2.2 consistency matrix; route on
VERDICT+DIGEST without opening artifacts; create the branch pre-mutation; write/maintain
`feature.yaml` (status, `review_sha`, `cycles_used`); sequence multi-squad segments; append
per-member blocks to STATE.md; append rolled-up DIGESTs to daily logs; ask/record/re-delegate open
questions (durable `answers-*` files); write `## Approval`; validate and apply `expertise_update` ops
for 3 leads + 4 reviewers; run lead curation (spawn lead, apply its ops); write and clear
`feedback.md`; enforce `max_total_cycles`; prune logs; create the PR; never merge.

**Mitigations that exist:** re-read-at-loop-top, checkpoint-before-dispatch (for *hosts'*
`state.yaml`), `digest_ref` replay for interrupted Expertise ops, re-prompt-once for malformed
returns.

**What's missing:** the orchestrator's own multi-step cycle is not checkpointed — "DIGEST received,
STATE appended, log not yet appended, ops not yet applied" is unrecoverable state held in an LLM's
context. A skipped duty is silent; §2.2 catches structural inconsistency, not omission. One bad
STATE.md write propagates into every subsequent spawn.

### Q4 — Expertise as attack surface: CONFIRMED ABSENT

Lifecycle of a wrong entry:

- **Ingress:** any completed task can propose an op; the only validation is *target-ID existence*
  (§5.3). Truth is never checked. Doers self-apply — the hook checks the path, not the content. pm
  and ai-dev hold Web tools, so a prompt-injection payload in researched content can become a
  persistent Expertise entry — which is then **injected into every future spawn of that agent as
  trusted context**, self-perpetuating.
- **Persistence:** indefinitely, if plausible and under cap. Curation triggers only on
  `expertise_full` overflow or a "light pass" at briefings; a wrong entry in a half-full section
  triggers nothing.
- **Detection:** an agent must independently observe a contradiction and propose `replace` — hope,
  not a mechanism. Member curation "does not reach your briefing" (§5.4), so you never see the 12
  workers' files unless you go read them.
- **Global tier:** worse — uncommitted (no PR visibility, the one audit channel the project tier
  has), loaded in every repo, promotion is agent judgment, and the spec's own words are "risk to
  accept." No provenance, no TTL, no re-confirmation.

### Q5 — Human bottleneck: CONFIRMED — supervision recreated under new names

Blocking touchpoints per feature:

1. PLAN + prototype approval (§13.1)
2. Question round-trips, 1–3 typical (§2.1 — DEC-43: each "costs a full re-delegation")
3. UAT execution — you personally hand-test (§11.6, "cannot ship on an unrun UAT")
4. CEO briefing ship/fix/re-scope decision (§10.3)
5. Merge (rides the briefing)
6. Plus per-project BRIEF approval and curation vetoes

**4–6 blocking waits per feature**, unbatchable as designed because they occur at different pipeline
stages. Lateral lead-routing (§13) genuinely removes *some* questions — that part works. But
"executes reliably without constant supervision" is false as written: you are the highest-latency
component in a serial pipeline, consulted mid-pipeline, per feature.

### Q6 — Contract enforcement: PARTIALLY ADDRESSED

Drift *policy* exists and is good: re-prompt once → `BLOCKED (contract violation)`, never guess
(§8.3, §5.3, DEC-30). But there is **no validator**: no schema file, no parser, no script.
"Normative" schemas (§8.1) are enforced by the host LLM's judgment of what counts as unparseable.
`severity_max: medium` vs `med`, a stringified `open_questions` count, a missing `matrix_ok` — each
is silently normalized or misrouted at the host's whim, and §8.2's conditional routing keys on
exactly these values. The repo's one script precedent (`check-domain.sh`) shows the authors know how
to make contracts mechanical; DIGESTs deserved the same and didn't get it.

### Q7 — Self-hosting circularity: PARTIALLY ADDRESSED — acknowledged, not resolved

SPEC §9.1 says it itself: "the reflexive case remains awkward… an improvement over passing on
judgment alone, not a resolution." Changes to `ai-dev` are gated by evals `ai-dev` authored;
validator-lead's "adequacy" check is advisory. The real control is that *rules* are human-authored
and deploy-overwritten (§6) — that part is sound. **What breaks first: eval quality.** Evals for
agent behavior are the hardest eval class; there is no reference dataset, no rubric standard, and the
author is the subject. The gate becomes green-stamp theater before anything else fails. BUILD.md's
sequencing gate (don't delete GSD until self-injection is proven) handles the bootstrap
chicken-and-egg competently.

### Q8 — Other omissions

- **(a) Bash bypass** — the biggest one not asked: see F2.
- **(b) Multi-developer:** absent; every "single-writer" guarantee assumes one main session; two
  terminals = two orchestrators, no lock file anywhere.
- **(c) Observability:** logs and `state.yaml` exist, but no aggregate view — no per-feature cost,
  cycle statistics, or gate-failure rates; you cannot answer "is the harness earning its overhead"
  from its own data, which given Q1/Q2 is the question.
- **(d) Platform drift:** serious finding #3 — five load-bearing undocumented behaviors,
  silent-fail-open on change, no re-runnable self-test.
- **(e) Half-built feature migration:** partially covered — `resume_from` + step-boundary resume +
  `schema_version` on `state.yaml`; crew-YAML changes mid-flight are unhandled.
- **(f) The lost GAP series:** BUILD.md admits five design gaps were tracked outside the documents
  and are unrecovered — the design is self-declared incomplete.

---

## 5. The null hypothesis

The null: one competent person in plain Claude Code, with plan mode, a good CLAUDE.md, and
`/code-review` before merge. Per feature: ~$2–10, 20–60 minutes, 1–2 touchpoints.

**What the harness prevents that the null doesn't:**

1. *Cross-session amnesia mid-feature* — real, but a 50-line STATE file + a plan doc solves 90% of it
   without 15 agents.
2. *Quietly skipped tests/review under pressure* — real, but the enforcement is the **qa test-matrix
   gate against the diff**, one agent's job; it doesn't need the org around it.
3. *Scope drift from the approved goal* — real; solved by BRIEF/SC-with-evidence, which are
   *artifacts*, not agents.
4. *Rubber-stamping a broken merge* — the UAT gate genuinely prevents this. Also one artifact.

**The economics:** the expensive failure this targets — "Claude shipped something wrong and I didn't
notice until later" — costs a seed-stage CTO roughly a rework day when it happens. If the null
hypothesis hits that on ~20% of features, expected loss is ~1.5 hours/feature. The harness charges
~2–4 hours of wall clock plus 4–6 interventions plus $15–250 on **every** feature to reduce it. The
insurance premium exceeds the expected loss, before counting the harness's own new failure modes
(F2, F3, F5). **It does not beat the null hypothesis as designed.**

What beats the null is the null *plus the harness's four best artifacts* (BRIEF/SC, test-matrix gate,
pinned-SHA review, UAT script) run as skills in the main session — roughly 5–8 spawns per feature,
one lead tier deleted, same gates.

---

## 6. What is genuinely good — do not break these

- **Checkpoint-before-dispatch + `resume_from` + `git log` attribution with `[harness:<step-id>]`
  prefixes** (§11.5, DEC-51) — resume-don't-re-prompt is the correct call and the mechanism is honest
  about step-boundary granularity.
- **Pinned `review_sha`** (DEC-50) — reviewers can't be gaslit by later commits. Keep regardless of
  everything else.
- **Feature-level cycle budget spanning runs** (DEC-49) and the exhaustion protocol that preserves
  everything and escalates rather than abandons (DEC-77).
- **The VERDICT enum distinguishing BLOCKED from FAIL**, ESCALATE outranking FAIL in roll-up, and
  re-prompt-once-then-BLOCKED (DEC-30) — "never guess a verdict" is the right invariant.
- **SC with declared `verify:` methods and evidence pointers; pm collects evidence rather than
  re-testing** (§11.6, DEC-73) — this makes "done" falsifiable. The best idea in the document.
- **UAT as a blocking, committed artifact** (DEC-74) and **approval reset on re-plan** (§2.2).
- **Decision vs. observation boundary** (DEC-23) — keeps Expertise from becoming a shadow decision
  log.
- **The exit-2 / stdin-JSON factual corrections** (DEC-81) and BUILD.md's willingness to record that
  the source's evidence was wrong, and that five gaps are *lost rather than invented* — the epistemic
  hygiene throughout is unusually good.
- **Logs separated from STATE.md; STATE bounded by construction** (DEC-45).

---

## 7. What could not be verified, and what would settle it

- **Actual per-spawn token counts and pricing.** Baseline components are measured from real files
  today, but rules/agents get rewritten during the build and pricing figures are from memory. Settle
  it by instrumenting one real `ship-feature` run (or `/cost` on a mock) — treat the dollar range as
  ±2×.
- **Spike 0b** (frontmatter `PreToolUse` exit-2 actually blocking) and **nested-spawn depth-2
  behavior** — the docs themselves mark these unproven; F2 stands *even if the hook works*, because
  of Bash.
- **Fix-cycle frequency** — assumed 2 per feature from the SPEC's own briefing example; the real rate
  moves the cost estimate more than any other assumption.
- **The five unrecovered GAPs** — by the document's own admission, nobody can verify the design is
  complete until they're recovered from session history.

---

## Prescription (one paragraph)

Keep §11's execution-state model, the SC/UAT machinery, the qa matrix gate, and pinned-SHA review as
**skills and artifacts in a plain Claude Code session**; delete the lead tier, DEC-71's mandatory
intermediation, and 15-agents-everywhere; cap the roster at pm, dev(s), qa, one reviewer panel; and
add the two numbers the design never had — a token budget per crew and a cost line in the briefing.
