# BRIEF — FEAT-59 Proportional flow

## Problem

The plan-to-ship loop costs the same whether the change is five lines or fifteen hundred, and the
cost has grown as gates were added. Measured on the owner root on 2026-09-11 from `feature.json`
ledgers and run artifacts:

- Median runs per feature: 10–16 for FEAT-01 through FEAT-50; **40** for FEAT-51 through FEAT-56.
  Median rework cycles: 4.5–8, then **13**. Shipped diff sizes did not grow to match (FEAT-54
  ≈1,100 lines, FEAT-43 ≈1,700).
- BUG-285 (a ~130-line fix): 19 runs and ~6h20m of dispatch time before a line of code, 9 of 10
  cycles consumed, 5 plan-panel cycles, 5 goal-checks, 3 runs that only transcribed findings, ~57,000
  words of planning artifacts. The operator stopped it; the fix shipped by direct dispatch and the
  receipt records that the plan was "left untouched and NOT followed". 5 of 8 re-cycle triggers
  were about document form, not code.
- FEAT-54 (51 runs, 22 cycles): 23 runs before production code, driven by `plan-merge.py` write
  mechanics (`apply` refuses any changed field, `lanes:` has no write route, `set-panel` re-wraps
  findings). The first build dispatch BLOCKED on five plan paths the layout gate forbids —
  "four goal-check cycles and three panel cycles read it and none noticed; the first build dispatch
  found it in one member spawn" (`observations/harness-orchestrator.md`). Three of six review cycles
  FAILed on SC-04, a repository-wide `check-state.sh` assertion red on other features' debris.
- FEAT-43 (49 runs, 29 cycles): 12 of 18 rework triggers were genuine defects, found one per cycle
  across six separate "final" reviews because readers run as sequential squad segments. Each defect
  cost ~4 runs plus a human authorization; `max_total_cycles` was raised seven times and always
  followed `cycles_used`, never led. No mechanical check enforces it.

The underlying mechanism: the reviewed artifact in the plan phase is a document, every edit voids
every proof recorded about it, every re-proof is a cold three-layer dispatch (~21 min), and nothing
in the loop scales with the size of the change. In the validate phase, readers are serialized so
findings arrive one cycle apart, and each cycle needs a human ruling.

## Done when — by perspective

**operator** — I trust the harness to judge, on its own: how much process a change deserves,
whether a finding changes shipped code or only a document, when to keep fixing and when to stop,
and whether a successor should continue. I sign once per feature and rule once on rework. I
verify that trust after the fact, from a record that states each judgement and its reason in one
line — never by ruling in-flight. When the harness is genuinely unsure, it asks me one question
with its recommendation; it never resolves uncertainty by adding process. A known-cause bug
reaches a signed intake in one run and ships in about four.

**code maintainer** — One statement of "done" per feature, in one place, which the goal-check
grades and the handoff cites. No run exists whose only work is to copy one file into another.
Plans anchor to symbols and survive `main` moving. The tools pm drives to write a plan do not
require a `/tmp` driver to be usable.

**reader (reviewer / qa / panel)** — I see the whole tree state once, alongside the other readers,
and my findings carry a kind that says whether they re-gate. I am never asked to find by reading
what a script can find by running.

**orchestrator** — I dispatch one run per phase seam, not one per squad hop. I inherit the
feature's cumulative spend across a succession. My budget is one I can actually exhaust.

## KPIs

Headline, trust, and guardrail; the rest are diagnostics. All measured from `feature.json`.

