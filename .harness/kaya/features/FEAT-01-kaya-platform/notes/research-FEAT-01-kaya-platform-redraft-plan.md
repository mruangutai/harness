# Kaya platform redraft — research and plan receipt

**BLUF:** The unsigned BRIEF and plan now specify a complete local platform, not a flat-root generator scaffold: ten ordered tasks, two plan-local decisions, 41 disjoint file anchors, and real server/provider/storage/UAT contracts. The canonical plan check exited **0**. This is a planning receipt, not implementation, compatibility, hosted-connectivity or ship evidence. Both approvals remain pending. Reader review and operator approval must precede execution.

## Evidence and settled boundaries

- Read-only Kaya baseline: `6303f9f`, `/Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform`. It contains documentation, not an executable application or test harness.
- Binding source organization: `docs/ARCHITECTURE.md:24-98`: private pnpm workspace, `apps/*` and `packages/*`, one lockfile and shared strictness; app/server/Mastra code under `apps/web/src`; packages only for demonstrated reuse, acyclic package edges, no package-to-app imports; colocated tests, subsystem `__tests__`, root `tests/e2e` only for cross-boundary probes. No empty packages, Turbo/Nx or package-source aliases.
- Accepted stack/mission: `docs/DECISIONS.md`, `docs/SPEC.md`, and planning `.harness/notes/grilling-kaya-platform-2026-10-05.md`. Anthropic and the mission plan are settled. No provider choice or mission re-grilling is requested.
- Read [Kaya issue #14](https://github.com/mruangutai/kaya/issues/14) through authenticated issue access after the public read returned 404. The issue's generator command, placeholder-provider instruction, provider-recording instruction and broad UI dependency install are obsolete: retire `pnpm dlx mastra@latest init`, an undecided/placeholder provider, re-recording the already accepted stack, and unused `@mastra/ai-sdk`, `@ai-sdk/react`, `ai`, AI Elements/Astryx UI scaffolding. Retain the actual install/typecheck/lint/build/dev/real-response objective with correct workspace commands. No issue was edited or closed during planning.
- Preserve `notes/research-draft-plan.md` and `runs/2026-10-05-1-plan-product/digest.md` as history. The prior tooling BLOCKED result is historical; the authorized repaired tools were used here. Product/runtime spike #7, workers/durability #8, accounts #2 and later issue contracts are not closed wholesale.
- Only five setting names: `ANTHROPIC_API_KEY`, `SUPABASE_PROJECT_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_DB_URL`, `KAYA_API_STUB_TOKEN`. No values were read or printed. The stub is a loopback API bearer guard, not end-user authentication.

## Scope proposal and outcome contract

The operator perspective covers fresh-clone setup, real local answers, independent persisted exchange retrieval and restart readback. The code-maintainer perspective covers reproducible runtime/dependencies, server boundary, operational-data ownership, meaningful runners and honest documentation. BRIEF contains the full outcome wording and nine falsifiable SCs; every SC is traced from tasks.

SC-01 through SC-04 are **operator UAT**, not automatic passes: setup, real Anthropic response plus persisted exchange, nonce readback after restart without model invocation, and real privileged Supabase/catalog/Data API evidence. SC-05 through SC-09 are inspection criteria requiring pinned shipped-code/QA/documentation evidence. All nine are presently `not_met`; there is no implementation in this assignment.

**Prototype omission is a proposal, not an approved exemption. The design reader decides.** Proposed UI is only a meaningful static server-rendered landing with README guidance; the command/API loop supplies the platform interface. There is no full chat, generative UI, account experience or browser interaction workflow. If the reader requires a prototype, amend scope and routing before signature rather than quietly implementing or waiving it.

D-01 reserves non-public operational schema `mastra`, direct or session-mode port 5432, no transaction-mode 6543/fallback. D-02 bounds the token to the local single-resource platform, not product auth. Accepted product decisions remain unchanged. No public financial schema, workers, extraction quality, deployment or production connection contract is introduced.

## Task order and execution routes

| Task | Predecessor | Route | Exclusive deliverable and boundary gate |
|---|---|---|---|
| T-01 | none | main-session-direct | 14 manifests/runtime/config files; exact pins, real runners and CLI scripts. Only installed-tool version checks here; no future app/tests/probe invoked. |
| T-02 | T-01 | harness-qa | 11 genuine behavioral test files, assertion-level red receipts before production. Deliberately MANUAL red-delivery gate; generic import/collection failures or wiring-only tests are not proof. |
| T-03 | T-02 | harness-backend-dev | 4 env/token/request/Supabase server modules; corresponding predecessor unit suites. |
| T-04 | T-02 | harness-data-engineer | Operational schema/revocation migration; predecessor SQL inspection test, not hosted permission proof. |
| T-05 | T-03,T-04 | harness-backend-dev | Mastra composition, Anthropic agent and pg Memory/storage; predecessor storage/agent units. |
| T-06 | T-05 | harness-backend-dev | Real Next GET/POST API handlers; predecessor functional and cross-module integration suites. |
| T-07 | T-02,T-06 | harness-frontend-dev | Layout and static page; predecessor metadata/render tests. Prototype proposal remains reader-controlled. |
| T-08 | T-07 | harness-backend-dev | Root cross-boundary real offline/live/readback/schema/Supabase probe; offline actual-Next HTTP gate only at this task. |
| T-09 | T-08 | main-session-direct | Product `.harness/harness.json` runner cutover and **terminal** cumulative offline gate. No unfinished executable successor. |
| T-10 | T-09 | harness-documentor | README, PLATFORM runbook and exact compatibility/evidence document. Documentation only after terminal code/config gate. |

Every product-write instruction confines writes to the assigned Kaya CODE worktree. No task shares a file; production owners may not weaken QA-owned tests. Main-session-direct is serialized, not assigned to a made-up specialist. The task types use registered matrix vocabulary. Local verification is stated on every task; intentionally red T-02 does not demand absent successors become green. Cumulative install-complete `pnpm verify:platform` belongs to T-09, not the scaffold task.

## Domain resolution receipt

Resolved each of the 41 planned paths with the repaired control tool `check-domain.py --resolve <absolute CODE path>`, not by inferring ownership from new folder names. Control manifest pin in lanes: `f35d3a724f02adba6e23aa14eb92034558cfd41c`.

- `package.json` and `pnpm-lock.yaml`: devops, explicitly **SHARED**; `pnpm-workspace.yaml` and `tsconfig.base.json`: devops. All are intentionally serialized in main-session-direct T-01.
- `apps/web/package.json`, `apps/web/tsconfig.json`, `apps/web/next.config.ts`, `apps/web/next-env.d.ts`, `apps/web/vitest.config.ts`, `eslint.config.mjs`, `.node-version`, `.npmrc`, `.env.example`, `.gitignore`: **NOBODY**, therefore main-session-direct T-01.
- `.harness/harness.json`: **NOBODY**, therefore main-session-direct T-09. Do not broaden the control domain manifest or copy it into Kaya.
- Source under `apps/web/src`: backend/frontend grants; select backend for server/Mastra/API and frontend for layout/page. QA is additionally granted by `*.test.*`; schema test also resolves data. Supabase migration resolves data; `tests/e2e/platform-live.ts` resolves backend/devops/qa and selects backend; README and docs resolve documentor.
- Important observed correction: bare `__tests__/route.functional.ts` and `__tests__/platform.integration.ts` did **not** resolve QA. Use `route.functional.test.ts` and `platform.integration.test.ts` instead; unit discovery excludes `__tests__` to prevent double selection. The lane does not grant arbitrary `__tests__` files.

Exact follow-up resolution stdout, both exit 0:

```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.agents/skills/harness/bin/check-domain.py --resolve /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform/apps/web/src/app/api/platform/__tests__/route.functional.test.ts
harness-backend-dev
harness-frontend-dev
harness-qa
python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.agents/skills/harness/bin/check-domain.py --resolve /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform/apps/web/src/mastra/__tests__/platform.integration.test.ts
harness-backend-dev
harness-frontend-dev
harness-qa
```

## Runner and evidence gaps

Current Kaya matrix has null commands for unit, functional, integration, component, ui, eval and typecheck, with stale root-suite detection. T-01 supplies actual executable node/DOM Vitest projects; T-02 proves assertions and zero-selection fail nonzero; T-09 cuts over commands/detection exactly once, shows no duplicate selection, demonstrates typecheck rejecting a real temporary error and restores it, and runs real suites/typecheck/lint/build/offline HTTP.

Component is needed for the actual static-page render; ui remains null because no interactive browser workflow is delivered. Eval remains null because no semantic extraction-quality contract is delivered. Both gaps remain explicit and #7 is not closed wholesale; a future required null runner is `not_met`, not a signed skip. No fake script/import tests, `true` commands or disguised collection-error evidence.

Offline integration controls only external provider/database I/O and proves real internal composition, not live persistence. T-08 uses the actual Next process and blank hosted/provider values plus a synthetic local token, so root dotenv loading cannot rehydrate privileged settings. CLI scripts use Node's `react-server` condition for legitimate server-only imports. Live schema application requires explicit matching-project confirmation and real TLS; pg catalogs must contain actual adapter relations, not merely an empty schema. Data API non-exposure requires a successful public API-root control and HTTP 406/PGRST106 for `Accept-Profile: mastra`, not any generic failure. Runtime singleton/pool bounds, storage-success-before-response, server resource/thread isolation, 256-token output, 30-second provider deadline and no automatic retries are explicit task contracts. Nothing here is a claim that those implementations or live checks already work.

## Compatibility research, not a proven matrix

Inherited candidate releases from `notes/research-draft-plan.md`: Next/@next/env 16.3.8, Mastra core 1.74.0/memory 1.35.0/pg 1.29.0, Anthropic SDK 3.0.103, Supabase JS 2.117.2, pg 8.23.1, pnpm 11.2.2, Node 24 LTS and `claude-sonnet-5-5`. These are **candidates**, not pins validated by this planning run. T-01 must inspect exact-release engines/peers/types, choose an exact Node patch plus real React/TypeScript/Zod/test-tool dependencies, pin all direct versions and stop on accepted-stack incompatibility rather than substituting technology. T-10 documents the actual chosen and exercised matrix.

Primary references read for this redraft:
- [Supabase connection methods](https://supabase.com/docs/guides/database/connecting-to-postgres): persistent local backend direct IPv6 or session pooler IPv4 on 5432; 6543 is transaction pooling; preserve certificate verification, never disable it to cure connectivity.
- [Supabase custom-schema exposure](https://supabase.com/docs/guides/api/using-custom-schemas): exposed-schema API configuration and SQL grants are separate controls.
- [PostgREST error reference](https://docs.postgrest.org/en/stable/references/errors.html): PGRST106/406 is a schema not configured for exposure; 404 relation/JWT/network errors prove something different.
- [server-only marker](https://www.npmjs.com/package/server-only): server-component-only marker, not a guard to remove for CLI convenience. Exact package exports/type/API compatibility remains T-01 research.

## Plan mutation receipts

All plan writes used authorized repaired `plan-merge.py` only. Every task-changing invocation captured and printed stdout in the tool transcript. Successful mutations printed `APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml`; no invocation printed `APPROVAL-RESET:`. No approval block was authored or mutated, and no forbidden status-sync/build-entry/issue-mirror action was taken.

Ordered operation ledger (stdout receipt descriptions here are summaries, not fabricated full-output copies):

1. `delete-items` all seven old tasks: exit 5, refused because an empty task list is illegal; no write.
2. `delete-items` T-01..T-06: exit 4, refused dangling T-07 predecessor edges; no write.
3. `apply --proposal -`, T-07 `depends_on: []`: exit 0, printed `REPLACED T-07.depends_on: ['T-03', 'T-05', 'T-06'] -> []`, then APPLIED.
4. `delete-items` T-01..T-06 with reason `Replace unsigned flat-src implementation tasks with disjoint workspace ownership and test-first ordering`: exit 0, printed six DELETED records, DELETED-ITEMS 6, then APPLIED.
5. `apply` first replacement proposal: exit 0, ADDED T-01..T-06, REPLACED D-01/D-02 choice/because records, APPLIED.
6. `delete-items` T-07 with reason `Retire obsolete documentation task before appending workspace tasks in dependency order`: exit 0, DELETED tasks:T-07, DELETED-ITEMS 1, APPLIED.
7. `apply` final tasks proposal: exit 0, ADDED T-07..T-10, APPLIED.
8. `set-lanes`: exit 0, LANES 25 row(s) at the control pin, APPLIED.
9. `apply` first proposal after QA suffix correction: exit 0, preserved decisions/T-03..T-06; replaced T-01 intent, T-02 files/intent; APPLIED. Full captured tool output: `artifact://100`.
10. `apply` final proposal matching runner detection: exit 0, preserved T-07/T-08/T-10; replaced T-09 intent; APPLIED. Full captured tool output: `artifact://101`.
11. `apply` first proposal adding root CLI dependency/server-only condition contract: exit 0, preserved decisions/T-02..T-06, replaced T-01 intent; APPLIED. Full captured tool output: `artifact://105`.
12. `apply` final proposal tightening offline blank settings and exact Data API evidence: exit 0, preserved T-07/T-09/T-10, replaced T-08 intent; APPLIED. Full captured tool output: `artifact://106`.
13. `set-lanes` narrowing QA subsystem lane to actual `*.test.ts`: exit 0, LANES 25 row(s) at the control pin, APPLIED.
14. `apply` first proposal clarifying that local-token comparison may read its configured token but must precede full hosted-setting validation/privileged-client creation/external calls: exit 0, preserved decisions/T-01/T-03..T-06, replaced T-02 intent; APPLIED. Full captured tool output: `artifact://110`.

Temporary proposal documents were PM-owned merge inputs, not deliverable or product scaffolds, and are removed after use. Existing historical research/run records remain untouched.

The automatic post-write check-state diagnostics explicitly reported unapproved BRIEF, pending plan approval, and INV-37 missing build-entry; also historical missing run dirs/unrelated STATE notes. Those are not a clean global-state receipt. Creating a build entry or changing approvals is outside this planning contract and was not attempted. The final canonical structural check below is the only claimed plan-check success.

## Canonical check — exact command and final output

```text
python3 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml --root /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform --code-root /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform
```

```text
OK T-01 14 anchor(s) resolved
OK T-02 11 anchor(s) resolved
OK T-03 4 anchor(s) resolved
OK T-04 1 anchor(s) resolved
OK T-05 3 anchor(s) resolved
OK T-06 1 anchor(s) resolved
OK T-07 2 anchor(s) resolved
OK T-08 1 anchor(s) resolved
OK T-09 1 anchor(s) resolved
OK T-10 3 anchor(s) resolved
CHECK /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml against /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform: 10 task(s), 41 anchor(s) resolved, 0 failure(s)
```

**Exit: 0.** Final complete lane-pinned contract check elapsed 1.94 seconds. Earlier authorized structural checks also passed before subsequent planning refinements. No product install/build/lint/test/formatter or live probe was run. Reader-wave evidence and the user's approvals remain the next gates; simplification readers belong to the lead before signature.

## Principles applied

- `harness-craft/experience-first`: define the usable fresh-clone command/API loop and honest restart demonstration before file scaffolding; static landing is a design-review proposal, not automatic waiver.
- `harness-craft/redesign-from-first-principles`: replace the obsolete root-generator plan with the binding workspace/server/operational-data boundaries; no compatibility shim or speculative package tree.
- Test-first and evidence discipline: QA owns actual red behavioral tests before production, offline composition never stands in for live provider/persistence/permissions, and an unsigned plan is not permission to build.
