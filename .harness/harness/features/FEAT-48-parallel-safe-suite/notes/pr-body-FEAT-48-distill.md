Post-merge Expertise distillation for FEAT-48-parallel-safe-suite (DEC-145), run after PR #1198 merged.

## What landed

24 new entries and 3 in-place displacements across 10 Expertise files, every one judged by the agent that owns the file:

| file | tier | change |
|---|---|---|
| harness-product-lead | craft | +O-07, +O-08 |
| harness-ui-reviewer | craft | +O-07, +O-08 |
| harness-qa | craft | P-06, G-06, G-09 displaced in place |
| harness-pm | repository | +P-03, +P-04, +P-05, +P-06, +G-15 |
| harness-orchestrator | repository | +P-02, +G-10 through +G-14 |
| harness-security-reviewer | repository | +G-03, +G-04, +G-05 |
| harness-code-reviewer | repository | +G-06, +G-07 |
| harness-qa | repository | +G-07, +G-08 |
| harness-validator-lead | repository | +G-03 |
| harness-product-lead | repository | +P-01 (file created) |

Plus five distillation receipts and the blocked-ops record under the feature's `notes/`, and four orchestrator observations.

**No entry was lost.** Every changed file was verified id-by-id against its committed base: zero removals, and the only text changes are qa's three intended displacements.

## Gate

`check-expertise.sh` exits 0 on both `.harness/expertise/` and `.harness/harness/expertise/`. The five ADVISORY lines are pre-existing and untouched by this branch.

## What this PR does NOT close

17 further ops were accepted by their owners on the merits and then refused mechanically. `expertise-merge.py` exposes one subcommand, `apply`; `compute_union` never deletes, so a same-id rewrite exits 7 and a new id over a section cap exits 8. Every mature craft file sits at Patterns 15 / Gotchas 15 / Outcomes 10, so the displacement `harness-distill` mandates is unreachable through the only sanctioned route.

All 17 are preserved verbatim in `notes/distill-blocked-ops-2026-09-02.md`. The remedy is a displace verb in a main-session-direct tree, so no lead in the org can build it.

Two harness defects surfaced and are carried in the orchestrator's return, not fixed here: the above, and `validate-digest.py`'s branch corroboration, which cannot pass for a code-reviewer distillation run in a worktree that is not on the feature branch.

No feature source, plan, brief or station was touched.