| KPI | Baseline | Target |
|---|---|---|
| **Runs to ship, median** | FEAT-51–56: 40; BUG flows: 12 | feature ≤ 20; bug ≤ 6 |
| **Judgement overrule rate** (`judgements[]` entries the operator overrules) | none — no ledger exists | ≤ 10% over the first 5 features |
| **Escaped-defect rate** (BUG flows opened against features shipped under the new flow) — guardrail | FEAT-41–56 rate | no increase per feature |
| Operator contacts per feature | FEAT-43: 13 rulings | 2 + at most 1 new-class question |
| Runs per substantive finding in validate | ~4 plus a human wait | ≤ 1.5 |
| Zero-value runs (transcription-only, form-only re-gate) | 3/19 (BUG-285), ~8/51 (FEAT-54) | 0 |
| Plan-phase wall-clock, grilling end → signature | BUG-285 6h20m | patch ≤ 30 min; plan ≤ 90 min |
| Tokens per feature | none — SC-18 creates it | first 5 features set the baseline |

The guardrail is asymmetric on purpose: the headline can halve and the feature still fails if
defects start escaping, because that would mean judgement was removed rather than procedure. The
trust number needs volume; it is read at five features, not one.

## Success criteria

Each SC names the perspective it discharges. `verify:` is one of `automated` (with `evidence:`
kind), `inspection`, or `uat`.

**Mission proportionality**

- SC-01 (operator): `harness-grilling` ends with the harness's own mission judgement, `patch` or
  `plan`, with a one-line reason, written to the grilling artifact; the operator confirms or
  overrides in the same dialog. `/harness-plan` refuses to start without a recorded mission.
  verify: automated  evidence: python
- SC-02 (operator): a `patch` mission produces an intake note (Problem, Done-when by perspective,
  SCs, ≤ 120 lines) and no `plan.yaml`; after signature it runs exactly build → qa → review → ship,
  with no pre-build panel. Demonstrated on one real bug flow end-to-end.
  verify: automated  evidence: integration
- SC-03 (orchestrator): a plan-panel finding of kind `proportionality` that no reader opposes
  causes the orchestrator to downgrade the mission to `patch` itself, record the reason, and
  return the intake note `pending`; the operator sees the downgrade at signature, not as a
  question. A re-cycle on a proportionality finding is a defect.
  verify: automated  evidence: python

**Plan phase collapsed**

- SC-04 (orchestrator): a `plan` mission for a feature with no substantive panel finding completes
  in one product-lead run: draft → parallel readers (scope, should-not-exist, architecture, design
  if UI) → pm applies findings → panel recorded → goal-check by perspective → return `pending`.
  verify: automated  evidence: integration
- SC-05 (code maintainer): `plan-merge.py record-panel --digest <path>` writes the `panel:` key
  from a lead digest; no run in any feature after this ships has a transcription-only purpose.
  verify: automated  evidence: unit
- SC-06 (reader): every panel and review finding carries `kind: substance | form`; a `form`
  finding is fixed in the same run and never triggers a re-read; a `substance` finding re-gates
  only the tasks it names. `validate-digest.py` rejects a finding without `kind`.
  verify: automated  evidence: unit
- SC-07 (code maintainer): plan task anchors are `file:symbol` or `file` + quoted content; a
  `plan-merge.py check` at plan exit resolves every anchor, every `files:` path against the layout
  gate, and every `execution_agent` route; a stale anchor at build entry is re-resolved by the
  builder and is not a FAIL. Line-number anchors are refused at write.
  verify: automated  evidence: unit
- SC-08 (code maintainer): any `plan-merge.py` verb that changes the task set sets
  `approval.status: pending`; only `sign-approval` writes `approved`. The `apply` verb accepts a
  changed field on an existing task id; `lanes:` has a write route; `set-panel` preserves byte
  identity of carried findings.
  verify: automated  evidence: unit
- SC-09 (operator): the goal-check runs once at plan exit and once at validate exit, graded per
  perspective; there is no per-cycle goal-check.
  verify: inspection

**One statement of done**

- SC-10 (code maintainer): the BRIEF template carries `## Done when — by perspective` and SCs
  tagged with a perspective; `REQ-NN` and the free-text `## Goal` are removed from the template.
  `check-state.sh` refuses a new BRIEF with a perspective that no SC discharges, or an SC with no
  perspective. Pre-existing BRIEFs are not graded.
  verify: automated  evidence: python
