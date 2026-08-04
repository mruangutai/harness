# Performance review — the agent workflow, speed without quality loss — 2026-08-04

Two independent read-only reviewers, non-overlapping scopes: one mined the run records
(`.harness/logs/`, `feature.yaml`, run digests), one read the loop's design (commands, skills,
agents, hooks). Ranked here best-first by **performance gain per unit of quality risk**.

The constraint was ZERO quality degradation. Where a change carries a real quality cost it is
named in the row rather than hidden — the judgement is the user's, not the reviewers'.

## Baseline (mechanically verified — `yaml.safe_load` over all six `feature.yaml`)

| Feature | Runs | Cycles | Cost | Budget |
|---|---|---|---|---|
| FEAT-01 | 1 | 1 | $0 | $40 |
| FEAT-02 | 4 | 4 | $49 | $40 |
| FEAT-03 | **19** | 6 | $358 | $120 |
| FEAT-04 | **15** | 6 | $324 | $120 |
| FEAT-05 | 6 | 3 | $240.82 | $120 |

Cost figures are snapshot-delta approximations and every `feature.yaml` says so; FEAT-05's is
additionally called a stale FLOOR. Order-of-magnitude comparisons hold; adjacent-run rankings
do not. **Nothing counts or budgets runs** — only cycles, and DEC-157 counts cycles as rework
only, which is why 19-runs-against-6-cycles never tripped anything.

## The stack rank

| # | Change | Perf | Quality cost | Risk | Effort |
|---|---|---|---|---|---|
| 1 | **Batch the user's rulings into one gate** — hold product-fix dispatches until all open questions are answered as a set | **High** | **Low** | Low | Low |
| 2 | **Dev runs its task's own `verify:` before returning** | **High** | **Low** | **Low** | **Low** |
| 3 | **Route-resolve every PLAN task at plan time** against `team-config.yaml`; unrouteable tasks become declared MAIN-SESSION steps | **High** | **None found** | Low–Med | Med |
| 4 | **Run qa phase 1 concurrently with the build** (it has no source access by design) | **High** | **Low** (arguably a gain) | Med | Med |
| 5 | **Probe bounded environment questions immediately** instead of inferring them | Med | **Negative** (quality improves) | Low | Low |
| 6 | **Collapse the close-out rounds** — dispatch the three leads concurrently, merge ship-refresh with distillation, drop the report-only half | Med | **Med** | Low | Low |
| 7 | **Chase the 11–21× PreToolUse hook-fire multiplier** (dedup only, never "fire less") | Med | None if dedup; **Med** if it becomes weaker enforcement | **High** (DEC-174 carve-out) | Med |
| 8 | **Drop `harness-team` from the orchestrator's preload** — flat mode is dead | Low wall-clock / Med cost | Low | Low–Med | Low |
| 9 | **Split `harness-expertise`'s distillation half** out of the universal preload | Low wall-clock / Med cost | Low–Med | Med | Low |
| 10 | **Count and budget runs, not just cycles** — observability so rows 1 and 6 get noticed live | Low (indirect) | None | Low | Low |
| 11 | **Fix `SPEC.md:1980`'s review row** — it shows a qa step `review.yaml` does not have | n/a (correctness) | n/a | Low | Low |
| 12 | **Give a held orchestrator read-only work** instead of idling it | Low | None | Low | Low |

## The evidence, row by row

### 1 — Batch the user's rulings (perf High / qual Low / risk Low / effort Low)

FEAT-03 runs 02–08 are seven serialized runs costing **$95** (`FEAT-03/feature.yaml:20-47`) — a
product-fix → eng-re-verify ping-pong repeated three times. The discriminator: **all three eng
re-verifications returned PASS with zero must_fix** (`:30`, `:38`, `:46`). No cycle was triggered
by a reviewer finding anything. Each round was triggered by a new user ruling arriving separately
(`.harness/logs/2026-07-31.md:4`, `:5`). Wall clock ~5 hours in the plan phase alone (`:2` 10:15
escalate → `:6` 15:08 approved).

### 2 — Run the task's `verify:` (perf High / qual Low / risk Low / effort Low)

Every PLAN task carries a mandatory `verify:` command returning pass/fail in under 60s
(`templates/PLAN.md:47`, `harness-spec-driven/SKILL.md:17`). **Verified absent from every rule
surface that reaches the four eng specialists** — `grep -l 'verify:'` over `harness-digest-dev/`,
`harness-tdd-enforcement/`, `harness-handoff/` and the four dev agent files returns nothing. The
cheapest gate in the system is authored and then run by nobody; the first thing catching a
task-level miss is the qa gate after the whole build segment, and that miss is a `loop_back` —
a cycle under DEC-157. DEC-105 prices two fix cycles at +10 spawns of 34. Fix is one line in the
one canonical copy (DEC-126).

### 3 — Route-resolve at plan time (perf High / qual None / risk Low–Med / effort Med)

