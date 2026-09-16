# SIMPLIFICATION — BUG-1699 lifecycle cards

**BLUF:** two small code-surface simplifications remain; neither alters the settled lifecycle projection or its assertions.

## Inspection boundary

Read the complete scoped base-to-tip diff from `60b8d4d99f50edab6a63352ea43ebbc4ffc09750` to `cab3c502` across the 23 named product, prompt, decision, and test files, plus current nearby implementation for the changed lifecycle projection, reconciliation, status sync, reset/resume, and test surfaces. This is SIMPLIFICATION only; approved D-01–D-06 behavior and assertion strength were not reconsidered. No source was mutated and no validation command was run.

## Findings

- **SIMP-01 — code surface** — `.claude/skills/harness/bin/check-state.py:2305-2329`: the newly retained `_derived`/`_statuses` branch ends in `pass`, so it no longer affects the active-card comparison. **Cost:** it computes unused values and leaves 25 lines describing a retired skip rule for readers to mentally disprove. **Alternative:** delete lines 2305-2329; continue directly to the recorded-card eligibility check at line 2331. Active-phase projection still reaches every recorded card.
- **SIMP-02 — code surface** — `.claude/skills/harness/bin/board_lifecycle.py:1009-1014`: `STATION` and newly added `STATUS` branches execute the identical `gh_board.set_station` call. **Cost:** one station-repair behavior now has two branches that can drift when the write signature or payload changes. **Alternative:** fold them into `if finding.kind in {"STATION", "STATUS"}:` with the existing shared call; leave `REASON` and `LABEL` branches unchanged.