- SC-11 (code maintainer): the handoff `## Done when` section is a pointer to the BRIEF's
  perspective block, not a re-derived scope statement; INV-17 accepts that form.
  verify: automated  evidence: unit
- SC-12 (reader): the plan-panel `scope` reader hunts orphan SCs (no task traces) instead of orphan
  REQs, with the same severity contract.
  verify: inspection

**Validate phase batched**

- SC-13 (reader): qa, code-reviewer, security-reviewer, ui-reviewer (if UI) and pm's goal-check run
  in parallel over one pinned `review_sha` in one validator-lead run with one consolidated must-fix
  list. No feature after this ships has two consecutive reader runs over the same sha.
  verify: automated  evidence: integration
- SC-14 (orchestrator): a fix cycle is one validator-lead run hosting the owning dev as a member
  and the readers re-verifying against the new sha in the same run; author and reviewer remain
  distinct personas.
  verify: automated  evidence: integration
- SC-15 (operator): at signature the operator records one rework ruling in `feature.json`
  (`rework: {rounds: N, wall_clock_minutes: M}`); the orchestrator loops inside it without asking
  and returns `awaiting_user` only on a new finding class (scope change, emergent SC) or budget
  exhaustion. `check-state.sh` enforces `cycles_used <= max_total_cycles` and refuses a raise
  without a `decision:` record in `feature.json` (DEC-157).
  verify: automated  evidence: python
- SC-16 (code maintainer): an SC whose `verify:` command asserts repository-wide state outside the
  union of the feature's `files:` is refused at BRIEF write; repository hygiene is a merge-time
  check, not a feature criterion.
  verify: automated  evidence: python
