# Build — T-01 and T-02 (main-session-direct, DEC-174) — 2026-11-22

## T-01 — toolchain

- Pre-implementation HEAD `bda50269` (signed plan a0b617ca + origin/main sync, worktree 0 behind).
- `bun add -d --exact typescript@7.0.2 @types/bun@1.4.5` resolved and wrote `bun.lock` (Bun 1.3.14); `package.json` is private with only those two exact devDependencies and `scripts.typecheck = tsc --noEmit -p tsconfig.json`.
- `tsconfig.json`: strict, noEmit, ESNext/bundler, allowImportingTsExtensions, skipLibCheck, `types: ["bun"]`; `include` is `**/*.ts` plus `.omp/**/*.ts`, because the compiler's wildcard skips dot-directories. `tsc --listFilesOnly` lists exactly the four tracked sources.
- **Amendment (advisor-approved, ledgered):** `git check-ignore -q node_modules/` stayed 1 because the repo tracked a stray vitest cache, `node_modules/.vite/vitest/da39a3ee…/results.json`, committed in 806a8558 (BUG-1756). It is untracked with `git rm --cached` and added to T-01's `files`; the verify also asserts `git ls-files node_modules` is empty.
- README: verified `bun update typescript` leaves an exact pin unchanged and `bun update --latest` bumps it (scratch project, 5.8.2 → 7.0.2), so the README documents `bun update --latest`.
- Literal verify (amended) rc 0: `receipts/T-01-verify.txt`.

## T-02 — eight fixture type errors

- Red first, before any edit: `bun run typecheck` → rc 1 with exactly the eight settled diagnostics (TS2339 ×3 at :1912/:1913/:1947, TS2769 ×2 at :2148, TS2769 ×3 at :2914–2916). Receipt: `receipts/T-02-red.txt`. Hook suite baseline: 186 pass / 0 fail, 1465 expect() calls (`receipts/T-02-hooks-baseline.txt`).
- Fixes, all in `tests/unit/omp-hooks.test.ts`, with no assertion changed, no suppression, no `any`:
  - `digestCalls` is generic over the element type, so the fixture's recorded `payload` survives the filter (:1657).
  - The `failed` expectation's `kind` is narrowed with `as const` (:2912).
  - The member-ops payload comparison maps each recorded payload to `unknown` (:2150). **Deviation from the intent's wording, recorded for review:** the intent asked for the fixture call record to represent member-ops arrays truthfully. The recorder's `payload` is typed as the production `PolicyRunner`'s `Dict`, and `harness-hooks.ts:1523` passes the ops list through `as unknown as Dict`. Widening the recorder to `Dict | unknown[]` would force narrowing at the 29 existing `.payload.<key>` reads, and the production cast is out of T-02's single-file scope. The assertion reads the recorded value as `unknown`, its honest static type, rather than casting an array to a record.
- Literal verify rc 0: compiler clean; registered wrapper 186 pass / 0 fail with the same 1465 expect() calls. Receipt: `receipts/T-02-verify-green.txt`.
