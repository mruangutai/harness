# Receipt: BUG-1016 T-01 simplify, ALTITUDE angle (harness-dev-ops)

BLUF: PASS, findings []. Rooting sits at the right depth. Read-only; nothing run (per dispatch).

Scope read: `git diff 8d79d63d..89b7d960 -- .omp/extensions/harness-hooks.ts` plus `harness-hooks.ts:260-312` for the existing path knowledge. Leaves read: angle-altitude.md, delete-first.md.

## Candidates considered (each ends fold-in / briefing-row / leave)

1. Tool-to-path-field table (`PATH_TOOLS`, `ROOT_DEFAULT_TOOLS`, ast_edit `paths`, edit patch) at `harness-hooks.ts:366-369,372-392` vs. the table in `preDomain` (`:298-302`). **leave.** The two tables answer different questions. `preDomain` lists only write/edit, the domain-gated mutating tools. Rooting also covers read/grep/glob/ast_*, which no gate inspects. Merging them would force the gate table to carry tools it must not gate. Header edit targets are already one authority: `EDIT_TARGET` (`:77`) is shared by `extractEditPaths` and `rootedInput`. Named tests: no behavior change either way (leave).
2. Root resolution placed in the adapter closure (`featureRoot`/`rootCall`, `:978-1012`) rather than a separate module. **leave.** The one authority is the existing `inflight_registry.py feature-root` resolver; the adapter only validates and caches its answer. The cache lifetime (per run id, feature, cwd; reset in `openRun` and at agent end) is stated beside the seam. Nothing else in the TS needs the root (deletion test: no second caller). Test impact: none.
3. Post-hook re-derives rooted input via `rootCall` for write/edit (`:1452-1456`) instead of threading the pre-hook revised input. **leave.** The host may return either the original or the revised input, so threading would be unsound. Rooting is idempotent, and the cache makes the second call cheap. This is the settled seam, not a bolt-on. Test impact: removing it would break the pre/post agreement tests; keeping it changes nothing.
4. `needsRoot` probing `rootedInput(.., "/")` (`:395`). **leave.** It reuses the one rooting function, so the "has anything to root" decision cannot drift from the rooting itself. A separate predicate would be a second statement of the rule. Test impact: none.
5. URI/abs/tilde passthrough in `rootTarget` (`:356`) reuses `URI_SCHEME` (`:269`) instead of restating it. **leave.** One statement, as required.

## Findings
[]

No fold-in or briefing-row recommended. No named BUG-1016 test is affected by any candidate disposition.