- SC-17 (reader): the qa gate requires, per `automated` SC, a demonstrated failing state before the
  fix (the test's fail-first evidence path in the qa digest); a green suite with no fail-first
  evidence is `FAIL`, not `PASS`.
  verify: automated  evidence: unit

**Spend visible across succession**

- SC-18 (orchestrator): every `runs[]` entry in `feature.json` carries `started_at`, `ended_at`,
  and `tokens` measured from the OMP transcript on disk (the `context-watch.py` method), never
  estimated; the feature-level sum is emitted in every orchestrator return.
  verify: automated  evidence: unit
- SC-19 (operator): a feature exceeding `budgets.plan_phase_warn_minutes` before build entry, or
  `rework.wall_clock_minutes` after, surfaces one advisory line in the return naming spend, budget
  and phase. Advisory, never blocking.
  verify: automated  evidence: python
- SC-20 (orchestrator): a successor orchestrator, on its first wake, decides continue / downgrade /
  stop from the feature's cumulative spend and the handoff's `## Next`, records the decision and
  reason, and reports it in its first return. It does not ask. The operator can overrule from the
  return.
  verify: automated  evidence: python

**Judgement is recorded, and uncertainty asks once**

- SC-21 (operator): every autonomous judgement — mission choice, finding `kind`, re-gate or not,
  continue or stop, succession — is appended to `feature.json` `judgements[]` as
  `{at, by, decision, reason}` with a one-line reason. `check-state.sh` refuses a mission change,
  re-gate, or succession with no matching entry. A ledger the operator can audit is the whole
  basis of trust; an unrecorded judgement is indistinguishable from an accident.
  verify: automated  evidence: python
- SC-22 (operator): when a reader or the orchestrator cannot classify a finding's `kind`, a
  mission's proportionality, or whether a finding is a new class, it returns `awaiting_user` with
  exactly one question and its own recommendation. It never resolves the doubt by choosing the
  heavier route (re-panel, re-cycle, `plan` over `patch`) by default.
  verify: inspection

**Acceptance — two live flows**

- SC-23 (operator): one real bug runs the `patch` lane end-to-end — grilling judgement, intake,
  signature, build, qa, review, ship — on the new tools. Its `feature.json` shows ≤ 6 runs, a full
  `judgements[]` ledger, and per-run spend. This is SC-02's live evidence.
  verify: automated  evidence: integration
- SC-24 (operator): one real feature runs the `plan` lane end-to-end — one plan run, signature with
  one rework ruling, build, batched validate rounds, ship — on the new tools. Its `feature.json`
  shows one plan-phase run, no transcription-only run, no two consecutive reader runs over one sha,
  no `awaiting_user` return except on a new finding class, and total runs at or below half the
  FEAT-51–56 median of 40. This is SC-04, SC-13 and SC-14's live evidence.
  verify: automated  evidence: integration

Neither flow is a fixture; both are the next real bug and the next real feature after step 3
lands. This brief is not done until both have shipped.

## Verification gaps

- `integration` kind runs the real dispatch chain under OMP; SC-02, SC-04, SC-13, SC-14 need one
  live flow each. If `test_kinds.integration.cmd` is null at build entry, those four rest on the
  `python` kind's replayed fixtures and the gap is recorded here and in the ship briefing.
- SC-22 is graded by inspection of the skill and playbook text plus the judgement ledgers of the
  first two features run after ship; a default-to-heavier route found there fails it.

## Constraints

Decisions this feature **amends** (each becomes a new entry; the old one is superseded, not
marked stale — DEC-188):

- **DEC-118** (a lead cannot dispatch another squad): retained for the build segment. For the plan
  run and the validate/fix run, one lead hosts personas from more than one squad as read-only or
  fix members. The independence that matters — reviewer distinct from author — is preserved at the
  persona level.
- **DEC-139** (no ungated bug lane): the `patch` mission is gated at qa and review on the diff, not
  at plan on a document.
- **DEC-176** (batched signature review): extended — the batched review is also the one rework
  ruling (SC-15).
- **DEC-178** (cost tracking removed): amended — wall-clock and tokens are recorded per run as
  measured signal, never a gate (SC-18, SC-19). DEC-134's "informational, flagged in headline"
  shape is the model.
- **FEAT-45 / DEC-207** (panel on every plan, no threshold): struck for `patch`; retained for
  `plan` with the `proportionality` downgrade route (SC-03).
- **DEC-132 / DEC-133** (pm authors SCs; feature id shape): unchanged. pm still authors; the
  perspective block is authored from the grilling artifact and signed with the SCs.
- **D-03 of the plan-feature team** (pm alone writes `plan.yaml`): amended by one key — the
  orchestrator may run `record-panel`, as it already runs `set-task-station`.

Decisions this feature **relies on** (supply, not block): DEC-120 (only the main session signs —
untouched; SC-08 gives `pending` a downward route only), DEC-150 (read by pointer), DEC-157 (raises
are recorded user decisions — SC-15 finally enforces it), DEC-174, DEC-188, DEC-198/201 (advisory
thresholds, seam-based handoff), DEC-204 (digest is a claim until disk confirms).

**DEC-174 routing.** SC-05, SC-06, SC-07, SC-08, SC-10, SC-11, SC-15, SC-16, SC-17, SC-18, SC-19
change `plan-merge.py`, `validate-digest.py`, `check-state.sh`, `check-domain.sh`, the qa gate, or
their tests. Those are main-session-direct work with explicit tests and human diff review; they do
not go through the enforcement path they change. The remaining SCs (skills, templates, team YAML,
agent prompts, decision text) go through the normal path. The plan sequences the direct batch
after the signed brief and before the normal-path build, so the normal path runs on the new tools.

## Out of scope

- Model or provider selection; nothing here touches `.omp/providers/*.yml` or role aliases.
- The build team's internal shape (eng-lead routing by `consult-when`) — unchanged.
- Retroactive grading of existing BRIEFs, plans or handoff notes against the new shapes.
- Feature-close distillation (DEC-145) — unchanged.
- Fixing the specific defects the three audited features surfaced in their own code.

## Approval

status: approved
date: 2026-09-11
by: operator, main session (direct work under DEC-174; two-flow acceptance SC-23/SC-24)
