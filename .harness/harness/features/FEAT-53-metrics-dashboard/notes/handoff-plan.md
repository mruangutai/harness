# Handoff — FEAT-53-metrics-dashboard, plan → build — written at 04f7655c, seq-1

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

- Five operator-ordered fixes B-19/B-20/B-21/B-22/B-24 landed at their named fields — read each
  field: `plan.yaml` T-19.intent :1306-1317, T-10.intent :743-781, D-08, D-20, D-23, T-07.intent
  :578-585; `BRIEF.md` :73-92 and :157-166; `DESIGN.md` :249-252 — verified-at 04f7655c (working
  tree; see Dead ends on the commit)
- Three cycle-5 panel residues closed: T-10 boundary bucket, T-19 baseline commit, D-23/C4-04 clause
  — `runs/2026-09-02-09-product/digest.md` — verified-at 04f7655c, by me at source, NOT by a panel
- Panel gates nothing: `must_fix: []`, `severity_max: med`, both readers ran —
  `runs/2026-09-02-08-validator/digest.md` + `digest-corrigendum.md` — verified-at 04f7655c
- Budget is 11/20 cycles, 20 runs recorded of `max_total_runs` 20 (INFORMATIONAL, INV-22 note only,
  it never stops a feature) — `feature.json` — verified-at 04f7655c
- `approval:` and `## Approval` are both `pending` and byte-untouched across all three cycle-5 runs —
  `plan.yaml:6-9`, `BRIEF.md:296-300` — verified-at 04f7655c
- T-19's succeeding-commit case is satisfiable only WITH the baseline commit — measured directly:
  `git init` + commit of one file leaves `?? a.txt` in `status --porcelain` — verified-at 04f7655c

## Dead ends

- Do NOT re-open DEC-5 (prototype gate), the accuracy/handoff-eval KPI (it is FEAT-54, verified
  absent from all three artifacts by regex), or backlog rows B-1..B-5, B-7..B-10, B-12..B-14, B-23,
  B-25 — all operator-accepted as backlog and carried by D-23 — `plan.yaml` D-23 + `panel.findings`
  — verified-at 04f7655c
- Do NOT treat `approval: pending` as a finding — raised and dismissed in five consecutive panels —
  `runs/2026-09-02-08-validator/digest.md` `assessed_and_dismissed` — verified-at 04f7655c
- Do NOT use the worktree-vendored `.claude/skills/harness/bin/plan-merge.py`: it is stale and
  predates `set-panel` and `--yaml-value`. Run the MAIN checkout binary with an absolute `--file` —
  `runs/2026-09-02-07-product/digest.md` — verified-at 04f7655c
- Do NOT set an acceptance criterion of the form "plan.yaml is the only changed file" via
  `git diff --stat`: this feature dir carries uncommitted work from several cycles and the criterion
  grades the tree, not the change — `notes/ship-review-2026-09-02-plan-c4.md` harness-defect 3 —
  source: prior orchestrator, verified-at 04f7655c
- The plan-phase artifacts are COMMITTED as of this handoff's commit; HEAD before it carried no
  D-23 at all, so any inherited claim of the form "unchanged since HEAD" taken before that commit is
  UNVERIFIED

## Working set

- `.harness/harness/features/FEAT-53-metrics-dashboard/plan.yaml` (22 tasks, 23 decisions, panel c5)
- `.harness/harness/features/FEAT-53-metrics-dashboard/BRIEF.md` (15 REQ, 20 SC, the approval gate)
- `.harness/harness/features/FEAT-53-metrics-dashboard/notes/ship-review-2026-09-02-plan-c5.md`
- `.harness/harness/features/FEAT-53-metrics-dashboard/feature.json` (budget, 20 runs)
- `.harness/harness/features/FEAT-53-metrics-dashboard/STATE.md`
