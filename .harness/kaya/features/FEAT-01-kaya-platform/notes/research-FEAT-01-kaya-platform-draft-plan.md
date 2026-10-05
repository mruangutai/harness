# Kaya #14 — platform draft research and planning receipts

## Result

BLOCKED, not signature-ready. BRIEF.md and the draft plan.yaml describe the operator-confirmed local platform destination. The exact required planning check returned exit 2, not 0. The canonical apply command also wrote a draft that its own post-check says cannot load because the pending-plan verify-command grammar excludes pnpm. No refusal was bypassed, no alternate check root was used, no product manifest was copied, and no approval/reset/signature/gh-sync/build-entry action was performed. Proposed signature decisions remain pending, not awaiting_user.

## Roots, identity and observed repository state

- Stable feature: FEAT-01-kaya-platform; source issue: mruangutai/kaya#14.
- Control-plane root: /Users/molchairuangutai/GitHub/harness. Canonical skill/tool paths used its .agents/skills/harness tree, not the worktree copy. Observed control HEAD: 6927e0527147cfb2d5593ccefd4a31c8b542e344.
- Feature root confirmed by canonical inflight_registry.py feature-root --feature FEAT-01-kaya-platform: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform.
- Artifacts exclusively under .harness/kaya/features/FEAT-01-kaya-platform in that root. No .harness/harness/features artifact was written.
- Read-only code root: /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform; assigned source pin 96b391233ac5481225978eaba5201597cae32a5e. Listing showed README.md, .gitignore, .harness/harness.json and docs/{SPEC,ARCHITECTURE,DECISIONS}.md; no package manifest, src/, tests/, supabase/ or CLAUDE.md. Product intentionally has no .harness/team-config.yaml.
- Intake: feature-tree .harness/notes/grilling-kaya-platform-2026-10-05.md. Provider is Anthropic; accepted stack decisions are not research questions. Available Node 26.0.0/pnpm 11.2.2 and a classified direct-5432 database endpoint are intake facts, not exercised compatibility/connectivity evidence. No credential value was read/copied/output.
- Open issue list distinguished platform #14 from runtime/production #7, storage/durable ingestion #8, extraction #9, chat #10 and Gmail #12. Platform does not close those work items. The issue’s old open provider/ADR wording is superseded by accepted Kaya records and operator intake; its latest/init suggestion is not a reproducibility contract.

## Accepted contract and scope

Kaya docs/DECISIONS.md DEC-002 fixes Mastra orchestration inside Next.js server routes; DEC-010 fixes existing hosted Kaya Supabase and @mastra/pg PostgresStore, isolated from the Data API; DEC-011 fixes Next.js, TypeScript and pnpm. DEC-009 prevents technology replacement to hide an integration failure. DEC-000 rejects retired-product scope. DEC-008 makes Kaya docs authoritative. DEC-012/013 remain binding for later chat but do not require chat packages/renderers in this platform feature.

The user-visible loop is fresh clone → private setup → localhost landing → authorized real Anthropic request → saved operational exchange → process restart → readback from the same hosted project. A separate hosted probe establishes actual Supabase server connectivity and specific Mastra-schema non-exposure. The model/provider are not placeholders or canned fallbacks; the initial agent is deliberately small and tool-free. Operational conversation memory is not a financial source of truth.

The five application names are ANTHROPIC_API_KEY, SUPABASE_PROJECT_URL, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_DB_URL and KAYA_API_STUB_TOKEN. Names/empty examples may be committed; values remain ignored/server-only. Local bearer authorization is a bounded platform probe boundary, not a premature login/account authorization design. Hosted writes require explicit project confirmation; a wrong project is a failure, not a fallback.

Out of scope: Gmail retrieval, extraction, financial tables, login/full chat UI, deployment, queues/background workers, unrelated spike closure and accepted-stack replacement. The future runtime/deployment, financial permissions and durability contracts remain unsolved by design, not silently declared complete.

## External evidence: candidates, not exercised compatibility

Observed metadata and official references on 2026-10-05:

