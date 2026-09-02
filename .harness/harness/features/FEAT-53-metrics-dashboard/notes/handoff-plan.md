# Handoff — FEAT-53-metrics-dashboard, plan → build — written at ac96e77e, seq-1

## Next

**Do nothing until the main session signs both artifacts.** The plan phase ends at a user gate:
`plan.yaml` `approval:` and `BRIEF.md` `## Approval` both read `pending`, and only the main session
signs — including BRIEF's `date`, which is load-bearing for the cycle-time KPI this very feature
builds (D-14). Once both read `approved`, the first build dispatch is the eng segment of the `build`
team to `harness-eng-lead` with the tasks that have no `depends_on` — **T-01** (grant
harness-frontend-dev the client subtree in team-config.yaml) and **T-06** (create
`bin/brief_approval.py`, `kpi.resolve_window`, and fixture project-a) — T-06 being the one task with
no dependencies and the authority half the plan calls. `T-20` and `T-04`'s node/npm prerequisite are
`main-session-direct` (`execution_reason` on each task) and are NOT the eng lead's to take.

## Trust

- All plan-phase artifacts are COMMITTED at `ac96e77e`; read any claim below with
  `git show ac96e77e:<path>` rather than the working tree — HEAD before it (`04f7655c`) carried no
  `D-23` at all, so any inherited "unchanged since HEAD" claim predating that commit is UNVERIFIED
- Five operator-ordered fixes B-19/B-20/B-21/B-22/B-24 landed at their named fields — read each
  field: `plan.yaml` T-19.intent :1306-1317, T-10.intent :743-781, D-08, D-20, D-23, T-07.intent
  :578-585; `BRIEF.md` :73-92 and :157-166; `DESIGN.md` :249-252 — verified-at ac96e77e
- Three cycle-5 panel residues closed: T-10 boundary bucket, T-19 baseline commit, D-23/C4-04 clause
  — `runs/2026-09-02-09-product/digest.md` — verified-at ac96e77e, by the orchestrator at source,
  **NOT by a panel** — no sixth panel read them
- Panel gates nothing: `must_fix: []`, `severity_max: med`, both readers ran —
  `runs/2026-09-02-08-validator/digest.md` + `digest-corrigendum.md` — verified-at ac96e77e
- Budget is 11/20 cycles, 20 runs of `max_total_runs` 20 (INFORMATIONAL, INV-22 note only, it never
  stops a feature) — `feature.json` — verified-at ac96e77e
- `approval:` and `## Approval` are both `pending` and byte-untouched across all three runs of this
  pass — `plan.yaml:6-9`, `BRIEF.md:296-300` — verified-at ac96e77e
- T-19's succeeding-commit case is satisfiable only WITH the baseline commit — measured directly:
  `git init` + add + commit of one file still leaves `?? a.txt` in `status --porcelain` —
  verified-at ac96e77e

## Dead ends

- Do NOT re-open DEC-5 (prototype gate), the accuracy/handoff-eval KPI (it is FEAT-54, verified
  absent from all three artifacts by regex), or backlog rows B-1..B-5, B-7..B-10, B-12..B-14, B-23,
  B-25 — all operator-accepted as backlog and carried by D-23 — `plan.yaml` D-23 + `panel.findings`
  — verified-at ac96e77e
- Do NOT treat `approval: pending` as a finding — raised and dismissed in five consecutive panels —
  `runs/2026-09-02-08-validator/digest.md` `assessed_and_dismissed` — verified-at ac96e77e
- Do NOT use the worktree-vendored `.claude/skills/harness/bin/plan-merge.py`: it is stale and
  predates `set-panel` and `--yaml-value`. Run the MAIN checkout binary with an absolute `--file` —
  `runs/2026-09-02-07-product/digest.md` — verified-at ac96e77e
- Do NOT set an acceptance criterion of the form "plan.yaml is the only changed file" via
  `git diff --stat` while the feature dir carries uncommitted work: it grades the tree, not the
  change — `notes/ship-review-2026-09-02-plan-c4.md` harness-defect 3 — source: prior orchestrator.
  From `ac96e77e` forward a diff IS meaningful, the tree being clean at that commit
- Do NOT ask a lead to run a checker: leads hold no Bash. Every mechanical gate is the
  orchestrator's own — source: `.harness/expertise/harness-orchestrator.md` G-10

## Working set

- `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml` (22 tasks, 23 decisions, panel c5)
- `.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md` (15 REQ, 20 SC, the approval gate)
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-02-plan-c5.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/feature.json` (budget, 20 runs)
- `.harness/harness/features/FEAT-53-metrics-dashboard/STATE.md`