Named as a **third recurrence** at `FEAT-05/feature.yaml:78-81`: dev-ops is granted neither
`.gitignore` nor `templates/**` nor `harness-init/SKILL.md`, so PLAN tasks became main-session
steps inside the build spine. FEAT-03 Q13 and FEAT-04 T-09/T-10 are the same wall. It cost a real
ESCALATE: FEAT-04 run 10, $16, the lead's own words — *"The ESCALATE is my dispatch error… I gave
documentor a fourth sub-step that its domain does not permit"*
(`runs/2026-08-02-10-product/digest.md:89-91`). FEAT-06 pre-computed it by hand and got a clean
answer before the build opened (`FEAT-06/feature.yaml:36-38`) — proof the fix works and that it is
currently manual.

### 4 — qa phase 1 concurrent with the build (perf High / qual Low / risk Med / effort Med)

`SPEC.md:463` defines qa phase 1 as deriving expected coverage from BRIEF/PLAN **with no source
access**, for anti-bias reasons. `SPEC.md:1978` still sequences it strictly after the entire build
segment. BRIEF and PLAN are both `approved` before a ship orchestrator may start
(`harness/SKILL.md:25-27`), so phase 1's whole input set is frozen before the first dev spawns.
Concurrent lead dispatch is already proven (`harness/SKILL.md:240` spawns all three leads in one
turn); DEC-118 constrains *reach*, not concurrency. Quality is arguably a small **gain** —
phase 1's expectations become a durable artifact phase 2 cannot silently revise. Honest costs: one
extra spawn, and DEC-159's build-exit predicate needs a companion clause since build and validate
would overlap.

### 5 — Probe, don't infer (perf Med / qual Negative / risk Low / effort Low)

One bounded question — which copy of a script a hook executes in a worktree — consumed a working
day and produced **two retracted claims to the user** (`2026-08-03.md:6` asserts, `:14` retracts,
`:17` retracts the orchestrator's identical over-claim, `:23` finally measures it and *disproves*
the original). Five consequences flipped at once when it was settled. The log's own verdict:
*"A file-difference check cannot answer a resolution question, and the probe that could took five
minutes."* Same class recurs at `:27`.

### 6 — Collapse the close-out (perf Med / qual Med / risk Low / effort Low)

Up to three sequential round trips through the lead tier after all substantive work is done:
ship-refresh (`harness/SKILL.md:159-170`), feature-close distillation (`:172-194`), CEO briefing
(`:235-241`). FEAT-03's close-out was six sequential runs; 14/15/16 were one domain report +
distillation each at $49 with no stated cross-domain dependency (`FEAT-03/feature.yaml:70-81`).
The orchestrator has already killed an equivalent round on judgement grounds — FEAT-04 skipped the
three-lead report round because *"Three lead spawns at ~20 USD each to re-narrate digests I hold is
spend with nothing to surface it"* (`FEAT-04/feature.yaml:161-165`).

**Two constraints, both real.** Do NOT collapse all three: distillation feeds the briefing's
curation block (`SPEC.md:881-886`, DEC-69) — two rounds, not one. And a lead given two jobs in one
dispatch does both less carefully; distillation is explicitly a *cold, stepping-back* job
(DEC-145) and pairing it with map-section routing pulls it back toward hot. Keep FEAT-04's
disclosure requirement: the round exists so the orchestrator is not narrating work it did not see.

### 7 — The hook-fire multiplier (perf Med / qual None-if-dedup / risk High / effort Med)

