# Receipt — harness-data-engineer — FEAT-01 simplify ALTITUDE (plan draft, flag-only)

Angle file read: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-altitude.md` (plus `harness-simplify/SKILL.md`).
Surface: BRIEF.md + plan.yaml (10 tasks); Kaya `docs/ARCHITECTURE.md:76,143-145,195` read for seam context. Nothing applied; no plan/BRIEF edits; no verify commands run.

BLUF: 2 findings (1 briefing-row, 1 fold-in); 3 checked-and-left. Schema contract itself (T-04) sits at the right depth.

## Findings

### F-1 — schema-apply migration runner lives inside a test probe
- Angle: altitude. File/line: `plan.yaml` T-08 intent (schema-apply paragraph, ~L273) with `files: tests/e2e/platform-live.ts` (L267); T-04 L205-209.
- Summary: the only executor of `supabase/migrations/202610050001_platform_mastra.sql` (project-confirm, TLS pg connect, transactional apply, PostgresStore init) is a mode of the e2e probe, a capability bolted onto a caller rather than a home of its own. ARCHITECTURE.md:76 says the migration location "does not settle the migration execution contract in #8", and ARCHITECTURE.md:69 reserves `scripts/` for repository maintenance commands.
- Concrete cost: a de facto migration-execution contract is chosen inside a test file. The next feature that adds a migration either extends a probe named `platform-live` or builds a second runner, and the apply path can drift from the offline test surface. Mixing the mutating command with read-only probes (`live`, `readback`, `supabase`) also means one file holds both an operator-destructive and a verifying role.
- Alternative: do not restructure now (the settled layout and #8 bound it). Add a briefing row stating that `schema:apply` is a platform-setup command whose placement in `tests/e2e` is provisional, that the execution contract remains #8's, and that a `scripts/` home needs its own lane row (none exists for `scripts/**` in `lanes.rows`) if relocated.
- Disposition: **briefing-row**

### F-2 — pinned values restated across task intents with no named authority
- Angle: altitude. File/line: `plan.yaml` T-05 L225 (pool 2 / 5000 ms / 10000 ms, schemaName `mastra`, resource `kaya-local-platform`, model `claude-sonnet-5-5`), restated in T-02 L177, T-06 L240, T-08 L271-273, T-10 L307, and D-01 L114 (connection mode).
- Summary: model id, fixed resource identity, schema name, pool bounds and 5432 mode are each stated in 3-5 task intents; the implementation owner is T-05 (storage/agent) but nothing marks T-05 as the authority.
- Concrete cost: a change at one site (e.g. pool bound or model id after T-01 provider inspection rejects `claude-sonnet-5-5`) leaves the tests, probe and docs asserting the old value; the failure surfaces as a red cumulative gate at T-09 or a wrong doc after it. Mitigant: separate dispatches need their own copies (so I do not call the duplication itself the defect), and T-02/T-08 assertions fail loudly, but T-10 docs have only a whitespace verify.
- Alternative: add one sentence to T-05 (or D-01) naming T-05 as the single source of these values, and have T-02/T-06/T-08/T-10 say "the T-05 values" while keeping the dispatch-visible literals only where a test must assert them. T-10 should read values from the shipped code rather than restate them.
- Disposition: **fold-in**

## Checked and left (no finding)
- T-04 verify is a static SQL-text test; real grant and Data API denial is proven only by T-08 `smoke:supabase` / UAT. The compensating control is named in T-04 intent and BRIEF Verification gaps, and the residual is accepted explicitly. Disposition: **leave**.
- Test-kind selection globs stated in T-01 (Vitest projects) and T-09 (`harness.json` detect): two statements, but T-09 intent requires zero-selection and nonzero-failure demonstrations and `pnpm verify:platform` runs both, so drift is caught. Disposition: **leave**.
- D-02 localhost bearer residual: compensating control (not account authorization; reserved to Kaya #2) is named in D-02, BRIEF constraints and T-10. Disposition: **leave**.
- Schema ownership boundary (adapter owns DDL, SQL owns schema + default grants only, T-04 L209) is at the right seam; no copied adapter DDL.

## Open questions
- None blocking.
