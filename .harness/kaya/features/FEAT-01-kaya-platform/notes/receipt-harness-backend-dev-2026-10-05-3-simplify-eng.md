# Receipt — harness-backend-dev — FEAT-01-kaya-platform — simplify REUSE (plan surface)

Angle file read: `/Users/molchairuangutai/GitHub/harness/.agents/skills/harness-simplify/references/angle-reuse.md` (also `harness-simplify/SKILL.md`).
Scope: `plan.yaml` (F2FB) + `BRIEF.md` (551A), read-only. Kaya CODE tree at 6303f9f is greenfield (README, docs/, .gitignore, .harness/harness.json only) — nothing exists to reuse in code; findings are task-vs-task re-statement. Flag-only; nothing applied; no verify commands run. Line numbers = plan.yaml.

BLUF: 4 findings (1 med, 3 low). Altitude disposition is not this angle's; all four are plan-text fold-ins for pm.

## Findings

### R-1 (med) — T-08 live/schema-apply/supabase modes re-specify what T-03 and T-05 already own
- File/line: plan.yaml:272-273 (T-08) vs 194-195 (T-03) and 225 (T-05).
- Summary: T-08 independently specifies loading the five names from root `.env.local`, validating the SUPABASE_PROJECT_URL ref against SUPABASE_DB_URL, the TLS `pg` connection, initializing PostgresStore in `mastra`, and a privileged Supabase admin probe. T-03 `env.ts` already owns root env loading and project-ref/5432 validation, T-03 `supabase.ts` already exposes a "safe connectivity probe operation using the real admin API", and T-05 `storage.ts` owns the pool/TLS/schemaName/init.
- Cost: two spellings of ref-matching, 5432/6543 refusal, TLS and pool settings in lockstep; a T-03/T-05 tightening (e.g. new endpoint rule) will not reach the probe, and the probe — an operator-run UAT path never exercised by CI — goes stale silently. `--conditions=react-server` (T-01:151) already exists so the probe CAN import server-only modules.
- Alternative: T-08 intent says to import `env.ts`, the `supabase.ts` probe and a `storage.ts` factory (pool/store construction with caller-owned shutdown, already required by T-05 "expose shutdown only for owning process/probe") instead of re-deriving; keep only probe-specific logic (confirmation prompt, catalog queries, Data API 406/PGRST106 check, SQL apply). Add the named exports to T-03/T-05 intents.

### R-2 (low) — fixed identity constants restated by value in four tasks
- File/line: plan.yaml:195 (T-03 "fixed server-only local resource identity", file unspecified), 225-226 (T-05 literal `kaya-local-platform`, `claude-sonnet-5-5`, `anthropic`), 240 (T-06 response provider/model literals), 272 (T-08 "exact provider/model identifiers").
- Summary: resource id, provider and model strings are spelled in T-05, T-06 and T-08; T-03's resource constant has no named file/export, so T-05 retypes it.
- Cost: a model bump edits T-05 but T-06's 200 body and T-08's live assertion are separate spellings; the tests (T-02) catch only what they assert, and T-06 has no ownership of platform-agent.ts to fix it.
- Alternative: name one export in each owner (resource id in T-03 `request.ts` or `env.ts`; provider/model from `platform-agent.ts`) and say T-06/T-08 import them (T-08 may assert against the imported value, not a literal, or keep one deliberately independent literal stated as such).

### R-3 (low) — HTTP status/error classification table is re-listed across T-02, T-03, T-06, T-10 with no single owner
- File/line: plan.yaml:177 (T-02 statuses), 195 (T-03: 400/401/503), 240 (T-06: 200/400/401/404/502/503), 307 (T-10 documents 400/401/404/502/503).
- Summary: T-03 owns 401/503/400 and "fixed safe classifications"; T-06 re-enumerates the full map including 404/502 whose classification (provider vs empty-output vs storage) originates in T-05's "classified errors".
- Cost: four spellings; a changed mapping (e.g. empty output 502→) needs lockstep edits and T-06's route can silently map differently than T-05's classified error kinds.
- Alternative: T-05 defines the classified-error kinds, T-06 intent says "map kinds to statuses per T-03/T-05 classification, table owned by T-06" once, T-10/T-02 reference T-06 rather than re-list.

### R-4 (low) — T-09 detect globs re-spell T-01 Vitest project selectors
- File/line: plan.yaml:150 (T-01 project selectors) vs 287 (T-09 detect patterns for unit/functional/integration/component).
- Summary: the four selection rules (non-JSX `*.test.ts` excluding `__tests__`, `*.test.tsx`, `__tests__/*.functional.test.ts`, `__tests__/*.integration.test.ts`) are written twice, once as Vitest includes, once as harness detect strings.
- Cost: the two must match exactly ("selected once in intended kind", line 287); a later glob change in `vitest.config.ts` leaves `.harness/harness.json` detect stale, and `detect` drives test-matrix attribution silently.
- Alternative: T-09 verify step derives/compares detect against `vitest.config.ts` projects (T-01 already says "show each test is selected once") — or, minimally, T-01 records its glob list as the single source and T-09 copies from that receipt, stating it is generated not re-authored.

## Checked, no finding
- T-02 vs T-07 page assertions: settled static-document baseline (PF-86e4a4c3); not flagged.
- T-04 SQL text test vs T-08 catalog probe: different evidence (text vs hosted), not duplicate.
- T-10 docs restating behaviours: documentation of record, inherent.
- Nothing in the Kaya tree (docs/ARCHITECTURE.md:24-98, harness.json) is re-implemented; layout in plan matches the cited convention.
