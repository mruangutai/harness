# Harness Design Review — Independent Reviewer (Synthesis of Two Reviews)

> **Reviewer persona:** independent third reviewer. Inputs: the design
> ([SPEC.md](docs/harness/SPEC.md), [DECISIONS.md](docs/harness/DECISIONS.md),
> [BUILD.md](docs/harness/BUILD.md)) plus two prior independent critiques —
> [REVIEW-claude-code-platform-engineer.md](REVIEW-claude-code-platform-engineer.md) ("PE") and
> [cto-reviewer.md](cto-reviewer.md) ("CTO").
> **Mandate:** (1) where the reviews agree — agreement on a fatal finding is the strongest signal
> available; (2) where they conflict, adjudicate on evidence; (3) what BOTH missed; (4) an ordered
> fix list before any code is written.
> **Method note:** disputed platform claims were re-verified against `code.claude.com/docs`
> (settings, sub-agents) on 2026-07-26 — with quotes. This mattered; see §0.

---

## 0. A finding about the reviews themselves (this reorders everything)

PE's FATAL-1 claims `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`, `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`,
and `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` "appear nowhere" in the documentation and were
fabricated by DEC-81/DEC-82. Fetched `code.claude.com/docs/en/sub-agents` on 2026-07-26: **all
three are documented**, with the exact numbers the design uses:

- *"To change the limit, set `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`… caps nesting at two layers…
  that second layer can't delegate further. Set 1 to turn nesting off."* (v2.1.217+)
- *"By default, Claude can spawn at most 200 subagents per session…
  `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION`"* (v2.1.212+)
- *"By default, when 20 subagents are running… `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`"* (v2.1.217+)

Three of PE's four "fabricated" claims are real — the review quotes "up to three layers" from the
very doc section that documents the env var a few lines later. Two things survive from FATAL-1:

1. **`delete: false` is genuinely absent** from the settings and sub-agents pages. SPEC §2.3's
   "blanket safety rail" remains a no-op as far as can be verified.
2. **BUILD § 0a's consequence table is inverted.** BUILD says nesting is "off by default" and "if
   missing, leads silently cannot spawn." The docs say the default depth is **3** (since v2.1.219).
   If the setting is missing, the failure is not flat-mode collapse — it is that **workers CAN
   delegate**, silently breaking "workers are always leaves." The real enforcement is omitting
   `Agent` from worker `tools:`, which the design already does. And everything here is
   version-gated at CLI ≥ 2.1.217, which no document pins.

The meta-lesson is stronger than either review stated: the design's DEC-81/82 *and* the review
built to audit them both made confident doc claims that don't hold. **Nothing labeled "verified" is
trustworthy without a URL + quote + version marker.**

---

## 1. Where they agree — the fatal consensus

Found independently, with converging detail. Highest-confidence findings on the table.

1. **The orchestrator is an unvalidated single point of failure** (PE FATAL-2 ≡ CTO F3). Both
   enumerate the same ~15 per-cycle duties and the same gap: workers get
   checkpoint-before-dispatch, but the orchestrator's own mid-cycle bookkeeping (`review_sha`
   pinning, `cycles_used` increments, expertise-op application, log appends) is checkpointed
   nowhere and audited by nothing. A skipped duty is silent; a bad `STATE.md` write poisons every
   subsequent spawn.
