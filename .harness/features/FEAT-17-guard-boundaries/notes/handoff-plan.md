# Handoff — FEAT-17-guard-boundaries, plan → build — written at a29ad06, seq-3

## Next

Do NOT dispatch anything until the operator signs. BRIEF.md `## Approval` and plan.yaml
`approval.status` both read pending and only the main session writes either. Once signed, the build
phase is SIX main-session-direct segments in depends_on order (T-01 extract harness_boundary.py →
T-02 → T-03 → T-04 → T-05 → T-06), each an ordinary edit with its `verify:` run explicitly and a
human reading the diff, and ONE team task, T-07 (docs), routed through product-lead to
harness-documentor. There is no build squad for T-01..T-06.

## Trust

- Both plan gates re-run against the RE-SCOPED plan: `check-plan-routes.py <plan>` reports 0
  violations across 1 plan (DEVIATION T-01..T-06, OK T-07), and all 11 unique literal `files:` paths
  (15 entries) resolve under check-domain.sh --resolve, each matching its declared lane. T-01..T-05
  resolve to harness-backend-dev/dev-ops but are correctly main-session-direct as DEC-174 carve-outs
  — verified-at a29ad06
- DEVIATION does not increment the violation counter (check-plan-routes.py:352-357) — verified-at
  a29ad06
- `harness_yaml.load_plan` parses the amended plan — I ran the real loader, 7 tasks. Closes the
  seq-2 line that stood UNVERIFIED — verified-at a29ad06
- THE RE-SCOPE: FEAT-09's shape-cap failure is OVERTAKEN by DEC-180 / issue #132. A rooted session's
  out-of-domain and over-cap writes are already refused (211-line feature.yaml exits 2, 70-line
  handoff note exits 2) — notes/answers-2026-08-11-rescope.md — operator-measured at a29ad06
- T-02's module-level hoist is CUT; the root-side check sits at the START of `domain_check`. The
  no-PyYAML cluster on both routes and REQ-02's bootstrap clause went with it. The divergence is
  recorded as D-09, reversible at signature — plan.yaml D-09, BRIEF.md REQ-02 — verified-at a29ad06
- The root-side RULE survives, on the stray-worktree-is-a-mistake ruling plus lost-work risk, never
  on FEAT-09. It is load-bearing for SC-06: the mutation flip is only reachable with the session
  root pinned inside a worktree — BRIEF.md SC-06, plan.yaml T-07 — verified-at a29ad06
- FIX 2 LANDED and is asserted both directions: the root-side verdict must contain
  `.claude/worktrees` and must NOT contain `git worktree remove`, with a paired POSITIVE so the
  negative is discriminating — BRIEF.md SC-03, SC-08 — verified-at a29ad06
- Counts are 9 REQ, 10 SC, 9 decisions, 7 tasks, counted from the files — verified-at a29ad06
- The out-of-place worktree (…/scratchpad/r6, at 52d8334) is CLEAN, so T-06 strands nothing; wt140
  is prunable and gone from disk — notes/measurements-2026-08-11.md — verified-at a29ad06
- FEAT-16's `files:` union moved 18→17; all three shared paths (test-check-domain.py, DECISIONS.md,
  DECISIONS-INDEX.md) are still members — product-lead re-derived membership — UNVERIFIED by me

## Dead ends

- Citing FEAT-09's shape-cap failure as LIVE evidence — overtaken by DEC-180, re-measured at a29ad06
  — notes/answers-2026-08-11-rescope.md. State it as closed; do not re-derive it.
- Restoring the module-level hoist without also restoring REQ-02's clause and SC-03's cluster — they
  are one decision — plan.yaml D-09.
- Consulting `git worktree list` to RESOLVE a sibling worktree onto the globs — offered and DECLINED
  by the operator — grilling `## Settled` ruling 1. Refuse, never resolve.
- Making INV-25 a warning — operator ruling, 2026-08-11: it stays a FAILURE.
- Re-adding mruangutai/harness to the fleet — asserted by test-no-distribution.py.
- Changing how .claude/worktrees/ or workspace_root/<product> are governed — both measured correct.
- Relaning T-06 to a squad to silence its DEVIATION — it touches carve-out surfaces.
- The `Permitted for you:` stderr line — skipped deliberately by the operator.

## Working set

- .harness/features/FEAT-17-guard-boundaries/plan.yaml
- .harness/features/FEAT-17-guard-boundaries/BRIEF.md
- .harness/features/FEAT-17-guard-boundaries/notes/answers-2026-08-11-rescope.md
- .harness/features/FEAT-17-guard-boundaries/runs/2026-08-11-06-rescope-product/digest.md