Two independent probes on 2026-08-03 measured **11 fires for one reported write**
(`2026-08-03.md:24`) and **21 fires for one write** (`:27` — "multiplier is not constant, not
chased"). Per-fire latency is already halved by FEAT-05: 80.63ms → 43.5ms, *"46% FASTER than the
pre-feature original while doing strictly more work"* (`:26`). At 21 × 43.5ms that is still ~0.9s
per tool call, paid by every agent on every write. **The fix must be deduplication only** — "fire
the hook less often" weakens enforcement and is disqualified. Squarely inside the DEC-174
carve-out: direct execution, human-read diff, no team run.

### 8 — Drop `harness-team` from the orchestrator (perf Low wall-clock, Med cost)

`harness-orchestrator.md:8-12` preloads `harness-team` — **verified 18,026 bytes**, ~4.5k tokens,
its largest preload after the playbook. Justified only by flat mode, and **flat mode is dead**:
`harness/SKILL.md:32-35` and `:260` forbid the orchestrator→member path with "no exceptions", and
`SPEC.md:1300` states outright *"Verified (DEC-100, DEC-102): hierarchical works. The flat fallback
is not needed."* Orchestrator preload is ~54.6KB ≈ 13.7k tokens; this is a third of it, paid 3–4×
per feature under DEC-159. **Two required riders:** move the ORCHESTRATOR-ONLY `cost-report.py`
paragraph (`harness-team/SKILL.md:200-213`) into `harness/SKILL.md` or INV-11's metering
instruction is lost; and delete the flat-mode sentences at `harness-team/SKILL.md:12-14`,
`SPEC.md:158`, `:1387`, `:1936`.

### 9 — Split `harness-expertise` (perf Low wall-clock, Med cost / risk Med)

Preloaded by all 16 agents at every spawn (`SPEC.md:279-282`), 125 lines / 6,816 bytes. Lines
51–113 — about half — govern distillation only, which per DEC-145 happens **once per agent per
feature**. ~850 tokens × 34 spawns ≈ 29k tokens/feature. The de-preload precedent is already in
the tree: DEC-158 did exactly this to `harness-systematic-debugging`
(`harness/SKILL.md:113-115`). **Quality risk is real** — DEC-125 is cited four times in this
codebase for things that "relied on being pointed at" and failed silently; the mitigation is that
`check-expertise.sh` catches format violations mechanically.

### 11 — `SPEC.md:1980` vs `review.yaml`

**Verified.** SPEC's review row reads `{code ∥ qa ∥ security ∥ ui} → validator-lead assesses`.
The shipped `.claude/skills/harness/teams/review.yaml` has exactly three steps — `code` (:22),
`security` (:36), `ui` (:49) — and no qa. This is a propagation miss `check-docs.sh` did not catch
(its registry is DECISIONS.md, literal-string class only, DEC-104). **It is also direct evidence
for the in-flight issue #8**, and evidence that qa alongside the panel was once the intent.

## Examined and REJECTED — with the reason

- **Cutting the goal-check or review passes.** DISQUALIFIED by this repo's own evidence:
  *"The GOAL-CHECK found what no code review did… because it asked 'does this do what you
  promised' rather than 'is this code correct'"* (`logs/2026-08-04.md:4`), corroborated at
  `notes/handoff-validate.md` and `notes/research-FEAT-05-goal-check-c1.md:1-4`, where the second
  goal-check cycle caught a reinterpretation of a signed constraint invented in the commit that
  needed it.
- **Cutting the lead tier for single-task work.** DEC-105 measures intermediation at 29% of cost,
  but DEC-71 already priced this exact trade — "Tradeoff accepted: one extra spawn for trivial
  single-task work" — for routing, assessment, and no unassessed work reaching STATE.md.
- **Parallelizing dev tasks.** PLAN tasks carry `files:` but no `depends_on`, so nothing declares
  independence; every dev task is `mutates_repo: true` and DEC-85 makes serialization — not the
  domain hook — the actual write-safety mechanism, because `check-domain.sh` cannot see `Bash`
  writes. Real parallelism costs a worktree per agent.
- **Reversing DEC-159's per-phase orchestrators.** Per-phase relay strictly increases wall-clock
  (a fresh ~10k preload plus a 30–50k working set per successor) but was traded knowingly against
  measured cost — 258–310k cache-read tokens/turn, growing with the square of session length
  (DEC-148).
- **Lowering `effort: high` on the judging tier.** DEC-152 pins effort per tier. Trades quality.
- **Running documentor concurrently with the panel.** Docs depend on final code; any panel FAIL
  loops back to a dev and makes them stale.

## What the rework data actually says

Member output being rejected is **not** where wall-clock goes. Exactly one hard rejection across
five features (FEAT-04 run 10), and the lead attributed it to its own dispatch error, not the
member; FEAT-03 records 3 send-backs across 19 runs. The two real sinks are **the user gate**
(row 1) and **the routing wall** (row 3).

The dominant rework class is self-inflicted and honestly logged: *"three of my fix rounds
introduced a new high while closing an old one, and six of the feature's non-discriminating tests
were mine… Every real defect was caught by proving RED before trusting GREEN"*
(`logs/2026-08-04.md:5`), corroborated three times in-flight on 2026-08-03 (`:25`, `:26`, `:30`).
The countermeasure is already working. No change proposed.

## The one big unexplored lever — NOT proposed, flagged only

FEAT-05's build produced **no member digests at all** — it ran main-session under the DEC-174
carve-out (`notes/handoff-build.md`) — and shipped 14/14 SCs in **3 cycles, the lowest count of
the three completed features**. The team layer was bypassed and the outcome did not degrade.
One data point, on the one feature that is unusual by construction (it modifies its own
enforcement layer). Nothing is proposed from it. It is recorded because it is the largest
unexplored speedup in the record and dismissing it silently would be worse than naming it.

## Caveats on the numbers above

- Every cost figure is a snapshot-delta approximation; each `feature.yaml` says so.
- Wall-clock exists only in `.harness/logs/*.md` and many entries read `NN:xx`. Hour-level
  durations are floor estimates, not instrumented timings.
- FEAT-05 has **no `runs/` directory** — all six run dirs pruned — so the feature with the longest
  review arc is the one whose digests cannot be cited. Its review-arc figures are sourced to
  `logs/2026-08-04.md:4` only.
