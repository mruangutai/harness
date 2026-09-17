# T-28 receipt — source error items

PASS — `69f40ec3c568a4a7e98a953fa7c7e4988d1a616e` renders each work payload source error as a semantic list item and retains each source path/reason pair.

- fail-first: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/work-view.test.tsx` exited 1: 1 test failed because role `list` named `Unreadable sources` was absent from the prior inline-Text rendering.
- green verify: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/work-view.test.tsx && npm --prefix .claude/skills/harness/bin/dashboard/client run build` exited 0; Vitest: 1 test file passed, 6 tests passed. The new case asserts two listitems for `errors.length === 2` and both source_path/reason pairs.
- build: Vite built successfully (2930 modules); generated `dist/assets/index-Ddotz-pN.js` and `dist/assets/index-BGeYwNXA.css`.
- dist evidence: `dist/index.html:7` references `./assets/index-Ddotz-pN.js`; the referenced bundle contains `Unreadable sources` and `Some sources could not be read`, shipping the semantic source-error list behavior.
- committed files: `.claude/skills/harness/bin/dashboard/client/src/work-view.tsx`, `.claude/skills/harness/bin/dashboard/client/src/work-view.test.tsx`, `.claude/skills/harness/bin/dashboard/client/dist/index.html`, and generated asset rename `dist/assets/index-DnXu7ssi.js` → `dist/assets/index-Ddotz-pN.js`.
- amendments: []
