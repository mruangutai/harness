# Simplify pass — BUG-2328 build diff — 2026-11-22

Scope: `git diff f502a7a8..cf5ef3ea -- .omp/extensions/digest-schema.ts tests/unit/omp-hooks.test.ts`.
Four parallel read-only `reviewer` dispatches, one angle each (harness-simplify, code surface).

| Angle | Reader | Result |
|---|---|---|
| reuse | S2328Reuse | no findings: the regression reuses the existing `schemaDir` fixture |
| simplification | S2328Simplify | no findings: removing the cache reduces state and branches |
| efficiency | S2328Efficiency | no findings: the per-dispatch reread (~20–22 KB) is the settled freshness trade-off |
| altitude | S2328Altitude | no findings: freshness is enforced at the shared loader boundary; leave |

Cost measured by the main session (bun, 16 personas warmed, then 200 fresh loads): **0.616 ms mean per
`loadDigestSchemaBundle` call**. Negligible on a per-dispatch path.

Nothing to apply. Build deviation from the plan intent, recorded for validation:

- `:1711` (`outputSchema` `toBe(bundle)`) was **deleted**, not turned into `toEqual`, because the
  assertion directly above it already compares the whole task item, `outputSchema` included, with
  `toEqual`. A second `toEqual` would repeat it.
- BUG-2305's test (merged into the base) also asserted the cached object's identity at `:1761` and
  `:1766`. The grilling's fact list missed them. They now assert `not.toBe(copy)`: the hook re-injects
  its own bundle instead of passing the caller's copy through, which is what those lines protected.