2. **"Normative" DIGEST contracts have no validator** (PE FATAL-3 ≡ CTO Serious #1/Q6). Identical
   failure named by both: §8.3 catches *missing* returns, not *drifted* ones —
   `severity_max: medium` vs `med`, `matrix_ok: "mostly"` — which an LLM reader charitably
   normalizes, so the hard gate soft-fails invisibly. Both point at `check-domain.sh` as the
   precedent proving the authors know how to make contracts mechanical.
3. **Token/cost/latency economics are confirmed absent** (PE FATAL-4 ≡ CTO F1/Q1/Q2).
   Independently derived spawn counts converge (~25–45 vs ~19–40 per feature). Both flag DEC-68
   (single-purpose curation spawns) and DEC-71 (mandatory lead intermediation — minimum 3 spawns
   for a one-line tweak) as the first casualties once anything is measured.
4. **Expertise is a persistent, unverified ingress path** (PE S-1 ≡ CTO F5/Q4). Same lifecycle
   trace from both: a wrong (or prompt-injected — pm and ai-dev hold Web tools) entry under its
   section cap triggers no curation, ever, and is re-injected into every future spawn as trusted
   context. The global tier is worst-in-class: uncommitted, no curator assigned, and the SPEC's own
   text is "risk to accept" with no mechanism.

**Second-tier agreements:** 4–8 blocking human touchpoints per feature (the "without constant
supervision" claim overstates); multi-developer use breaks every single-writer guarantee; platform
drift has no re-runnable self-test; the five GAPs are lost and the design is self-declared
incomplete; self-hosting circularity is acknowledged but operationally undefined.

**Agreed keep-list (near-verbatim overlap):** checkpoint-before-dispatch + `resume_from` +
`[harness:<step-id>]` attribution; pinned `review_sha`; feature-level cycle budget; the VERDICT
enum with re-prompt-once-then-BLOCKED; and SC-with-declared-`verify:`-and-evidence — both call it
the best idea in the document.

---

## 2. Where they conflict — adjudicated

### (a) Verdict: "build it after fixes" (PE) vs "do not build the org" (CTO)

CTO has the better evidence *frame* — the only review that priced the design against a null
hypothesis (plain session + the four best artifacts as skills: ~5–8 spawns, 1–2 touchpoints), with
real file-size measurements. But its dollar figures are self-admitted ±2× on guessed defect rates,
and PE never engaged "should the org exist" at all. **Settle it:** run the same 2–3 real features
both ways — null-hypothesis-plus-artifacts vs the full org (or a mocked slice) — logging spawns,
tokens, wall-clock, touchpoints. A week of usage data versus months of building 15 agents on an
unpriced premise.

### (b) Platform facts: fabricated (PE) vs real-but-fragile (CTO)

**Settled by fetching the docs** (§0): CTO was closer — the mechanisms are real — but neither was
right. Env vars exist; `delete: false` doesn't; BUILD 0a's "if missing" consequence is inverted;
CTO's version-pinning complaint gains force (everything requires CLI ≥ 2.1.217). The empirical 0b
spike both reviews demand still stands.

### (c) Domain-hook enforcement: platform mechanics (PE) vs conceptual bypass (CTO)

CTO's F2 is the stronger finding and its premise checks out: SPEC §3.4's roster grants **Bash to
all eight doers**, while §4.2 names only dev-ops as "the sharp edge." Any doer writing via
`sed -i`, `cat >`, or a build script bypasses `check-domain.sh` entirely — and §8.5 already
serializes repo-mutators, so the hook apparatus protects a surface the design mostly doesn't
parallelize. PE only flagged the dev-ops either/or (S-8). **Settle it:** nothing empirical needed —
it's readable in the SPEC. Pick one: strip Bash from doers that don't need it, match Bash in the
hooks (unwinnable, per both reviews), or accept serialization + `isolation: worktree` as the real
mechanism and demote the hook to a guardrail.

### (d) Orchestrator fix: add a validator script (PE) vs shrink the duty list (CTO)

Not truly contradictory — PE assumes the org stays, CTO doesn't. Resolution rides on conflict (a):
if the pilot kills the lead tier, most duties evaporate; whatever survives gets the
`check-state.sh` treatment. Do both.

---

## 3. What BOTH missed

1. **The CEO edits code with their own hands, and the design has no story for it.** Every
   guarantee — single-writer domains, `review_sha` diffs, STATE consistency, the qa matrix
   "against the PR diff" — assumes all repo mutations flow through agents. A hands-on solo CTO
   *will* hotfix a file mid-feature. Worse, §8.6's dirty-tree rule halts crews with `BLOCKED` on
   anything outside the harness-owned whitelist, so your own uncommitted edit deadlocks the system;
   a manual commit to the feature branch lands unreviewed and unattributed between pinned SHAs.
   Both reviews modeled "two developers" as the concurrency threat and missed the one that happens
   on day one: *one* developer who doesn't always go through the front door.
2. **The disjoint-domain premise is false for shared files.** Both reviews attacked the hook's
   *enforcement* (exit codes, Bash bypass); neither attacked the claim being enforced — that a
   codebase partitions into disjoint frontend/backend/ai/data write globs. It doesn't:
   `package.json`, lockfiles, shared type/schema files, route registries, and env config are
   legitimately written by multiple specialists. Either the globs overlap (parallel-safety claim
   void even with a perfect hook) or they don't (routine tasks BLOCK on files nobody may touch).
   "Eng-lead routing guarantees two specialists never own the same file" is asserted at the roster
   level and impossible at the file level. This is the foundation under §2.3, §4.2, and spike 0b,
   and neither reviewer entered it.
3. **Cross-feature concurrency.** §10.5 explicitly promises "a BLOCKED feature does not silently
   block the whole project — independent features remain workable," which means two in-flight
   features: two branches diverging from main with committed expertise files,
   `STATE.md ## Current` (singular by construction), logs, and PLAN.md task statuses guaranteed to
   conflict at merge. Mutator serialization is per-crew, not cross-feature. Both reviews audited
   one feature's lifecycle; nobody ran two.
4. **The reviews' own verification layer** — demonstrated rather than hypothesized: the reviewer
   whose mandate was "distrust every claim until checked against current documentation" reported
   documented env vars as fabricated (§0). Any fix process that "re-verifies all claims" needs
   quotes and version markers attached, or it launders the same failure mode.

---

## 4. Ordered fix list — before any code is written

1. **Re-verify every platform claim with URL + quote + min-version, and pin the CLI version**
   (≥ 2.1.217) in BUILD 0a. Fix the inverted "if missing" row (default depth is 3 — a missing
   setting means workers *can* delegate); delete `delete: false` or replace it with something real
   (a PreToolUse hook on destructive Bash patterns); treat DEC-81/82 *and* both reviews' claims as
   inputs to re-cite, not facts.
2. **Settle the org-shape question with data, not argument:** run 2–3 real features as
   null-hypothesis-plus-artifacts (BRIEF/SC, qa matrix gate, pinned-SHA review, UAT script as
   plain-session skills) with `/cost` logged, before writing any of the 15 agent files. The
   cheapest experiment on the table; it decides whether items 4–7 apply to a 15-agent org or a
   4-artifact skill set.
3. **Resolve write-safety honestly:** confront the Bash bypass (all eight doers) and the
   shared-file domain overlap together. The likely honest answer is CTO's — serialization +
   `isolation: worktree` is the mechanism, the hook is a guardrail — plus an explicit shared-paths
   policy (who may touch `package.json`, schemas, config).
4. **Ship the two deterministic validators** both reviews demand: `check-state.sh` (state
   invariants — `review_sha` set before validator dispatch, `cycles_used` ≥ FAIL count,
   approval-reset-after-replan) and a ~40-line DIGEST schema validator routing drift into the
   existing `BLOCKED (contract violation)` path.
5. **Add cost accounting as a design axis:** tokens/spawns logged per run in `state.yaml`,
   per-crew budgets alongside `max_cycles`, a cost line in the CEO briefing, cheaper model tiers as
   the doer/reviewer default — and rewrite DEC-68 and DEC-71 contingent on the numbers from item 2.
6. **Close the expertise governance holes:** provenance (run ID) + decay/re-confirmation on every
   entry; scheduled curation for all 15 agents, not just leads; global-tier writes human-gated or
   the tier deleted; and fix the S-5 spec bug (doers' expertise paths are missing from the manifest
   domains — the hook as written blocks the self-apply mechanism §5.3 depends on).
7. **Batch human touchpoints to two:** one planning checkpoint (PLAN + prototype + accumulated
   questions) and one ship checkpoint (briefing + UAT + merge), per CTO F4 — and restate the core
   value claim as "no *mid-stage* supervision."
8. **Write the missing operating-constraints section:** single-operator by design; out-of-band
   human edits get a legal path (hand edits land as attributed commits the state check reconciles;
   the dirty-tree whitelist covers them); one feature in flight at a time until cross-feature merge
   semantics exist.
9. **Recover the five lost GAPs** from session history before declaring the design settled (both
   reviews; the document's own instruction), and fix the small ambiguities while in there:
   multi-squad run-dir ownership (§13 vs §11.4) and the dirty-tree whitelist definition.

---

**Process note — the strongest single takeaway isn't any finding:** three parties (the design,
then a review built to catch the design's doc errors) each produced confident, wrong platform
claims in the same week. Whatever re-verification pass runs for item 1, make
"quote + URL + version marker or it doesn't count" the rule.