| Item | Observation | Limit / planned closure |
| --- | --- | --- |
| Next | [Next npm metadata](https://registry.npmjs.org/next/latest): 16.3.8, Node >=20.9.0, React peers support ^19.0.0 (also React 18/RC alternatives). @next/env is 16.3.8. | T-01 chooses exact compatible React/type/tool versions, then T-02 records exact pins/lockfile. No Next install/build was run. |
| Mastra core | [Core npm metadata](https://registry.npmjs.org/@mastra%2fcore/latest): 1.74.0, Node >=22.13.0, Zod ^3.25 or ^4.0. Its dev aliases include Anthropic 3.0.103 for SDK v6 and 4.0.22 for v7. | Dev aliases establish candidate test coverage in the package manifest, not proof of this application or a blanket latest-provider guarantee. T-01 inspects exact-release types and API compatibility. |
| Postgres adapter | [Adapter metadata](https://registry.npmjs.org/@mastra%2fpg/latest): 1.29.0, Node >=22.13.0, core peer >=1.68.0 <2.0.0, pg dependency ^8.22.0. | Candidate core 1.74.0 and pg 8.23.1 fit declared ranges. Exact lifecycle, schema initialization, readback and persistence still need versioned API checks and tests. |
| Memory | [Memory metadata](https://registry.npmjs.org/@mastra%2fmemory/latest): 1.35.0, Node >=22.13.0, core peer >=1.4.1 <2.0.0, Zod ^4.6.4. | T-01 must intersect this with provider/core Zod constraints and pin one exact version; do not omit the transitive/API constraint. |
| Anthropic provider | [Exact provider 3.0.103](https://registry.npmjs.org/@ai-sdk%2fanthropic/3.0.103): Node >=18 and provider v3 dependencies. [Latest provider metadata](https://registry.npmjs.org/@ai-sdk%2fanthropic/latest) was 4.0.71 with Node >=22 and provider v4 dependencies. | Choose 3.0.103 as a bounded candidate associated with the inspected core v6 alias, not latest indiscriminately. Use it through Mastra, no separate AI SDK backend. A complete exact-package API contract remains T-01 work. |
| Supabase | [Supabase JS metadata](https://registry.npmjs.org/@supabase%2fsupabase-js/latest): 2.117.2, Node >=22. | Constructing a client is not proof of connectivity or safe privileges. The named live probe exercises the service against the real existing project. |
| pg | [pg metadata](https://registry.npmjs.org/pg/latest): 8.23.1, Node >=16; satisfies adapter ^8.22.0. | Declared range fit is not SQL/TLS/session-mode verification. |
| pnpm | [Exact pnpm 11.2.2 metadata](https://registry.npmjs.org/pnpm/11.2.2): Node >=22.13.0. Publication under Node 26.0.0 was observed. | Publication runtime is not this repo’s tested runtime. Pin it explicitly and exercise frozen install only in implementation/UAT. |
| Node | [Node previous-releases page](https://nodejs.org/en/about/previous-releases) listed Node 24.21.0 as LTS; Node 26 was Current. | Node 24.21.0 is the candidate LTS satisfying the known intersection. Exact support package constraints and actual exercise remain required; no claim that the available Node 26 is supported. |
| Model | [Anthropic model overview](https://platform.claude.com/docs/en/models/overview) listed claude-sonnet-5-5 as a current snapshot identifier. [Mastra Anthropic catalog](https://mastra.ai/models/providers/anthropic) listed anthropic/claude-sonnet-5-5 and ANTHROPIC_API_KEY automatic loading. | Prefer that current documented model over a near-retirement older candidate. Versioned provider support and account access are separate gates; metadata does not certify billing/availability. |

These latest metadata URLs are observed research inputs, not immutable evidence for a future install. T-01 must cite exact-version endpoints/published types for the candidate matrix and finish all unspecified React/TypeScript/Zod/server-only/ESLint/Vitest/tsx/@types pins before T-02. An accepted-stack incompatibility stops dependent tasks; it is not permission to replace technologies. T-01 is bounded integration research, not another destination decision or open-ended spike.

## Integration and connection evidence

- [Mastra Next integration](https://mastra.ai/integrations/frameworks/next-js) documents direct server-route Agent invocation and Node >=22.13.0. Its additional AI Elements/chat examples are not authorized platform scope and must not be copied. No standalone Mastra HTTP server is needed.
- [Agent.generate](https://mastra.ai/reference/agents/generate) documents memory thread/resource options and modelSettings output/time/retry bounds. A nonstream JSON route does not establish chat streaming protocol compatibility; that remains later work.
- [PostgreSQL integration](https://mastra.ai/integrations/databases/postgresql) documents PostgresStore connectionString/pool, schemaName (default public), initialization, TLS and reusable pool semantics. Default public is explicitly prohibited by Kaya. Provided pool lifecycle belongs to its owner; server/HMR reuse matters locally. Latest docs alone do not settle exact-release readback/init signatures.
- [Supabase Postgres connection guide](https://supabase.com/docs/guides/database/connecting-to-postgres) distinguishes direct-5432 (IPv6 unless an IPv4 add-on), session pooler-5432 (IPv4 and persistent connection semantics) and transaction pooler-6543 (limited session/prepared-statement compatibility). A persistent local Next server does not need transaction mode. Direct/session selection is explicit setup based on actual network reachability, not silent runtime retry/fallback. Session endpoint/user must come privately from the same Kaya project dashboard, not a guessed region/credential template.
- SQL role revocation and a non-public schema are necessary, not sufficient: Supabase’s exposed-schema setting must independently exclude mastra. The live probe must distinguish specific unexposed-schema rejection from generic authorization or network failure.
- Privileged service credentials and database connections do not represent browser RLS authorization. Source/test/client-canary checks and future account authorization cannot be replaced by successful model output.

## Principles applied

Consulted harness-craft and its experience-first reference. Start with the operator’s reproducible command loop and explicit failure observations, not a module inventory or a decorative UI phase. A static non-chat page plus API/CLI loop is the actual platform interface; no visual prototype/design phase is needed. Secret isolation, narrow schema ownership, one provider path, and server-lifetime client reuse are structural controls, not an extra abstraction layer. Accepted choices are not re-opened; unknown exact APIs are bounded before implementation. Compatibility metadata, QA execution, pinned inspection, and personal UAT are distinct evidence classes.

## Draft plan mapping and routing

Seven proposed tasks, two pending trade-off decisions. Task file ownership is disjoint:

- T-01: bounded exact-release compatibility report, docs/platform-compatibility.md; harness-documentor.
- T-02: package/lock/runtime/Next/tool root configuration and empty settings/ignore files; main-session-direct because shared/ungranted root configuration has no single domain owner.
- T-03: src/app static page and protected server route plus src/server environment/agent/storage/Supabase lifecycle; harness-backend-dev.
- T-04: operational-only supabase/migrations SQL; harness-data-engineer.
- T-05: tests, tooling contract and credential-safe operator CLI; harness-backend-dev. All test ownership stays here, not split with T-03.
- T-06: .harness/harness.json runner cutover; explicitly main-session-direct, not a squad edit.
- T-07: README.md and docs/PLATFORM.md local operation/evidence documentation; harness-documentor.

Canonical domain manifest inspected at control pin 6927e0527147cfb2d5593ccefd4a31c8b542e344. Frontend grant is web/src/**, not this proposed src/** tree; backend owns src/** and tests/**. The data grant covers supabase/migrations/**. Docs/README belong to documentor. Shared package/lock/TypeScript configs and ungranted root files are serialized main-session writes. Although the general dev-ops grant lists product .harness/harness.json, this assignment explicitly requires its main-session-direct landing seam. No team-config copy is allowed by DEC-221.

Trace coverage is proposed, not shipped: operator SC-01/02/03 have task traces and future personal UAT; maintainer SC-04/05/06/07 have task traces and pinned-source inspection. All outcomes are not_met today. No QA DIGEST/review receipt exists for product implementation; no automated pass or UAT-ready status is asserted. All current required kinds are null, so the BRIEF does not pretend they already supply automated SC evidence. T-02/T-05/T-06 explicitly define honest scripts, test discovery, failure exits and runner cutover; component/ui/eval remain unconfigured and out of this feature’s behavior claims.

### Draft defects that must be corrected before signature

The canonical refusal prevents treating this plan as a fully checked handoff. In addition to tool compatibility repair, the draft sequencing needs correction under the governed edit tools: T-02 currently verifies via a T-05 file, T-04 verification waits for later tests, and T-05 final cumulative verification depends on T-03/T-06 while T-06 depends on T-05. These commands are explicitly deferred in intent, but a real task graph must instead separate red-first fixture delivery from final cumulative verification or provide task-local prerequisite checks, so no task requires a completed successor to receive its own PASS. T-03 needs a formal red-test dependency before production edits, not merely coordination prose. No production work is authorized while this remains unresolved. The written drafts are retained as evidence of the failed bootstrap, not promoted as signed/ready.

BRIEF Approval is main-session-owned and absent by this dispatch’s no-approval-write rule. Main must insert pending Approval; PM did not author it. plan-merge bootstrap supplied approval.status pending automatically when the proposal omitted approval. PM supplied no approval mapping, signature, review_sha or reset acknowledgement.

## Exact governed receipts

### Task-changing invocation: canonical apply

Invocation: current canonical plan-merge.py apply --file <feature>/plan.yaml --proposal -, supplied one draft YAML proposal via printf stdin, with no approval key. Tool displayed command exit 0 and the following complete output. APPLIED is the captured successful-write stdout. The tool also emitted post-check diagnostics; no APPROVAL-RESET: receipt appeared, so no gh-sync status was attempted.

```text
check-state --changed after /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml:
  VIOLATION  .harness/kaya/features/FEAT-01-kaya-platform/plan.yaml does not load, so INV-3/4/5 cannot be checked for it: failed to parse YAML in /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml: tasks[] (T-02) verify: 'pnpm exec tsx tests/tooling-contract.ts' is neither runnable nor manual — accepted forms are `MANUAL — <what must be built>` (em dash) or a command/path invocation
  VIOLATION  .harness/kaya/features/FEAT-01-kaya-platform/BRIEF.md has no '## Approval' section — cannot tell if the goal is signed.
  VIOLATION  INV-29: /Users/molchairuangutai/GitHub/harness/.claude/worktrees/skill-optimization is a standing worktree whose terminal status could not be determined — worktree path is not under WORKTREES_SEGMENT. A lookup that FAILED is not an exemption; the worktree is reported rather than passed over. The tree is dirty: `remove` will DECLINE until those changes are committed, landed or discarded. Its path did not resolve to a repository and id, so no removal command can be composed for it.
  note       FEAT-01-kaya-platform: run r-20261004-1 is referenced but its dir is absent (pruned, or never created).
  note       FEAT-01-kaya-platform: run 2026-10-04-1-product is referenced but its dir is absent (pruned, or never created).
  note       INV-23 .harness/harness/features/FEAT-02/STATE.md has illegal section(s) ['## Feature', '## Mission', '## Success criteria (binding; pm may refine wording, not weaken)', '## Constraints', '## Log'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md is 170 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-05-pyyaml-file-parsers/STATE.md has illegal section(s) ['## Landed', '## Two rulings LANDED, 2026-08-03 — both were mine to raise, neither mine to decide', '## Carried forward', '## Backlog nit — not fixed here', '## Cost'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md is 153 lines — budget is 120. It holds no history: ## Current is replaced, never appended (DEC-150).
  note       INV-23 .harness/harness/features/FEAT-43-code-risk-grading/STATE.md has illegal section(s) ['## Cycle 29 — the origin/main reconciliation and the count-predicate defect', '## Cycle 28 — the crash class, CLOSED', '## Cycle 27 — the CI blocker, and what fixing it uncovered'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
  note       INV-23 .harness/harness/features/FEAT-59-proportional-flow/STATE.md has illegal section(s) ['## Open questions', '## Pointers'] — STATE.md is `## Current` + `## Open Questions` and nothing else (SPEC §2).
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
```

The task-changing stdout receipt itself is exact:

```text
APPLIED /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml
```

Canonical harness_yaml.py:328-329 lists bare commands cd/set/python3/bash/git/grep/test/diff/true/false; pnpm/node are absent. This is not evidence that pnpm is unavailable. A tool inconsistency report was submitted to xd://report_issue for APPLIED exit 0 after a schema-invalid bootstrap write. No wrapper, alternate command grammar, manual file edit or dependency installation was used to evade the refusal.

### Required planning check

Exact command executed once:

```sh
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/plan-merge.py check --file /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-01-kaya-platform/.harness/kaya/features/FEAT-01-kaya-platform/plan.yaml --root /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform
```

Exit: 2. Exact displayed refusal:

```text
plan-merge: /Users/molchairuangutai/GitHub/harness-factories/kaya/.claude/worktrees/kaya/FEAT-01-kaya-platform carries no .harness/team-config.yaml, so no route can be resolved against it — --root must be a harness checkout.
```

Canonical plan_merge/check.py _check_inputs requires harness_boundary.MARKER, defined as .harness/team-config.yaml. check-plan-routes resolution likewise expects an owner-root manifest. This conflicts with the exact assigned product root and DEC-221’s central manifest/product-only JSON boundary. A root switch would not prove the product files; copying a manifest would violate the assignment. Missing src/tests/supabase parent directories also do not satisfy canonical plan_anchors bare-file resolution. The inspected grammar is path, path#symbol or {path, quote}; it has no create annotation for absent directories. These are tooling prerequisites, not permission to fabricate anchor success or write product directories during planning.

### Verification not performed

No product installation, build, lint, test, formatter, smoke, live hosted request or credential read occurred. Only planning/governance commands and research reads ran. No product code/config was written. No APPROVAL-RESET: was emitted or acknowledged, so no issue status sync was performed. Unrelated existing global check-state notes/violations were preserved as observations, not modified.

## Exact missing prerequisites / next owner

1. Main/control-plane owner must provide a governed canonical check path that actually resolves the assigned onboarded product --root against the current central manifest, while respecting DEC-221; this PM cannot substitute roots/copy manifests.
2. Canonical pending verify grammar/bootstrap validation must accept genuine pnpm/node invocations or otherwise supply an explicitly governed correction path for the already-written invalid draft. Do not claim current plan load success.
3. Governed anchor handling must support planned creation under absent product directories without fake existing files or unauthorized planning product writes.
4. Main session must provide BRIEF pending Approval, then task-local red-first sequencing and cumulative verification must be corrected through canonical plan editing before a zero check and signature request. No approval is requested from the user yet; proposed trade-off decisions remain pending.

The product destination is understandable and technically plausible by published constraints, but these prerequisites make this dispatch BLOCKED. Research and draft artifacts are not a substitute for the required exit-zero receipt.
