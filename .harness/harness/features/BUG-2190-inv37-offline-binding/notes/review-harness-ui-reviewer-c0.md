# BUG-2190 — UI review c0

PASS — scoped out: the measured feature-only census changes CLI gate logic, tests, classification metadata and records; no visual or interactive UI surface changes.

## Pinned scope and census

Reviewed `c6bd42d20fa9bf58e4c1dd3ede417caefc23a853..33c0c181e62c5e75692c8320fc01aaaaf06fa40b`. The unrestricted name-status census reports 5,023 paths because it includes the unrelated `907225c1` origin/main merge. `git log --first-parent --no-merges --name-status` isolates six BUG-2190 commits (`4612447f`, `0a3302f6`, `655f71ae`, `df1fd837`, `a480d028`, `33c0c181`): 13 final feature paths plus the retired unit-test name (R100 rename).

- Runtime: `.claude/skills/harness/bin/check_state/{board,table}.py` — repository selection/local validation and `gh:auth` dependency declaration; no rendering or interaction code.
- Tests: `tests/integration/test-check-state-inv37-offline.py`, `tests/unit/test-check-state-inv37-local-binding.py` — CLI/runtime regression fixtures; the former unit basename `test-check-state-inv37-offline.py` is a pure rename, not another surface.
- Classification: `tests/integration/canonical-reader-classification.json` — one feature-owned local fleet-reader row. Corpus-prune changes in the same file are excluded using the exact `0a3302f6` patch.
- Authority: `.harness/harness/docs/{DECISIONS,DECISIONS-INDEX}.md` — offline exception and decision navigation, not visual specifications.
- Feature records: `feature.json`, `plan.yaml`, and `notes/{amendment-T-01-reader-inventory-2026-11-08,amendment-T-01-unit-basename-2026-11-08,amendment-T-01-table-row-2026-11-08,build-evidence-2026-11-08}.md` — execution/provenance records, not rendered-surface contracts.

The bounded census contains zero HTML/CSS/SCSS/LESS/TSX/JSX/Vue/Svelte paths. Direct `git ls-tree` at the review pin returns no feature `DESIGN.md` or `notes/prototypes/` objects. Markdown changes concern runtime policy and records, not spacing, colour, component states or interaction.

## Contract and limits

Read BRIEF SC-01–SC-06, plan, build evidence, research and operator signature (`notes/operator-signature-2026-11-08.md`). Product AGENTS.md names the canonical SPEC/decision authority. DEC-220 preserves receipt/provenance rules; DEC-221:7264–7272 records the approved local-only offline exception. BRIEF explicitly excludes an additional offline output note. The source patch changes binding selection while retaining existing finding construction; user-visible gate outcomes are not a visual UI change.

Accessibility, light/dark parity, focus and layout: not applicable to this bounded nonvisual change, not visually passed. No rendering, tests, builds, linters or formatters run. Runtime correctness and verification remain with the code/QA readers.

Must-fix: none. Open questions: none.
