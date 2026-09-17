# T-28 receipt

Commits: `884fafe3`, `533e4a6d`.

## Fail-first proof — cycle 0
`npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/work-view.test.tsx` exited 1 with four behavior cases failing before production implementation, including missing `6 of 6 items` and `window.matchMedia is not a function` in the initial harness test environment.

## Fix cycle 1
Reproduced `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx`: `renders /work/FEAT-1` and URL-state navigation failed. Restored compatible defaults for sparse legacy payloads and retained only window/repository search on KPI routes. The scoped routes regression then passed: 10 tests passed.

## Signed verify
Exact command:
```
npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/work-view.test.tsx && npm --prefix .claude/skills/harness/bin/dashboard/client run build
```
Output: 1 test file / 5 tests passed; Vite transformed 2926 modules and built successfully. Vite emitted existing `inlineDynamicImports` and >500 kB chunk warnings.

The build-generated `dist/index.html` and `dist/assets/index-hkwR5g06.js` were removed after `git restore`; final dist is assets/.gitkeep-only. Only T-28 files were committed. DEC-229 amendment: none.
