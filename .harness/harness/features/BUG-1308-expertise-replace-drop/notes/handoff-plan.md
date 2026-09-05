# Handoff — BUG-1308, plan → build — written at 43bfe19, seq-1

## Next

Take the operator's ONE batched signature review over `plan.yaml` and `BRIEF.md ## Approval`
(DEC-176): present all seven `panel.findings`, take every ruling in that single pass, then either
`plan-merge.py sign-approval` — with `--overrule PF-ID:<reason>` for each finding whose risk the
operator accepts — or dispatch pm ONCE with a consolidated revision covering the accepted change
requests. The gating one is `PF-f4d258f365f54f04d9cc976baf0ad981` (high): T-01 Step D. Do not
dispatch a pre-signature fix for it. Build entry afterwards is T-01 (`plan.yaml` T-01,
`depends_on: []`, the only dependency-free task) to `harness-eng-lead`.

## Trust

- BRIEF and plan both read `approval.status: pending`, by design — `plan.yaml` `approval`, `BRIEF.md ## Approval` — verified-at 43bfe19, read by me from disk
- `panel` carries `last_run: 2026-09-05-plan-panel-c1-validator`, `cycle: 1`, both readers `ran`, 7 findings all `disposition: open`, severities 1 high / 3 med / 2 low / 1 info — `plan.yaml` `panel` — verified-at 43bfe19, loaded and counted by me
- `lanes.resolved_at` is `c369fb1` and every lane row reproduces from `check-domain.sh --resolve` — I ran the resolver on expertise-merge.py, harness_merge.py, check-expertise.sh, tests/integration/test-expertise-merge.py and harness-distill/SKILL.md — verified-at 43bfe19
- `.claude/skills/harness-distill/SKILL.md` resolves to NOBODY, which is why T-03 is `main-session-direct` — same resolver run — verified-at 43bfe19
- `.harness/harness/docs/SPEC.md` resolves to `harness-documentor`; repo-root `docs/SPEC.md` does not exist — I re-ran the resolver after pm's Q2 — verified-at 43bfe19
- DEC-216 is the next free number; DEC-66, DEC-199, DEC-213 exist and are cited correctly — `DECISIONS-INDEX.md`, highest entry DEC-215 — verified-at 43bfe19
- The issue's premise holds: `expertise-merge.py` exposes only `apply`, and `compute_union` appends only — `.claude/skills/harness/bin/expertise-merge.py` — verified-at 43bfe19, read by me
- Goal-check c1 returns PASS with all six cycle-0 findings closed in the artifacts — `notes/research-BUG-1308-expertise-replace-drop-goalcheck-plan-c1.md` — UNVERIFIED by me beyond spot-checking T-02 traces and SC-11's presence
- The seven PF- ids are reproducible as `PF-` + first 32 hex of `sha256(reader + "\n" + whitespace-collapsed lowercased summary)` — panel-record digest — UNVERIFIED by me

## Dead ends

- Do not dispatch a pre-signature fix cycle for any panel finding — DEC-176 batches every change request into one revision after the operator has read to exhaustion — `DECISIONS.md` DEC-176 — verified-at 43bfe19
- Do not accept the high finding's risk at any tier below the operator; only `sign-approval --overrule` records acceptance — `harness` skill, plan-phase panel section — source: doctrine
- Do not settle the `merge`-verb versus optional-`section` vocabulary question inside a squad; the panel states it cannot — `runs/2026-09-05-plan-panel-c1-validator/digest.md` `adequacy_notes` — verified-at 43bfe19
- Do not run any `gh-sync.py` subcommand for this phase; the plan station is written by `board-station.py` at the `/harness-plan` door and the plan phase is one the main session holds — `references/github-mirror.md` station table — verified-at 43bfe19
- Do not re-litigate D-10, D-12 or T-02's `change_type: scaffolding`; the operator-delegated Advisor ruled on all three — `notes/research-BUG-1308-expertise-replace-drop-advisor-c1.md`, D-14 — verified-at 43bfe19

## Working set

- `.harness/harness/features/BUG-1308-expertise-replace-drop/plan.yaml` — 14 decisions, 4 tasks, the `panel` key
- `.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md` — REQ-01..09, SC-01..11
- `.harness/harness/features/BUG-1308-expertise-replace-drop/runs/2026-09-05-plan-panel-c1-validator/digest.md` — the seven findings with anchors and the three Advisor answers
- `.harness/harness/features/BUG-1308-expertise-replace-drop/notes/research-BUG-1308-expertise-replace-drop-advisor-c1.md` — what A1/A2/A3 settle
- `.harness/harness/features/BUG-1308-expertise-replace-drop/notes/review-harness-code-reviewer-planpanel-c1.md` — the high finding's own anchors

## Done when

Scope: Operator signature ruling on the plan-phase approval artifacts
Authority: approval:.claude/worktrees/harness/BUG-1308-expertise-replace-drop/.harness/harness/features/BUG-1308-expertise-replace-drop/BRIEF.md#Approval
