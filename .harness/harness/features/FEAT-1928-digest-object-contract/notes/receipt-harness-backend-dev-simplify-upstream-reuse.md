# Receipt: simplify-upstream-eng · REUSE angle (merge integration)

**BLUF: PASS, no findings.** The three conflict files integrate upstream BUG-1016 without restating anything the tree already has.

Read-only; no checks run. Scope: `.omp/extensions/harness-hooks.ts`, `tests/unit/omp-hooks.test.ts`, `.harness/harness/docs/DECISIONS-INDEX.md`.

## Evidence
- `harness-hooks.ts`: `EDIT_TARGET` (L78) is one matcher shared by `extractEditPaths` (L84) and `rootedInput` (L303). `rootPathList` (L290) reuses `rootTarget`. `openRun` (L995-997) resets `runGate`, `digestBinding` and `featureRootCache` together. `agent_end` (L1456-1461) resets `runGate` and `featureRootCache` only, with no legacy fallback.
- `omp-hooks.test.ts`: the upstream BUG-1016 cases (L1245-1556) sit inside "OMP task lifecycle adapter", before the `loadDigestSchemaBundle` describe (L1701). The describe closes at L1698. `rootedHooks` (L1242) wraps the existing `governedUriHooks` (L973), which wraps `fixture` (L126). No second harness is built; `featureRoot` is an option on `fixture` (L126, L168-169).
- `DECISIONS-INDEX.md`: DEC-156 (L159) and DEC-237 (L231) are present, and DEC-251 (L234) is present with its `@` anchor.

## Principles applied
None cited; no leaf read for this angle.
