# Handoff — FEAT-25-claim-feature-root, plan → build — written at d1ffd7f, seq-1

## Next

Do nothing until the operator signs BRIEF `## Approval` and plan.yaml `approval:` — both are
`pending` and only the main session writes a signature. On signature: cut the branch
`git checkout -b feat/FEAT-25-claim-feature-root` from `d1ffd7f` or later (SC-08 diffs three-dot
against `d1ffd7f`; a branch cut before it fails clause (a) on unrelated files), run
`gh-sync.py open`, then dispatch the `build` team to harness-eng-lead with T-01 first — T-02 and
T-03 both `depends_on: [T-01]`, so there is no parallel opening move.

## Trust

- All three `verify:` blocks are RED against the unfixed tree — extracted with `safe_load`, run
  with CLAUDE_PROJECT_DIR set, each exit 1 on its own discriminating clause — verified-at d1ffd7f
- Suite baselines are 114 / 106 / 40 (claim / integration / layout), all suites exit 0; every count
  clause is re-pinned to them (≥116, ≥106, ≥120, ≥41) — verified-at d1ffd7f
- `check-plan-routes.py` exits 0; T-02 sits at the 50-line machine-field cap with ZERO headroom, so
  a doer needing another verify line must restructure, never append — plan.yaml:232-272,
  check-plan-routes.py:281 — verified-at d1ffd7f
- The defect is real and fails CLOSED: `factory_claim.py:43` builds `.harness/features`, which does
  not exist; `_blocker_gate:140-142` returns `("edge_i", …)` for every candidate — verified-at d1ffd7f
- SC-08 is graded at the goal-check, which precedes distillation and ship-refresh, so
  `.harness/expertise/*.md` writes are outside the graded set — playbook close-out ordering plus
  `git show --pretty=format: --name-only d1ffd7f` — verified-at d1ffd7f
- #500 alone may not unblock unit 8: `factory_decompose.py:276-283`/`:360` always label
  `feature:<id>`, so a kaya feature dir outside the harness segment stays unreadable — verified-at d1ffd7f

## Dead ends

- D-01 (fixed `harness` segment) and D-02 are NOT reopened — a derived rule was mounted as a
  concrete attack by eng-lead and by pm and failed on reachability; plan.yaml D-01/D-02,
  runs/2026-08-18-01-eng/digest.md F-1 — verified-at d1ffd7f
- Do not widen any count clause when `main` moves — re-derive the baselines and report instead;
  a derived baseline cannot tell "case deleted" from "baseline moved" — T-01 intent — verified-at d1ffd7f
- The two new stderr texts are out of ui-reviewer's lens and stay unjudged until the post-build
  panel — runs/2026-08-18-1-planreview-validator/digest.md Q1 — source: validator run
- `.harness/harness/features/FEAT-26-pr-linkage-recorded/` and `FEAT-27-expertise-repository-tier/`
  are other paused flows — never staged, never edited — source: dispatch

## Working set

- .harness/harness/features/FEAT-25-claim-feature-root/plan.yaml
- .harness/harness/features/FEAT-25-claim-feature-root/BRIEF.md
- .harness/harness/features/FEAT-25-claim-feature-root/notes/research-FEAT-25-claim-feature-root.md
- .claude/skills/harness/bin/factory_claim.py
- .harness/harness/features/FEAT-25-claim-feature-root/runs/2026-08-18-3-product/digest.md
