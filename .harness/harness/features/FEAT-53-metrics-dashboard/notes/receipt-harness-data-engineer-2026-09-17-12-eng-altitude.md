# FEAT-53 ALTITUDE receipt

BLUF: Two altitude findings remain. The repository selector has a second, hard-coded authority instead of using the server’s configured-repository seam; and the metrics modules form three import cycles around the KPI composer. The changed modules otherwise have meaningful, local responsibilities; the dashboard’s disk collector, attention derivation, API factory, trend store, and client renderer cross their intended interfaces. No persistent adapter lifetime is implicit: `create_app(root)` owns one resolved project root for the application lifetime, and no pooled or persistent client was introduced.

## Reviewed scope

- Diff: `a18d6a9f1f832084df84be22097a409d73bf4f61..HEAD` (264 changed paths).
- Reviewed changed executable/runtime source, client source, tests, harness configuration and integration seams. Excluded the dispatch-specified feature `feature.json`, `STATE.md`, `runs/**`, `notes/receipt-*`, and `observations/**`; did not raise signed visual/product decisions, immutable prototypes, the generated bundle, or documentation-only changes.
- Checks performed: deletion test on newly added dashboard modules; one-authority trace for window, lifecycle, thresholds, repositories and trend records; seam/adapter and lifetime trace through Flask, Git, disk collection and client fetches; and interface-surface scan of changed Python and TSX tests.

## Findings

### ALT-1
- **File and exact line:** `.claude/skills/harness/bin/dashboard/client/src/routes.tsx:13`; server authority is `.claude/skills/harness/bin/dashboard/serve.py:141-154`.
- **One-line summary:** `SharedHeader` hard-codes `Alpha` as the only non-`all` repository option while the server derives repository identities from the configured fleet.
- **Concrete cost:** Adding, removing, or renaming a configured repository leaves a server-valid `repo` value unavailable from the UI (or presents stale `Alpha`); fleet configuration and the committed client now require lockstep edits.
- **Concrete alternative:** Expose the configured repository names through the dashboard response (or a small read-only repository endpoint) and derive the selector options from that interface, keeping fleet enumeration as the sole authority.
- **Recommendation:** fold-in

### ALT-2
- **File and exact line:** `.claude/skills/harness/bin/dashboard/kpi.py:9-15`, `.claude/skills/harness/bin/dashboard/trend.py:8-10`, `.claude/skills/harness/bin/dashboard/attribution.py:8`, `.claude/skills/harness/bin/dashboard/defects.py:7`.
- **One-line summary:** The KPI composer and its metric modules depend on each other in three cycles (`kpi↔trend`, `kpi↔attribution`, `kpi↔defects`), including `trend` calling KPI-private helpers.
- **Concrete cost:** Import order is now part of the hidden interface; an otherwise local import-time initializer or refactor can fail against a partially initialized module, and changing shared window/snapshot behavior requires navigating bidirectional dependencies rather than one leaf seam.
- **Concrete alternative:** Make `kpi` a one-way payload composer: extract the shared window and feature-snapshot helpers into dependency-free leaf modules, then have `trend`, `attribution`, and `defects` import those leaves rather than `kpi`.
- **Recommendation:** briefing-row

## Cleared

- `grilling_status.py` is the sole lifecycle parser/writer and its callers reuse it.
- `attention.py` owns threshold validation and attention ordering; `work.py` supplies records rather than duplicating those rules.
- Added dashboard modules pass the deletion test: their collection, persistence, derivation, rendering, and server-factory behavior would otherwise reappear across callers.
- Changed tests predominantly call `compute`, `read`/`append`, `collect`, or Flask routes rather than duplicating their implementation logic.
